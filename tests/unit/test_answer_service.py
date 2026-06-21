from app.providers.llm.base import LLMProvider
from app.services.answer_service import AnswerService


class FakeLLMProvider(LLMProvider):
    model_name = "fake-llm"

    def generate_answer(self, question: str, context: str) -> str:
        return "llm fallback answer"


def test_answer_service_prefers_explicit_fix_from_context() -> None:
    service = AnswerService(llm_provider=FakeLLMProvider())
    context = "\n".join(
        [
            "[Document 1]",
            "Title: Supabase local edge function is not printing console.log statements to the terminal",
            "Tags: docker, express, supabase, deno",
            "Answer Excerpt: I had the same problem today. A downgrade from the CLI version to 2.1.4 solved this issue.",
            "Source: https://stackoverflow.com/questions/79320453",
        ]
    )

    answer, confidence, notes = service.answer(
        "Supabase local edge function console.log not printing",
        context,
    )

    assert "2.1.4" in answer
    assert "CLI" in answer or "版本" in answer
    assert confidence == "high"
    assert any("明确结论" in note for note in notes)


def test_answer_service_returns_low_confidence_when_context_missing() -> None:
    service = AnswerService(llm_provider=FakeLLMProvider())

    answer, confidence, notes = service.answer("test", "")

    assert confidence == "low"
    assert "上下文不足" in answer
    assert any("上下文不足" in note for note in notes)
