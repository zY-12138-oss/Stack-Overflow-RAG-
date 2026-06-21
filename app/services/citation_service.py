from app.api.schemas.qa import CitationItem


class CitationService:
    def build_citations(self, ranked_results: list[dict[str, object]], max_items: int = 3) -> list[CitationItem]:
        citations: list[CitationItem] = []
        seen: set[str] = set()
        for item in ranked_results:
            document = item["document"]
            url = document.source_url.strip("`")
            if url in seen:
                continue
            seen.add(url)
            citations.append(CitationItem(title=document.title, url=url))
            if len(citations) >= max_items:
                break
        return citations
