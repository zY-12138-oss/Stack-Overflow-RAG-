from app.providers.llm.base import LLMProvider


class RewriteService:
    TERM_MAP = {
        "反序列化": "deserialization",
        "批量写入": "bulk write",
        "报错": "error",
        "怎么办": "",
        "上传": "upload",
        "校验": "validation",
    }

    def __init__(self, llm_provider: LLMProvider | None = None, use_llm: bool = False) -> None:
        self.llm_provider = llm_provider
        self.use_llm = use_llm

    def rewrite(self, normalized_query: str, language: str) -> str:
        if language == "en":
            return normalized_query

        if self.use_llm and self.llm_provider is not None:
            rewritten = self.llm_provider.rewrite_query(normalized_query)
            if rewritten:
                return " ".join(rewritten.split()).strip()

        rewritten = normalized_query
        for zh, en in self.TERM_MAP.items():
            rewritten = rewritten.replace(zh, en)
        return " ".join(rewritten.split()).strip()
