"""
ascii-chart 基本使用示例
"""

from ascii_chart import ChartManager, OpenAIClient


def main():
    # 初始化 OpenAI 客户端
    client = OpenAIClient(
        base_url="https://api.openai.com/v1",
        api_key="your-api-key-here",
        model="gpt-4",
    )

    # 创建图表管理器
    manager = ChartManager(client)

    # 示例 1: 生成流程图
    print("=" * 50)
    print("示例 1: 用户登录流程图")
    print("=" * 50)
    result = manager.draw_flowchart("用户登录流程：输入用户名密码，验证身份，成功则生成 Token，失败返回错误")
    print(result)
    print()

    # 示例 2: 生成架构图
    print("=" * 50)
    print("示例 2: 微服务架构图")
    print("=" * 50)
    result = manager.draw_architecture("一个电商系统的微服务架构，包含用户服务、订单服务、商品服务、支付服务，前端有 Web 和 App")
    print(result)
    print()

    # 示例 3: 生成序列图
    print("=" * 50)
    print("示例 3: 订单创建序列图")
    print("=" * 50)
    result = manager.draw_sequence("用户下单流程：客户端发起订单请求，网关转发到订单服务，订单服务调用库存服务和支付服务，最后返回订单结果")
    print(result)
    print()

    # 示例 4: 生成表格
    print("=" * 50)
    print("示例 4: 员工信息表")
    print("=" * 50)
    result = manager.draw_table("员工信息表，包含姓名、职位、部门、邮箱")
    print(result)
    print()

    # 示例 5: 自动推断图表类型
    print("=" * 50)
    print("示例 5: 自动推断类型")
    print("=" * 50)
    result = manager.draw("画一个状态机：空闲状态可以启动变为运行，运行状态可以暂停变为暂停，暂停可以继续变为运行，暂停和运行都可以停止变为停止")
    print(result)
    print()


if __name__ == "__main__":
    main()
