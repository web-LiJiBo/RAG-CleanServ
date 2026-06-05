from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from rag.vector_store import load_vector_store
from utils.BM25_utils import init_bm25, bm25_retrieve
from utils.Cache_utils import get_question_cache, set_question_cache, set_cache_with_tags, get_combined_cache
from utils.config import get_llm_config, get_vector_store_config
from utils.Fusion_utils import rrf_fusion
from utils.logger import setup_logger
from utils.Rerank_docs import rerank_documents

logger = setup_logger(__name__)   #给每个文件单独创建日志器，用来**区分日志来自哪个代码文件**，方便排查问题。

"""
    2026年5月27日，修改RAG中召回模块，如下：
    
        用户问题
           ↓
        向量检索（召回 Top10）
           ↓
        重排模型打分 + 重新排序  【新增】
           ↓
        截取最终 Top3 最相关文档  【新增】
           ↓
        拼接上下文 + 送入 LLM
           ↓
        返回回答
"""

"""
    2026年5月29日上午，新增问题级MD5缓存，优化RAG召回模块，流程更新如下：
    
        用户问题
          ↓
        【问题级MD5缓存查询】
          ├─ 命中缓存 → 直接返回历史回答
          └─ 未命中缓存 → 进入RAG流程
               ↓
        向量检索（召回 Top10）
               ↓
        重排模型打分 + 重新排序
               ↓
        截取最终 Top3 最相关文档
               ↓
        拼接上下文 + 送入 LLM
               ↓
        生成回答并写入【问题级MD5缓存】
       ↓
返回回答
"""

"""
    2026年5月29日下午，升级为：MD5精确缓存 + 标签语义缓存 双层缓存
    流程更新如下：

        用户问题
          ↓
        【1. MD5精确缓存查询】
          ├─ 命中 → 直接返回
          └─ 未命中 → 【2. 标签语义缓存查询】
               ├─ 命中 → 直接返回
               └─ 未命中 → 进入完整RAG流程
                    ↓
        向量检索（召回 Top10）
               ↓
        BM25检索 + RRF融合
               ↓
        重排模型打分 + 重新排序
               ↓
        截取最终 Top3 最相关文档
               ↓
        拼接上下文 + 送入 LLM
               ↓
        生成回答并写入【MD5缓存 + 标签缓存】
       ↓
返回回答
"""



SUMMARY_PROMPT = ChatPromptTemplate.from_template(
"""
    你是一个专业的扫地机器人客服助手。请根据以下知识库检索结果，回答用户的问题。
    要求：
    - 回答准确、简洁，直接回应用户的问题。
    - 优先使用知识库中的信息，不要编造。
    - 如果知识库中的信息不足以回答问题，请诚实告知。
    - 对于操作步骤类问题，分步骤列出。
    
    知识库检索结果：
    {context}
    
    用户问题：{question}
    
    请回答：
""")

# 配置LLM
def get_llm():
    """获取 LLM 实例。"""
    llm_cfg = get_llm_config()
    llm_kwargs = dict(
        model=llm_cfg["model_name"],
        api_key=llm_cfg["api_key"],
        base_url=llm_cfg["base_url"],
        temperature=llm_cfg.get("temperature", 0.7),
        max_tokens=llm_cfg.get("max_tokens", 2048),
    )
    if llm_cfg.get("extra_body"):
        llm_kwargs["extra_body"] = llm_cfg["extra_body"]
    if llm_cfg.get("model_kwargs"):
        llm_kwargs["model_kwargs"] = llm_cfg["model_kwargs"]
    return ChatOpenAI(**llm_kwargs)

# 【新】核心RAG主逻辑
def rag_summary(question: str) -> str:

    vs_cfg = get_vector_store_config()
    vectorstore = load_vector_store()# 获取向量库
    retrieve_top = vs_cfg.get("retrieve_top", 10)  # 先检索召回10篇
    final_top = vs_cfg.get("final_top", 3)  # 重排后只是保留 Top-3

    # 【新】1 使用双层统一缓存查询
    cache_ans = get_combined_cache(question)
    if cache_ans is not None:
        return cache_ans

    # 【新】2.1 向量检索
    retriever = vectorstore.as_retriever(search_kwargs={"k": retrieve_top})
    docs = retriever.invoke(question)

    #【新】2.2初始化BM25 + BM25检索
    all_store_docs = vectorstore.get()["documents"]
    init_bm25(all_store_docs)
    bm25_docs = bm25_retrieve(question,retrieve_top)

    # 无结果兜底
    if not docs and not bm25_docs:
        return "抱歉，我在知识库中没有找到相关信息，建议您联系人工客服获取帮助。"

    #【新】2.3 RRF融合
    fused_docs = rrf_fusion(docs, bm25_docs)
    logger.info(f"向量召回:{len(docs)} 条, BM25召回:{len(bm25_docs)} 条, 融合后:{len(fused_docs)} 条")

    """
        向量库召回的docs是Python的list类型，列表中每个元素都是“Document”对象
        （1）docs[0]：第一条Document对象
        （2）docs[0].page_content：字符串。纯文本内容
        （3）docs[0].metadata：字典，附加信息
    """

    # 【新】3. 重排 + 截取最终 TopK
    reranked_docs = rerank_documents(question, fused_docs)  # 此时的fused_docs是更优质的向量文档
    top_k_docs = reranked_docs[:final_top]

    # 4.拼接上下文
    context = "\n\n---\n\n".join(
        f"[来源: {doc.metadata.get('source', '未知')}]\n{doc.page_content}"
        for doc in top_k_docs
    )

    # 5. 调用 LLM 生成回答
    llm = get_llm()
    chain = SUMMARY_PROMPT | llm
    response = chain.invoke({"context": context, "question": question})
    answer = response.content

    # 【新】6.写入缓存 + 写入标签缓存
    set_cache_with_tags(question, answer)

    return response.content  # 返回用户结果
