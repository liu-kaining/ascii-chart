"""
架构图数据结构
"""

from dataclasses import dataclass, field
from typing import Optional
from ascii_chart.charts.base import ChartData


@dataclass
class Component:
    """架构组件"""
    id: str
    name: str
    description: Optional[str] = None

    def to_dict(self) -> dict:
        result = {"id": self.id, "name": self.name}
        if self.description:
            result["description"] = self.description
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Component":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
        )


@dataclass
class Layer:
    """架构层"""
    name: str
    components: list[Component] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "components": [c.to_dict() for c in self.components],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Layer":
        return cls(
            name=data["name"],
            components=[Component.from_dict(c) for c in data.get("components", [])],
        )


@dataclass
class ArchitectureData(ChartData):
    """架构图数据"""
    type: str = "architecture"
    layers: list[Layer] = field(default_factory=list)

    def to_dict(self) -> dict:
        result = super().to_dict()
        result["layers"] = [l.to_dict() for l in self.layers]
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "ArchitectureData":
        chart_data = super().from_dict(data)
        chart_data.layers = [Layer.from_dict(l) for l in data.get("layers", [])]
        return chart_data

    def get_all_components(self) -> list[Component]:
        """获取所有组件"""
        components = []
        for layer in self.layers:
            components.extend(layer.components)
        return components
