from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class MatchSignals:
    framework_hits: int = 0
    task_hits: int = 0
    error_hits: int = 0
    version_hits: int = 0
    title_hits: int = 0
    tag_hits: int = 0
    multi_route: bool = False
    accepted: bool = False
    answer_score: int = 0


class RerankService:
    FRAMEWORK_TERMS = {
        "fastapi",
        "redis",
        "docker",
        "typescript",
        "javascript",
        "python",
        "java",
        "spring",
        "react",
        "vue",
        ".net",
        "c#",
        "mysql",
        "postgres",
        "chroma",
        "msal",
        "azure",
        "supabase",
        "deno",
        "express",
        "next.js",
        "nextjs",
        "kotlin",
        "android",
        "ios",
        "flutter",
        "rust",
        "go",
        "golang",
        "php",
        "laravel",
        "ruby",
        "rails",
    }

    GENERIC_TERMS = {
        "how",
        "what",
        "why",
        "fix",
        "issue",
        "problem",
        "help",
        "after",
        "when",
        "with",
    }

    ERROR_HINT_TERMS = {
        "error",
        "exception",
        "invalid",
        "failed",
        "failure",
        "timeout",
        "denied",
        "refused",
        "deserialize",
        "deserialization",
        "serialize",
        "serialization",
        "validation",
        "unprocessable",
        "missing",
    }

    TASK_HINT_TERMS = {
        "upload",
        "multipart",
        "form",
        "uploadfile",
        "file",
        "bulk",
        "write",
        "cache",
        "token",
        "login",
        "auth",
        "query",
        "index",
        "cluster",
        "connection",
    }

    def rerank(
        self,
        query: str,
        results: list[dict[str, object]],
        preprocess_result: dict[str, object] | None = None,
    ) -> list[dict[str, object]]:
        boosted = []
        query_tokens = self._normalize_tokens(query)
        preprocess_result = preprocess_result or {}
        keywords = [str(item).lower() for item in preprocess_result.get("keywords", [])]
        error_terms = [str(item).lower() for item in preprocess_result.get("error_terms", [])]
        versions = [str(item).lower() for item in preprocess_result.get("versions", [])]

        task_terms = self._infer_task_terms(keywords, query_tokens)
        framework_terms = self._infer_framework_terms(keywords, query_tokens)
        special_terms = self._infer_special_terms(keywords, query_tokens, framework_terms, task_terms, error_terms)

        for item in results:
            document = item["document"]
            base_score = float(item["score"])
            signals = self._collect_signals(
                document=document,
                framework_terms=framework_terms,
                task_terms=task_terms,
                error_terms=error_terms,
                versions=versions,
                special_terms=special_terms,
                routes=item.get("routes", []),
            )
            rerank_bonus = self._score_signals(signals)
            rerank_penalty = self._penalize_mismatch(signals)
            item["score"] = base_score + rerank_bonus - rerank_penalty
            boosted.append(item)

        return sorted(boosted, key=lambda result: float(result["score"]), reverse=True)

    def _collect_signals(
        self,
        document,
        framework_terms: set[str],
        task_terms: set[str],
        error_terms: list[str],
        versions: list[str],
        special_terms: set[str],
        routes: list[str],
    ) -> MatchSignals:
        title = document.title.lower()
        content = document.content.lower()
        tags = [tag.lower() for tag in document.tags]
        haystack = f"{title}\n{content}"

        framework_hits = sum(1 for term in framework_terms if self._contains_term(term, haystack, tags))
        task_hits = sum(1 for term in task_terms | special_terms if self._contains_term(term, haystack, tags))
        error_hits = sum(1 for term in error_terms if self._contains_term(term, haystack, tags))
        version_hits = sum(1 for term in versions if self._contains_term(term, haystack, tags))
        title_hits = sum(
            1
            for term in framework_terms | task_terms | special_terms | set(error_terms) | set(versions)
            if self._contains_term(term, title, tags=[])
        )
        tag_hits = sum(
            1
            for term in framework_terms | task_terms | special_terms
            if any(term == tag or term in tag for tag in tags)
        )

        return MatchSignals(
            framework_hits=framework_hits,
            task_hits=task_hits,
            error_hits=error_hits,
            version_hits=version_hits,
            title_hits=title_hits,
            tag_hits=tag_hits,
            multi_route=len(routes) > 1,
            accepted=bool(getattr(document, "is_accepted", False)),
            answer_score=int(getattr(document, "score", 0)),
        )

    def _score_signals(self, signals: MatchSignals) -> float:
        score = 0.0
        score += min(signals.framework_hits, 2) * 0.05
        score += min(signals.task_hits, 4) * 0.11
        score += min(signals.error_hits, 3) * 0.14
        score += min(signals.version_hits, 2) * 0.05
        score += min(signals.title_hits, 4) * 0.08
        score += min(signals.tag_hits, 3) * 0.06
        score += 0.08 if signals.multi_route else 0.0
        score += 0.05 if signals.accepted else 0.0
        score += min(max(signals.answer_score, 0), 20) / 400

        if signals.framework_hits and signals.task_hits:
            score += 0.12
        if signals.task_hits and signals.error_hits:
            score += 0.15
        if signals.title_hits >= 2 and signals.task_hits:
            score += 0.08
        if signals.task_hits >= 2 and signals.error_hits >= 1:
            score += 0.06

        return score

    def _penalize_mismatch(self, signals: MatchSignals) -> float:
        penalty = 0.0
        if signals.framework_hits and not signals.task_hits and not signals.error_hits:
            penalty += 0.18
        if signals.framework_hits and signals.task_hits == 0 and signals.title_hits <= 1:
            penalty += 0.08
        if signals.framework_hits == 0 and signals.task_hits == 0 and signals.error_hits == 0:
            penalty += 0.25
        if signals.title_hits == 0 and signals.tag_hits == 0:
            penalty += 0.10
        return penalty

    def _infer_framework_terms(self, keywords: list[str], query_tokens: list[str]) -> set[str]:
        return {
            token
            for token in [*keywords, *query_tokens]
            if token in self.FRAMEWORK_TERMS
        }

    def _infer_task_terms(self, keywords: list[str], query_tokens: list[str]) -> set[str]:
        return {
            token
            for token in [*keywords, *query_tokens]
            if token in self.TASK_HINT_TERMS or len(token) >= 5 and token not in self.GENERIC_TERMS
        }

    def _infer_special_terms(
        self,
        keywords: list[str],
        query_tokens: list[str],
        framework_terms: set[str],
        task_terms: set[str],
        error_terms: list[str],
    ) -> set[str]:
        return {
            token
            for token in [*keywords, *query_tokens]
            if token not in framework_terms
            and token not in task_terms
            and token not in error_terms
            and token not in self.GENERIC_TERMS
            and any(char.isdigit() for char in token) or any(char.isupper() for char in token)
        }

    @staticmethod
    def _normalize_tokens(text: str) -> list[str]:
        return [token.lower() for token in re.split(r"[^A-Za-z0-9_+#.-]+", text) if token]

    @staticmethod
    def _contains_term(term: str, text: str, tags: list[str]) -> bool:
        if term in text:
            return True
        return any(term == tag or term in tag for tag in tags)
