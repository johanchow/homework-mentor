"""
会话实体类 - 定义会话的基本结构和属性
"""

import json
from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from pydantic import PrivateAttr
from enum import Enum
from datetime import datetime
from entity.base import BaseModel
from entity.message import Message, MessageRole, MessageType
from entity.question import Question, Subject
from entity.goal import Goal
from utils.helpers import random_uuid

class TopicType(str, Enum):
    """主题类型枚举"""
    QUESTION = "question"  # 问题
    GOAL = "goal"         # 目标

class Session(BaseModel, table=True):
    """会话实体类"""

    # 基本信息
    id: Optional[str] = Field(default_factory=lambda: random_uuid(), primary_key=True, description="会话唯一标识")
    topic: TopicType = Field(..., description="主题类型")
    # 多态外键，可能是question_id，也可能是goal_id
    topic_id: str = Field(..., description="主题ID")

    # 可能关联问题
    _question: Optional[Question] = PrivateAttr(default=None)
    _goal: Optional[Goal] = PrivateAttr(default=None)

    
    # 消息列表 - 使用JSON字符串存储
    messages: Optional[str] = Field(default=None, description="消息列表JSON字符串")
    
    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 状态信息
    is_deleted: bool = Field(default=False, description="是否已删除")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True

    def add_message(self, message: Message) -> None:
        """
        添加消息到会话

        Args:
            message: 要添加的消息
        """
        messages_list = self.get_messages_list()
        messages_list.append(message.to_dict())
        self.messages = json.dumps(messages_list, ensure_ascii=False)
        self.updated_at = datetime.now()

    def get_messages(self) -> List[Message]:
        """获取消息列表"""
        if self.messages:
            messages = json.loads(self.messages)
            return [Message.from_dict(msg) for msg in messages]
        return []

    def get_messages_list(self) -> List[Dict[str, Any]]:
        """获取消息列表"""
        messages = self.get_messages()
        return [msg.to_dict() for msg in messages]

    def clear_messages(self) -> None:
        """清空所有消息"""
        self.messages = json.dumps([], ensure_ascii=False)
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

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "topic": self.topic,
            "topic_id": self.topic_id,
            "messages": self.get_messages_list(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_deleted": self.is_deleted
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """从字典创建Session对象"""
        messages = data.get("messages", [])
        return cls(
            id=data.get("id"),
            topic=data.get("topic"),
            topic_id=data.get("topic_id"),
            messages=json.dumps(messages, ensure_ascii=False) if messages else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            is_deleted=data.get("is_deleted", False)
        )

    def __str__(self) -> str:
        """字符串表示"""
        return f"Session(id={self.id}, topic={self.topic}, topic_id={self.topic_id})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"Session(id={self.id}, topic={self.topic}, topic_id={self.topic_id}"


# 创建会话的工厂函数
def create_session(
    topic: TopicType,
    topic_id: str,
    messages: Optional[List[Message]] = None,
) -> Session:
    """创建会话实例的工厂函数"""
    session = Session(
        topic=topic,
        topic_id=topic_id,
    )
    
    if messages:
        messages_data = [msg.to_dict() for msg in messages]
        session.messages = json.dumps(messages_data, ensure_ascii=False)
    
    return session


# 示例用法
if __name__ == "__main__":
    # 创建一个会话示例
    session = create_session(
        topic=TopicType.QUESTION,
        topic_id="question123",
    )

    # 添加一些消息
    session.add_user_message("你好，我有一个问题")
    session.add_assistant_message("你好！请告诉我你的问题，我会尽力帮助你。")

    print(session)
    print(f"主题类型: {session.topic}")
    print(f"主题ID: {session.topic_id}")
    print(f"消息数量: {session.get_message_count()}")
    print(f"最后消息: {session.get_last_message()}")
