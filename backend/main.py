"""FastAPI 应用入口"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from utils.config import setup_huggingface_mirror
from utils.logger import setup_logger
from routers import knowledge, chat

setup_huggingface_mirror()
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("RAG-CleanServ Backend 启动")
    yield
    logger.info("RAG-CleanServ Backend 关闭")


app = FastAPI(
    title="RAG-CleanServ API",
    description="扫地机器人智能客服系统 - 后端 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(knowledge.router, prefix="/api/knowledge", tags=["知识库管理"])
app.include_router(chat.router, prefix="/api/chat", tags=["对话服务"])


@app.get("/")
async def root():
    return {"message": "RAG-CleanServ API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
