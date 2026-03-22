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
        """渲染流程图 - 简化版，垂直布局"""
        if not data.nodes:
            return ""

        # 构建节点映射
        node_map = {n.id: n for n in data.nodes}

        # 找起始节点（入度为0的节点）
        in_degree = {n.id: 0 for n in data.nodes}
        for edge in data.edges:
            in_degree[edge.to_node] += 1
        start_nodes = [n for n in data.nodes if in_degree[n.id] == 0]
        start = start_nodes[0] if start_nodes else data.nodes[0]

        # 计算最大宽度
        max_width = max(len(n.label) + 4 for n in data.nodes)
        max_width = max(max_width, 30)

        lines = []

        # 从起始节点开始深度优先遍历
        visited = set()
        self._render_flowchart_node(start, node_map, data, visited, lines, max_width)

        return "\n".join(lines)

    def _render_flowchart_node(self, node, node_map, data, visited, lines, width):
        """递归渲染流程图节点"""
        if node.id in visited:
            return
        visited.add(node.id)

        # 渲染节点
        if node.node_type == "start" or node.node_type == "end":
            lines.append(self._render_rounded_box(node.label, width))
        elif node.node_type == "decision":
            lines.append(self._render_diamond(node.label, width))
        else:
            lines.append(self._render_rectangle(node.label, width))

        # 获取出边
        outgoing = data.get_outgoing_edges(node.id)

        if outgoing:
            if len(outgoing) == 1:
                # 单向出边，渲染向下箭头
                lines.append(self._render_arrow_down(width))
                self._render_flowchart_node(node_map[outgoing[0].to_node], node_map, data, visited, lines, width)
            elif len(outgoing) == 2:
                # 分支 - 先渲染一个向下箭头，然后渲染两个分支
                lines.append(self._render_arrow_down(width))
                # 渲染分支
                lines.append(self._render_branch(width))
                # 分支1
                edge1 = outgoing[0]
                label1 = f"({edge1.label}) " if edge1.label else ""
                lines.append(self._render_branch_node_line(label1 + node_map[edge1.to_node].label, width, 'left'))
                lines.append(self._render_branch_connector(width, 'left'))
                visited.add(edge1.to_node)  # 标记已访问
                # 分支2
                edge2 = outgoing[1]
                label2 = f"({edge2.label}) " if edge2.label else ""
                lines.append(self._render_branch_node_line(label2 + node_map[edge2.to_node].label, width, 'right'))
                lines.append(self._render_branch_connector(width, 'right'))
                visited.add(edge2.to_node)
        else:
            # 末端节点，渲染底部
            pass

    def _render_rectangle(self, text: str, width: int) -> str:
        """渲染矩形框"""
        text = text[:width - 4]
        return f"┌{'─' * (width - 2)}┐\n│ {text:^{width - 4}} │\n└{'─' * (width - 2)}┘"

    def _render_rounded_box(self, text: str, width: int) -> str:
        """渲染圆角框"""
        text = text[:width - 4]
        return f"╭{'─' * (width - 2)}╮\n│ {text:^{width - 4}} │\n╰{'─' * (width - 2)}╯"

    def _render_diamond(self, text: str, width: int) -> str:
        """渲染菱形（决策节点）"""
        inner_width = width - 4
        lines = []
        # 上半部分
        for i in range(inner_width // 2):
            padding = i + 1
            lines.append(' ' * padding + '╱' + ' ' * (inner_width - padding * 2) + '╲')
        # 中间行
        lines.append(f" {text:^{inner_width}} ")
        # 下半部分
        for i in range(inner_width // 2 - 1, -1, -1):
            padding = i + 1
            lines.append(' ' * padding + '╲' + ' ' * (inner_width - padding * 2) + '╱')
        return "\n".join(lines)

    def _render_arrow_down(self, width: int) -> str:
        """渲染向下箭头"""
        return '│' + ' ' * (width // 2) + '▼' + ' ' * (width - width // 2 - 1) + '│'

    def _render_branch(self, width: int) -> str:
        """渲染分支起点"""
        inner = width - 2
        half = inner // 2
        return '├' + '─' * half + '┴' + '─' * (inner - half) + '┤'

    def _render_branch_node_line(self, text: str, width: int, side: str) -> str:
        """渲染分支节点行"""
        if side == 'left':
            return '│' + text + ' ' * (width - len(text) - 1)
        else:
            return ' ' * (width // 2 + 1) + text + '│'

    def _render_branch_connector(self, width: int, side: str) -> str:
        """渲染分支连接线"""
        if side == 'left':
            return '│' + ' ' * (width - 1)
        else:
            return ' ' * (width // 2 + 1) + '│'

    def _topological_sort_flowchart(self, data: FlowchartData) -> list[str]:
        """拓扑排序流程图节点"""
        in_degree = {n.id: 0 for n in data.nodes}
        for edge in data.edges:
            in_degree[edge.to_node] = in_degree.get(edge.to_node, 0) + 1

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

        if len(result) != len(data.nodes):
            return [n.id for n in data.nodes]

        return result

    def _render_architecture(self, data: ArchitectureData) -> str:
        """渲染分层架构图 - 整体矩形框，内部用虚线分隔层"""
        if not data.layers:
            return ""

        # 计算每层需要的宽度
        # 宽度 = max(所有组件名的最大长度, 20)
        max_component_len = 0
        for layer in data.layers:
            for comp in layer.components:
                max_component_len = max(max_component_len, len(comp.name))

        # 每层显示宽度
        layer_width = max(max_component_len + 4, 24)

        # 总宽度 = 层宽 + 左右边框(2)
        total_width = layer_width + 2

        lines = []

        # 渲染顶层边框
        lines.append("┌" + "─" * (total_width - 2) + "┐")

        # 渲染每一层
        for layer_idx, layer in enumerate(data.layers):
            # 层名行
            layer_name = f"│ {layer.name} │"
            lines.append(layer_name)

            # 层内分隔线（用虚线表示）
            if layer.components:
                for comp in layer.components:
                    comp_line = f"│ {comp.name:<{layer_width - 2}} │"
                    lines.append(comp_line)

            # 层之间加分隔线（最后一层除外）
            if layer_idx < len(data.layers) - 1:
                lines.append("├" + "─" * (total_width - 2) + "┤")

        # 渲染底层边框
        lines.append("└" + "─" * (total_width - 2) + "┘")

        return "\n".join(lines)

    def _render_sequence(self, data: SequenceData) -> str:
        """渲染序列图"""
        if not data.participants:
            return ""

        lines = []
        col_width = 20

        # 计算总宽度
        total_width = 4 + len(data.participants) * col_width

        # 渲染参与者头部
        header = "┌" + "─" * (total_width - 2) + "┐"
        lines.append(header)

        names_line = "│"
        for p in data.participants:
            names_line += f" {p.name:^{col_width - 2}} │"
        lines.append(names_line)

        # 渲染生命线
        lifeline = "├"
        for i in range(len(data.participants)):
            lifeline += "┬" + "─" * (col_width - 2) if i < len(data.participants) - 1 else "─" * (col_width - 2) + "┤"
        lines.append(lifeline)

        # 渲染交互
        for interaction in data.interactions:
            from_idx = next((i for i, p in enumerate(data.participants) if p.id == interaction.from_participant), 0)
            to_idx = next((i for i, p in enumerate(data.participants) if p.id == interaction.to_participant), 0)

            # 构建消息行
            msg_line = "│"
            for i in range(len(data.participants)):
                if i == from_idx:
                    if from_idx < to_idx:
                        msg_line += f"──{interaction.arrow}─▶│"
                    else:
                        msg_line += f"◀──{interaction.arrow}─│"
                elif i == to_idx:
                    msg_line += f" {interaction.message:<{col_width - 4}} │"
                else:
                    msg_line += " " * col_width + "│"
            lines.append(msg_line)
            lines.append(lifeline)

        # 渲染底部
        bottom = "└" + "─" * (total_width - 2) + "┘"
        lines.append(bottom)

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
        if not data.nodes:
            return ""

        lines = []
        node_map = {n.id: n for n in data.nodes}

        for node in data.nodes:
            outgoing = data.get_outgoing_edges(node.id)

            # 渲染状态
            lines.append(f"╭─────────╮")
            lines.append(f"│ {node.label:^7} │")
            lines.append(f"╰─────────╯")

            # 渲染转换
            for edge in outgoing:
                target = node_map.get(edge.to_node)
                if target:
                    label = edge.label or ""
                    lines.append(f"    │")
                    lines.append(f"    ↓ {label}")
                    lines.append(f"╭─────────╮")
                    lines.append(f"│ {target.label:^7} │")
                    lines.append(f"╰─────────╯")

        return "\n".join(lines)
