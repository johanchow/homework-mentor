"""
高级多轮对话管理器
支持状态持久化、错误处理和更好的用户体验
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from agent_graph import create_workflow, create_conversation_session
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

class AdvancedConversationManager:
    """高级对话管理器"""

    def __init__(self, session_id: Optional[str] = None, storage_path: str = "conversations"):
        """
        初始化对话管理器

        Args:
            session_id: 会话ID，如果为None则创建新会话
            storage_path: 对话历史存储路径
        """
        load_dotenv('.env')
        self.app = create_workflow()
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        if session_id:
            self.session = self._load_session(session_id)
        else:
            self.session = create_conversation_session()
            self._save_session()

    def _save_session(self):
        """保存会话状态"""
        session_file = self.storage_path / f"{self.session['session_id']}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(self.session, f, ensure_ascii=False, indent=2)

    def _load_session(self, session_id: str) -> Dict[str, Any]:
        """加载会话状态"""
        session_file = self.storage_path / f"{session_id}.json"
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"会话 {session_id} 不存在")

    def send_message(self, message: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        发送消息并获取回复

        Args:
            message: 用户消息
            user_id: 用户ID（可选）

        Returns:
            包含回复和状态的字典
        """
        try:
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

            # 添加用户信息
            if user_id:
                self.session["user_id"] = user_id

            # 保存会话
            self._save_session()

            # 返回结果
            ai_response = response["messages"][-1].content if response.get("messages") else "抱歉，没有收到回复"

            return {
                "success": True,
                "response": ai_response,
                "session_id": self.session["session_id"],
                "conversation_length": len(self.session["conversation_history"]),
                "subject": self.session.get("subject", ""),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "session_id": self.session["session_id"],
                "timestamp": datetime.now().isoformat()
            }

    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取对话历史

        Args:
            limit: 限制返回的对话轮数

        Returns:
            对话历史列表
        """
        history = self.session.get("conversation_history", [])
        if limit:
            history = history[-limit:]
        return history

    def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息"""
        return {
            "session_id": self.session["session_id"],
            "conversation_length": len(self.session.get("conversation_history", [])),
            "subject": self.session.get("subject", ""),
            "user_id": self.session.get("user_id"),
            "created_at": self.session.get("created_at", ""),
            "last_updated": datetime.now().isoformat()
        }

    def reset_conversation(self):
        """重置对话"""
        self.session = create_conversation_session()
        self._save_session()

    def export_conversation(self, format: str = "json") -> str:
        """
        导出对话历史

        Args:
            format: 导出格式 ("json" 或 "txt")

        Returns:
            导出的内容
        """
        history = self.get_conversation_history()

        if format == "json":
            return json.dumps({
                "session_id": self.session["session_id"],
                "conversation_history": history,
                "exported_at": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)

        elif format == "txt":
            lines = [f"会话ID: {self.session['session_id']}", ""]
            for entry in history:
                role = "用户" if entry["role"] == "user" else "AI助手"
                lines.append(f"{role}: {entry['content']}")
                lines.append("")
            return "\n".join(lines)

        else:
            raise ValueError(f"不支持的导出格式: {format}")

    @classmethod
    def list_sessions(cls, storage_path: str = "conversations") -> List[Dict[str, Any]]:
        """列出所有会话"""
        storage_dir = Path(storage_path)
        if not storage_dir.exists():
            return []

        sessions = []
        for session_file in storage_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    sessions.append({
                        "session_id": session_data["session_id"],
                        "conversation_length": len(session_data.get("conversation_history", [])),
                        "subject": session_data.get("subject", ""),
                        "user_id": session_data.get("user_id"),
                        "created_at": session_data.get("created_at", ""),
                        "file_path": str(session_file)
                    })
            except Exception as e:
                print(f"读取会话文件 {session_file} 时出错: {e}")

        return sessions

def demo_conversation():
    """演示多轮对话"""
    print("=== 高级多轮对话演示 ===")

    # 创建对话管理器
    manager = AdvancedConversationManager()

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

        result = manager.send_message(message, user_id="user_001")

        if result["success"]:
            print(f"AI助手: {result['response']}")
            print(f"会话ID: {result['session_id']}")
            print(f"对话长度: {result['conversation_length']}")
        else:
            print(f"错误: {result['error']}")

    # 显示会话信息
    print(f"\n=== 会话信息 ===")
    session_info = manager.get_session_info()
    for key, value in session_info.items():
        print(f"{key}: {value}")

    # 导出对话历史
    print(f"\n=== 导出对话历史 ===")
    exported_json = manager.export_conversation("json")
    print("JSON格式:")
    print(exported_json[:200] + "..." if len(exported_json) > 200 else exported_json)

    exported_txt = manager.export_conversation("txt")
    print("\nTXT格式:")
    print(exported_txt[:200] + "..." if len(exported_txt) > 200 else exported_txt)

def demo_session_management():
    """演示会话管理"""
    print("\n=== 会话管理演示 ===")

    # 列出所有会话
    sessions = AdvancedConversationManager.list_sessions()
    print(f"找到 {len(sessions)} 个会话:")
    for session in sessions:
        print(f"- {session['session_id']}: {session['conversation_length']} 轮对话")

if __name__ == "__main__":
    demo_conversation()
    demo_session_management()
