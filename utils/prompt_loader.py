import os
from utils.file_utils import read_text


def load_prompt(prompt_name: str) -> str:
    """从 prompts 目录加载提示词模板。"""
    prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
    file_path = os.path.join(prompts_dir, prompt_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt file not found: {file_path}")
    return read_text(file_path)
