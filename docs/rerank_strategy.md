# Rerank 方案说明

## 目标

本项目的 `rerank` 不追求“文档是否属于同一个技术领域”，而是优先判断：

1. 候选文档是否和用户在解决同一类任务
2. 候选文档是否包含同一类错误或症状
3. 候选文档是否共享关键术语、版本号或标题信号

这套方案特别适合当前项目的特点：

- 用户问题可能是中文
- 知识库正文主要是英文 Stack Overflow 问答
- 检索前会做 query rewrite
- 候选集规模较小，适合规则可解释的二次排序

## 为什么需要这套方案

仅依赖向量召回或“同框架词命中”容易出现以下问题：

- 问题是 `FastAPI 文件上传校验失败`
- 候选文档却是 `MSAL Package for FastAPI`

这类候选文档虽然命中了 `FastAPI`，但并不是“同一个问题”。

因此，`rerank` 的统一原则是：

- `同问题` 优先于 `同框架`
- `任务词` 和 `错误词` 权重大于 `框架词`
- `标题命中` 大于 `正文泛命中`
- `多类信号交叉命中` 需要额外加分
- `只命中框架词` 的误导型结果需要惩罚

## 统一打分逻辑

当前实现位于 [app/services/rerank_service.py](E:/Agent_program/app/services/rerank_service.py)。

最终得分由三部分组成：

1. 原始召回分
2. 重排加分
3. 误导惩罚

公式可概括为：

```text
final_score = retrieval_score + rerank_bonus - rerank_penalty
```

### 加分信号

当前版本综合以下信号：

- 框架词命中
  - 例如 `fastapi`、`redis`、`docker`
- 任务词命中
  - 例如 `upload`、`multipart`、`bulk`、`write`
- 错误词命中
  - 例如 `error`、`validation`、`deserialization`
- 版本/术语命中
  - 例如 `v8`、`TValue`
- 标题命中
  - 标题中的匹配比正文更重要
- 标签命中
  - tags 是轻量但高价值的相关性信号
- 多路召回命中
  - 同一文档同时被向量召回和关键词召回命中时加分
- 最佳答案 / Stack Overflow 分数
  - 用于轻量质量修正

### 组合加分

以下组合会得到额外加分：

- 框架词 + 任务词
- 任务词 + 错误词
- 标题命中 + 任务词命中
- 多个任务词 + 至少一个错误词

这部分的目的，是把“同问题”的文档稳定顶上去，而不是只靠单词孤立出现。

### 惩罚信号

当前版本重点惩罚两类误导结果：

- 只命中框架词，不命中任务词，也不命中错误词
- 框架词命中但标题信号很弱，且缺乏同问题证据

例如：

- `MSAL Package for FastAPI`
  - 对 `FastAPI 文件上传校验失败` 来说应当被压低

## 信号来源

`rerank` 所依赖的信号主要来自两处：

1. 用户原始问题
2. `QAService` 中 merge 后的 `preprocess_result`

当前 [app/services/qa_service.py](E:/Agent_program/app/services/qa_service.py) 会在 query rewrite 后，把英文 rewrite token 合并回：

- `keywords`
- `error_terms`
- `versions`

这样中文问题的英文关键术语也能参与关键词召回和重排。

## 适用场景

这套方案适合当前项目的阶段：

- 文档规模中等
- 候选集主要来自双路召回 + 关键词召回
- 需要快速定位“为什么排成这样”
- 需要对错误类问题有更强的排序控制力

典型收益场景：

- `Redis 批量写入后反序列化报错`
- `FastAPI 文件上传校验失败`
- `TypeScript 泛型约束报错`
- `Docker 连接 Redis 失败`

## 当前局限

这套规则并不能替代更强的语义重排模型，当前局限主要有：

- 对知识库覆盖不足的问题，`rerank` 只能尽量降误判，不能凭空补知识
- 对长文本、复杂多意图问题，规则表达能力有限
- 对非常细粒度语义差异，Cross-Encoder 通常更强

## 后续演进建议

建议按以下顺序演进：

1. 保持当前规则版 `rerank` 作为默认方案
2. 持续补充高频问题领域的知识库覆盖
3. 为高价值 query 建立更细的术语词表
4. 引入可选 Cross-Encoder 作为第二阶段重排
5. 用评测集验证不同加权配置的收益

## 测试覆盖

当前与 `rerank` 直接相关的测试包括：

- [tests/unit/test_rerank_service.py](E:/Agent_program/tests/unit/test_rerank_service.py)
  - 验证预处理信号会带来加分
  - 验证“同任务文档”会压过“只同框架的文档”

后续如果扩展规则，优先补以下场景的测试：

- 中文 query 改写后的英文术语排序
- 仅框架词命中的误导惩罚
- 标题强匹配优先于正文弱匹配
- 多路命中文档优先级提升

## 与答案生成层的配合

`rerank` 负责把“更像同一个问题”的文档排到前面，但最终是否能给出具体答案，还取决于回答生成层是否能提炼出明确结论。

当前项目已经在 [app/services/answer_service.py](E:/Agent_program/app/services/answer_service.py) 中增加了轻量答案提取逻辑：

- 如果上下文中存在明确动作词，例如：
  - `downgrade to ...`
  - `upgrade to ...`
  - `solved this issue`
  - `fixed this issue`
- 则优先直接生成结构化中文结论
- 否则再退回通用 LLM 摘要生成

这套搭配的目标是：

- `rerank` 解决“找对文档”
- `answer_service` 解决“把结论说清楚”

像 `Supabase local edge function is not printing console.log ...` 这类问题，命中文档里已经有清晰解决方案时，系统应优先输出版本和操作结论，而不是只说“建议核对版本差异”。
