"""Pydantic 数据模型"""
from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    """对话请求"""
    question: str
    user_id: Optional[str] = "user_001"
    thread_id: Optional[str] = None


class ChatResponse(BaseModel):
    """对话响应"""
    answer: str
    thread_id: str
    sources: Optional[List[str]] = None


class UploadResponse(BaseModel):
    """上传响应"""
    success: bool
    message: str
    files_count: Optional[int] = None


class KnowledgeStatsResponse(BaseModel):
    """知识库统计"""
    total_documents: int
    total_chunks: int
    vector_store_ready: bool
