from langchain_core.documents import Document

def rrf_fusion(list_a: list[Document], list_b: list[Document], k: int = 60) -> list[Document]:
    """RRF 倒数排序融合，自动去重"""
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