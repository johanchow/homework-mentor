"""
中文老师Agent测试文件 - 验证中文教学功能
"""

import asyncio
import json
from agents.chinese_agent import ChineseTeacherAgent
from utils.helpers import setup_logging


async def test_teaching_guidance():
    """测试教学指导功能"""
    logger = setup_logging("chinese_test")
    agent = ChineseTeacherAgent()
    
    print("🧪 开始中文老师Agent教学指导测试...")
    
    # 测试1: 写作指导
    print("\n📝 测试1: 写作指导")
    task1 = "如何写好一篇记叙文？"
    result1 = await agent.execute(task1, {
        "student_level": "初中生",
        "learning_goal": "提高记叙文写作水平"
    })
    print(f"任务: {task1}")
    print(f"任务类型: {result1['result']['teaching_type']}")
    print(f"教学方法: {result1['result']['teaching_methods']}")
    print(f"学习原则: {result1['result']['learning_principles']}")
    print(f"练习建议: {result1['result']['practice_suggestions'][:2]}...")
    
    # 测试2: 阅读理解
    print("\n📖 测试2: 阅读理解")
    task2 = "如何提高阅读理解能力？"
    result2 = await agent.execute(task2, {
        "student_level": "高中生",
        "learning_goal": "提高阅读理解准确率"
    })
    print(f"任务: {task2}")
    print(f"任务类型: {result2['result']['teaching_type']}")
    print(f"教学方法: {result2['result']['teaching_methods']}")
    
    # 测试3: 语法学习
    print("\n🔤 测试3: 语法学习")
    task3 = "如何学习文言文语法？"
    result3 = await agent.execute(task3, {
        "student_level": "高中生",
        "learning_goal": "掌握文言文语法规律"
    })
    print(f"任务: {task3}")
    print(f"任务类型: {result3['result']['teaching_type']}")
    print(f"教学方法: {result3['result']['teaching_methods']}")
    
    print("\n✅ 教学指导测试完成!")


async def test_conversation():
    """测试多轮对话功能"""
    print("\n💬 开始多轮对话测试...")
    
    agent = ChineseTeacherAgent()
    
    # 开始对话会话
    session_id = agent.start_conversation({
        "student_name": "小明",
        "grade": "初三",
        "weakness": "作文写作"
    })
    print(f"会话ID: {session_id}")
    
    # 第一轮对话
    print("\n👤 学生: 老师，我写作文总是不知道写什么，怎么办？")
    result1 = await agent.execute("老师，我写作文总是不知道写什么，怎么办？", {
        "is_conversation": True,
        "session_id": session_id,
        "conversation_history": []
    })
    print(f"🤖 老师: {result1['result']['response'][:100]}...")
    
    # 第二轮对话
    print("\n👤 学生: 那具体应该怎么积累素材呢？")
    conversation_history = result1['result']['conversation_history']
    result2 = await agent.execute("那具体应该怎么积累素材呢？", {
        "is_conversation": True,
        "session_id": session_id,
        "conversation_history": conversation_history
    })
    print(f"🤖 老师: {result2['result']['response'][:100]}...")
    
    # 第三轮对话
    print("\n👤 学生: 我平时观察力不够，怎么提高？")
    conversation_history = result2['result']['conversation_history']
    result3 = await agent.execute("我平时观察力不够，怎么提高？", {
        "is_conversation": True,
        "session_id": session_id,
        "conversation_history": conversation_history
    })
    print(f"🤖 老师: {result3['result']['response'][:100]}...")
    
    # 获取对话总结
    summary = agent.get_conversation_summary(session_id)
    print(f"\n📊 对话总结:")
    print(f"总轮次: {summary['total_turns']}")
    print(f"主要话题: {summary['main_topics']}")
    
    print("\n✅ 多轮对话测试完成!")


async def test_different_topics():
    """测试不同主题的中文教学"""
    print("\n📚 开始不同主题测试...")
    
    agent = ChineseTeacherAgent()
    
    topics = [
        {
            "name": "诗词鉴赏",
            "task": "如何欣赏古诗词的意境美？",
            "context": {"student_level": "高中生", "learning_goal": "提高诗词鉴赏能力"}
        },
        {
            "name": "文言文学习",
            "task": "文言文翻译有什么技巧？",
            "context": {"student_level": "高中生", "learning_goal": "掌握文言文翻译方法"}
        },
        {
            "name": "现代文阅读",
            "task": "如何分析文章的中心思想？",
            "context": {"student_level": "初中生", "learning_goal": "提高阅读理解能力"}
        }
    ]
    
    for topic in topics:
        print(f"\n🎯 测试主题: {topic['name']}")
        result = await agent.execute(topic['task'], topic['context'])
        print(f"任务类型: {result['result']['teaching_type']}")
        print(f"教学方法: {result['result']['teaching_methods']}")
        print(f"学习原则: {result['result']['learning_principles']}")
    
    print("\n✅ 不同主题测试完成!")


def main():
    """主测试函数"""
    print("🚀 中文老师Agent功能测试")
    print("=" * 50)
    
    # 运行测试
    asyncio.run(test_teaching_guidance())
    asyncio.run(test_conversation())
    asyncio.run(test_different_topics())
    
    print("\n🎉 所有测试完成!")


if __name__ == "__main__":
    main() 