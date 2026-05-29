"""提示词动态切换机制：支持普通客服模式 / 报告生成模式切换。"""

from utils.file_utils import read_text
from utils.logger import setup_logger
import os

logger = setup_logger(__name__)

_current_mode: str = "default"

PROMPT_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")


def set_prompt_mode(mode: str):
    """切换当前提示词模式。

    Args:
        mode: "default"（普通客服模式）或 "report"（报告生成模式）。
    """
    global _current_mode
    if mode not in ("default", "report"):
        raise ValueError(f"Unknown prompt mode: {mode}")
    _current_mode = mode
    logger.info(f"[Prompt Switch] Switched to '{mode}' mode")


def get_current_mode() -> str:
    """获取当前提示词模式。"""
    return _current_mode


def get_active_prompt() -> str:
    """根据当前模式返回对应的提示词模板路径。"""
    if _current_mode == "report":
        prompt_file = "report_mode.txt"
    else:
        prompt_file = "default_chat.txt"

    filepath = os.path.join(PROMPT_DIR, prompt_file)
    return read_text(os.path.abspath(filepath))
