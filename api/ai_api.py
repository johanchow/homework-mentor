"""
AI API模块 - 处理AI相关的HTTP请求
"""

from flask import Blueprint, request, jsonify
import logging
import json
from agents.agent_graph import agent_graph
from entity.session import create_session, TopicType
from dao.session_dao import session_dao
from entity.message import create_message, MessageRole, MessageType
from entity.goal import create_goal

logger = logging.getLogger(__name__)

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

@ai_bp.route('/generate-questions', methods=['POST'])
def generate_questions():
    """创建AI"""
    data = request.get_json()

    required_fields = ['ai_prompt', 'subject', 'count']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    ai_prompt = data.get('ai_prompt')
    subject = data.get('subject')
    count = data.get('count')
    session_id = data.get('session_id')

    if not session_id:
        session = create_session(TopicType.GOAL, '')
        session._goal = create_goal(name='', subject=subject, ai_prompt=ai_prompt, creator_id='')
    else:
        session = session_dao.get_full_by_id(session_id)

    new_message = create_message(
        role=MessageRole.USER,
        content=f"请根据以下新的提示生成{count}个{subject}题目:\n{ai_prompt}",
        message_type=MessageType.TEXT
    )
    state = agent_graph.invoke({
        "session": session,
        "latest_message": new_message,
    }, config={"configurable": {"thread_id": session_id}})
    questions = state.get('questions')

    # 添加用户消息
    session.add_message(create_message(
        role=MessageRole.USER,
        content=ai_prompt,
        message_type=MessageType.TEXT
    ))
    if session_id:
        session_dao.update(session)
    else:
        session_dao.create(session)

    return jsonify({
        "questions": [q.to_dict() for q in questions],
        "session_id": session.id
    })


@ai_bp.route('/import-questions', methods=['POST'])
def import_questions():
    """导入题目"""
    data = request.get_json()
    pass


