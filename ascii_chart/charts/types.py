"""
图表类型常量定义
"""

# 支持的图表类型
CHART_TYPE_FLOWCHART = "flowchart"
CHART_TYPE_ARCHITECTURE = "architecture"
CHART_TYPE_SEQUENCE = "sequence"
CHART_TYPE_TABLE = "table"
CHART_TYPE_STATE = "state"

# 所有支持的图表类型
SUPPORTED_CHART_TYPES = [
    CHART_TYPE_FLOWCHART,
    CHART_TYPE_ARCHITECTURE,
    CHART_TYPE_SEQUENCE,
    CHART_TYPE_TABLE,
    CHART_TYPE_STATE,
]

# 图表类型描述
CHART_TYPE_DESCRIPTIONS = {
    CHART_TYPE_FLOWCHART: "流程图 - 描述流程和决策路径",
    CHART_TYPE_ARCHITECTURE: "架构图 - 描述系统分层和组件关系",
    CHART_TYPE_SEQUENCE: "序列图 - 描述对象间的交互顺序",
    CHART_TYPE_TABLE: "表格 - 以行列形式展示数据",
    CHART_TYPE_STATE: "状态图 - 描述状态转换",
}
