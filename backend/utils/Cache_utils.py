from typing import Dict, List, Optional

from langchain_openai import ChatOpenAI

from utils.MD5_record import get_text_md5
from utils.config import get_llm_config

# 【MD5缓存】：key=问题MD5，value=回答文本
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


# 【新】===================== 标签语义缓存模块 =====================

# 【标签缓存】：列表，每个元素为字典 {"tags": [标签列表], "answer": 对应回答}
_tag_cache: List[Dict] = []

# 复用项目统一LLM配置
def get_cache_llm():
    llm_cfg = get_llm_config()
    llm_kwargs = dict(
        model=llm_cfg["model_name"],
        api_key=llm_cfg["api_key"],
        base_url=llm_cfg["base_url"],
        temperature=0.0
    )
    return ChatOpenAI(**llm_kwargs)

def generate_question_tags(question: str) -> List[str]:
    """
    基于LLM提取用户问题的业务意图标签
    用于后续语义匹配，区分故障、操作、报错等意图
    :param question: 用户原始问题
    :return: 清洗后的标签字符串列表
    """
    llm = get_cache_llm()
    prompt = f"""
            你是扫地机器人客服，提取用户问题3-5个简短关键词标签，英文逗号分隔，只输出标签。
            分类：故障部位、故障现象、报错代码、操作咨询、使用问题。
            用户问题：{question}
            标签：
            """
    res = llm.invoke(prompt)
    # 按逗号分割 + 去除空格 + 过滤空字符串，得到标准标签列表
    tags = [t.strip() for t in res.content.split(",") if t.strip()]
    return tags

def calc_jaccard(set_a: set, set_b: set) -> float:
    """
    计算两组标签集合的杰卡德相似度
    公式：交集元素数 / 并集元素数，取值范围 [0, 1]，越接近1代表语义越相似
    :param set_a: 当前用户标签集合
    :param set_b: 缓存中历史问题标签集合
    :return: 相似度浮点值
    """
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union != 0 else 0.0

# 根据标签相似度匹配历史缓存回答
def match_by_tags(user_tags: List[str], threshold: float = 0.6) -> Optional[str]:
    """
    阈值控制匹配严格程度，超过阈值则判定为同义问题
    :param user_tags: 当前用户问题标签列表
    :param threshold: 相似度阈值，默认0.6
    :return: 匹配成功返回对应回答，匹配失败返回 None
    """
    user_set = set(user_tags)
    best_ans = None  # 记录最优回答
    max_score = 0.0

    # 遍历所有标签缓存数据
    for item in _tag_cache:
        tag_set = set(item["tags"])
        # 计算标签相似度
        score = calc_jaccard(user_set, tag_set)
        # 超过阈值
        if score > threshold and score > max_score:
            max_score = score
            best_ans = item["answer"]
    return best_ans

def set_cache_with_tags(question: str, answer: str) -> None:
    """
    统一写入接口：同时更新 MD5精确缓存 + 标签语义缓存
    一次调用完成两套缓存落地
    :param question: 用户原始问题
    :param answer: 模型生成的回答
    """
    # 写入原有MD5缓存
    set_question_cache(question, answer)
    # 生成标签并写入标签缓存
    tags = generate_question_tags(question)
    _tag_cache.append({"tags": tags, "answer": answer})

def get_combined_cache(question: str) -> Optional[str]:
    """
    双层缓存统一查询入口（对外主接口）
    执行顺序：优先MD5精确匹配(速度最快) → 未命中再走标签语义匹配(兼容同义问法)
    :param question: 用户原始问题
    :return: 任意一层缓存命中则返回回答，全部未命中返回 None
    """
    # 1. 精确MD5匹配
    exact_hit = get_question_cache(question)
    if exact_hit:
        return exact_hit
    # 2. 标签语义匹配
    user_tags = generate_question_tags(question)
    semantic_hit = match_by_tags(user_tags)
    return semantic_hit