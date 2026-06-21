from __future__ import annotations

from typing import Any

import httpx

from app.providers.llm.base import LLMProvider


class OpenAICompatibleLLMProvider(LLMProvider):
    def __init__(
        self,
        api_key: str,
        model_name: str,
        base_url: str,
        timeout_seconds: float = 60.0,
        rewrite_model_name: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.rewrite_model_name = rewrite_model_name or model_name

    def generate_answer(self, question: str, context: str) -> str:
        system_prompt = (
            "你是一个技术问答助手。"
            "请仅根据提供的 Stack Overflow 检索上下文回答用户问题。"
            "如果上下文不足，请明确说明。"
            "回答使用中文，但保留关键英文术语、报错信息、类名、方法名、配置项原文。"
            "回答要求：\n"
            "1. 先给出问题原因（基于上下文推断）。\n"
            "2. 再给出具体可操作的排查步骤或解决方案（如命令、代码片段、配置修改）。\n"
            "3. 如果上下文中包含解决代码或配置示例，请直接引用。\n"
            "4. 不要编造上下文中不存在的信息。\n"
            "5. 不要输出空泛的建议（如'建议核对报错原文'），要给出实质性内容。"
        )
        user_prompt = (
            f"用户问题：{question}\n\n"
            f"检索上下文：\n{context}\n\n"
            "请输出中文回答，包含原因分析和具体解决步骤。"
        )
        return self._chat(
            model=self.model_name,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        )

    def rewrite_query(self, query: str) -> str:
        system_prompt = (
            "你是一个面向英文技术知识库的查询改写器。"
            "请将中文技术问题改写为适合 Stack Overflow 检索的简洁英文查询。"
            "保留关键英文术语、错误信息、类名、方法名、库名、版本号。"
            "不要解释，不要加引号，只输出英文检索语句。"
        )
        return self._chat(
            model=self.rewrite_model_name,
            system_prompt=system_prompt,
            user_prompt=query,
            temperature=0.0,
        ).strip()

    def _chat(self, model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        return payload["choices"][0]["message"]["content"].strip()
