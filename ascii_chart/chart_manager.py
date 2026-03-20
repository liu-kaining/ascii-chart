"""
图表管理器 - 统一入口
"""

import json
from typing import Optional
from ascii_chart.llm.base import BaseLLMClient, ChatMessage, LLMError, ParseError
from ascii_chart.charts.base import ChartData
from ascii_chart.charts.flowchart import FlowchartData
from ascii_chart.charts.architecture import ArchitectureData
from ascii_chart.charts.sequence import SequenceData
from ascii_chart.charts.table import TableData
from ascii_chart.charts.state import StateData
from ascii_chart.charts.types import SUPPORTED_CHART_TYPES, CHART_TYPE_DESCRIPTIONS
from ascii_chart.renderers.ascii import ASCIRenderer
from ascii_chart.config import LLMConfig


# 系统提示词
SYSTEM_PROMPT = """你是一个专业的 ASCII 图表生成器。用户会输入图表描述，你需要生成对应的结构化 JSON 数据。

支持的图表类型：
- flowchart: 流程图，用于描述流程和决策路径
- architecture: 架构图，用于描述系统分层和组件关系
- sequence: 序列图，用于描述对象间的交互顺序
- table: 表格，用于以行列形式展示数据
- state: 状态图，用于描述状态转换

输出格式要求：
1. 严格按照 JSON 格式输出，不要包含其他内容
2. 确保 JSON 可以被 Python json.loads() 解析
3. 所有文本使用中文或英文都可以

图表格式说明：

【流程图 flowchart】
{
  "type": "flowchart",
  "nodes": [
    {"id": "node1", "label": "节点标签", "node_type": "start/end/process/decision"}
  ],
  "edges": [
    {"from_node": "node1", "to_node": "node2", "label": "可选标签"}
  ]
}

【架构图 architecture】
{
  "type": "architecture",
  "layers": [
    {
      "name": "层名称",
      "components": [
        {"id": "comp1", "name": "组件名称"}
      ]
    }
  ]
}

【序列图 sequence】
{
  "type": "sequence",
  "participants": [
    {"id": "p1", "name": "参与者名称"}
  ],
  "interactions": [
    {"from_participant": "p1", "to_participant": "p2", "message": "消息内容", "arrow": "→"}
  ]
}

【表格 table】
{
  "type": "table",
  "headers": ["列1", "列2"],
  "rows": [
    ["值1", "值2"]
  ]
}

【状态图 state】
{
  "type": "state",
  "nodes": [
    {"id": "s1", "label": "状态名称", "node_type": "start/end"}
  ],
  "edges": [
    {"from_node": "s1", "to_node": "s2", "label": "转换条件"}
  ]
}
"""


class ChartManager:
    """图表管理器 - 统一入口"""

    def __init__(
        self,
        llm_client: BaseLLMClient,
        renderer: Optional[ASCIRenderer] = None,
        width: int = 80,
    ):
        """
        初始化图表管理器

        Args:
            llm_client: LLM 客户端实例
            renderer: ASCII 渲染器，默认使用 ASCIRenderer
            width: 输出宽度，默认 80
        """
        self.llm = llm_client
        self.renderer = renderer or ASCIRenderer(width=width)
        self.width = width

    def draw(self, description: str, chart_type: Optional[str] = None) -> str:
        """
        主入口方法 - 根据描述生成 ASCII 图表

        Args:
            description: 图表描述，自然语言描述
            chart_type: 图表类型，不指定则让 LLM 推断

        Returns:
            ASCII 图表字符串
        """
        # 1. 构建提示词
        prompt = self._build_prompt(description, chart_type)

        # 2. 调用 LLM
        messages = [
            ChatMessage(role="system", content=SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ]

        try:
            response = self.llm.chat(messages)
        except LLMError as e:
            raise LLMError(f"LLM 调用失败: {e}")

        # 3. 解析 JSON
        chart_data = self._parse_response(response)

        # 4. 渲染为 ASCII
        return self.renderer.render(chart_data)

    def _build_prompt(self, description: str, chart_type: Optional[str]) -> str:
        """构建提示词"""
        if chart_type and chart_type in SUPPORTED_CHART_TYPES:
            type_desc = CHART_TYPE_DESCRIPTIONS.get(chart_type, "")
            return f"请生成一个 {chart_type} ({type_desc})：\n\n{description}\n\n请直接输出 JSON，不要包含其他内容。"
        else:
            return f"""请根据以下描述生成图表。首先判断最合适的图表类型，然后生成对应的 JSON。

描述：{description}

请先说明图表类型，然后直接输出 JSON，不要包含其他内容。"""

    def _parse_response(self, response: str) -> ChartData:
        """
        解析 LLM 响应，提取 JSON 并转换为 ChartData

        Args:
            response: LLM 响应文本

        Returns:
            ChartData 对象
        """
        # 尝试提取 JSON
        json_str = self._extract_json(response)

        if not json_str:
            raise ParseError("无法从响应中提取 JSON")

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ParseError(f"JSON 解析失败: {e}")

        # 根据类型转换为对应的 ChartData
        chart_type = data.get("type", "")

        if chart_type == "flowchart":
            return FlowchartData.from_dict(data)
        elif chart_type == "architecture":
            return ArchitectureData.from_dict(data)
        elif chart_type == "sequence":
            return SequenceData.from_dict(data)
        elif chart_type == "table":
            return TableData.from_dict(data)
        elif chart_type == "state":
            return StateData.from_dict(data)
        else:
            raise ParseError(f"未知的图表类型: {chart_type}")

    def _extract_json(self, text: str) -> Optional[str]:
        """
        从文本中提取 JSON 字符串

        处理 Markdown 代码块等格式

        Args:
            text: 原始文本

        Returns:
            JSON 字符串，如果不存在则返回 None
        """
        import re

        # 尝试直接解析
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            pass

        # 尝试从代码块中提取
        # ```json ... ```
        pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                json.loads(match.strip())
                return match.strip()
            except json.JSONDecodeError:
                continue

        # 尝试找 { ... }
        brace_start = text.find("{")
        if brace_start != -1:
            # 找到最后一个 }
            brace_end = text.rfind("}")
            if brace_end != -1:
                candidate = text[brace_start:brace_end + 1]
                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError:
                    pass

        return None

    def draw_flowchart(self, description: str) -> str:
        """直接生成流程图"""
        return self.draw(description, "flowchart")

    def draw_architecture(self, description: str) -> str:
        """直接生成架构图"""
        return self.draw(description, "architecture")

    def draw_sequence(self, description: str) -> str:
        """直接生成序列图"""
        return self.draw(description, "sequence")

    def draw_table(self, description: str) -> str:
        """直接生成表格"""
        return self.draw(description, "table")

    def draw_state(self, description: str) -> str:
        """直接生成状态图"""
        return self.draw(description, "state")
