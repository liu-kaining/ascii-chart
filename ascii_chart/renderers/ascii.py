"""
ASCII 渲染器 - 将图表数据渲染为 ASCII 字符
"""

from abc import ABC, abstractmethod
from typing import Optional
from ascii_chart.charts.base import ChartData
from ascii_chart.charts.flowchart import FlowchartData
from ascii_chart.charts.architecture import ArchitectureData
from ascii_chart.charts.sequence import SequenceData
from ascii_chart.charts.table import TableData
from ascii_chart.charts.state import StateData


class BaseRenderer(ABC):
    """渲染器抽象基类"""

    @abstractmethod
    def render(self, chart_data: ChartData) -> str:
        """将图表数据渲染为 ASCII 字符串"""
        pass


class ASCIRenderer:
    """ASCII 图表渲染器"""

    def __init__(self, width: int = 80):
        self.width = width

    def render(self, chart_data: ChartData) -> str:
        """
        根据图表类型调用对应的渲染方法

        Args:
            chart_data: 图表数据

        Returns:
            ASCII 字符串
        """
        if isinstance(chart_data, FlowchartData):
            return self._render_flowchart(chart_data)
        elif isinstance(chart_data, ArchitectureData):
            return self._render_architecture(chart_data)
        elif isinstance(chart_data, SequenceData):
            return self._render_sequence(chart_data)
        elif isinstance(chart_data, TableData):
            return self._render_table(chart_data)
        elif isinstance(chart_data, StateData):
            return self._render_state(chart_data)
        else:
            raise ValueError(f"Unsupported chart type: {type(chart_data)}")

    def _render_flowchart(self, data: FlowchartData) -> str:
        """渲染流程图"""
        lines = []

        # 按拓扑排序排列节点
        ordered = self._topological_sort_flowchart(data)
        node_map = {n.id: n for n in data.nodes}

        # 计算每个节点的出度和入度
        for i, node_id in enumerate(ordered):
            node = node_map[node_id]
            outgoing = data.get_outgoing_edges(node_id)

            # 渲染节点
            if node.node_type == "start" or node.node_type == "end":
                # 圆角矩形
                lines.append(f"┌───────┐")
                lines.append(f"│ {node.label:^5} │")
                lines.append(f"└───────┘")
            elif node.node_type == "decision":
                # 菱形
                label = node.label
                lines.append(f"   ╱ {label} ╲")
                lines.append(f"  ╱       ╲")
                lines.append(f" ╱         ╲")
            elif node.node_type == "comment":
                # 注释/说明
                lines.append(f"│ {node.label}")
            else:
                # 普通矩形
                label = node.label
                lines.append(f"┌────┐")
                lines.append(f"│{label}│")
                lines.append(f"└────┘")

            # 渲染连接线
            if outgoing:
                if len(outgoing) == 1:
                    lines.append(" │")
                    lines.append(" ▼")
                elif len(outgoing) == 2:
                    # 分支
                    lines.append(" │")
                    lines.append(" ├──○")
                    lines.append(" │")
                    lines.append(" └──○")
                    # 继续渲染两个分支
                    for edge in outgoing:
                        branch_label = edge.label or ""
                        branch_node = node_map.get(edge.to_node)
                        if branch_node:
                            lines.append(f" │  (分支: {branch_label})")
                            if branch_node.node_type in ("start", "end"):
                                lines.append(f" │  ┌───────┐")
                                lines.append(f" │  │ {branch_node.label:^5} │")
                                lines.append(f" │  └───────┘")
                            else:
                                lines.append(f" │  ┌────┐")
                                lines.append(f" │  │{branch_node.label}│")
                                lines.append(f" │  └────┘")
                else:
                    lines.append(" │")
                    lines.append(" ▼")

        return "\n".join(lines)

    def _topological_sort_flowchart(self, data: FlowchartData) -> list[str]:
        """拓扑排序流程图节点"""
        # 简单的拓扑排序
        in_degree = {n.id: 0 for n in data.nodes}
        for edge in data.edges:
            in_degree[edge.to_node] = in_degree.get(edge.to_node, 0) + 1

        # 找到入度为0的节点（通常应该是start）
        result = []
        queue = [n.id for n in data.nodes if in_degree[n.id] == 0]

        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            for edge in data.edges:
                if edge.from_node == node_id:
                    in_degree[edge.to_node] -= 1
                    if in_degree[edge.to_node] == 0:
                        queue.append(edge.to_node)

        # 如果没有排序成功（可能有环），按原始顺序返回
        if len(result) != len(data.nodes):
            return [n.id for n in data.nodes]

        return result

    def _render_architecture(self, data: ArchitectureData) -> str:
        """渲染架构图"""
        lines = []
        separator = "─" * (self.width - 2)

        for i, layer in enumerate(data.layers):
            # 渲染层名
            lines.append("┌─ " + layer.name + " " + "─" * (self.width - len(layer.name) - 4) + "┐")

            # 渲染该层的组件
            components_str = " │ ".join(c.name for c in layer.components)
            lines.append(f"│ {components_str:<{self.width - 4}} │")

            # 渲染层分隔符
            if i < len(data.layers) - 1:
                lines.append(f"├─ {separator} ┤")
            else:
                lines.append(f"└─ {separator} ┘")

        return "\n".join(lines)

    def _render_sequence(self, data: SequenceData) -> str:
        """渲染序列图"""
        lines = []

        # 渲染参与者头部
        participant_names = [p.name for p in data.participants]
        header = "│ " + " │ ".join(f"{name:^15}" for name in participant_names) + " │"
        lines.append(header)

        # 渲染分隔线
        divider = "├─" + "─┼─".join("─" * 17 for _ in data.participants) + "─┤"
        lines.append(divider)

        # 渲染生命线
        lifeline = "│ " + " │ ".join("▼" * 15 for _ in data.participants) + " │"
        lines.append(lifeline)

        # 渲染交互
        for interaction in data.interactions:
            # 找到 from 和 to 的索引
            from_idx = next(i for i, p in enumerate(data.participants) if p.id == interaction.from_participant)
            to_idx = next(i for i, p in enumerate(data.participants) if p.id == interaction.to_participant)

            # 构建消息行
            spaces = ["          " for _ in data.participants]
            if from_idx < to_idx:
                # 向右箭头
                spaces[from_idx] = f"──{interaction.arrow}─"
                spaces[to_idx] = f"──→         "
            else:
                # 向左箭头（返回）
                spaces[from_idx] = f"←──"
                spaces[to_idx] = f"──{interaction.arrow}  "

            spaces[from_idx] = spaces[from_idx][:8] + interaction.message[:8]

            msg = "│ " + "│".join(spaces) + " │"
            lines.append(msg)
            lines.append(divider)

        return "\n".join(lines)

    def _render_table(self, data: TableData) -> str:
        """渲染表格"""
        if not data.headers:
            return ""

        # 计算每列的最大宽度
        col_widths = [len(h) for h in data.headers]
        for row in data.rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        lines = []

        # 渲染表头
        header_line = "┌─" + "─┬─".join("─" * w for w in col_widths) + "─┐"
        lines.append(header_line)
        header_cells = "│ " + " │ ".join(f"{h:^{col_widths[i]}}" for i, h in enumerate(data.headers)) + " │"
        lines.append(header_cells)

        # 渲染表头与内容的分隔
        header_divider = "├─" + "─┼─".join("─" * w for w in col_widths) + "─┤"
        lines.append(header_divider)

        # 渲染数据行
        for row in data.rows:
            cells = []
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    cells.append(f"{str(cell):^{col_widths[i]}}")
                else:
                    cells.append(f"{str(cell):^15}")
            row_line = "│ " + " │ ".join(cells) + " │"
            lines.append(row_line)

        # 渲染表格底部
        bottom_line = "└─" + "─┴─".join("─" * w for w in col_widths) + "─┘"
        lines.append(bottom_line)

        return "\n".join(lines)

    def _render_state(self, data: StateData) -> str:
        """渲染状态图"""
        lines = []

        # 简单的状态渲染
        for i, node in enumerate(data.nodes):
            if i == 0:
                lines.append(f"◎─→┌ {node.label} ┐")
            elif node.node_type == "end":
                lines.append(f"  └─→ ◎ {node.label}")
            else:
                lines.append(f"  └─→┌ {node.label} ┐")

            # 渲染转换
            for edge in data.get_outgoing_edges(node.id):
                label = edge.label or ""
                lines.append(f"     │  {label}")

        return "\n".join(lines)
