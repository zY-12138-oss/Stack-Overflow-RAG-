from abc import ABC, abstractmethod


class LLMProvider(ABC):
    model_name: str = "unknown"

    @abstractmethod
    def generate_answer(self, question: str, context: str) -> str:
        raise NotImplementedError

    def rewrite_query(self, query: str) -> str:
        return query
