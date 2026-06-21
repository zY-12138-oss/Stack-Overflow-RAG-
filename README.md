# Stack Overflow RAG QA System

基于 RAG（Retrieval-Augmented Generation）技术的跨语言技术问答系统，支持中文提问、英文检索、中文回答。

## 项目简介

本项目是一个面向 Stack Overflow 知识源的智能问答系统，通过检索增强生成技术，为用户提供准确、可追溯的技术问题解答。系统核心特点：

- **跨语言支持**：中文提问 → 英文检索 → 中文回答
- **双路召回**：英文改写召回 + 中文原问召回，提升检索质量
- **可追溯引用**：每个回答都附带 Stack Overflow 原始链接
- **模块化架构**：支持灵活替换 Embedding、LLM、向量库等组件
- **生产级特性**：索引版本管理、健康检查、降级机制、运行监控

## 核心功能

### 问答能力
- 支持中英文技术问答
- 智能查询改写（中文 → 英文检索表达）
- 双路向量召回与重排序
- 结构化答案生成与引用溯源

### 数据管理
- Stack Overflow 数据导入与清洗
- 知识单元自动生成
- ChromaDB 向量索引管理
- 索引版本控制与活动版本切换

### 运维监控
- 健康检查接口（Redis/MySQL 连接状态）
- 运行指标收集与查询
- 启动期健康校验与自动降级
- 查询日志结构化存储

## 技术栈

- **后端框架**：FastAPI + Uvicorn
- **向量数据库**：ChromaDB（支持 in_memory 模式）
- **缓存**：Redis（可选，支持本地文件降级）
- **数据库**：MySQL（可选，支持本地文件降级）
- **数据校验**：Pydantic
- **Python 版本**：3.11+

## 快速开始

### 1. 安装依赖

```bash
pip install -e .
```

### 2. 配置环境变量

创建 `.env` 文件（参考 `.env.example`）：

```env
# LLM 配置
SO_RAG_LLM_PROVIDER=openai_compatible
SO_RAG_LLM_BASE_URL=https://api.openai.com/v1
SO_RAG_LLM_API_KEY=your-api-key
SO_RAG_LLM_MODEL=gpt-3.5-turbo

# Embedding 配置
SO_RAG_EMBEDDING_PROVIDER=local_hash

# 向量库配置
SO_RAG_VECTOR_STORE=chroma

# 存储后端配置（可选）
SO_RAG_CACHE_BACKEND=local_file
SO_RAG_QUERY_LOG_BACKEND=local_file
```

### 3. 导入数据

```bash
# 导入 Stack Overflow 数据
python scripts/ingest_stackoverflow.py

# 重建索引
python scripts/rebuild_index.py
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload
```

服务启动后访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/v1/health

## API 接口

### 问答接口

```bash
POST /api/v1/qa/ask
```

请求示例：
```json
{
  "query": "Redis 批量写入后反序列化报错怎么办",
  "top_k": 5
}
```

响应示例：
```json
{
  "answer": "根据检索结果，这类问题通常与...",
  "confidence": "high",
  "citations": [
    {
      "title": "Unable to deserialize the data into TValue",
      "url": "https://stackoverflow.com/questions/79320365/..."
    }
  ]
}
```

### 管理接口

- `POST /api/v1/admin/rebuild-index` - 重建索引
- `POST /api/v1/admin/ingest` - 导入数据
- `GET /api/v1/admin/index/versions` - 查看索引版本
- `POST /api/v1/admin/index/switch` - 切换活动索引
- `GET /api/v1/admin/runtime/metrics` - 查询运行指标

## 项目结构

```
app/
├── api/              # HTTP 接口层
├── core/             # 核心配置与异常
├── services/         # 业务逻辑层
├── providers/        # 第三方服务适配（Embedding/LLM/VectorStore）
├── repositories/     # 数据访问层
├── models/           # 数据模型
├── tasks/            # 异步任务
└── utils/            # 工具函数
scripts/              # 数据导入与运维脚本
tests/                # 测试用例
data/                 # 数据存储目录
docs/                 # 文档
```

## 开发状态

当前处于第三阶段开发，已完成：
- ✅ 基础 RAG 问答闭环
- ✅ 双路召回与重排序
- ✅ ChromaDB 向量索引
- ✅ 索引版本管理
- ✅ Redis/MySQL 可选接入
- ✅ 健康检查与降级机制
- ✅ 运行指标监控

## 许可证

MIT
