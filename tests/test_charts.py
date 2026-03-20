"""
图表数据结构的单元测试
"""

import pytest
from ascii_chart.charts.base import Node, Edge, ChartData
from ascii_chart.charts.flowchart import FlowchartData
from ascii_chart.charts.architecture import ArchitectureData, Layer, Component
from ascii_chart.charts.sequence import SequenceData, Participant, Interaction
from ascii_chart.charts.table import TableData
from ascii_chart.charts.state import StateData


class TestNode:
    """节点测试"""

    def test_node_creation(self):
        node = Node(id="n1", label="测试节点", node_type="process")
        assert node.id == "n1"
        assert node.label == "测试节点"
        assert node.node_type == "process"

    def test_node_to_dict(self):
        node = Node(id="n1", label="测试节点")
        result = node.to_dict()
        assert result == {"id": "n1", "label": "测试节点", "node_type": "default"}

    def test_node_from_dict(self):
        data = {"id": "n1", "label": "测试节点", "node_type": "start"}
        node = Node.from_dict(data)
        assert node.id == "n1"
        assert node.label == "测试节点"
        assert node.node_type == "start"


class TestEdge:
    """边测试"""

    def test_edge_creation(self):
        edge = Edge(from_node="n1", to_node="n2")
        assert edge.from_node == "n1"
        assert edge.to_node == "n2"
        assert edge.label is None

    def test_edge_with_label(self):
        edge = Edge(from_node="n1", to_node="n2", label="成功")
        assert edge.label == "成功"

    def test_edge_to_dict(self):
        edge = Edge(from_node="n1", to_node="n2", label="成功")
        result = edge.to_dict()
        assert result == {"from_node": "n1", "to_node": "n2", "label": "成功"}


class TestFlowchartData:
    """流程图数据测试"""

    def test_flowchart_creation(self):
        nodes = [
            Node(id="start", label="开始", node_type="start"),
            Node(id="process", label="处理", node_type="process"),
            Node(id="end", label="结束", node_type="end"),
        ]
        edges = [
            Edge(from_node="start", to_node="process"),
            Edge(from_node="process", to_node="end"),
        ]
        data = FlowchartData(nodes=nodes, edges=edges)

        assert data.type == "flowchart"
        assert len(data.nodes) == 3
        assert len(data.edges) == 2

    def test_get_start_nodes(self):
        nodes = [
            Node(id="start", label="开始", node_type="start"),
            Node(id="end", label="结束", node_type="end"),
        ]
        data = FlowchartData(nodes=nodes)
        assert len(data.get_start_nodes()) == 1
        assert data.get_start_nodes()[0].id == "start"

    def test_get_outgoing_edges(self):
        nodes = [
            Node(id="n1", label="节点1"),
            Node(id="n2", label="节点2"),
            Node(id="n3", label="节点3"),
        ]
        edges = [
            Edge(from_node="n1", to_node="n2"),
            Edge(from_node="n1", to_node="n3"),
        ]
        data = FlowchartData(nodes=nodes, edges=edges)

        outgoing = data.get_outgoing_edges("n1")
        assert len(outgoing) == 2


class TestArchitectureData:
    """架构图数据测试"""

    def test_architecture_creation(self):
        layers = [
            Layer(
                name="前端",
                components=[
                    Component(id="web", name="Web App"),
                    Component(id="mobile", name="Mobile App"),
                ]
            ),
            Layer(
                name="后端",
                components=[
                    Component(id="api", name="API Server"),
                ]
            ),
        ]
        data = ArchitectureData(layers=layers)

        assert data.type == "architecture"
        assert len(data.layers) == 2
        assert len(data.get_all_components()) == 3

    def test_architecture_to_dict(self):
        layers = [
            Layer(name="测试层", components=[Component(id="c1", name="组件1")])
        ]
        data = ArchitectureData(layers=layers)
        result = data.to_dict()

        assert result["type"] == "architecture"
        assert len(result["layers"]) == 1


class TestTableData:
    """表格数据测试"""

    def test_table_creation(self):
        headers = ["姓名", "年龄", "职位"]
        rows = [
            ["张三", "28", "工程师"],
            ["李四", "32", "产品经理"],
        ]
        data = TableData(headers=headers, rows=rows)

        assert data.type == "table"
        assert data.get_column_count() == 3
        assert data.get_row_count() == 2

    def test_table_to_dict(self):
        data = TableData(
            headers=["列1", "列2"],
            rows=[["值1", "值2"]]
        )
        result = data.to_dict()

        assert result["headers"] == ["列1", "列2"]
        assert result["rows"] == [["值1", "值2"]]


class TestSequenceData:
    """序列图数据测试"""

    def test_sequence_creation(self):
        participants = [
            Participant(id="client", name="客户端"),
            Participant(id="server", name="服务器"),
        ]
        interactions = [
            Interaction(from_participant="client", to_participant="server", message="请求"),
        ]
        data = SequenceData(participants=participants, interactions=interactions)

        assert data.type == "sequence"
        assert len(data.participants) == 2
        assert len(data.interactions) == 1
