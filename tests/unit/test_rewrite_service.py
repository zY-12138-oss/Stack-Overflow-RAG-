from app.providers.llm.base import LLMProvider
from app.services.rewrite_service import RewriteService


class FakeRewriteLLMProvider(LLMProvider):
    model_name = "fake-rewrite-llm"

    def generate_answer(self, question: str, context: str) -> str:
        return "unused"

    def rewrite_query(self, query: str) -> str:
        return "redis bulk write deserialization error TValue"


def test_rewrite_service_uses_llm_when_enabled() -> None:
    service = RewriteService(llm_provider=FakeRewriteLLMProvider(), use_llm=True)

    rewritten = service.rewrite("Redis 批量写入后反序列化报错怎么办", "zh")

    assert rewritten == "redis bulk write deserialization error TValue"
