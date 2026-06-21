import re


class PreprocessService:
    def process(self, query: str) -> dict[str, object]:
        normalized = re.sub(r"\s+", " ", query).strip()
        language = "zh" if re.search(r"[\u4e00-\u9fff]", normalized) else "en"
        keywords = [token for token in re.split(r"[^A-Za-z0-9_+#.-]+", normalized) if token][:8]
        return {
            "raw_query": query,
            "normalized_query": normalized,
            "language": language,
            "keywords": keywords,
            "error_terms": [token for token in keywords if token.lower().endswith("exception") or "error" in token.lower()],
            "versions": [token for token in keywords if any(char.isdigit() for char in token)],
        }
