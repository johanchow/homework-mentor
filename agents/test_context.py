"""
测试上下文传递功能
验证Agent是否能正确处理多轮对话的上下文
"""

from agent_graph import create_workflow, create_conversation_session
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

def test_context_preservation():
    """测试上下文保持功能"""
    print("=== 测试上下文保持功能 ===")

    load_dotenv('.env')
    app = create_workflow()
    session = create_conversation_session()

    # 第一轮：自我介绍
    print("\n--- 第一轮对话 ---")
    resp1 = app.invoke({
        "messages": [HumanMessage(content="你好，我是小明，我想学习中文。")],
        "session_id": session["session_id"],
        "conversation_history": session["conversation_history"],
        "subject": session["subject"]
    })
    print(f"用户: 你好，我是小明，我想学习中文。")
    print(f"AI: {resp1['messages'][-1].content if resp1['messages'] else '无回复'}")

    # 第二轮：询问写作建议
    print("\n--- 第二轮对话 ---")
    resp2 = app.invoke({
        "messages": [HumanMessage(content="我想学习写作，有什么建议吗？")],
        "session_id": session["session_id"],
        "conversation_history": resp1.get("conversation_history", []),
        "subject": resp1.get("subject", "")
    })
    print(f"用户: 我想学习写作，有什么建议吗？")
    print(f"AI: {resp2['messages'][-1].content if resp2['messages'] else '无回复'}")

    # 第三轮：基于前文继续询问
    print("\n--- 第三轮对话 ---")
    resp3 = app.invoke({
        "messages": [HumanMessage(content="能具体说说怎么写好开头吗？")],
        "session_id": session["session_id"],
        "conversation_history": resp2.get("conversation_history", []),
        "subject": resp2.get("subject", "")
    })
    print(f"用户: 能具体说说怎么写好开头吗？")
    print(f"AI: {resp3['messages'][-1].content if resp3['messages'] else '无回复'}")

    # 第四轮：测试上下文记忆
    print("\n--- 第四轮对话 ---")
    resp4 = app.invoke({
        "messages": [HumanMessage(content="刚才你提到的那个方法能再详细说说吗？")],
        "session_id": session["session_id"],
        "conversation_history": resp3.get("conversation_history", []),
        "subject": resp3.get("subject", "")
    })
    print(f"用户: 刚才你提到的那个方法能再详细说说吗？")
    print(f"AI: {resp4['messages'][-1].content if resp4['messages'] else '无回复'}")

    # 显示完整对话历史
    print(f"\n=== 完整对话历史 ===")
    final_history = resp4.get("conversation_history", [])
    for i, entry in enumerate(final_history, 1):
        role = "用户" if entry["role"] == "user" else "AI助手"
        print(f"{i}. {role}: {entry['content']}")

def test_subject_switching():
    """测试学科切换功能"""
    print("\n\n=== 测试学科切换功能 ===")

    load_dotenv('.env')
    app = create_workflow()
    session = create_conversation_session()

    # 第一轮：中文问题
    print("\n--- 第一轮：中文问题 ---")
    resp1 = app.invoke({
        "messages": [HumanMessage(content="我想学习中文语法。")],
        "session_id": session["session_id"],
        "conversation_history": session["conversation_history"],
        "subject": session["subject"]
    })
    print(f"用户: 我想学习中文语法。")
    print(f"AI: {resp1['messages'][-1].content if resp1['messages'] else '无回复'}")

    # 第二轮：闲聊问题
    print("\n--- 第二轮：闲聊问题 ---")
    resp2 = app.invoke({
        "messages": [HumanMessage(content="今天天气怎么样？")],
        "session_id": session["session_id"],
        "conversation_history": resp1.get("conversation_history", []),
        "subject": resp1.get("subject", "")
    })
    print(f"用户: 今天天气怎么样？")
    print(f"AI: {resp2['messages'][-1].content if resp2['messages'] else '无回复'}")

    # 第三轮：回到中文问题
    print("\n--- 第三轮：回到中文问题 ---")
    resp3 = app.invoke({
        "messages": [HumanMessage(content="我们继续学习中文吧，刚才说的语法能再详细解释一下吗？")],
        "session_id": session["session_id"],
        "conversation_history": resp2.get("conversation_history", []),
        "subject": resp2.get("subject", "")
    })
    print(f"用户: 我们继续学习中文吧，刚才说的语法能再详细解释一下吗？")
    print(f"AI: {resp3['messages'][-1].content if resp3['messages'] else '无回复'}")

def test_conversation_manager():
    """测试对话管理器"""
    print("\n\n=== 测试对话管理器 ===")

    from conversation_example import ConversationManager

    manager = ConversationManager()

    # 测试多轮对话
    conversations = [
        "你好，我是小红，我想学习中文写作。",
        "我想写一篇关于春天的作文。",
        "能给我一些关于春天的好词好句吗？",
        "刚才你提到的那些词语能用在开头吗？",
        "谢谢你的帮助！"
    ]

    for i, message in enumerate(conversations, 1):
        print(f"\n--- 第{i}轮对话 ---")
        print(f"用户: {message}")

        response = manager.send_message(message)
        print(f"AI: {response}")

    # 显示对话历史
    print(f"\n=== 对话历史 ===")
    history = manager.get_conversation_history()
    for entry in history:
        role = "用户" if entry["role"] == "user" else "AI助手"
        print(f"{role}: {entry['content']}")

if __name__ == "__main__":
    test_context_preservation()
    test_subject_switching()
    test_conversation_manager()
