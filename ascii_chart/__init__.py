"""
ascii-chart: LLM-powered ASCII chart generator

Usage:
    from ascii_chart import ChartManager, OpenAIClient

    client = OpenAIClient(api_key="sk-xxx")
    manager = ChartManager(client)
    result = manager.draw("画一个用户登录的流程图")
    print(result)
"""

__version__ = "0.1.0"

from ascii_chart.config import LLMConfig, ChartConfig
from ascii_chart.llm.base import BaseLLMClient, ChatMessage
from ascii_chart.llm.openai_client import OpenAIClient
from ascii_chart.llm.anthropic_client import AnthropicClient
from ascii_chart.charts.base import ChartData, Node, Edge
from ascii_chart.charts.flowchart import FlowchartData
from ascii_chart.charts.architecture import ArchitectureData
from ascii_chart.charts.sequence import SequenceData
from ascii_chart.charts.table import TableData
from ascii_chart.charts.state import StateData
from ascii_chart.renderers.ascii import ASCIRenderer
from ascii_chart.chart_manager import ChartManager

__all__ = [
    # Version
    "__version__",
    # Config
    "LLMConfig",
    "ChartConfig",
    # LLM
    "BaseLLMClient",
    "ChatMessage",
    "OpenAIClient",
    "AnthropicClient",
    # Charts
    "ChartData",
    "Node",
    "Edge",
    "FlowchartData",
    "ArchitectureData",
    "SequenceData",
    "TableData",
    "StateData",
    # Renderers
    "ASCIRenderer",
    # Manager
    "ChartManager",
]
