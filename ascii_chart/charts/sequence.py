"""
序列图数据结构
"""

from dataclasses import dataclass, field
from typing import Optional
from ascii_chart.charts.base import ChartData


@dataclass
class Participant:
    """序列图参与者"""
    id: str
    name: str

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}

    @classmethod
    def from_dict(cls, data: dict) -> "Participant":
        return cls(id=data["id"], name=data["name"])


@dataclass
class Interaction:
    """序列图交互"""
    from_participant: str
    to_participant: str
    message: str
    arrow: str = "→"  # → (同步), ← (返回), ⇄ (双向)
    is_return: bool = False

    def to_dict(self) -> dict:
        return {
            "from_participant": self.from_participant,
            "to_participant": self.to_participant,
            "message": self.message,
            "arrow": self.arrow,
            "is_return": self.is_return,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Interaction":
        return cls(
            from_participant=data["from_participant"],
            to_participant=data["to_participant"],
            message=data["message"],
            arrow=data.get("arrow", "→"),
            is_return=data.get("is_return", False),
        )


@dataclass
class SequenceData(ChartData):
    """序列图数据"""
    type: str = "sequence"
    participants: list[Participant] = field(default_factory=list)
    interactions: list[Interaction] = field(default_factory=list)

    def to_dict(self) -> dict:
        result = super().to_dict()
        result["participants"] = [p.to_dict() for p in self.participants]
        result["interactions"] = [i.to_dict() for i in self.interactions]
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "SequenceData":
        chart_data = super().from_dict(data)
        chart_data.participants = [
            Participant.from_dict(p) for p in data.get("participants", [])
        ]
        chart_data.interactions = [
            Interaction.from_dict(i) for i in data.get("interactions", [])
        ]
        return chart_data
