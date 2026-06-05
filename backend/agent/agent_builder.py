"""Agent 构建器：组装工具、记忆、中间件，创建 Agent 实例。（LangChain 1.2+）"""

from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_openai import ChatOpenAI

from utils.config import get_llm_config
from utils.logger import setup_logger
from middlewares.prompt_switch import get_active_prompt
from middlewares.monitor_callback import create_monitor_middleware

logger = setup_logger(__name__)


def build_agent(tools: list, verbose: bool = True):
    """创建并返回配置好的 Agent 实例。（LangChain 1.2+ create_agent）

    Args:
        tools: LangChain Tool 列表。
        verbose: 保留参数，兼容旧接口。

    Returns:
        (agent, checkpointer, monitor_stats) 三元组。
    """
    llm_cfg = get_llm_config()
    llm_kwargs = dict(
        model=llm_cfg["model_name"],
        api_key=llm_cfg["api_key"],
        base_url=llm_cfg["base_url"],
        temperature=llm_cfg.get("temperature", 0.7),
        max_tokens=llm_cfg.get("max_tokens", 2048),
    )
    if llm_cfg.get("extra_body"):
        llm_kwargs["extra_body"] = llm_cfg["extra_body"]
    if llm_cfg.get("model_kwargs"):
        llm_kwargs["model_kwargs"] = llm_cfg["model_kwargs"]
    llm = ChatOpenAI(**llm_kwargs)

    system_prompt = get_active_prompt()

    checkpointer = MemorySaver()

    monitor_middlewares, stats = create_monitor_middleware()

    # 历史对话自动压缩中间件
    summarization = SummarizationMiddleware(
        model=llm,
        trigger=[("tokens", 3000), ("messages", 20)],
        keep=("messages", 10),
    )

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        middleware=[*monitor_middlewares, summarization],
        checkpointer=checkpointer,
    )

    logger.info(f"Agent built with {len(tools)} tools, memory enabled, summarization on")
    return agent, checkpointer, stats
