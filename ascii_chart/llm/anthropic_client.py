"""
Anthropic 客户端
"""

import json
import os
from typing import Optional
from ascii_chart.llm.base import BaseLLMClient, ChatMessage, LLMError


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude API 客户端"""

    ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1"

    def __init__(
        self,
        api_key: str = "",
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._session = None

    def _get_session(self):
        """懒加载会话"""
        if self._session is None:
            import requests
            self._session = requests.Session()
        return self._session

    def chat(self, messages: list[ChatMessage]) -> str:
        """
        发送对话请求到 Anthropic API

        Args:
            messages: 对话消息列表

        Returns:
            LLM 响应的文本内容
        """
        if not self.api_key:
            raise LLMError("API key is required")

        # 将消息格式转换为 Anthropic 格式
        system_message = ""
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                })

        url = f"{self.ANTHROPIC_BASE_URL}/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }
        payload = {
            "model": self.model,
            "messages": anthropic_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if system_message:
            payload["system"] = system_message

        try:
            session = self._get_session()
            response = session.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()

            if "content" not in data or len(data["content"]) == 0:
                raise LLMError("No response from LLM")

            # Anthropic 返回的是 content blocks 格式
            return data["content"][0]["text"]

        except Exception as e:
            if isinstance(e, LLMError):
                raise
            raise LLMError(f"Anthropic API error: {e}")

    def set_temperature(self, temperature: float) -> None:
        """设置温度参数"""
        self.temperature = temperature

    def set_max_tokens(self, max_tokens: int) -> None:
        """设置最大 token 数"""
        self.max_tokens = max_tokens
