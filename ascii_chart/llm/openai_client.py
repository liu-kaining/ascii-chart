"""
OpenAI 兼容客户端
"""

import json
import requests
from typing import Optional
from ascii_chart.llm.base import BaseLLMClient, ChatMessage, LLMError


class OpenAIClient(BaseLLMClient):
    """OpenAI 兼容的 LLM 客户端"""

    def __init__(
        self,
        base_url: str = "https://api.openai.com/v1",
        api_key: str = "",
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._session = requests.Session()

    def chat(self, messages: list[ChatMessage]) -> str:
        """
        发送对话请求到 OpenAI 兼容 API

        Args:
            messages: 对话消息列表

        Returns:
            LLM 响应的文本内容
        """
        if not self.api_key:
            raise LLMError("API key is required")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": self.model,
            "messages": [msg.to_dict() for msg in messages],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        try:
            response = self._session.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()

            if "choices" not in data or len(data["choices"]) == 0:
                raise LLMError("No response from LLM")

            return data["choices"][0]["message"]["content"]

        except requests.exceptions.Timeout:
            raise LLMError("Request timeout")
        except requests.exceptions.RequestException as e:
            raise LLMError(f"Request failed: {e}")
        except json.JSONDecodeError:
            raise LLMError("Invalid JSON response")
        except KeyError as e:
            raise LLMError(f"Unexpected response format: {e}")

    def set_temperature(self, temperature: float) -> None:
        """设置温度参数"""
        self.temperature = temperature

    def set_max_tokens(self, max_tokens: int) -> None:
        """设置最大 token 数"""
        self.max_tokens = max_tokens
