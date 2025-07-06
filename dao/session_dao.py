"""
会话数据访问对象 - 提供会话相关的数据库操作
"""

from typing import List, Optional, Dict, Any
from sqlmodel import Session as DBSession, select, update, delete
from datetime import datetime
from entity.session import Session, TopicType
from entity.message import Message, MessageRole, MessageType
from dao.base_dao import BaseDao
from dao.question_dao import QuestionDAO
from dao.goal_dao import GoalDAO
import json
from entity.message import create_message

class SessionDAO(BaseDao):
    """会话数据访问对象"""

    def get_by_id(self, id: str) -> Session:
        """
        根据ID获取会话

        Args:
            id: 会话ID

        Returns:
            会话对象
        """
        session = self._get_by_id(Session, id)
        # 手动初始化 pydantic private attr
        if session.__pydantic_private__ is None:
            session.__pydantic_private__ = type(session)().__pydantic_private__
        return session

    def search_by_kwargs(self, kwargs: dict, skip: int = 0, limit: int = 100) -> List[Session]:
        """
        根据关键字搜索会话

        Args:
            kwargs: 搜索条件
            skip: 跳过数量
            limit: 返回数量限制

        Returns:
            会话列表
        """
        return self._search_by_kwargs(Session, kwargs, skip, limit)

    def count_by_kwargs(self, kwargs: dict) -> int:
        """
        根据关键字统计会话数量

        Args:
            kwargs: 搜索条件

        Returns:
            会话数量
        """
        return self._count_by_kwargs(Session, kwargs)

    def get_full_by_id(self, id: str) -> Session:
        """
        根据ID获取会话
        """
        session = self.get_by_id(id)
        if session.topic == TopicType.QUESTION and session.topic_id:
            session.question = QuestionDAO.get_by_id(session.topic_id)
        elif session.topic == TopicType.GOAL and session.topic_id:
            session.goal = GoalDAO.get_by_id(session.topic_id)
        return session
            

    def add_message(self, session_id: str, message: Message) -> Optional[Session]:
        """
        向会话添加消息

        Args:
            session_id: 会话ID
            message: 要添加的消息

        Returns:
            更新后的会话对象，如果会话不存在则返回None
        """
        session = self.get_by_id(session_id)
        if not session:
            return None

        # 获取现有消息列表
        messages_list = session.get_messages_list()
        
        # 添加新消息
        messages_list.append(message.to_dict())
        
        # 更新会话
        session.messages = json.dumps(messages_list, ensure_ascii=False)
        return self.update(session)

    def add_user_message(self, session_id: str, message_content: str) -> Optional[Session]:
        """
        向会话添加用户消息
        """
        message = create_message(role=MessageRole.USER, content=message_content, message_type=MessageType.TEXT)
        return self.add_message(session_id, message)

session_dao = SessionDAO()

# 示例用法
if __name__ == "__main__":
    # 这里需要实际的数据库连接
    # dao = SessionDAO()
    #     
    # # 创建会话
    # session = dao.create_session(TopicType.QUESTION, "question123")
    # print(f"创建会话: {session}")
    #     
    # # 添加消息
    # updated_session = dao.add_user_message(session.id, "你好，我有一个问题")
    # print(f"添加用户消息后: {updated_session.get_message_count()} 条消息")
    #     
    # # 添加助手回复
    # updated_session = dao.add_assistant_message(session.id, "你好！请告诉我你的问题，我会尽力帮助你。")
    # print(f"添加助手消息后: {updated_session.get_message_count()} 条消息")
    pass
