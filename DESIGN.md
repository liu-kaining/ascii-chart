# ascii-chart 技术设计文档

## 1. 项目概述

### 1.1 项目简介

`ascii-chart` 是一个基于 LLM 的 ASCII 图表生成工具，能够将自然语言描述、文本描述或结构化数据转换为纯 ASCII 字符图表。

**核心价值**：让大模型和开发者能够低成本、高效率地生成可直接使用的 ASCII 图表，适用于 Markdown 文档、终端展示、AI Agent 交互等场景。

### 1.2 目标用户

- **AI 应用开发者**：集成到 Agent 工作流中，让 AI 能够生成图表
- **文档作者**：在 Markdown 中嵌入 ASCII 图表，无需外部图片
- **后端工程师**：快速绘制架构图、流程图进行技术沟通
- **数据分析师**：终端内直接查看数据图表

### 1.3 核心特性

- **多输入模式**：支持自然语言描述、简化语法、Python API 调用
- **多图表类型**：流程图、架构图、序列图、表格、状态图等
- **多 LLM 支持**：OpenAI / Anthropic 兼容 API，自定义 base_url
- **多使用形态**：Python SDK、CLI 工具、大模型 Tool
- **稳定输出**：JSON 结构化数据 + 模板渲染，确保格式对齐

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户入口                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │   CLI    │  │Python SDK│  │MCP Server│  │大模型Tool│    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        └─────────────┬┴─────────────┴�─────────────┘
                      ▼
            ┌─────────────────┐
            │   ChartManager  │  图表管理器（统一入口）
            └────────┬────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌───────────────┐       ┌─────────────────┐
│  LLM 适配层   │       │  渲染器适配层   │
│               │       │                 │
│  ┌─────────┐  │       │  ┌───────────┐  │
│  │OpenAI   │  │       │  │ASCIIRenderer│  │
│  │Anthropic│  │       │  └───────────┘  │
│  │Custom   │  │       │                 │
│  └─────────┘  │       └─────────────────┘
└───────────────┘
```

### 2.2 目录结构

```
ascii-chart/
├── ascii_chart/                 # 主包
│   ├── __init__.py              # 包入口，导出主要 API
│   ├── cli.py                   # CLI 入口
│   ├── config.py                # 配置管理
│   ├── llm/                     # LLM 适配层
│   │   ├── __init__.py
│   │   ├── base.py              # LLM 基类
│   │   ├── openai_client.py     # OpenAI 兼容客户端
│   │   ├── anthropic_client.py  # Anthropic 客户端
│   │   └── prompts.py           # Prompt 模板
│   ├── charts/                  # 图表类型定义
│   │   ├── __init__.py
│   │   ├── base.py              # 图表基类和数据结构
│   │   ├── flowchart.py         # 流程图
│   │   ├── architecture.py      # 架构图
│   │   ├── sequence.py          # 序列图
│   │   ├── table.py             # 表格
│   │   ├── state.py             # 状态图
│   │   └── types.py             # 类型定义
│   └── renderers/               # 渲染器
│       ├── __init__.py
│       └── ascii.py             # ASCII 渲染器
├── tests/                       # 测试
│   ├── __init__.py
│   ├── test_llm.py
│   ├── test_charts.py
│   └── test_renderers.py
├── examples/                    # 示例
│   ├── basic_usage.py
│   └── cli_usage.sh
├── docs/                        # 文档
│   └── api_reference.md
├── pyproject.toml              # 项目配置
├── README.md
└── DESIGN.md                   # 本文档
```

---

## 3. 模块设计

### 3.1 配置管理 (config.py)

#### 配置项

```python
@dataclass
class LLMConfig:
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4"
    api_key: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048

@dataclass
class ChartConfig:
    default_width: int = 80
    default_chart_type: str = "flowchart"
```

#### 环境变量支持

- `ASCII_CHART_BASE_URL`
- `ASCII_CHART_API_KEY`
- `ASCII_CHART_MODEL`

### 3.2 LLM 适配层

#### 接口设计

```python
class BaseLLMClient(ABC):
    @abstractmethod
    def chat(self, messages: list[ChatMessage]) -> str:
        """发送对话请求，返回文本响应"""
        pass

@dataclass
class ChatMessage:
    role: str  # "system", "user", "assistant"
    content: str
