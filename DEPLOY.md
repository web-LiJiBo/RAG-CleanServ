# RAG-CleanServ 部署启动文档

## 项目结构

```
RAG-CleanServ/
├── backend/                 # FastAPI 后端
│   ├── main.py              # FastAPI 应用入口
│   ├── schemas.py           # 数据模型
│   ├── requirements.txt      # Python 依赖
│   ├── routers/             # API 路由
│   │   ├── __init__.py
│   │   ├── knowledge.py     # 知识库管理接口
│   │   └── chat.py          # 对话接口
│   ├── agent/               # Agent 源码（原样迁移）
│   ├── rag/                 # RAG 源码（原样迁移）
│   ├── tools/               # 工具函数（原样迁移）
│   ├── utils/               # 工具类（原样迁移）
│   ├── middlewares/         # 中间件（原样迁移）
│   ├── prompts/             # 提示词模板（原样迁移）
│   └── data/                # 数据目录
│       ├── raw/             # 原始文档
│       └── vector_store/    # 向量库存储
├── frontend/                # Vue3 前端
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── services/
│       │   └── api.js       # API 调用
│       └── views/
│           ├── KnowledgeUpload.vue  # 知识库上传页
│           └── ChatPage.vue         # 对话聊天页
└── README.md
```

## 后端启动

### 1. 安装依赖

```bash
cd backend

# 安装 Python 依赖（包含原有项目依赖）
pip install -r requirements.txt

# 原有项目的依赖也需要安装
pip install langchain>=0.3.0 langchain-community>=0.3.0 langchain-openai>=0.2.0
pip install chromadb>=0.5.0 sentence-transformers>=2.7.0 openai>=1.30.0
pip install rank-bm25>=0.2.2 jieba>=0.42.1 torch>=2.0.0 python-dotenv>=1.0.0
pip install pyyaml>=6.0 requests>=2.31.0
```

### 2. 启动服务

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 前端启动

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

前端启动后访问: http://localhost:3000

## API 接口说明

### 知识库管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/knowledge/upload` | POST | 上传文档（支持多文件） |
| `/api/knowledge/rebuild` | POST | 重建向量库 |
| `/api/knowledge/stats` | GET | 获取知识库统计 |

### 对话服务

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat/chat` | POST | 对话接口（同步） |
| `/api/chat/stream` | POST | 对话接口（流式） |

## 核心算法说明

项目保留原有算法实现：

1. **MD5 校验**：`utils/MD5_record.py`
   - 文档去重：计算文件 MD5 判断是否新文件
   - chunk 去重：计算每个文本块 MD5

2. **RRF 排序融合**：`utils/Fusion_utils.py`
   - k=60 平滑常数
   - 混合向量检索与 BM25 检索结果

3. **相似度阈值**：`utils/Rerank_docs.py`
   - 0.6 相似度阈值（重排后截取 Top3）
   - BGE-reranker-base 模型

## 注意事项

1. 首次启动后端会自动加载 `data/raw` 目录下的文档构建向量库
2. 上传新文档后需调用 `/api/knowledge/rebuild` 重建向量库
3. 前端代理配置已将 `/api` 请求转发到后端 `8000` 端口
4. 环境变量 `DASHSCOPE_API_KEY` 可覆盖配置文件中的 API Key
