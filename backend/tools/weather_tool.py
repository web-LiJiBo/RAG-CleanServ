import requests
from langchain_core.tools import tool
from utils.config import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)

AMAP_WEATHER_URL = "https://restapi.amap.com/v3/weather/weatherInfo"

# 高德城市名→adcode 映射（全国主要城市，未覆盖的会直接用城市名查询）
CITY_ADCODE = {
    "北京": "110000", "北京市": "110000",
    "上海": "310000", "上海市": "310000",
    "广州": "440100", "广州市": "440100",
    "深圳": "440300", "深圳市": "440300",
    "杭州": "330100", "杭州市": "330100",
    "成都": "510100", "成都市": "510100",
    "南京": "320100", "南京市": "320100",
    "武汉": "420100", "武汉市": "420100",
    "重庆": "500000", "重庆市": "500000",
    "天津": "120000", "天津市": "120000",
    "苏州": "320500", "苏州市": "320500",
    "西安": "610100", "西安市": "610100",
    "长沙": "430100", "长沙市": "430100",
    "青岛": "370200", "青岛市": "370200",
    "郑州": "410100", "郑州市": "410100",
    "大连": "210200", "大连市": "210200",
    "厦门": "350200", "厦门市": "350200",
    "宁波": "330200", "宁波市": "330200",
    "济南": "370100", "济南市": "370100",
    "合肥": "340100", "合肥市": "340100",
    "福州": "350100", "福州市": "350100",
    "哈尔滨": "230100", "哈尔滨市": "230100",
    "沈阳": "210100", "沈阳市": "210100",
    "昆明": "530100", "昆明市": "530100",
    "贵阳": "520100", "贵阳市": "520100",
    "南宁": "450100", "南宁市": "450100",
    "拉萨": "540100", "拉萨市": "540100",
    "乌鲁木齐": "650100", "乌鲁木齐市": "650100",
    "呼和浩特": "150100", "呼和浩特市": "150100",
}

# 无 API Key 时的模拟数据兜底
MOCK_WEATHER = {
    "北京": "晴，温度 22°C，湿度 35%，风力 2级",
    "上海": "多云，温度 25°C，湿度 60%，风力 3级",
    "杭州": "小雨，温度 23°C，湿度 75%，风力 2级",
    "广州": "雷阵雨，温度 28°C，湿度 80%，风力 3级",
    "深圳": "多云，温度 27°C，湿度 65%，风力 2级",
    "成都": "阴，温度 20°C，湿度 70%，风力 1级",
}


def _get_api_key() -> str:
    cfg = load_config()
    return cfg.get("weather", {}).get("api_key", "")


def _query_real_weather(city: str) -> str:
    """调用高德天气 API 获取实时天气。"""
    api_key = _get_api_key()
    adcode = CITY_ADCODE.get(city, city)
    params = {
        "key": api_key,
        "city": adcode,
        "extensions": "base",  # base=实时天气, all=预报
    }
    try:
        resp = requests.get(AMAP_WEATHER_URL, params=params, timeout=5)
        data = resp.json()
        if data["status"] == "1" and data["lives"]:
            live = data["lives"][0]
            return (
                f"{live['city']}天气：{live['weather']}，"
                f"温度 {live['temperature']}°C，"
                f"湿度 {live['humidity']}%，"
                f"风力 {live['windpower']}级{live['winddirection']}，"
                f"实时数据（{live['reporttime']}发布）"
            )
        return f"天气查询失败：{data.get('info', '未知错误')}"
    except requests.RequestException as e:
        logger.error(f"Weather API request failed: {e}")
        return f"天气服务暂时不可用，请稍后重试。"


@tool
def get_weather(city: str) -> str:
    """查询指定城市的实时天气信息（通过高德天气 API）。

    Args:
        city: 城市名称，如 "北京"、"上海"、"杭州"。

    Returns:
        天气描述字符串，包含天气状况、温度、湿度、风力。
    """
    logger.info(f"[Weather Tool] Querying weather for: {city}")

    if _get_api_key():
        logger.info("[Weather Tool] Using real Amap API")
        return _query_real_weather(city)

    logger.info("[Weather Tool] No API key, using mock data")
    result = MOCK_WEATHER.get(city)
    if result:
        return f"{city}天气：{result}"
    return f"{city}天气：晴间多云，温度 23°C，湿度 50%，风力 2级（模拟数据，配置高德API Key后可获取真实天气）"
