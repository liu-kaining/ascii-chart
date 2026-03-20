"""
渲染器的单元测试
"""

import pytest
from ascii_chart.renderers.ascii import ASCIRenderer
from ascii_chart.charts.flowchart import FlowchartData
from ascii_chart.charts.architecture import ArchitectureData, Layer, Component
from ascii_chart.charts.sequence import SequenceData, Participant, Interaction
from ascii_chart.charts.table import TableData
from ascii_chart.charts.base import Node, Edge


class TestFlowchartRenderer:
    """流程图渲染器测试"""

    def test_render_simple_flowchart(self):
        """测试简单流程图渲染"""
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

        renderer = ASCIRenderer(width=80)
        result = renderer.render(data)

        assert "开始" in result
        assert "处理" in result
        assert "结束" in result

    def test_render_decision_flowchart(self):
        """测试带决策节点的流程图"""
        nodes = [
            Node(id="start", label="开始", node_type="start"),
            Node(id="decision", label="是否成功?", node_type="decision"),
            Node(id="success", label="成功", node_type="process"),
            Node(id="fail", label="失败", node_type="process"),
        ]
        edges = [
            Edge(from_node="start", to_node="decision"),
            Edge(from_node="decision", to_node="success", label="是"),
            Edge(from_node="decision", to_node="fail", label="否"),
        ]
        data = FlowchartData(nodes=nodes, edges=edges)

        renderer = ASCIRenderer(width=80)
        result = renderer.render(data)

        assert "开始" in result
        assert "是否成功" in result or "?" in result
        assert "成功" in result
        assert "失败" in result


class TestArchitectureRenderer:
    """架构图渲染器测试"""

    def test_render_simple_architecture(self):
        """测试简单架构图渲染"""
        layers = [
            Layer(
                name="前端层",
                components=[
                    Component(id="web", name="Web App"),
                    Component(id="mobile", name="Mobile App"),
                ]
            ),
            Layer(
                name="后端层",
                components=[
                    Component(id="api", name="API Gateway"),
                ]
            ),
            Layer(
                name="数据层",
                components=[
                    Component(id="db", name="MySQL"),
                    Component(id="cache", name="Redis"),
                ]
            ),
        ]
        data = ArchitectureData(layers=layers)

        renderer = ASCIRenderer(width=80)
        result = renderer.render(data)

        assert "前端层" in result
        assert "后端层" in result
        assert "数据层" in result
        assert "Web App" in result
        assert "MySQL" in result


class TestTableRenderer:
    """表格渲染器测试"""

    def test_render_simple_table(self):
        """测试简单表格渲染"""
        data = TableData(
            headers=["姓名", "年龄", "职位"],
            rows=[
                ["张三", "28", "工程师"],
                ["李四", "32", "产品经理"],
            ]
        )

        renderer = ASCIRenderer(width=80)
        result = renderer.render(data)

        assert "姓名" in result
        assert "年龄" in result
        assert "职位" in result
        assert "张三" in result
        assert "李四" in result
        # 检查边框字符
        assert "┌" in result
        assert "┐" in result
        assert "└" in result
        assert "┘" in result

    def test_render_empty_table(self):
        """测试空表格"""
        data = TableData(headers=[], rows=[])
        renderer = ASCIRenderer(width=80)
        result = renderer.render(data)

        assert result == ""

    def test_render_table_single_column(self):
        """测试单列表格"""
        data = TableData(
            headers=["项目"],
            rows=[["值1"], ["值2"], ["值3"]]
        )
        renderer = ASCIRenderer(width=80)
        result = renderer.render(data)

        assert "项目" in result
        assert "值1" in result
        assert "值2" in result


class TestSequenceRenderer:
    """序列图渲染器测试"""

    def test_render_simple_sequence(self):
        """测试简单序列图渲染"""
        participants = [
            Participant(id="client", name="客户端"),
            Participant(id="server", name="服务器"),
            Participant(id="db", name="数据库"),
        ]
        interactions = [
            Interaction(from_participant="client", to_participant="server", message="请求"),
            Interaction(from_participant="server", to_participant="db", message="查询"),
            Interaction(from_participant="db", to_participant="server", message="结果"),
            Interaction(from_participant="server", to_participant="client", message="响应"),
        ]
        data = SequenceData(participants=participants, interactions=interactions)

        renderer = ASCIRenderer(width=80)
        result = renderer.render(data)

        assert "客户端" in result
        assert "服务器" in result
        assert "数据库" in result
