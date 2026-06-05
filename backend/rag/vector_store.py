
import os  # 用于处理文件路径和目录
from langchain_community.document_loaders import DirectoryLoader, TextLoader  # 文档加载器：批量加载目录和单个文本文件
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 文本分块器：按规则拆分长文档
from langchain_community.embeddings import HuggingFaceBgeEmbeddings  # 词嵌入模型：BGE系列（中文效果优秀）
from langchain_community.vectorstores import Chroma  # 向量数据库：轻量级本地向量库

from utils.MD5_record import load_md5_record, get_text_md5, save_md5_record
from utils.config import get_embedding_config, get_vector_store_config  # 自定义配置读取工具（读取embedding和向量库参数）
from utils.logger import setup_logger  # 自定义日志工具：记录运行信息和错误

# 初始化日志器，用于打印脚本运行信息
logger = setup_logger(__name__)

"""
    2026年5月28日，修改RAG中向量入库，如下：

        txt文档 → 计算文件MD5（判断是否新文件）
            ↓
        解析 + 文本切块 → 对每个chunk计算MD5（去重）
            ↓
        无重复 → 生成Embedding向量 → 存入向量库（附带MD5元数据）
            ↓
        用户提问 → 问题MD5查缓存 → 有缓存直接返回答案
            ↓
        无缓存 → 向量检索 → LLM 生成回答
"""

# 返回文本嵌入模型
def get_embeddings():
    """
    获取 embedding 模型实例。
    作用：读取配置文件中的参数，初始化词嵌入模型。
    返回：HuggingFaceBgeEmbeddings 实例
    """
    # 从配置文件中读取embedding模型的参数（比如模型名称、设备）
    emb_cfg = get_embedding_config()
    logger.info(f"Loading embedding model: {emb_cfg['model_name']}")

    # 初始化BGE词嵌入模型
    return HuggingFaceBgeEmbeddings(
        model_name=emb_cfg["model_name"],  # 模型名称: BAAI/bge-small-zh-v1.5
        model_kwargs={"device": emb_cfg.get("device", "cpu")},  # 模型运行设备，默认CPU，可配置为cuda
    )

# 构建向量库
def build_vector_store():
    vs_cfg = get_vector_store_config()

    raw_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    persist_dir = os.path.join(os.path.dirname(__file__), "..", vs_cfg["persist_dir"])
    raw_dir = os.path.abspath(raw_dir)
    persist_dir = os.path.abspath(persist_dir)
    md5_record_path = os.path.abspath(vs_cfg["md5_record_path"])

    logger.info(f"Loading documents from: {raw_dir}")

    # 1. 加载文档
    loader = DirectoryLoader(
        raw_dir,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()
    logger.info(f"Loaded {len(documents)} documents")

    # 2. 文本分块
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=vs_cfg["chunk_size"],
        chunk_overlap=vs_cfg["chunk_overlap"],
        separators=["\n\n", "\n", "。", "；", "，", " ", ""],
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Split into {len(chunks)} chunks")

    # 3. MD5 去重（修复了属性名！）
    exist_md5 = load_md5_record(md5_record_path)
    new_chunks = []
    new_md5 = set()

    for chunk in chunks:
        content = chunk.page_content.strip()
        chunk_md5 = get_text_md5(content)

        if chunk_md5 not in exist_md5:
            new_chunks.append(chunk)
            new_md5.add(chunk_md5)

    # 4. 保存 MD5 记录（现在代码能跑到这里了！）
    all_md5 = exist_md5.union(new_md5)
    save_md5_record(md5_record_path, all_md5)
    logger.info(f"Save {len(all_md5)} md5 records to file")

    # 无新切片时直接加载已有向量库
    if not new_chunks:
        logger.info("No new chunks, skip building vector store")
        embeddings = get_embeddings()
        return Chroma(persist_directory=persist_dir, embedding_function=embeddings)

    # 5. 构建向量库
    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(
        documents=new_chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    logger.info("Vector store built successfully")
    return vectorstore

# 返回向量库-对外的接口------向量库的父类是vectorstore
def load_vector_store() -> Chroma:
    """
    加载已持久化的 Chroma 向量库。如果不存在则自动构建。
    作用：封装向量库加载逻辑，支持「存在则加载，不存在则自动构建」，避免重复构建。
    返回：已加载的 Chroma 向量库实例
    """
    vs_cfg = get_vector_store_config()
    # 获取向量库持久化目录的绝对路径
    persist_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", vs_cfg["persist_dir"])
    )
    # 【新】获取md5文件地址
    md5_record_path = os.path.abspath(vs_cfg["md5_record_path"])

    # 1. 检查向量库是否存在
    if not os.path.exists(persist_dir) or len(os.listdir(persist_dir)) == 0:
        logger.info("Vector store not found, building new one...")
        os.makedirs(persist_dir, exist_ok=True)  # 创建目录（如果不存在）
        return build_vector_store()  # 【返回构建好的向量库】

    # 2. 尝试加载已存在的向量库
    try:
        logger.info(f"Loading existing vector store from: {persist_dir}")
        embeddings = get_embeddings()  # 初始化词嵌入模型（必须和构建时的模型一致）
        return Chroma(persist_directory=persist_dir, embedding_function=embeddings)

    # 3. 加载失败时的处理（比如向量库文件损坏）
    except Exception as e:
        logger.warning(f"Failed to load vector store ({e}), rebuilding...")
        import shutil
        shutil.rmtree(persist_dir, ignore_errors=True)  # 删除损坏的向量库目录
        os.makedirs(persist_dir, exist_ok=True)  # 重新创建目录
        # 【新】如果向量库损坏，直接删除MD5记录
        if os.path.exists(md5_record_path):
            os.remove(md5_record_path)
        return build_vector_store()  # 重新构建向量库