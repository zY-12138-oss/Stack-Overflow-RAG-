# Stack Overflow RAG QA

这是根据 [技术方案设计](技术方案设计.md) 和 [项目计划书](项目计划书.md) 搭建并持续演进的分阶段项目骨架。

## 当前阶段

当前代码已进入第三阶段早期开发，具备索引版本管理、活动版本切换、运行状态接口、运行指标接口，以及 Redis / MySQL 连接状态检查与启动期健康校验。

### 第一阶段已完成

- 项目目录与分层结构初始化
- FastAPI 基础接口
- 最小可用跨语言 RAG 闭环
- 本地 JSONL 种子数据加载
- 导入、重建、评估脚本
- 基础测试样例

### 第二阶段已完成

- 双路召回：英文改写召回 + 中文原问召回
- 合并去重与增强重排序
- 结构化查询日志
- 第二阶段评测集与评测脚本
- 可切换向量库：`in_memory` / `chroma`
- ChromaDB 本地持久化索引
- ChromaDB 增量更新（基于本地状态文件）
- LLM 云端 + Embedding 本地独立配置

### 第三阶段已完成的当前部分

- 索引版本 catalog
- 活动索引版本切换
- 运行状态接口
- 运行指标接口
- 运行指标本地落盘与清空
- Redis 缓存可切换接入
- MySQL 查询日志可切换接入
- Redis / MySQL 连接状态检查
- 启动期健康校验与可选降级到本地存储
- 健康检查返回活动版本与后端状态

### 第三阶段待继续

- 更完整的运维与可观测能力
- 更强的灰度切换与重建策略
- 更细粒度错误统计和审计日志落盘

## 存储后端切换

### 本地文件模式

```env
SO_RAG_CACHE_BACKEND=local_file
SO_RAG_QUERY_LOG_BACKEND=local_file
```

### Redis 缓存

```env
SO_RAG_CACHE_BACKEND=redis
SO_RAG_REDIS_URL=redis://127.0.0.1:6379/0
SO_RAG_REDIS_CACHE_PREFIX=so_rag:answer:
```

### MySQL 查询日志

```env
SO_RAG_QUERY_LOG_BACKEND=mysql
SO_RAG_MYSQL_URL=mysql+pymysql://root:password@127.0.0.1:3306/stack_overflow_rag
```

### 启动期健康校验与降级

```env
SO_RAG_DEGRADE_ON_STORAGE_UNAVAILABLE=true
```

说明：
- 当 `cache_backend=redis` 且 Redis 不可用时，会回退到本地文件缓存。
- 当 `query_log_backend=mysql` 且 MySQL 不可用时，会回退到本地文件查询日志。
- 连接状态会显示在：
  - `GET /api/v1/health`
  - `GET /api/v1/ready`
  - `GET /api/v1/admin/runtime/status`

## 说明

- 当前已进入第三阶段的第一批能力建设，但还不是完整生产版。
- 现在最核心的新能力是"索引版本可见、活动版本可切换、运行状态与运行指标可观测，并支持 Redis / MySQL 连接检查与启动期健康校验"。
