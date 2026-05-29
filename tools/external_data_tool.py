import os
from langchain_core.tools import tool
from utils.file_utils import read_json
from utils.logger import setup_logger

logger = setup_logger(__name__)


@tool
def get_user_usage_records(user_id: str = "", year_month: str = "") -> dict:
    """从模拟数据库获取特定用户在指定月份的使用记录。

    Args:
        user_id: 用户ID，如 "user_001"。如果为空则使用当前用户。
        year_month: 查询月份，格式 "YYYY-MM"，如 "2026-03"。如果为空则查询当月。

    Returns:
        包含用户使用记录的字典，含每条清扫记录和月度汇总。
    """
    from tools.user_tools import get_current_user_id

    if not user_id:
        user_id = get_current_user_id()

    logger.info(f"[External Data Tool] Fetching records for user={user_id}, month={year_month or 'current'}")

    records_file = os.path.join(
        os.path.dirname(__file__), "..", "data", "mock_usage_records.json"
    )
    all_records = read_json(os.path.abspath(records_file))

    user_data = all_records.get(user_id)
    if not user_data:
        return {"error": f"未找到用户 {user_id} 的数据"}

    if year_month:
        month_prefix = year_month
        filtered = [r for r in user_data["records"] if r["date"].startswith(month_prefix)]
        return {
            "user_name": user_data["user_name"],
            "device_model": user_data["device_model"],
            "purchase_date": user_data["purchase_date"],
            "records": filtered,
            "record_count": len(filtered),
        }

    return user_data
