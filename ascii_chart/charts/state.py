"""
状态图数据结构
"""

from dataclasses import dataclass, field
from typing import Optional
from ascii_chart.charts.base import ChartData, Node, Edge


@dataclass
class StateData(ChartData):
    """状态图数据"""
    type: str = "state"

    def get_initial_states(self) -> list[Node]:
        """获取初始状态"""
        # 状态图使用 metadata 标记初始状态
        return [n for n in self.nodes if n.node_type == "start"]

    def get_final_states(self) -> list[Node]:
        """获取最终状态"""
        return [n for n in self.nodes if n.node_type == "end"]
