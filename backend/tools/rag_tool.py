from langchain_core.tools import tool
from rag.rag_summary import rag_summary
from utils.logger import setup_logger

logger = setup_logger(__name__)


@tool
def search_knowledge_base(question: str) -> str:
    """从扫地机器人知识库中检索相关信息回答问题。

    适用场景：
    - 用户询问故障排除方法（如：机器人无法开机、吸力不足、无法回充等）
    - 用户询问使用技巧或最佳实践
    - 用户询问产品参数、配件信息、维护保养方法
    - 任何需要从产品知识库中查找答案的问题

    Args:
        question: 用户的具体问题，应包含足够的上下文信息。

    Returns:
        基于知识库检索结果生成的答案字符串。
    """
    logger.info(f"[RAG Tool] Searching knowledge base for: {question[:80]}")
    return rag_summary(question)
