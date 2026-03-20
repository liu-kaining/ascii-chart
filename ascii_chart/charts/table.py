"""
表格数据结构
"""

from dataclasses import dataclass, field
from typing import Optional
from ascii_chart.charts.base import ChartData


@dataclass
class TableData(ChartData):
    """表格数据"""
    type: str = "table"
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        result = super().to_dict()
        result["headers"] = self.headers
        result["rows"] = self.rows
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "TableData":
        chart_data = super().from_dict(data)
        chart_data.headers = data.get("headers", [])
        chart_data.rows = data.get("rows", [])
        return chart_data

    def get_column_count(self) -> int:
        """获取列数"""
        return len(self.headers)

    def get_row_count(self) -> int:
        """获取行数"""
        return len(self.rows)
