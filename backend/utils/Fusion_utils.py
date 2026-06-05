from langchain_core.documents import Document

def rrf_fusion(list_a: list[Document], list_b: list[Document], k: int = 60) -> list[Document]:
    """
    RRF 倒数排序融合算法，用于混合检索结果合并，并自动去重
    公式：RRF_score(d) = Σ 1 / (k + rank + 1)
    :param list_a: 第一路检索结果（如向量检索），按相关性降序排列
    :param list_b: 第二路检索结果（如BM25检索），按相关性降序排列
    :param k: 平滑常数，默认60，防止排名为0时分母为0，也可控制排名权重衰减速度
    :return: 融合后的文档列表，按RRF分数降序排列，已去重
    """
    doc_rank = {}
    # 第一路打分
    for rank, doc in enumerate(list_a):
        doc_id = id(doc)
        doc_rank[doc_id] = doc_rank.get(doc_id, 0) + 1 / (k + rank + 1)
    # 第二路打分
    for rank, doc in enumerate(list_b):
        doc_id = id(doc)
        doc_rank[doc_id] = doc_rank.get(doc_id, 0) + 1 / (k + rank + 1)

    # 按分数倒序
    sorted_items = sorted(doc_rank.items(), key=lambda x: x[1], reverse=True)
    doc_map = {id(d): d for d in list_a + list_b}

    # 去重
    seen = set()
    fused_docs = []
    for doc_id, _ in sorted_items:
        if doc_id not in seen:
            seen.add(doc_id)
            fused_docs.append(doc_map[doc_id])
    return fused_docs