"""
流程图数据结构
"""

from dataclasses import dataclass, field
from typing import Optional
from ascii_chart.charts.base import ChartData, Node, Edge


@dataclass
class FlowchartData(ChartData):
    """流程图数据"""
    type: str = "flowchart"

    def get_start_nodes(self) -> list[Node]:
        """获取开始节点"""
        return [n for n in self.nodes if n.node_type == "start"]

    def get_end_nodes(self) -> list[Node]:
        """获取结束节点"""
        return [n for n in self.nodes if n.node_type == "end"]

    def get_decision_nodes(self) -> list[Node]:
        """获取决策节点"""
        return [n for n in self.nodes if n.node_type == "decision"]

    def get_outgoing_edges(self, node_id: str) -> list[Edge]:
        """获取节点的所有出边"""
        return [e for e in self.edges if e.from_node == node_id]

    def get_incoming_edges(self, node_id: str) -> list[Edge]:
        """获取节点的所有入边"""
        return [e for e in self.edges if e.to_node == node_id]
