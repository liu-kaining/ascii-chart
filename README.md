# ascii-chart

LLM-powered ASCII 图表生成器 - 用纯 ASCII 字符绘制流程图、架构图、序列图等。

## 特性

- **多图表类型**: 流程图、架构图、序列图、表格、状态图
- **多 LLM 支持**: OpenAI / Anthropic 兼容 API，支持自定义 base_url
- **多使用形态**: Python SDK、CLI 工具、大模型 Tool
- **稳定输出**: JSON 结构化数据 + 模板渲染，确保格式对齐
- **Markdown 友好**: 输出的纯 ASCII 文本可直接嵌入 Markdown

## 安装

```bash
pip install ascii-chart
```

## 快速开始

### Python SDK

```python
from ascii_chart import ChartManager, OpenAIClient

# 初始化
client = OpenAIClient(
    base_url="https://api.openai.com/v1",
    api_key="your-api-key",
    model="gpt-4",
)
manager = ChartManager(client)

# 生成流程图
result = manager.draw_flowchart("用户登录流程：输入用户名密码，验证身份，成功生成 Token")
print(result)
```

### CLI

```bash
# 设置环境变量
export ASCII_CHART_API_KEY="your-api-key"

# 生成流程图
ascii-chart draw "画一个用户登录的流程图"

# 指定图表类型
ascii-chart draw -t architecture "画一个微服务架构"

# 指定模型
ascii-chart draw -m "gpt-4o" "画一个订单处理的流程图"
```

## 图表类型

### 流程图 (flowchart)

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

### 架构图 (architecture)

```
┌─ 前端层 ─────────────────────────────────────────────┐
│ Web App │ Mobile App                                 │
├─ 网关层 ─────────────────────────────────────────────┤
│ API Gateway                                          │
├─ 服务层 ─────────────────────────────────────────────┤
│ 用户服务 │ 订单服务 │ 商品服务 │ 支付服务            │
├─ 数据层 ─────────────────────────────────────────────┤
│ MySQL │ Redis │ MongoDB                              │
└─────────────────────────────────────────────────────┘
```

### 表格 (table)

```
┌─ 姓名 ──┬─ 年龄 ──┬─ 职位 ─────┐
│ 张三    │ 28      │ 工程师     │
├─────────┼─────────┼────────────┤
│ 李四    │ 32      │ 产品经理   │
├─────────┼─────────┼────────────┤
│ 王五    │ 25      │ 设计师     │
└─────────┴─────────┴────────────┘
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `ASCII_CHART_API_KEY` | API 密钥 | - |
| `ASCII_CHART_BASE_URL` | API 地址 | `https://api.openai.com/v1` |
| `ASCII_CHART_MODEL` | 模型名称 | `gpt-4` |
| `ASCII_CHART_TEMPERATURE` | 温度参数 | `0.7` |
| `ASCII_CHART_MAX_TOKENS` | 最大 token 数 | `2048` |

## 开发

```bash
# 克隆仓库
git clone https://github.com/yourname/ascii-chart.git
cd ascii-chart

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化和检查
ruff check .
ruff format .
mypy ascii_chart/
```

## License

MIT
