# utils/MD5_record.py
import hashlib
import json
import os
from typing import Set

def get_text_md5(text: str) -> str:
    """计算文本的MD5值"""
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def load_md5_record(record_path: str) -> Set[str]:
    """加载已存在的MD5记录"""
    if not os.path.exists(record_path):
        return set()
    try:
        with open(record_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 读取时必须和写入的键名一致
        return set(data.get("md5_list", []))
    except Exception as e:
        print(f"读取MD5文件失败: {e}")
        return set()

def save_md5_record(record_path: str, md5_set: Set[str]) -> None:
    """保存MD5记录，强制覆盖写入"""
    try:
        # 先确保目录存在
        os.makedirs(os.path.dirname(record_path), exist_ok=True)
        with open(record_path, "w", encoding="utf-8") as f:
            json.dump({"md5_list": list(md5_set)}, f, ensure_ascii=False, indent=2)
        print(f"✅ 成功写入 {len(md5_set)} 条MD5记录到: {record_path}")
    except Exception as e:
        print(f"❌ 写入MD5文件失败: {e}")