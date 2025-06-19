"""
API路由定义
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
import asyncio
from workflows.coordinator import MultiAgentCoordinator
from utils.helpers import validate_task_input, format_response, sanitize_task_id, setup_logging

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 创建协调器实例
coordinator = MultiAgentCoordinator()

# 设置日志
logger = setup_logging()


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return format_response(
        success=True,
        data={"status": "healthy", "service": "langgraph_agents"},
        message="服务运行正常"
    )


@api_bp.route('/task', methods=['POST'])
def submit_task():
    """提交新任务"""
    try:
        data = request.get_json()
        if not data:
            return format_response(
                success=False,
                error="请求体不能为空"
            ), 400
        
        task = data.get('task', '')
        priority = data.get('priority', 'medium')
        context = data.get('context', {})
        
        # 验证输入
        validation = validate_task_input(task, priority, context)
        if not validation['valid']:
            return format_response(
                success=False,
                error=f"输入验证失败: {', '.join(validation['errors'])}"
            ), 400
        
        # 提交任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            coordinator.submit_task(validation['task'], validation['priority'], validation['context'])
        )
        loop.close()
        
        logger.info(f"任务已提交: {result['task_id']}")
        
        return format_response(
            success=True,
            data=result,
            message="任务提交成功"
        )
        
    except Exception as e:
        logger.error(f"提交任务失败: {str(e)}")
        return format_response(
            success=False,
            error=f"提交任务失败: {str(e)}"
        ), 500


@api_bp.route('/task/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    try:
        task_id = sanitize_task_id(task_id)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        status = loop.run_until_complete(coordinator.get_task_status(task_id))
        loop.close()
        
        if not status:
            return format_response(
                success=False,
                error="任务不存在"
            ), 404
        
        return format_response(
            success=True,
            data=status,
            message="获取任务状态成功"
        )
        
    except Exception as e:
        logger.error(f"获取任务状态失败: {str(e)}")
        return format_response(
            success=False,
            error=f"获取任务状态失败: {str(e)}"
        ), 500


@api_bp.route('/task/<task_id>/result', methods=['GET'])
def get_task_result(task_id):
    """获取任务结果"""
    try:
        task_id = sanitize_task_id(task_id)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coordinator.get_task_result(task_id))
        loop.close()
        
        if result is None:
            return format_response(
                success=False,
                error="任务结果不存在或任务未完成"
            ), 404
        
        return format_response(
            success=True,
            data=result,
            message="获取任务结果成功"
        )
        
    except Exception as e:
        logger.error(f"获取任务结果失败: {str(e)}")
        return format_response(
            success=False,
            error=f"获取任务结果失败: {str(e)}"
        ), 500


@api_bp.route('/task/<task_id>', methods=['DELETE'])
def cancel_task(task_id):
    """取消任务"""
    try:
        task_id = sanitize_task_id(task_id)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coordinator.cancel_task(task_id))
        loop.close()
        
        if not result['success']:
            return format_response(
                success=False,
                error=result['error']
            ), 400
        
        return format_response(
            success=True,
            data=result,
            message="任务取消成功"
        )
        
    except Exception as e:
        logger.error(f"取消任务失败: {str(e)}")
        return format_response(
            success=False,
            error=f"取消任务失败: {str(e)}"
        ), 500


@api_bp.route('/task/sync', methods=['POST'])
def execute_task_sync():
    """同步执行任务"""
    try:
        data = request.get_json()
        if not data:
            return format_response(
                success=False,
                error="请求体不能为空"
            ), 400
        
        task = data.get('task', '')
        context = data.get('context', {})
        
        # 验证输入
        validation = validate_task_input(task, context=context)
        if not validation['valid']:
            return format_response(
                success=False,
                error=f"输入验证失败: {', '.join(validation['errors'])}"
            ), 400
        
        # 同步执行任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            coordinator.execute_task_sync(validation['task'], validation['context'])
        )
        loop.close()
        
        logger.info(f"同步任务执行完成: {task}")
        
        return format_response(
            success=True,
            data=result,
            message="任务执行成功"
        )
        
    except Exception as e:
        logger.error(f"同步执行任务失败: {str(e)}")
        return format_response(
            success=False,
            error=f"执行任务失败: {str(e)}"
        ), 500


@api_bp.route('/status', methods=['GET'])
def get_system_status():
    """获取系统状态"""
    try:
        status = coordinator.get_system_status()
        
        return format_response(
            success=True,
            data=status,
            message="获取系统状态成功"
        )
        
    except Exception as e:
        logger.error(f"获取系统状态失败: {str(e)}")
        return format_response(
            success=False,
            error=f"获取系统状态失败: {str(e)}"
        ), 500


@api_bp.route('/agents', methods=['GET'])
def get_agents_info():
    """获取所有Agent信息"""
    try:
        agent_status = coordinator.router.get_agent_status()
        
        return format_response(
            success=True,
            data=agent_status,
            message="获取Agent信息成功"
        )
        
    except Exception as e:
        logger.error(f"获取Agent信息失败: {str(e)}")
        return format_response(
            success=False,
            error=f"获取Agent信息失败: {str(e)}"
        ), 500


# 中文教学相关接口
@api_bp.route('/chinese/teach', methods=['POST'])
def chinese_teaching():
    """中文教学指导接口"""
    try:
        data = request.get_json()
        if not data:
            return format_response(
                success=False,
                error="请求体不能为空"
            ), 400
        
        question = data.get('question', '')
        student_level = data.get('student_level', '中等水平')
        learning_goal = data.get('learning_goal', '提高语文能力')
        
        if not question or len(question.strip()) < 5:
            return format_response(
                success=False,
                error="问题描述至少需要5个字符"
            ), 400
        
        # 构建上下文
        context = {
            "student_level": student_level,
            "learning_goal": learning_goal
        }
        
        # 同步执行中文教学任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            coordinator.execute_task_sync(question, context)
        )
        loop.close()
        
        logger.info(f"中文教学任务完成: {question}")
        
        return format_response(
            success=True,
            data=result,
            message="中文教学指导完成"
        )
        
    except Exception as e:
        logger.error(f"中文教学失败: {str(e)}")
        return format_response(
            success=False,
            error=f"中文教学失败: {str(e)}"
        ), 500


@api_bp.route('/chinese/conversation/start', methods=['POST'])
def start_chinese_conversation():
    """开始中文教学对话"""
    try:
        data = request.get_json() or {}
        student_info = data.get('student_info', {})
        
        # 获取中文老师Agent
        chinese_agent = coordinator.router.available_agents.get('chinese_teacher')
        if not chinese_agent:
            return format_response(
                success=False,
                error="中文老师Agent不可用"
            ), 500
        
        # 开始对话会话
        session_id = chinese_agent.start_conversation(student_info)
        
        return format_response(
            success=True,
            data={"session_id": session_id},
            message="对话会话已开始"
        )
        
    except Exception as e:
        logger.error(f"开始对话失败: {str(e)}")
        return format_response(
            success=False,
            error=f"开始对话失败: {str(e)}"
        ), 500


@api_bp.route('/chinese/conversation/chat', methods=['POST'])
def chinese_conversation_chat():
    """中文教学对话聊天"""
    try:
        data = request.get_json()
        if not data:
            return format_response(
                success=False,
                error="请求体不能为空"
            ), 400
        
        message = data.get('message', '')
        session_id = data.get('session_id', '')
        conversation_history = data.get('conversation_history', [])
        
        if not message or len(message.strip()) < 2:
            return format_response(
                success=False,
                error="消息内容至少需要2个字符"
            ), 400
        
        # 构建对话上下文
        context = {
            "is_conversation": True,
            "session_id": session_id,
            "conversation_history": conversation_history
        }
        
        # 执行对话任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            coordinator.execute_task_sync(message, context)
        )
        loop.close()
        
        return format_response(
            success=True,
            data=result,
            message="对话回复完成"
        )
        
    except Exception as e:
        logger.error(f"对话聊天失败: {str(e)}")
        return format_response(
            success=False,
            error=f"对话聊天失败: {str(e)}"
        ), 500


@api_bp.route('/chinese/conversation/<session_id>/summary', methods=['GET'])
def get_conversation_summary(session_id):
    """获取对话总结"""
    try:
        session_id = sanitize_task_id(session_id)
        
        # 获取中文老师Agent
        chinese_agent = coordinator.router.available_agents.get('chinese_teacher')
        if not chinese_agent:
            return format_response(
                success=False,
                error="中文老师Agent不可用"
            ), 500
        
        # 获取对话总结
        summary = chinese_agent.get_conversation_summary(session_id)
        
        if "error" in summary:
            return format_response(
                success=False,
                error=summary["error"]
            ), 404
        
        return format_response(
            success=True,
            data=summary,
            message="获取对话总结成功"
        )
        
    except Exception as e:
        logger.error(f"获取对话总结失败: {str(e)}")
        return format_response(
            success=False,
            error=f"获取对话总结失败: {str(e)}"
        ), 500 