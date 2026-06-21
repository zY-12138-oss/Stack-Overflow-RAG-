# 第三阶段：生产版发布

## 目标

- 优化时延与稳定性。
- 增强日志记录与排障能力。
- 增加增量更新。
- 完善管理接口和运维能力。

## 当前已落地

- 索引版本 catalog
- 活动索引版本记录与切换
- `ChromaDB` 集合按版本隔离
- 管理接口支持查看索引版本
- 管理接口支持切换活动索引版本
- 索引重建状态流转：`building -> ready / failed`
- 切换前校验目标版本是否就绪
- 切换失败自动回滚到上一活动版本
- 运行状态接口：查看阶段、活动版本、向量库与模型模式
- 运行指标接口：请求量、缓存命中、成功数、失败数、平均耗时
- 运行指标本地落盘与清空
- Redis 缓存可切换接入
- MySQL 查询日志可切换接入
- Redis / MySQL 连接状态检查
- 启动期健康校验与可选降级
- 健康检查与就绪检查返回活动索引版本和后端状态

## 已开放接口

- `GET /api/v1/health`
- `GET /api/v1/ready`
- `GET /api/v1/admin/index/versions`
- `POST /api/v1/admin/index/switch`
- `GET /api/v1/admin/runtime/status`
- `GET /api/v1/admin/runtime/metrics`
- `POST /api/v1/admin/runtime/metrics/clear`
- `POST /api/v1/admin/rebuild-index`

## 下一步建议

- 增加索引重建到指定版本的独立脚本
- 引入更完整的错误统计与审计日志落盘
- 将 Redis / MySQL 连接状态纳入更细粒度告警
- 增加 Cross-Encoder rerank 或更强检索质量评估
