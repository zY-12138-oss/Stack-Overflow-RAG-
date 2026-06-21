from app.providers.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    model_name = "mock-answer-summarizer"

    def generate_answer(self, question: str, context: str) -> str:
        if not context.strip():
            return "当前检索到的上下文不足以确认答案，建议补充错误日志、版本号或关键代码片段后再试。"

        lines = [line.strip() for line in context.splitlines() if line.strip()]
        excerpt = "；".join(lines[:3])
        return (
            f"基于当前召回结果，问题“{question}”最可能与以下信息相关：{excerpt}。"
            "建议优先核对报错原文、数据结构与版本差异，并结合引用帖子中的解决步骤逐项排查。"
        )
