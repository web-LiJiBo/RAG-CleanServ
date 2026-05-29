"""执行器：调用 Agent 并返回回答。（LangChain 1.2+）"""

from langchain_core.messages import HumanMessage
from utils.logger import setup_logger

logger = setup_logger(__name__)

# 同步执行，接收问题，返回结果
def execute_sync(agent, user_input: str, thread_id: str = "default") -> str:
    """同步执行 Agent，返回完整回答。

    Args:
        agent: create_agent 返回的 CompiledStateGraph。
        user_input: 用户输入文本。
        thread_id: 会话线程 ID，用于区分不同对话（checkpointer 以此隔离状态）。

    Returns:
        完整的回答字符串。
    """
    logger.info(f"[Executor] Input: {user_input[:100]}...")

    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
        )
        messages = result.get("messages", [])
        if messages:
            last_msg = messages[-1]
            return last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        return "抱歉，没有生成回答。"

    except Exception as e:
        logger.error(f"[Executor] Error: {e}")
        return f"抱歉，处理您的请求时出现了错误：{str(e)}"

# 逐段生成内容
def execute_stream(agent, user_input: str, thread_id: str = "default"):
    """流式执行 Agent，逐步 yield 输出块。
    Args:
        agent: create_agent 返回的 CompiledStateGraph。
        user_input: 用户输入文本。
        thread_id: 会话线程 ID。

    Yields:
        字符串形式的内容块。
    """
    logger.info(f"[Executor] Streaming input: {user_input[:100]}...")

    config = {"configurable": {"thread_id": thread_id}}

    try:
        for chunk in agent.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="values",
        ):
            messages = chunk.get("messages", [])
            if messages:
                last_msg = messages[-1]
                content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
                yield content
    except Exception as e:
        logger.error(f"[Executor] Error: {e}")
        yield f"抱歉，处理您的请求时出现了错误：{str(e)}"

# 删除会话记录
def clear_memory(checkpointer, thread_id: str = "default"):
    """清除指定会话的对话记忆。"""
    try:
        checkpointer.delete_thread(thread_id)
        logger.info(f"[Executor] Cleared memory for thread: {thread_id}")
    except Exception as e:
        logger.warning(f"[Executor] Failed to clear memory: {e}")
