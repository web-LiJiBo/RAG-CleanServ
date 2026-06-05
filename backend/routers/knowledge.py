"""知识库管理路由"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from schemas import UploadResponse, KnowledgeStatsResponse
from rag.vector_store import build_vector_store
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


@router.post("/upload", response_model=UploadResponse)
async def upload_documents(files: list[UploadFile] = File(...)):
    """上传文档到知识库"""
    try:
        saved_files = []
        for file in files:
            if not file.filename.endswith(".txt"):
                logger.warning(f"跳过非 txt 文件: {file.filename}")
                continue

            file_path = os.path.join(RAW_DIR, file.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            content = await file.read()
            with open(file_path, "wb", encoding="utf-8") as f:
                f.write(content)
            saved_files.append(file.filename)
            logger.info(f"保存文件: {file.filename}")

        if not saved_files:
            return UploadResponse(
                success=False,
                message="没有找到有效的 txt 文件"
            )

        return UploadResponse(
            success=True,
            message=f"成功上传 {len(saved_files)} 个文件",
            files_count=len(saved_files)
        )

    except Exception as e:
        logger.error(f"上传文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rebuild", response_model=UploadResponse)
async def rebuild_vector_store():
    """重建向量库（重新加载所有文档并构建索引）"""
    try:
        logger.info("开始重建向量库...")
        vectorstore = build_vector_store()
        logger.info("向量库重建完成")
        return UploadResponse(
            success=True,
            message="向量库重建完成"
        )
    except Exception as e:
        logger.error(f"重建向量库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=KnowledgeStatsResponse)
async def get_knowledge_stats():
    """获取知识库统计信息"""
    try:
        from rag.vector_store import load_vector_store

        vectorstore = load_vector_store()
        docs = vectorstore.get()

        return KnowledgeStatsResponse(
            total_documents=len(docs.get("documents", [])),
            total_chunks=len(docs.get("documents", [])),
            vector_store_ready=True
        )
    except Exception as e:
        logger.warning(f"获取统计信息失败: {e}")
        return KnowledgeStatsResponse(
            total_documents=0,
            total_chunks=0,
            vector_store_ready=False
        )
