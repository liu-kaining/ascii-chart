"""
图表基础模块 - 定义通用数据结构和基类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass
class Node:
    """图表节点"""
    id: str
    label: str
    node_type: str = "default"  # "start", "end", "process", "decision", "comment"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "node_type": self.node_type,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Node":
        return cls(
            id=data["id"],
            label=data["label"],
            node_type=data.get("node_type", "default"),
        )


@dataclass
class Edge:
    """图表边/连接"""
    from_node: str
    to_node: str
    label: Optional[str] = None

    def to_dict(self) -> dict:
        result = {
            "from_node": self.from_node,
            "to_node": self.to_node,
        }
        if self.label:
            result["label"] = self.label
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Edge":
        return cls(
            from_node=data["from_node"],
            to_node=data["to_node"],
            label=data.get("label"),
        )


@dataclass
class ChartData:
    """图表数据结构基类"""
    type: str  # "flowchart", "architecture", "sequence", "table", "state"
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChartData":
        nodes = [Node.from_dict(n) for n in data.get("nodes", [])]
        edges = [Edge.from_dict(e) for e in data.get("edges", [])]
        return cls(
            type=data["type"],
            nodes=nodes,
            edges=edges,
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "ChartData":
        """从 JSON 字符串解析"""
        import json
        data = json.loads(json_str)
        return cls.from_dict(data)
