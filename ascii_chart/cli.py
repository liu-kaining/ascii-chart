"""
命令行工具入口
"""

import sys
import os
import argparse
from ascii_chart import ChartManager, OpenAIClient, AnthropicClient


# 统一的环境变量前缀
ENV_PREFIX = "ASCII_CHART_"

# Provider 配置
PROVIDERS = {
    "openai": {
        "client": OpenAIClient,
        "default_base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4",
    },
    "anthropic": {
        "client": AnthropicClient,
        "default_base_url": "https://api.anthropic.com/v1",
        "default_model": "claude-3-5-sonnet-20241022",
    },
}


def detect_provider_from_base_url(base_url: str) -> str:
    """根据 base_url 自动推断 provider"""
    if "anthropic" in base_url.lower():
        return "anthropic"
    return "openai"


def main():
    parser = argparse.ArgumentParser(
        description="ascii-chart: LLM-powered ASCII chart generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用 OpenAI (默认)
  ascii-chart draw "画一个用户登录的流程图"

  # 使用 Anthropic
  ascii-chart draw -p anthropic "画一个流程图"

  # 指定模型
  ascii-chart draw -m gpt-4o "画一个流程图"

统一环境变量:
  ASCII_CHART_API_KEY      API 密钥
  ASCII_CHART_BASE_URL     API 地址 (默认: https://api.openai.com/v1)
  ASCII_CHART_MODEL        模型名称 (默认: gpt-4)
  ASCII_CHART_PROVIDER     Provider (默认: openai，可选: anthropic)
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # draw 子命令
    draw_parser = subparsers.add_parser("draw", help="生成 ASCII 图表")
    draw_parser.add_argument("description", help="图表描述")
    draw_parser.add_argument(
        "-t",
        "--type",
        dest="chart_type",
        choices=["flowchart", "architecture", "sequence", "table", "state"],
        help="图表类型",
    )
    draw_parser.add_argument(
        "-p",
        "--provider",
        dest="provider",
        choices=["openai", "anthropic"],
        help="LLM Provider (默认: openai，或根据 BASE_URL 自动推断)",
    )
    draw_parser.add_argument("-m", "--model", dest="model", help="模型名称")
    draw_parser.add_argument("--base-url", dest="base_url", help="API 地址")
    draw_parser.add_argument("-k", "--api-key", dest="api_key", help="API 密钥")

    # 解析参数
    args = parser.parse_args()

    if args.command == "draw":
        draw_ascii_chart(args)
    else:
        parser.print_help()
        sys.exit(1)


def draw_ascii_chart(args):
    """执行图表绘制"""
    # 1. 获取 base_url（参数 > 环境变量 > 默认值）
    base_url = args.base_url or os.getenv(f"{ENV_PREFIX}BASE_URL", PROVIDERS["openai"]["default_base_url"])

    # 2. 推断 provider（参数 > 环境变量 > 根据 base_url 自动推断）
    if args.provider:
        provider = args.provider
    else:
        provider = os.getenv(f"{ENV_PREFIX}PROVIDER", "")
        if not provider:
            provider = detect_provider_from_base_url(base_url)

    provider_config = PROVIDERS[provider]
    client_class = provider_config["client"]

    # 3. 获取其他配置（参数 > 环境变量 > 默认值）
    api_key = args.api_key or os.getenv(f"{ENV_PREFIX}API_KEY", "")
    model = args.model or os.getenv(f"{ENV_PREFIX}MODEL", provider_config["default_model"])

    # 如果参数指定了 base_url，覆盖默认值
    if not args.base_url:
        base_url = os.getenv(f"{ENV_PREFIX}BASE_URL", provider_config["default_base_url"])

    if not api_key:
        print(
            f"错误: 请设置 API_KEY\n"
            f"  参数: -k xxx\n"
            f"  环境变量: {ENV_PREFIX}API_KEY",
            file=sys.stderr,
        )
        sys.exit(1)

    # 初始化客户端
    if provider == "openai":
        client = client_class(
            base_url=base_url,
            api_key=api_key,
            model=model,
            temperature=0.7,
            max_tokens=2048,
        )
    else:
        # Anthropic
        client = client_class(
            api_key=api_key,
            model=model,
            temperature=0.7,
            max_tokens=2048,
        )

    # 创建管理器
    manager = ChartManager(client)

    # 生成图表
    try:
        result = manager.draw(args.description, args.chart_type)
        print(result)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