```

#### 支持的 Provider

| Provider | Base URL | 备注 |
|----------|----------|------|
| OpenAI | `https://api.openai.com/v1` | 默认 |
| Anthropic | `https://api.anthropic.com/v1` | 需要不同的请求格式 |
| 自定义 | 用户指定 | 支持任何 OpenAI 兼容 API |

### 3.3 Prompt 设计

#### System Prompt

```
你是一个专业的 ASCII 图表生成器。用户会输入图表描述，你需要生成对应的结构化 JSON 数据。

支持的图表类型：
- flowchart: 流程图
- architecture: 架构图
- sequence: 序列图
- table: 表格
- state: 状态图

输出格式要求：
1. 严格按照 JSON 格式输出，不要包含其他内容
2. 确保 JSON 可以被 Python json.loads() 解析
3. 图表元素使用 ASCII 字符绘制
```

#### User Prompt 模板

```python
FLOWCHART_PROMPT = """
请生成一个流程图，描述以下场景：

{description}

要求：
1. 包含开始和结束节点
2. 使用 [ ] 包裹节点文本
3. 使用 → 表示流程方向
4. 分支用 ↓ 和 → 组合表示

请直接输出 JSON，不要包含其他内容：
"""

ARCHITECTURE_PROMPT = """
请生成一个架构图，描述以下系统：

{description}

要求：
1. 使用分层架构
2. 每层用不同的边框样式区分
3. 组件用 | | 包裹
4. 层之间用 │ 连接

请直接输出 JSON，不要包含其他内容：
"""

# ... 其他图表类型类似
```

### 3.4 图表数据结构

#### 基础类型

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Node:
    id: str
    label: str
    node_type: str = "default"  # "start", "end", "process", "decision", "comment"

@dataclass
class Edge:
    from_node: str
    to_node: str
    label: Optional[str] = None

@dataclass
class ChartData:
    type: str  # "flowchart", "architecture", "sequence", "table", "state"
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
```

#### JSON Schema 示例

**流程图输出格式**：
```json
{
  "type": "flowchart",
  "nodes": [
    {"id": "start", "label": "开始", "node_type": "start"},
    {"id": "input", "label": "输入用户名密码", "node_type": "process"},
    {"id": "verify", "label": "验证身份", "node_type": "decision"},
    {"id": "success", "label": "登录成功", "node_type": "process"},
    {"id": "fail", "label": "登录失败", "node_type": "process"},
    {"id": "end", "label": "结束", "node_type": "end"}
  ],
  "edges": [
    {"from_node": "start", "to_node": "input"},
    {"from_node": "input", "to_node": "verify"},
    {"from_node": "verify", "to_node": "success", "label": "成功"},
    {"from_node": "verify", "to_node": "fail", "label": "失败"},
    {"from_node": "success", "to_node": "end"},
    {"from_node": "fail", "to_node": "end"}
  ]
}
```

**架构图输出格式**：
```json
{
  "type": "architecture",
  "layers": [
    {
      "name": "前端层",
      "components": [
        {"id": "web", "name": "Web App"},
        {"id": "mobile", "name": "Mobile App"}
      ]
    },
    {
      "name": "网关层",
      "components": [
        {"id": "gateway", "name": "API Gateway"}
      ]
    },
    {
      "name": "服务层",
      "components": [
        {"id": "user", "name": "用户服务"},
        {"id": "order", "name": "订单服务"}
      ]
    },
    {
      "name": "数据层",
      "components": [
        {"id": "db", "name": "MySQL"},
        {"id": "cache", "name": "Redis"}
      ]
    }
  ]
}
```

**序列图输出格式**：
```json
{
  "type": "sequence",
  "participants": [
    {"id": "client", "name": "客户端"},
    {"id": "gateway", "name": "网关"},
    {"id": "service", "name": "业务服务"},
    {"id": "db", "name": "数据库"}
  ],
  "interactions": [
    {"from": "client", "to": "gateway", "message": "请求登录", "arrow": "→"},
    {"from": "gateway", "to": "service", "message": "转发请求", "arrow": "→"},
    {"from": "service", "to": "db", "message": "查询用户", "arrow": "→"},
    {"from": "db", "to": "service", "message": "返回用户信息", "arrow": "←"},
    {"from": "service", "to": "gateway", "message": "返回 Token", "arrow": "←"},
    {"from": "gateway", "to": "client", "message": "返回结果", "arrow": "←"}
  ]
}
```

**表格输出格式**：
```json
{
  "type": "table",
  "headers": ["姓名", "年龄", "职位"],
  "rows": [
    ["张三", "28", "工程师"],
    ["李四", "32", "产品经理"],
    ["王五", "25", "设计师"]
  ]
}
```

**状态图输出格式**：
```json
{
  "type": "state",
  "states": [
    {"id": "idle", "name": "空闲"},
    {"id": "running", "name": "运行中"},
    {"id": "paused", "name": "暂停"},
    {"id": "stopped", "name": "已停止"}
  ],
  "transitions": [
    {"from": "idle", "to": "running", "label": "启动"},
    {"from": "running", "to": "paused", "label": "暂停"},
    {"from": "paused", "to": "running", "label": "继续"},
    {"from": "running", "to": "stopped", "label": "停止"},
    {"from": "paused", "to": "stopped", "label": "停止"}
  ]
}
```

### 3.5 渲染器设计

#### ASCII 渲染器接口

```python
class BaseRenderer(ABC):
    @abstractmethod
    def render(self, chart_data: ChartData) -> str:
        """将图表数据渲染为 ASCII 字符串"""
        pass
