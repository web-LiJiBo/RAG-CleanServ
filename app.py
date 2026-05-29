"""扫地机器人智能客服系统 — Streamlit 前端入口。（LangChain 1.2+）"""

import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils.config import load_config, setup_huggingface_mirror
from utils.logger import setup_logger

setup_huggingface_mirror()
logger = setup_logger(__name__)

# ---------- 页面配置 ----------
cfg = load_config()
st.set_page_config(
    page_title=cfg["streamlit"]["title"],
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- 工具函数 ----------

@st.cache_resource
def _get_tools():
    """缓存导入工具列表，避免重复 import。"""
    from tools.rag_tool import search_knowledge_base
    from tools.date_tool import get_current_date
    from tools.weather_tool import get_weather
    from tools.user_tools import get_current_user_id, get_user_location, set_user_context
    from tools.external_data_tool import get_user_usage_records
    from tools.report_tool import generate_usage_report

    return [
        search_knowledge_base,
        get_current_date,
        get_weather,
        get_current_user_id,
        get_user_location,
        get_user_usage_records,
        generate_usage_report,
    ]


def _init_agent():
    """构建 Agent，返回 (agent, checkpointer, stats)。"""
    from agent.agent_builder import build_agent
    from tools.user_tools import set_user_context

    set_user_context(st.session_state.user_id)
    tools = _get_tools()
    agent, checkpointer, stats = build_agent(tools)
    logger.info(f"Agent initialized with {len(tools)} tools")
    return agent, checkpointer, stats


# ---------- 会话状态 ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "checkpointer" not in st.session_state:
    st.session_state.checkpointer = None
if "monitor_stats" not in st.session_state:
    st.session_state.monitor_stats = []
if "user_id" not in st.session_state:
    st.session_state.user_id = cfg["streamlit"]["default_user_id"]
if "thread_id" not in st.session_state:
    st.session_state.thread_id = uuid.uuid4().hex[:12]
if "init_done" not in st.session_state:
    st.session_state.init_done = False
if "custom_city" not in st.session_state:
    st.session_state.custom_city = ""

# ---------- 自动初始化 Agent ----------
if not st.session_state.init_done:
    with st.spinner("正在启动智能客服系统..."):
        try:
            agent, checkpointer, stats = _init_agent()
            st.session_state.agent = agent
            st.session_state.checkpointer = checkpointer
            st.session_state.monitor_stats = stats
            st.session_state.init_done = True
        except Exception as e:
            st.error(f"系统启动失败：{e}")
            logger.error(f"Auto-init failed: {e}")

# ---------- 标题栏 ----------
st.title("RAG-CleanServ")
st.caption("基于 RAG + Agent — 知识问答 | 使用报告 | 天气查询")

# ---------- 侧边栏 ----------
with st.sidebar:
    # ---- 状态指示 ----
    if st.session_state.agent is not None:
        st.success("🟢 系统就绪")
    else:
        st.error("🔴 系统未就绪，请点击下方「重新加载」")

    # ---- 模式切换 ----
    st.subheader("📋 工作模式")
    from middlewares.prompt_switch import get_current_mode, set_prompt_mode

    current_mode = get_current_mode()
    mode_labels = {
        "default": "普通客服 — 知识问答",
        "report": "报告生成 — 使用报告",
    }
    selected_label = st.radio(
        "选择模式",
        options=list(mode_labels.values()),
        index=0 if current_mode == "default" else 1,
        horizontal=False,
        help="普通客服模式：通过知识库回答产品问题\n报告生成模式：根据使用数据生成个性化报告",
    )
    new_mode = "default" if "普通" in selected_label else "report"
    if new_mode != current_mode:
        set_prompt_mode(new_mode)
        st.session_state.agent = None  # 触发自动重建
        st.rerun()

    # 模式切换后自动重建 Agent
    if st.session_state.agent is None and st.session_state.init_done:
        with st.spinner(f"正在切换到{mode_labels[new_mode]}..."):
            try:
                agent, checkpointer, stats = _init_agent()
                st.session_state.agent = agent
                st.session_state.checkpointer = checkpointer
                st.session_state.monitor_stats = stats
                st.success(f"已切换到{mode_labels[new_mode]}")
            except Exception as e:
                st.error(f"切换失败：{e}")

    st.divider()

    # ---- 用户设置 ----
    st.subheader("👤 用户设置")
    new_user_id = st.text_input(
        "用户ID",
        value=st.session_state.user_id,
        help="用于个性化报告（可切换 user_001 / user_002 体验）",
    )
    if new_user_id != st.session_state.user_id:
        st.session_state.user_id = new_user_id
        st.session_state.custom_city = ""
        from tools.user_tools import set_user_context
        set_user_context(new_user_id)
        st.rerun()

    from tools.user_tools import get_user_location
    # 改正：错误1
    current_location = get_user_location.invoke({})
    if current_location:
        st.caption(f"📍 当前城市：{current_location}" + (" (手动)" if st.session_state.custom_city else " (自动)"))

    new_city = st.text_input(
        "手动设置城市",
        value=st.session_state.custom_city,
        placeholder="输入城市名覆盖自动定位，如：郑州",
        help="IP定位可能不准，手动输入后即可使用正确的城市查询天气",
    )
    if new_city != st.session_state.custom_city:
        st.session_state.custom_city = new_city
        from tools.user_tools import set_user_context, get_current_user_id
        if new_city:
            set_user_context(get_current_user_id.invoke({}), location=new_city)
        else:
            set_user_context(get_current_user_id.invoke({}))
        st.rerun()

    st.divider()

    # ---- 操作按钮 ----
    st.subheader("🔧 操作")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 重新加载", use_container_width=True):
            with st.spinner("重新加载中..."):
                try:
                    agent, checkpointer, stats = _init_agent()
                    st.session_state.agent = agent
                    st.session_state.checkpointer = checkpointer
                    st.session_state.monitor_stats = stats
                    st.success("重新加载完成")
                    st.rerun()
                except Exception as e:
                    st.error(f"加载失败：{e}")
    with col2:
        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state.messages = []
            from agent.executor import clear_memory
            if st.session_state.checkpointer:
                clear_memory(st.session_state.checkpointer, st.session_state.thread_id)
            st.rerun()

    st.divider()

    # ---- 工具状态 ----
    st.subheader("📊 最近工具调用")
    stats = st.session_state.monitor_stats
    if stats:
        for stat in stats[-5:]:
            icon = "✅" if stat["status"] == "success" else "❌"
            st.caption(f"{icon} `{stat['tool']}` — {stat['elapsed_seconds']}s")
    else:
        st.caption("暂无记录，发送消息后显示")

    st.divider()
    st.caption("💡 试试这些：")
    st.caption("• 机器人无法开机怎么办？")
    st.caption("• 帮我生成 2026年3月 使用报告")
    st.caption("• 今天天气怎么样？")

# ---------- 主界面 ----------

# 欢迎界面（无聊天记录时）
if not st.session_state.messages:
    current_m = get_current_mode()
    if current_m == "default":
        st.info("""
        👋 **你好，我是RAG-CleanServ，你的专属扫地机器人客服！**

        我可以帮你：
        - 📚 **查知识库** — 故障排除、使用技巧、维护保养等问题
        - 🌤️ **查天气** — 我自动知道你在哪个城市哦
        - 📊 **出报告** — 切换到「报告生成模式」，生成你的月度使用报告

        直接在下方输入问题开始吧！
        """)
    else:
        st.info("""
        📊 **报告生成模式已激活**

        在此模式下，我会优先帮你生成个性化使用报告。

        试试输入：**"帮我生成 2026年3月 的使用报告"**
        当前可用用户：`user_001`（张三）、`user_002`（李四）
        """)

# 聊天记录
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- 用户输入 ----------
if prompt := st.chat_input("请输入您的问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.agent is None:
        with st.chat_message("assistant"):
            msg = "⚠️ 系统正在启动中，请稍后再试。如持续出现问题，请点击侧边栏「重新加载」。"
            st.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
    else:
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    from agent.executor import execute_sync

                    # ~ 前端界面调用execute_sync
                    result = execute_sync(
                        st.session_state.agent,
                        prompt,
                        thread_id=st.session_state.thread_id,
                    )
                    st.markdown(result)
                    st.session_state.messages.append({"role": "assistant", "content": result})
                except Exception as e:
                    error_msg = f"❌ 处理出错：{str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    logger.error(f"Chat error: {e}")
