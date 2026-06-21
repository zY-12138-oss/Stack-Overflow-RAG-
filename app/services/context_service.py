from app.models.document import Document


class ContextService:
    def build_context(self, ranked_results: list[dict[str, object]], max_items: int = 3) -> str:
        blocks: list[str] = []
        for index, item in enumerate(ranked_results[:max_items], start=1):
            document: Document = item["document"]
            blocks.append(
                "\n".join(
                    [
                        f"[Document {index}]",
                        f"Title: {document.title}",
                        f"Tags: {', '.join(document.tags)}",
                        f"Answer Excerpt: {document.content[:1500]}",
                        f"Source: {document.source_url}",
                    ]
                )
            )
        return "\n\n".join(blocks)