```

#### 流程图渲染器示例

```python
class FlowchartRenderer(BaseRenderer):
    def render(self, chart_data: ChartData) -> str:
        # 构建节点位置映射
        # 计算连接线
        # 渲染边框和对齐
        # 组装最终输出
        pass
```

**渲染输出示例**：

```
┌─────────┐
│  开始   │
└────┬────┘
     │
     ▼
┌─────────────┐
│ 输入用户名密码 │
└──────┬──────┘
       │
       ▼
   ┌───────┐
  ╱ 验证   ╲
 ╱  身份   ╲ ───→ 失败 ──→ ┌─────────┐
 ──────────              │ 登录失败 │
   │ 成功                 └─────────┘
   ▼
┌─────────┐
│ 生成Token│
└────┬────┘
     │
     ▼
┌─────────┐
│  结束   │
└─────────┘
```

### 3.6 图表管理器

```python
class ChartManager:
    def __init__(self, llm_client: BaseLLMClient, renderer: BaseRenderer):
        self.llm = llm_client
        self.renderer = renderer

    def draw(self, description: str, chart_type: str = None) -> str:
        """
        主入口方法
        1. 如果未指定 chart_type，让 LLM 推断
        2. 调用 LLM 生成结构化 JSON
        3. 解析 JSON 为 ChartData
        4. 使用渲染器生成 ASCII
        """
        pass
```

---

## 4. 使用方式

### 4.1 Python SDK

```python
from ascii_chart import ChartManager, OpenAIClient, FlowchartRenderer

# 初始化
client = OpenAIClient(
    base_url="https://api.openai.com/v1",
    api_key="sk-xxx",
    model="gpt-4"
)
manager = ChartManager(llm_client=client)

# 生成流程图
result = manager.draw("画一个用户登录的流程图")
print(result)
```

### 4.2 CLI

```bash
# 设置环境变量
export ASCII_CHART_API_KEY="sk-xxx"
export ASCII_CHART_BASE_URL="https://api.openai.com/v1"

# 使用
ascii-chart draw "画一个用户登录的流程图"

# 指定图表类型
ascii-chart draw -t architecture "画一个微服务架构图"

# 指定模型
ascii-chart draw -m "gpt-4o" "画一个订单处理的流程图"
```

### 4.3 MCP Server

```python
# 导出为 MCP Tool
from ascii_chart.mcp import get_mcp_tools

tools = get_mcp_tools()
# 返回符合 MCP 协议的工具定义
```

### 4.4 大模型 Tool Calling

```python
# 作为 Tool 供 Agent 调用
TOOL_DEFINITION = {
    "name": "draw_ascii_chart",
    "description": "生成 ASCII 字符图表，支持流程图、架构图、序列图等",
    "parameters": {
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "图表描述，自然语言描述所需图表"
            },
            "chart_type": {
                "type": "string",
                "enum": ["flowchart", "architecture", "sequence", "table", "state"],
                "description": "图表类型，不指定则自动推断"
            }
        }
    }
}
```

---

## 5. 错误处理

### 5.1 错误类型

| 错误类型 | 说明 | 处理方式 |
|----------|------|----------|
| `LLMError` | LLM 调用失败 | 重试 / 返回默认图表 / 抛出异常 |
| `ParseError` | JSON 解析失败 | 尝试修复 / 返回原始文本 / 抛出异常 |
| `ValidationError` | 数据校验失败 | 抛出异常，包含详细信息 |
| `ConfigError` | 配置错误 | 抛出异常，提示检查配置 |

### 5.2 容错机制

```python
def draw_with_fallback(self, description: str) -> str:
    try:
        return self.draw(description)
    except ParseError:
        # 如果 JSON 解析失败，尝试让 LLM 修复
        return self._retry_with_correction(description)
    except LLMError:
        # LLM 调用失败，返回示例图表
        return self._return_sample_chart()
