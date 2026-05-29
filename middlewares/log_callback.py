"""日志中间件：打印模型输入与工具调用。（LangChain 1.2+ middleware）"""

from langchain.agents.middleware import wrap_tool_call, wrap_model_call
from utils.logger import setup_logger

logger = setup_logger(__name__)


@wrap_tool_call
def log_tool_call(request, handler):
    """记录每个工具调用的输入和输出。"""
    tool_name = request.tool_call.get("name", "unknown") if hasattr(request, "tool_call") else "unknown"
    logger.info(f"[Tool Start] {tool_name} — input: {str(request.tool_call)[:200]}")
    try:
        result = handler(request)
        logger.info(f"[Tool End] output: {str(result)[:200]}...")
        return result
    except Exception as e:
        logger.error(f"[Tool Error] {e}")
        raise


@wrap_model_call
def log_model_call(request, handler):
    """记录每次 LLM 调用的输入。"""
    logger.info("[LLM Start] Processing...")
    result = handler(request)
    logger.info("[LLM End] Response received")
    return result
