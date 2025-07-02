from typing import List, Optional, Dict, Any
from datetime import datetime
from .message import Message, MessageRole
from .question import Question
from utils.helpers import random_uuid


class Session:
    """会话类，管理对话消息"""

    def __init__(
        self,
        id: str,
        question: Question,
    ):
        """
        初始化会话

        Args:
            id: 会话ID，标识当前具体会话
            question: 问题对象
        """
        self.id = id
        self.question = question
        self.messages = []
        self.created_at = datetime.now()

    def add_message(self, message: Message) -> None:
        """
        添加消息到会话

        Args:
            message: 要添加的消息
        """
        self.messages.append(message)
        self.updated_at = datetime.now()

    def add_user_message(self, content: str, message_type: str = "text") -> Message:
        """
        添加用户消息

        Args:
            content: 消息内容
            message_type: 消息类型

        Returns:
            创建的消息对象
        """
        message = Message(
            role=MessageRole.USER,
            content=content,
            message_id=random_uuid()
        )
        self.add_message(message)
        return message

    def add_assistant_message(self, content: str, message_type: str = "text") -> Message:
        """
        添加助手消息

        Args:
            content: 消息内容
            message_type: 消息类型

        Returns:
            创建的消息对象
        """
        message = Message(
            role=MessageRole.ASSISTANT,
            content=content,
            message_id=random_uuid()
        )
        self.add_message(message)
        return message

    def get_messages(self, limit: Optional[int] = None, offset: int = 0) -> List[Message]:
        """
        获取消息列表

        Args:
            limit: 限制返回的消息数量
            offset: 偏移量

        Returns:
            消息列表
        """
        messages = self.messages[offset:]
        if limit:
            messages = messages[:limit]
        return messages

    def get_user_messages(self) -> List[Message]:
        """获取所有用户消息"""
        return [msg for msg in self.messages if msg.role == MessageRole.USER]

    def get_assistant_messages(self) -> List[Message]:
        """获取所有助手消息"""
        return [msg for msg in self.messages if msg.role == MessageRole.ASSISTANT]

    def get_last_message(self) -> Optional[Message]:
        """获取最后一条消息"""
        return self.messages[-1] if self.messages else None

    def get_last_user_message(self) -> Optional[Message]:
        """获取最后一条用户消息"""
        for msg in reversed(self.messages):
            if msg.role == MessageRole.USER:
                return msg
        return None

    def get_last_assistant_message(self) -> Optional[Message]:
        """获取最后一条助手消息"""
        for msg in reversed(self.messages):
            if msg.role == MessageRole.ASSISTANT:
                return msg
        return None

    def get_message_count(self) -> int:
        """获取消息总数"""
        return len(self.messages)

    def clear_messages(self) -> None:
        """清空所有消息"""
        self.messages.clear()
        self.updated_at = datetime.now()

    def get_messages_for_llm(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取用于LLM的消息格式

        Args:
            limit: 限制消息数量

        Returns:
            LLM格式的消息列表
        """
        messages = self.get_messages(limit=limit)
        return [msg.to_llm_message() for msg in messages]

    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        获取会话摘要

        Returns:
            会话摘要信息
        """
        return {
            "id": self.id,
            "question": self.get_question_summary(),
            "total_messages": self.get_message_count(),
            "user_messages": len(self.get_user_messages()),
            "assistant_messages": len(self.get_assistant_messages()),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_message": self.get_last_message().to_dict() if self.get_last_message() else None
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "question": self.question.to_dict(),
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """从字典创建Session对象"""
        from .message import Message

        messages = [Message.from_dict(msg_data) for msg_data in data.get("messages", [])]
        question = Question.from_dict(data["question"])

        return cls(
            question=question,
            messages=messages,
            id=data.get("id"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            metadata=data.get("metadata", {})
        )

    def __str__(self) -> str:
        """字符串表示"""
        return f"Session(id={self.id}, messages={len(self.messages)}, question='{self.question.title[:50]}...')"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"Session(id={self.id}, question_id={self.question.id}, messages_count={len(self.messages)})"
