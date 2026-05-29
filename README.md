# 扫地机器人智能客服系统

基于 LangChain RAG + Agent 的智能客服系统，支持知识库问答和个性化使用报告生成。

## 功能特性

- **智能问答**：采用向量检索 + BM25 关键词检索 + RRF 融合 + 重排的混合检索架构，基于 6 份产品知识库检索信息，调用 DeepSeek LLM 生成自然回答
- **报告生成**：根据用户使用记录自动生成 Markdown 格式的个性化月度使用报告
- **工具集成**：天气查询、日期查询、用户管理等7个 Agent 工具
- **流式响应**：支持流式输出，实时展示回答内容
- **提示词切换**：支持普通客服模式 / 报告生成模式动态切换
- **执行监控**：工具调用耗时统计与状态监控
- **多级 MD5 去重与缓存**：文件级、文本块级、问题级三层 MD5 校验，避免重复解析、重复向量化与重复调用大模型，大幅提升响应效率


## 技术栈

- **框架**: LangChain 1.2+、LangChain-OpenAI、LangChain-Community
- **模型**: GPT-mini-4o 
- **向量库**: ChromaDB、BGE 中文 Embedding、BM25、RRF 融合、Rerank 重排
- **前端**: Streamlit
- **语言**: Python 3.10+

## 项目结构

```
RAG-CleanServ/
├── agent/                      # Agent 构建与执行器
│   ├── agent_builder.py        # Agent 组装（工具、记忆、中间件）
│   └── executor.py             # 流式/同步执行器
├── data/
│   ├── raw/                    # 6份知识库文档
│   │   ├── 01_故障排除.txt
│   │   ├── 02_常见对答.txt
│   │   ├── 03_维护保养.txt
│   │   ├── 04_产品说明.txt
│   │   ├── 05_使用技巧.txt
│   │   └── 06_配件信息.txt
│   ├── vector_store/           # Chroma 向量库持久化目录
│   └── mock_usage_records.json # 模拟用户使用记录
├── middlewares/                # 中间件
│   ├── log_callback.py         # 日志中间件
│   ├── monitor_callback.py     # 工具监控中间件
│   └── prompt_switch.py        # 提示词切换机制
├── prompts/                    # 提示词模板
│   ├── default_chat.txt        # 普通客服模式
│   └── report_mode.txt         # 报告生成模式
├── rag/                        # RAG 检索增强模块
│   ├── vector_store.py         # 向量库构建、加载、MD5去重
│   └── rag_summary.py          # 混合检索、重排、LLM 生成逻辑
├── tools/                      # Agent 工具集
│   ├── rag_tool.py             # 知识库检索工具
│   ├── date_tool.py            # 日期查询工具
│   ├── weather_tool.py         # 天气查询工具
│   ├── user_tools.py           # 用户ID/位置管理工具
│   ├── external_data_tool.py   # 使用记录抽取工具
│   └── report_tool.py          # 报告生成工具
├── utils/                      # 通用工具模块
│   ├── config.py               # 配置加载
│   ├── logger.py               # 日志设置
│   ├── file_utils.py           # 文件读写
│   ├── prompt_loader.py        # 提示词加载
│   ├── MD5_record.py           # 文件/文本块 MD5 去重
│   ├── Cache_utils.py          # 问题级 MD5 缓存
│   ├── BM25_utils.py           # BM25 关键词检索
│   ├── Fusion_utils.py         # RRF 结果融合
│   └── Rerank_docs.py          # 文档重排
├── app.py                      # Streamlit 前端入口
├── config.yaml                 # 全局配置文件
├── requirements.txt            # 项目依赖列表
└── README.md
```

## 快速开始

### 1. 克隆项目并创建虚拟环境

```bash
cd AGENT_project
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 配置 API Key

编辑 `config.yaml`，将 `llm.api_key` 替换为你的 DeepSeek API Key：

```yaml
llm:
  api_key: "sk-your-deepseek-api-key"
```

（首次运行时会自动下载 BGE 中文 Embedding 模型，约 100MB）

### 4. 运行应用

```bash
streamlit run app.py
```

浏览器访问 `http://localhost:8501` 即可使用。

### 5. 初始化 Agent

在侧边栏点击「初始化 Agent」按钮，系统会自动构建向量库并加载所有工具。

## 使用示例

### 知识问答
- "机器人无法开机怎么办？"
- "HEPA滤网多久换一次？"
- "机器人适合什么地面？"

### 报告生成
- "帮我生成 2026年3月 的使用报告"
- "查看我的使用情况"

### 其他功能
- "今天天气怎么样？"
- "现在是什么日期？"

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `llm.api_key` | DeepSeek API 密钥 | - |
| `llm.model_name` | 模型名称 | deepseek-chat |
| `llm.temperature` | 生成温度 | 0.7 |
| `embedding.model_name` | Embedding 模型 | BAAI/bge-small-zh-v1.5 |
| `vector_store.chunk_size` | 文档分块大小 | 500 |
| `vector_store.search_k` | 检索文档数 | 4 |

## 扩展方向

- [ ] 接入真实数据库（MySQL/PostgreSQL）
- [ ] 支持文件上传（用户日志分析）
- [ ] 多轮报告对比
- [ ] 用户画像与个性化推荐
- [ ] 【推荐】加入Redis缓存
