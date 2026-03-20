"""
LLM 基础模块 - 定义接口和消息结构
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChatMessage:
    """对话消息"""
    role: str  # "system", "user", "assistant"
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


class BaseLLMClient(ABC):
    """LLM 客户端抽象基类"""

    @abstractmethod
    def chat(self, messages: list[ChatMessage]) -> str:
        """
        发送对话请求，返回文本响应

        Args:
            messages: 对话消息列表

        Returns:
            LLM 响应的文本内容
        """
        pass

    @abstractmethod
    def set_temperature(self, temperature: float) -> None:
        """设置温度参数"""
        pass

    @abstractmethod
    def set_max_tokens(self, max_tokens: int) -> None:
        """设置最大 token 数"""
        pass


class LLMError(Exception):
    """LLM 调用错误"""
    pass


class ParseError(Exception):
    """JSON 解析错误"""
    pass


class ValidationError(Exception):
    """数据校验错误"""
    pass
