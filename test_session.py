#!/usr/bin/env python3
"""
测试Session实体类和SessionDAO的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from entity.session import Session, TopicType, create_session
from entity.message import Message, MessageRole, MessageType
from datetime import datetime


def test_session_entity():
    """测试Session实体类的基本功能"""
    print("=== 测试Session实体类 ===")
    
    # 创建会话
    session = create_session(
        topic=TopicType.QUESTION,
        topic_id="question123"
    )
    print(f"创建会话: {session}")
    
    # 添加用户消息
    user_msg = session.add_user_message("你好，我有一个数学问题")
    print(f"添加用户消息: {user_msg}")
    
    # 添加助手消息
    assistant_msg = session.add_assistant_message("你好！请告诉我你的数学问题，我会尽力帮助你。")
    print(f"添加助手消息: {assistant_msg}")
    
    # 获取消息统计
    print(f"消息总数: {session.get_message_count()}")
    print(f"用户消息数: {len(session.get_user_messages())}")
    print(f"助手消息数: {len(session.get_assistant_messages())}")
    
    # 获取最后一条消息
    last_msg = session.get_last_message()
    print(f"最后一条消息: {last_msg}")
    
    # 获取会话摘要
    summary = session.get_conversation_summary()
    print(f"会话摘要: {summary}")
    
    # 转换为字典
    session_dict = session.to_dict()
    print(f"会话字典: {session_dict}")
    
    # 从字典创建会话
    new_session = Session.from_dict(session_dict)
    print(f"从字典创建的会话: {new_session}")
    
    print("Session实体类测试完成！\n")


def test_message_creation():
    """测试Message创建"""
    print("=== 测试Message创建 ===")
    
    # 创建文本消息
    text_msg = Message(
        role=MessageRole.USER,
        content="这是一个文本消息",
        message_type=MessageType.TEXT
    )
    print(f"文本消息: {text_msg}")
    
    # 创建包含图片的消息
    image_msg = Message(
        role=MessageRole.ASSISTANT,
        content=[
            {"type": "text", "text": "这是图片说明"},
            {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
        ],
        message_type=MessageType.IMAGE
    )
    print(f"图片消息: {image_msg}")
    
    print("Message创建测试完成！\n")


def test_session_with_goal():
    """测试与Goal相关的会话"""
    print("=== 测试Goal会话 ===")
    
    # 创建Goal类型的会话
    goal_session = create_session(
        topic=TopicType.GOAL,
        topic_id="goal456"
    )
    print(f"创建Goal会话: {goal_session}")
    
    # 添加学习目标相关的消息
    goal_session.add_user_message("我想学习Python编程")
    goal_session.add_assistant_message("很好的学习目标！Python是一个优秀的编程语言。让我们制定一个学习计划。")
    goal_session.add_user_message("我应该从哪里开始？")
    goal_session.add_assistant_message("建议从基础语法开始：变量、数据类型、控制流等。")
    
    print(f"Goal会话消息数: {goal_session.get_message_count()}")
    print(f"Goal会话摘要: {goal_session.get_conversation_summary()}")
    
    print("Goal会话测试完成！\n")


if __name__ == "__main__":
    print("开始测试Session相关功能...\n")
    
    try:
        test_message_creation()
        test_session_entity()
        test_session_with_goal()
        
        print("所有测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc() 