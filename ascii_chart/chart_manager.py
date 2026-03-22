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


# 系统提示词 - 针对不同图表类型优化
SYSTEM_PROMPT = """你是一个 ASCII 图表生成器。请根据用户描述生成结构化 JSON 数据。

【重要规则】
1. 只输出纯 JSON，不要任何 Markdown 代码块包裹
2. JSON 必须能被 Python json.loads() 直接解析
3. 不要输出任何解释性文字

【图表类型与格式】

1. 流程图 (flowchart) - 用于业务流程、决策路径
```json
{
  "type": "flowchart",
  "nodes": [
    {"id": "n1", "label": "显示文本", "node_type": "start/end/process/decision"}
  ],
  "edges": [
    {"from_node": "n1", "to_node": "n2", "label": "条件(可选)"}
  ]
}
```
node_type 说明：start=开始, end=结束, process=处理步骤, decision=判断分支

2. 架构图 (architecture) - 用于系统分层、组件关系
```json
{
  "type": "architecture",
  "layers": [
    {"name": "层名", "components": [{"id": "c1", "name": "组件名"}]}
  ]
}
```

3. 序列图 (sequence) - 用于对象交互、时序流程
```json
{
  "type": "sequence",
  "participants": [{"id": "p1", "name": "参与者名"}],
  "interactions": [{"from_participant": "p1", "to_participant": "p2", "message": "消息内容"}]
}
```

4. 表格 (table) - 用于展示数据
```json
{
  "type": "table",
  "headers": ["列1", "列2"],
  "rows": [["值1", "值2"]]
}
```

5. 状态图 (state) - 用于状态机、状态转换
```json
{
  "type": "state",
  "nodes": [{"id": "s1", "label": "状态名", "node_type": "start/end"}],
  "edges": [{"from_node": "s1", "to_node": "s2", "label": "转换条件"}]
}
```

【节点ID命名规则】
- 英文简短ID，如 n1, n2, n3 或 start, process, end
- 确保 edges 中的 from_node/to_node 引用存在
- ID 保持唯一

请直接输出 JSON。
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
            return f"请生成一个 {chart_type}（{type_desc}）：\n\n{description}\n\n直接输出 JSON。"
        else:
            return f"""请根据以下描述生成图表。判断最合适的图表类型，然后生成对应的 JSON。

描述：{description}

直接输出 JSON，不要有任何其他文字。"""

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
            json.loads(text.strip())
            return text.strip()
        except json.JSONDecodeError:
            pass

        # 清理 Markdown 代码块
        # ```json ... ``` 或 ``` ... ```
        pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                json.loads(match.strip())
                return match.strip()
            except json.JSONDecodeError:
                continue

        # 尝试找 { ... } 块
        brace_start = text.find("{")
        if brace_start != -1:
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
