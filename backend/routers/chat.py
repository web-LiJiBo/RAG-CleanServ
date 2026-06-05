"""对话服务路由"""
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from schemas import ChatRequest, ChatResponse
from agent.agent_builder import build_agent
from agent.executor import execute_sync, execute_stream
from tools.rag_tool import search_knowledge_base
from tools.date_tool import get_current_date
from tools.weather_tool import get_weather
from tools.user_tools import get_current_user_id, get_user_location, set_user_context
from tools.external_data_tool import get_user_usage_records
from tools.report_tool import generate_usage_report
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

# 全局 agent 实例
_agent_instance = None
_checkpointer_instance = None


def get_tools():
    """获取工具列表"""
    return [
        search_knowledge_base,
        get_current_date,
        get_weather,
        get_current_user_id,
        get_user_location,
        get_user_usage_records,
        generate_usage_report,
    ]


def get_or_create_agent():
    """获取或创建 agent 实例"""
    global _agent_instance, _checkpointer_instance
    if _agent_instance is None:
        tools = get_tools()
        _agent_instance, _checkpointer_instance, _ = build_agent(tools)
        logger.info(f"Agent 初始化完成，共 {len(tools)} 个工具")
    return _agent_instance, _checkpointer_instance


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """对话接口（同步）"""
    try:
        thread_id = request.thread_id or uuid.uuid4().hex[:12]

        # 设置用户上下文
        set_user_context(request.user_id)

        agent, _ = get_or_create_agent()
        answer = execute_sync(agent, request.question, thread_id)

        return ChatResponse(
            answer=answer,
            thread_id=thread_id
        )

    except Exception as e:
        logger.error(f"对话处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """对话接口（流式）"""
    try:
        thread_id = request.thread_id or uuid.uuid4().hex[:12]

        # 设置用户上下文
        set_user_context(request.user_id)

        agent, _ = get_or_create_agent()

        async def stream_generator():
            for chunk in execute_stream(agent, request.question, thread_id):
                yield f"data: {chunk}\n\n"

        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream"
        )

    except Exception as e:
        logger.error(f"流式对话处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
