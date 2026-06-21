# 第二阶段：内测版建设

## 目标

- 增加双路召回。
- 接入重排序增强。
- 增加缓存与日志。
- 建立评测集。

## 当前已落地

- 双路召回：英文改写召回 + 原始中文召回
- 合并去重与增强重排序
- 内存缓存：答案缓存与缓存统计
- 结构化查询日志与管理查询接口
- 第二阶段评测集与评测脚本骨架
- 可切换向量库：`in_memory` / `chroma`
- ChromaDB 本地持久化索引

## 已开放接口

- `POST /api/v1/qa/ask`
- `GET /api/v1/health`
- `GET /api/v1/ready`
- `GET /api/v1/admin/query-logs`
- `GET /api/v1/admin/cache/stats`
- `POST /api/v1/admin/rebuild-index`

## ChromaDB 配置

```env
SO_RAG_VECTOR_STORE_PROVIDER=chroma
SO_RAG_CHROMA_PERSIST_PATH=data/indexes/chroma
SO_RAG_CHROMA_COLLECTION_NAME=stack_overflow_qa
```

## 下一步建议

- 将内存缓存替换为 Redis
- 接入真实 Cross-Encoder rerank
- 将评测集扩展到 Redis / MySQL / Python / FastAPI 常见问题
- 增加向量库版本管理与灰度切换
