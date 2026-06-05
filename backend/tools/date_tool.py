from datetime import datetime
from langchain.tools import tool


@tool
def get_current_date() -> str:
    """获取当前日期和时间。

    Returns:
        格式为 "YYYY年MM月DD日 HH:MM:SS" 的当前时间字符串。
    """
    now = datetime.now()
    return now.strftime("%Y年%m月%d日 %H:%M:%S")
