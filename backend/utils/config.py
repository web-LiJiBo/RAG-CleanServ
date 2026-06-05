import os
import yaml

_CONFIG = None   # 用于存放congfig.yaml 转成的python字典


def load_config(config_path: str = None) -> dict:
    """加载 YAML 配置文件，返回配置字典。"""
    global _CONFIG
    if _CONFIG is not None:
        return _CONFIG

    # 如果传入的路径没有
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    config_path = os.path.abspath(config_path)

    # 加载解析ymal文件，存入全局变量
    with open(config_path, "r", encoding="utf-8") as f:
        _CONFIG = yaml.safe_load(f)
    return _CONFIG


def get_llm_config() -> dict:
    cfg = load_config()
    llm_cfg = cfg["llm"].copy()
    # 如果未填写 api_key，从环境变量 DASHSCOPE_API_KEY 读取
    if not llm_cfg.get("api_key"):
        llm_cfg["api_key"] = os.getenv("DASHSCOPE_API_KEY", "")
    return llm_cfg


def setup_huggingface_mirror():
    """根据配置设置 HuggingFace 镜像端点（用于国内加速下载）。"""
    cfg = load_config()
    endpoint = cfg.get("huggingface", {}).get("endpoint", "")
    if endpoint:
        os.environ["HF_ENDPOINT"] = endpoint


def get_embedding_config() -> dict:
    cfg = load_config()
    return cfg["embedding"]

"""  下面是python字典
{
    "embedding": {
        "model_name": "BAAI/bge-small-zh-v1.5",
        "device": "cpu"
    }
}
"""

def get_vector_store_config() -> dict:
    cfg = load_config()
    return cfg["vector_store"]

#
