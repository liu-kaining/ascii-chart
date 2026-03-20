#!/bin/bash
# ascii-chart CLI 使用示例

# 设置 API Key (替换为你的 key)
export ASCII_CHART_API_KEY="your-api-key-here"
export ASCII_CHART_BASE_URL="https://api.openai.com/v1"
export ASCII_CHART_MODEL="gpt-4"

# 方式 1: 直接使用 (需要先安装: pip install -e .)
echo "=== 生成流程图 ==="
ascii-chart draw "画一个用户登录的流程图"

echo ""
echo "=== 生成架构图 ==="
ascii-chart draw -t architecture "画一个简单的三层架构：前端层、业务层、数据层"

echo ""
echo "=== 生成序列图 ==="
ascii-chart draw -t sequence "用户下单的序列图：用户、订单服务、库存服务、支付服务"

echo ""
echo "=== 生成表格 ==="
ascii-chart draw -t table "产品信息表：产品名、价格、库存"

echo ""
echo "=== 生成状态图 ==="
ascii-chart draw -t state "订单状态机：待支付、已支付、已发货、已完成、已取消"

# 方式 2: 通过参数指定
echo ""
echo "=== 指定模型 ==="
ascii-chart draw -m "gpt-4o" "画一个简单的开始结束流程图"

# 方式 3: 指定 API 地址 (如使用代理或自建模型)
# ascii-chart draw --base-url "http://localhost:8080/v1" -k "sk-local" "画一个流程图"
