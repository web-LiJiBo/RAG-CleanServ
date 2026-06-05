import os
import json


def ensure_dir(dir_path: str):
    """确保目录存在，不存在则创建。"""
    os.makedirs(dir_path, exist_ok=True)


def read_text(file_path: str) -> str:
    """读取文本文件内容。"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(file_path: str, content: str):
    """写入文本文件。"""
    ensure_dir(os.path.dirname(file_path))
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def read_json(file_path: str) -> dict:
    """读取 JSON 文件。"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(file_path: str, data: dict):
    """写入 JSON 文件。"""
    ensure_dir(os.path.dirname(file_path))
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
