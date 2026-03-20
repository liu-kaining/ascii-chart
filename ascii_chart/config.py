"""
配置管理模块
"""

import os
from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    """LLM 配置"""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4"
    api_key: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """从环境变量加载配置"""
        return cls(
            base_url=os.getenv("ASCII_CHART_BASE_URL", "https://api.openai.com/v1"),
            model=os.getenv("ASCII_CHART_MODEL", "gpt-4"),
            api_key=os.getenv("ASCII_CHART_API_KEY", ""),
            temperature=float(os.getenv("ASCII_CHART_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("ASCII_CHART_MAX_TOKENS", "2048")),
        )


@dataclass
class ChartConfig:
    """图表配置"""
    default_width: int = 80
    default_chart_type: str = "flowchart"
    max_node_label_length: int = 40

    @classmethod
    def from_env(cls) -> "ChartConfig":
        """从环境变量加载配置"""
        return cls(
            default_width=int(os.getenv("ASCII_CHART_WIDTH", "80")),
            default_chart_type=os.getenv("ASCII_CHART_DEFAULT_TYPE", "flowchart"),
            max_node_label_length=int(os.getenv("ASCII_CHART_MAX_LABEL_LEN", "40")),
        )
