import jieba
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document

# 全局单例变量：全局仅初始化一次BM25模型，避免重复构建索引消耗性能
_bm25_model: BM25Okapi | None = None
# 全局缓存全量文档列表，与BM25索引一一对应
_all_docs_cache: list[Document] | None = None

# 简易中文分词器
def simple_tokenize(text: str) -> list[str]:
    return jieba.lcut(text)

# 全局初始化BM25稀疏检索模型
def init_bm25(all_docs: list[Document]) -> None:
    """
     全局初始化BM25稀疏检索模型
     全局单例设计，服务生命周期内仅执行一次索引构建
     :param all_documents: 向量库中全量Document文档对象列表
    """
    global _bm25_model, _all_docs_cache
    # 模型已存在则直接返回，避免重复初始化
    if _bm25_model is not None:
        return

    #对所有文档执行分词，构建BM25语料库
    tokenized_corpus = [simple_tokenize(docs) for docs in all_docs]
    # 实例化BM25模型，构建倒排索引
    _bm25_model = BM25Okapi(tokenized_corpus)
    # 全局保存原始文档
    _all_docs_cache = all_docs

# 基于BM25算法做关键词检索召回
def bm25_retrieve(query: str, top_k: int) -> list[Document] :
    """
    基于BM25算法的关键词检索
    擅长精确关键词、专有名词、型号匹配，作为向量检索的补充
    :param query: 用户原始查询问题
    :param top_k: 需要召回的文档数量
    :return: 按相关性降序排列的Document文档列表；模型未初始化则返回空列表
    """
    # 校验模型和文档缓存是否完成初始化，未初始化直接返回空
    if _bm25_model is None or _all_docs_cache is None:
        return []

    #（1）先对用户问题执行分词
    tokenized_query = simple_tokenize(query)
    #（2）基于BM25计算每个向量文档与用户查询的相关分数
    scores = _bm25_model.get_scores(tokenized_query)
    #（3) 得到向量文档中分数从高到低的排序的下标
    sorted_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    #（4）截取前top-k个下标，返回对应的向量文档
    return [_all_docs_cache[idx] for idx in sorted_idx[:top_k]]










