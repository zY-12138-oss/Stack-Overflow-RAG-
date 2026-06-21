from __future__ import annotations

import re

from app.providers.llm.base import LLMProvider


class AnswerService:
    SOLUTION_PATTERNS = (
        re.compile(r"\bdowngrade(?:d)?(?: from [^.,;\n]+)? to ([^.,;\n]+)", re.IGNORECASE),
        re.compile(r"\bupgrade(?:d)?(?: from [^.,;\n]+)? to ([^.,;\n]+)", re.IGNORECASE),
        re.compile(r"\bsolved(?: this issue| the issue| it)?\b", re.IGNORECASE),
        re.compile(r"\bfixed(?: this issue| the issue| it)?\b", re.IGNORECASE),
    )

    VERSION_PATTERN = re.compile(r"\b(?:cli|supabase|deno|docker)?\s*\d+\.\d+(?:\.\d+)?\b", re.IGNORECASE)

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm_provider = llm_provider

    def answer(self, question: str, context: str) -> tuple[str, str, list[str]]:
        if not context.strip():
            return (
                "当前检索到的上下文不足以确认答案，建议补充错误日志、版本号或关键代码片段后再试。",
                "low",
                [
                    "回答基于当前检索上下文生成。",
                    "当前上下文不足，建议补充原始报错、版本号或代码片段。",
                ],
            )

        extracted = self._extract_actionable_answer(context)
        if extracted is not None:
            answer, confidence, notes = extracted
            return answer, confidence, notes

        answer = self.llm_provider.generate_answer(question=question, context=context)
        return (
            answer,
            "medium",
            [
                "回答基于当前检索上下文生成。",
                "关键英文术语建议与原帖对照确认。",
            ],
        )

    def _extract_actionable_answer(self, context: str) -> tuple[str, str, list[str]] | None:
        lines = [line.strip() for line in context.splitlines() if line.strip()]
        title = self._find_prefixed_value(lines, "Title:")
        excerpt = self._find_multiline_prefixed_value(lines, "Answer Excerpt:")

        if not excerpt:
            return None
        if not any(pattern.search(excerpt) for pattern in self.SOLUTION_PATTERNS):
            return None

        versions = self.VERSION_PATTERN.findall(excerpt)
        versions = [item.strip() for item in versions if item.strip()]
        versions = list(dict.fromkeys(versions))

        reason = self._build_reason_summary(title, versions)
        action = self._build_action_summary(excerpt)
        notes = [
            "回答优先提取了命中文档中的明确结论或操作建议。",
            "建议仍与原始 Stack Overflow 回帖对照确认版本和操作步骤。",
        ]
        if versions:
            notes.append(f"命中文档中识别到的版本信息：{', '.join(versions[:3])}")

        return f"{reason}{action}", "high", notes

    @staticmethod
    def _find_prefixed_value(lines: list[str], prefix: str) -> str:
        for line in lines:
            if line.startswith(prefix):
                return line[len(prefix):].strip()
        return ""

    @staticmethod
    def _find_multiline_prefixed_value(lines: list[str], prefix: str) -> str:
        result = []
        capturing = False
        for line in lines:
            if line.startswith(prefix):
                capturing = True
                result.append(line[len(prefix):].strip())
            elif capturing:
                if line.startswith("[Document") or line.startswith("Title:") or line.startswith("Tags:") or line.startswith("Source:"):
                    break
                result.append(line)
        return " ".join(result)

    @staticmethod
    def _build_action_summary(excerpt: str) -> str:
        downgrade_match = re.search(
            r"\bdowngrade(?:d)?(?: from [^.,;\n]+)? to ([\d.]+)",
            excerpt,
            re.IGNORECASE,
        )
        if downgrade_match:
            return f"解决方式是将相关版本降级到 `{downgrade_match.group(1).strip()}`。"

        upgrade_match = re.search(
            r"\bupgrade(?:d)?(?: from [^.,;\n]+)? to ([\d.]+)",
            excerpt,
            re.IGNORECASE,
        )
        if upgrade_match:
            return f"解决方式是将相关版本升级到 `{upgrade_match.group(1).strip()}`。"

        lowered = excerpt.lower()
        if "solved" in lowered or "fixed" in lowered:
            return "命中文档表明这是一个已知问题，按帖子中的版本调整或兼容方案处理后可以恢复正常。"

        return "命中文档中存在明确的修复结论，建议按原帖中的操作步骤直接验证。"

    @staticmethod
    def _build_reason_summary(title: str, versions: list[str]) -> str:
        if versions:
            version_text = "、".join(versions[:2])
            return (
                f"根据命中的帖子“{title}”，这更像是 `{version_text}` "
                "相关的本地运行时或 CLI 版本问题，而不是业务代码本身写错。"
            )
        return f"根据命中的帖子“{title}”，这更像是工具链或运行时版本问题，而不是业务代码本身写错。"