```

---

## 6. 扩展性设计

### 6.1 新增图表类型

```python
# 1. 定义新的 ChartData 子类
@dataclass
class GanttChartData(ChartData):
    type: str = "gantt"
    tasks: list[Task] = field(default_factory=list)

# 2. 实现对应的渲染器
class GanttRenderer(BaseRenderer):
    def render(self, chart_data: GanttChartData) -> str:
        pass

# 3. 注册到 ChartManager
manager.register_renderer("gantt", GanttRenderer())
```

### 6.2 新增 LLM Provider

```python
# 1. 继承 BaseLLMClient
class OllamaClient(BaseLLMClient):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model

    def chat(self, messages: list[ChatMessage]) -> str:
        # 实现 Ollama API 调用
        pass

# 2. 使用
client = OllamaClient(base_url="http://localhost:11434", model="llama2")
```

---

## 7. 测试策略

### 7.1 单元测试

```python
# tests/test_charts/test_flowchart.py
def test_flowchart_renderer_basic():
    data = FlowchartData(
        nodes=[Node("start", "开始", "start"), Node("end", "结束", "end")],
        edges=[Edge("start", "end")]
    )
    renderer = FlowchartRenderer()
    result = renderer.render(data)
    assert "开始" in result
    assert "结束" in result
```

### 7.2 集成测试

```python
# tests/test_integration.py
def test_full_flowchart_generation():
    client = MockOpenAIClient()  # 使用 mock
    manager = ChartManager(client)
    result = manager.draw("画一个简单的开始结束流程")
    assert result is not None
    assert len(result) > 0
```

---

## 8. 性能考虑

### 8.1 缓存机制

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def _render_flowchart_cached(self, json_str: str) -> str:
    """缓存渲染结果"""
    chart_data = ChartData.from_json(json_str)
    return self._do_render(chart_data)
```

### 8.2 异步支持

```python
import asyncio

async def draw_async(self, description: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, self.draw, description)
```

---

## 9. 发布计划

### Phase 1: 核心功能 (MVP)
- [ ] 项目基础结构搭建
- [ ] LLM 适配层（OpenAI 兼容）
- [ ] 流程图图表类型
- [ ] ASCII 渲染器
- [ ] CLI 工具
- [ ] Python SDK
- [ ] 基本测试

### Phase 2: 扩展图表类型
- [ ] 架构图
- [ ] 序列图
- [ ] 表格
- [ ] 状态图

### Phase 3: 完善和发布
- [ ] Anthropic 支持
- [ ] MCP Server 导出
- [ ] Tool Calling 定义
- [ ] 完整测试覆盖
- [ ] PyPI 发布

---

## 10. 依赖设计

```toml
# pyproject.toml
[project]
name = "ascii-chart"
version = "0.1.0"
description = "LLM-powered ASCII chart generator"
requires-python = ">=3.10"
dependencies = [
    "requests>=2.28.0",
    "anthropic>=0.18.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
```

---

## 11. 命名规范

### 11.1 模块命名

- `ascii_chart` - 包名，全小写
- `llm/` - 模块，全小写
- `charts/` - 模块，全小写
- `renderers/` - 模块，全小写

### 11.2 类命名

- `BaseLLMClient` - 基类，前缀 Base
- `OpenAIClient` - 具体实现，使用Provider前缀
- `FlowchartRenderer` - 渲染器，图表类型 + Renderer
- `ChartManager` - 管理器，核心逻辑类

### 11.3 方法命名

- `draw()` - 主入口方法
- `render()` - 渲染方法
- `chat()` - LLM 对话方法
- `_private_method()` - 私有方法，前缀下划线

---

## 12. 参考资料

- ASCII 字符绘图规范
- Mermaid 图表类型定义
- Graphviz DOT 语言
- PlantUML 图表语法
