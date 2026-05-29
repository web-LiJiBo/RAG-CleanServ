import requests
from langchain_core.tools import tool
from utils.config import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)

AMAP_IP_URL = "https://restapi.amap.com/v3/ip"

_current_user_id: str = "user_001"
_current_location: str = "北京市朝阳区"


def _get_weather_api_key() -> str:
    cfg = load_config()
    return cfg.get("weather", {}).get("api_key", "")


def detect_location() -> str:
    """通过高德 IP 定位 API 自动获取当前城市。

    Returns:
        城市名，如"北京市"；失败返回空字符串。
    """
    api_key = _get_weather_api_key()
    if not api_key:
        logger.info("[Location] No API key, skip IP detection")
        return ""

    try:
        resp = requests.get(AMAP_IP_URL, params={"key": api_key}, timeout=3)
        data = resp.json()
        if data["status"] == "1":
            province = data.get("province", "")
            city = data.get("city", "")
            if not city:
                city = province
            # 去掉末尾的"市"如果省份也带的话保持简洁
            adcode = data.get("adcode", "")
            logger.info(f"[Location] IP detected: {province} {city} (adcode={adcode})")
            return city if city else province
    except Exception as e:
        logger.warning(f"[Location] IP detection failed: {e}")

    return ""


def set_user_context(user_id: str, location: str = ""):
    """设置当前用户上下文（由 Streamlit 调用）。location 为空时自动通过 IP 定位。"""
    global _current_user_id, _current_location
    _current_user_id = user_id
    if location:
        _current_location = location
    else:
        detected = detect_location()
        if detected:
            _current_location = detected
            logger.info(f"[Location] Auto-detected: {_current_location}")


@tool
def get_current_user_id() -> str:
    """获取当前用户的ID。

    Returns:
        当前用户的ID字符串。
    """
    return _current_user_id


@tool
def get_user_location() -> str:
    """获取当前用户的地理位置信息（通过高德 IP 定位自动获取）。

    Returns:
        用户所在的城市。
    """
    return _current_location
