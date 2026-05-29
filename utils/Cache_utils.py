from typing import Dict
from utils.MD5_record import get_text_md5

# 模拟内存缓存：key=问题MD5，value=回答文本
_qa_cache: Dict[str, str] = {}

def get_question_cache(question: str) -> str | None:
    """根据问题获取缓存答案，命中返回答案，未命中返回 None"""
    q_md5 = get_text_md5(question)
    return _qa_cache.get(q_md5)

def set_question_cache(question: str, answer: str) -> None:
    """将 问题-答案 写入缓存"""
    q_md5 = get_text_md5(question)
    _qa_cache[q_md5] = answer

def clear_qa_cache() -> None:
    """清空问答缓存（运维/刷新知识库时用）"""
    _qa_cache.clear()