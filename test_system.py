"""
系统测试文件 - 验证多Agent协同系统功能
"""

import asyncio
import json
from workflows.coordinator import MultiAgentCoordinator
from utils.helpers import setup_logging


async def test_basic_functionality():
    """测试基本功能"""
    logger = setup_logging("test")
    coordinator = MultiAgentCoordinator()
    
    print("🧪 开始系统功能测试...")
    
    # 测试1: 研究任务
    print("\n📋 测试1: 研究任务")
    task1 = "研究最新的AI技术发展趋势"
    result1 = await coordinator.execute_task_sync(task1)
    print(f"任务: {task1}")
    print(f"分配Agent: {result1['assigned_agent']}")
    print(f"路由决策: {result1['routing_decision']['reasoning']}")
    print(f"结果类型: {result1['result']['task_type']}")
    
    # 测试2: 分析任务
    print("\n📊 测试2: 分析任务")
    task2 = "分析当前市场环境对AI行业的影响"
    result2 = await coordinator.execute_task_sync(task2)
    print(f"任务: {task2}")
    print(f"分配Agent: {result2['assigned_agent']}")
    print(f"路由决策: {result2['routing_decision']['reasoning']}")
    print(f"结果类型: {result2['result']['task_type']}")
    
    # 测试3: 总结任务
    print("\n📝 测试3: 总结任务")
    task3 = "总结AI技术发展的主要趋势和挑战"
    result3 = await coordinator.execute_task_sync(task3)
    print(f"任务: {task3}")
    print(f"分配Agent: {result3['assigned_agent']}")
    print(f"路由决策: {result3['routing_decision']['reasoning']}")
    print(f"结果类型: {result3['result']['task_type']}")
    
    # 测试4: 系统状态
    print("\n🔍 测试4: 系统状态")
    status = coordinator.get_system_status()
    print(f"总任务数: {status['total_tasks']}")
    print(f"状态统计: {status['status_counts']}")
    print(f"队列长度: {status['queue_length']}")
    
    # 测试5: Agent状态
    print("\n🤖 测试5: Agent状态")
    agent_status = coordinator.router.get_agent_status()
    for agent_type, info in agent_status.items():
        print(f"{agent_type}: {info['status']['status']} (负载: {info['workload']:.2f})")
    
    print("\n✅ 系统功能测试完成!")


async def test_async_tasks():
    """测试异步任务处理"""
    print("\n🔄 开始异步任务测试...")
    
    coordinator = MultiAgentCoordinator()
    
    # 提交多个异步任务
    tasks = [
        "研究机器学习算法的发展",
        "分析数据科学工具链",
        "总结AI应用案例"
    ]
    
    task_ids = []
    for task in tasks:
        result = await coordinator.submit_task(task, priority="medium")
        task_ids.append(result['task_id'])
        print(f"提交任务: {task} -> {result['task_id']}")
    
    # 等待任务完成
    print("⏳ 等待任务完成...")
    await asyncio.sleep(10)
    
    # 检查任务状态
    for task_id in task_ids:
        status = await coordinator.get_task_status(task_id)
        if status:
            print(f"任务 {task_id}: {status['status']}")
            if status['status'] == 'completed':
                result = await coordinator.get_task_result(task_id)
                if result:
                    print(f"  结果类型: {result.get('task_type', 'unknown')}")
    
    print("✅ 异步任务测试完成!")


def main():
    """主测试函数"""
    print("🚀 LangGraph多Agent协同系统测试")
    print("=" * 50)
    
    # 运行测试
    asyncio.run(test_basic_functionality())
    asyncio.run(test_async_tasks())
    
    print("\n🎉 所有测试完成!")


if __name__ == "__main__":
    main() 