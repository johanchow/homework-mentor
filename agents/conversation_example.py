"""
多轮对话使用示例
展示如何使用改造后的agent_graph进行多轮对话
"""

from agent_graph import create_workflow, create_conversation_session
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

class ConversationManager:
    """对话管理器"""

    def __init__(self):
        load_dotenv('.env')
        self.app = create_workflow()
        self.session = create_conversation_session()

    def send_message(self, message: str):
        """发送消息并获取回复"""
        # 准备输入状态
        input_state = {
            "messages": [HumanMessage(content=message)],
            "session_id": self.session["session_id"],
            "conversation_history": self.session.get("conversation_history", []),
            "subject": self.session.get("subject", "")
        }

        # 调用工作流
        response = self.app.invoke(input_state)

        # 更新会话状态
        self.session["conversation_history"] = response.get("conversation_history", [])
        self.session["subject"] = response.get("subject", "")

        # 返回AI回复
        if response.get("messages"):
            return response["messages"][-1].content
        return "抱歉，没有收到回复"

    def get_conversation_history(self):
        """获取对话历史"""
        return self.session.get("conversation_history", [])

    def reset_conversation(self):
        """重置对话"""
        self.session = create_conversation_session()

def main():
    """主函数 - 演示多轮对话"""
    print("=== 多轮对话演示 ===")

    # 创建对话管理器
    manager = ConversationManager()

    # 对话示例
    conversations = [
        "你好，我是小明，我想学习中文。",
        "我想学习写作，有什么建议吗？",
        "能具体说说怎么写好开头吗？",
        "今天天气怎么样？",
        "我想继续学习中文语法。"
    ]

    for i, message in enumerate(conversations, 1):
        print(f"\n--- 第{i}轮对话 ---")
        print(f"用户: {message}")

        response = manager.send_message(message)
        print(f"AI助手: {response}")

    # 显示对话历史
    print(f"\n=== 对话历史 ===")
    history = manager.get_conversation_history()
    for entry in history:
        role = "用户" if entry["role"] == "user" else "AI助手"
        print(f"{role}: {entry['content']}")

if __name__ == "__main__":
    main()
