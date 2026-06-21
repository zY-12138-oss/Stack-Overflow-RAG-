# 第一阶段：PoC 验证

## 目标

- 建立项目骨架。
- 打通数据导入与英文知识入库。
- 实现单路召回。
- 实现中文回答生成。

## 当前落地内容

- FastAPI 基础接口：`/api/v1/health`、`/api/v1/ready`、`/api/v1/qa/ask`
- 基于本地 JSONL 的种子数据加载
- 最小可用问答链路：预处理 -> 中文改写 -> 检索 -> 规则重排 -> Context -> 中文回答 -> 引用
- 导入、重建索引、检索评估脚本

## 下一步验收

- 使用真实 Embedding 与 LLM Provider 替换 mock 适配器
- 将 `data/processed/knowledge_units.jsonl` 纳入统一入库流程
- 补充首批评测集
