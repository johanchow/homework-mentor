"""
测试TypistAgent的功能
"""

import asyncio
from agents.planner_typist_agent import TypistAgent
from entity.message import Message, MessageRole


async def test_text_input():
    """测试纯文本输入"""
    print("🧪 测试纯文本输入...")

    agent = TypistAgent()

    # 测试选择题
    text_input = Message(role=MessageRole.USER, content="""
    下列词语中加点字的读音完全正确的一项是：
    A. 憧憬(chōng jǐng)
    B. 憧憬(chōng jìng)
    C. 憧憬(chōng jīng)
    D. 憧憬(chōng jīng)
    答案：A
    """)

    result = agent.process_input(text_input)
    print(f"处理结果: {result}")

    print("✅ 纯文本输入测试完成!")


async def test_multimodal_input():
    """测试多模态输入（文字+图片）"""
    print("\n🧪 测试多模态输入...")

    agent = TypistAgent()

    # 创建包含图片的消息
    message = Message(
        role=MessageRole.USER,
        content=[
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://clothing-try-on-1306401232.cos.ap-guangzhou.myqcloud.com/homework-mentor/admin-test.png"
                }
            },
        ]
    )

    questions = agent.process_input(message)
    print(f"生成题目数量: {len(questions)}")

    for i, question in enumerate(questions, 1):
        print(f"题目{i}: {question.title}")
        print(f"  科目: {question.subject}")
        print(f"  类型: {question.type}")

    print("✅ 多模态输入测试完成!")


async def main():
    """主测试函数"""
    print("🚀 开始测试TypistAgent...")

    try:
        # await test_text_input()
        await test_multimodal_input()

        print("\n🎉 所有测试通过!")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    from dotenv import load_dotenv
    print('----------- load_dotenv -----------')
    load_dotenv('.env')
    asyncio.run(main())