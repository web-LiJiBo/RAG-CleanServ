import os
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from utils.config import get_llm_config
from utils.file_utils import read_json
from utils.prompt_loader import load_prompt
from utils.logger import setup_logger

logger = setup_logger(__name__)


@tool
def generate_usage_report(user_id: str, year_month: str) -> str:
    """根据用户指定月份的使用记录，调用 LLM 生成个性化使用报告（Markdown格式）。

    适用场景：
    - 用户明确要求"生成报告"、"我的使用报告"、"X月报告"等。
    - 用户想了解自己的使用情况和获得优化建议。

    Args:
        user_id: 用户ID，如 "user_001"。
        year_month: 报告月份，格式 "YYYY-MM"，如 "2026-03"。

    Returns:
        Markdown 格式的结构化使用报告。
    """
    logger.info(f"[Report Tool] Generating report for user={user_id}, month={year_month}")

    # 加载用户数据
    records_file = os.path.join(
        os.path.dirname(__file__), "..", "data", "mock_usage_records.json"
    )
    all_records = read_json(os.path.abspath(records_file))
    user_data = all_records.get(user_id)

    if not user_data:
        return f"## 错误\n\n未找到用户 **{user_id}** 的使用数据，请检查用户ID是否正确。"

    month_prefix = year_month
    month_records = [r for r in user_data["records"] if r["date"].startswith(month_prefix)]

    if not month_records:
        return f"## {year_month} 使用报告\n\n用户 **{user_data['user_name']}** 在 {year_month} 暂无清扫记录。"

    # 计算统计数据
    total_area = round(sum(r["area"] for r in month_records), 1)
    total_duration = sum(r["duration"] for r in month_records)
    total_dust = sum(r["dust_collected"] for r in month_records)
    clean_count = len(month_records)

    # 使用模式统计
    mode_counts = {}
    for r in month_records:
        mode = r["mode"]
        mode_counts[mode] = mode_counts.get(mode, 0) + 1

    avg_area = round(total_area / clean_count, 1)
    avg_duration = round(total_duration / clean_count, 1)
    days_in_month = 30
    avg_interval = round(days_in_month / clean_count, 1)

    # 构建数据摘要
    data_summary = f"""
## 用户信息
- 用户名：{user_data['user_name']}
- 设备型号：{user_data['device_model']}
- 购买日期：{user_data['purchase_date']}

## {year_month} 使用统计
- 清扫次数：{clean_count} 次
- 清扫总面积：{total_area} ㎡
- 清扫总时长：{total_duration} 分钟（{round(total_duration/60, 1)} 小时）
- 总集尘量：{total_dust} ml

## 平均数据
- 每次平均清扫面积：{avg_area} ㎡
- 每次平均清扫时长：{avg_duration} 分钟
- 平均清扫间隔：{avg_interval} 天/次

## 使用模式分布
""" + "\n".join(f"- {mode}：{count} 次" for mode, count in mode_counts.items())

    # 调用 LLM 生成报告
    llm_cfg = get_llm_config()
    llm = ChatOpenAI(
        model=llm_cfg["model_name"],
        api_key=llm_cfg["api_key"],
        base_url=llm_cfg["base_url"],
        temperature=0.5,
        max_tokens=llm_cfg.get("max_tokens", 2048),
    )

    report_prompt = load_prompt("report_mode.txt")

    response = llm.invoke(
        f"{report_prompt}\n\n以下是用户的使用数据，请据此生成完整报告：\n\n{data_summary}"
    )

    return response.content
