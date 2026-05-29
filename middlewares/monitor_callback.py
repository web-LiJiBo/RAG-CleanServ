"""工具执行监控中间件：记录每个工具的执行耗时与结果。（LangChain 1.2+ middleware）"""

import time
from langchain.agents.middleware import wrap_tool_call, wrap_model_call
from utils.logger import setup_logger

logger = setup_logger(__name__)


def create_monitor_middleware():
    """创建监控中间件，返回 (middleware_list, stats_list)。

    stats_list 会被实时追加工具调用记录，每条格式：
        {"tool": str, "elapsed_seconds": float, "status": "success|error"}
    """
    stats = []

    @wrap_tool_call
    def monitor_tool(request, handler):
        tool_name = request.tool_call.get("name", "unknown") if hasattr(request, "tool_call") else "unknown"
        start = time.time()
        try:
            result = handler(request)
            elapsed = round(time.time() - start, 3)
            logger.info(f"[Monitor] Tool '{tool_name}' completed in {elapsed}s")
            stats.append({"tool": tool_name, "elapsed_seconds": elapsed, "status": "success"})
            return result
        except Exception as e:
            elapsed = round(time.time() - start, 3)
            logger.error(f"[Monitor] Tool '{tool_name}' FAILED in {elapsed}s: {e}")
            stats.append({"tool": tool_name, "elapsed_seconds": elapsed, "status": "error", "error": str(e)})
            raise

    @wrap_model_call
    def monitor_model(request, handler):
        start = time.time()
        try:
            result = handler(request)
            elapsed = round(time.time() - start, 3)
            logger.info(f"[Monitor] LLM completed in {elapsed}s")
            stats.append({"tool": "LLM", "elapsed_seconds": elapsed, "status": "success"})
            return result
        except Exception as e:
            elapsed = round(time.time() - start, 3)
            logger.error(f"[Monitor] LLM FAILED in {elapsed}s: {e}")
            stats.append({"tool": "LLM", "elapsed_seconds": elapsed, "status": "error", "error": str(e)})
            raise

    return [monitor_tool, monitor_model], stats
