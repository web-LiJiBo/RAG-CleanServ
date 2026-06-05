
from sentence_transformers import CrossEncoder

# 使用开源 “BGE中文重排模型”，本地运行无需额外接口
reranker = CrossEncoder("BAAI/bge-reranker-base")

# 文档（向量库召回的列表）重排函数
def rerank_documents(query:str, docs):
    """
    对检索文档做重排序
    :param query: 用户问题
    :param docs: 向量检索返回的文档列表
    :return: 按相关性从高到低排好序的文档列表
    """
    if not docs:
        return []
    # 构造[问题，文档]配对
    pairs = [[query,doc.page_content] for doc in docs]
    # 重排模型打分
    scores = reranker.predict(pairs)
    # 按分数降序排序
    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)

    return [doc for doc, _ in ranked]