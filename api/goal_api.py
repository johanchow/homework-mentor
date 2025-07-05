"""
目标API - 提供目标相关的RESTful接口
"""

from flask import Blueprint, request, jsonify
from typing import List, Optional
import logging
from datetime import datetime
from entity.goal import Goal, GoalStatus, Subject, create_goal
from dao.goal_dao import goal_dao
from dao.user_dao import user_dao
from utils.jwt_utils import require_auth

logger = logging.getLogger(__name__)

goal_bp = Blueprint('goal', __name__, url_prefix='/goal')


def goal_to_response(goal: Goal) -> dict:
    """将Goal实体转换为响应格式"""
    return {
        "id": goal.id,
        "name": goal.name,
        "subject": goal.subject,
        "status": goal.status,
        "ai_prompt": goal.ai_prompt,
        "creator_id": goal.creator_id,
        "created_at": goal.created_at.isoformat(),
        "updated_at": goal.updated_at.isoformat(),
        "is_active": goal.is_active,
        "is_deleted": goal.is_deleted
    }


def validate_creator_exists(creator_id: str) -> bool:
    """验证创建人是否存在"""
    creator = user_dao.get_by_id(creator_id)
    return creator is not None


# API接口

@goal_bp.route('/create', methods=['POST'])
@require_auth
def create_goal_api():
    """
    创建目标

    请求参数:
    - name: 目标名称
    - subject: 科目
    - ai_prompt: AI提示词
    - creator_id: 创建人ID
    - status: 目标状态（可选，默认为pending）
    """
    try:
        data = request.get_json()

        # 验证必需字段
        required_fields = ['name', 'subject', 'creator_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必需字段: {field}'}), 400

        # 验证创建人是否存在
        if not validate_creator_exists(data['creator_id']):
            return jsonify({'error': '创建人不存在'}), 400

        # 创建目标
        goal = create_goal(
            name=data['name'],
            subject=data['subject'],
            ai_prompt=data['ai_prompt'],
            creator_id=data['creator_id'],
            status=data.get('status', GoalStatus.PREPARING)
        )

        # 保存到数据库
        created_goal = goal_dao.create(goal)

        logger.info(f"创建目标成功: {created_goal.id}")
        return jsonify({
            'code': 0,
            'message': '目标创建成功',
            'goal': goal_to_response(created_goal)
        }), 201

    except Exception as e:
        logger.error(f"创建目标失败: {e}")
        return jsonify({'error': f'创建目标失败: {str(e)}'}), 500


@goal_bp.route('/<goal_id>', methods=['GET'])
@require_auth
def get_goal_api(goal_id):
    """
    根据ID获取目标详情

    路径参数:
    - goal_id: 目标ID
    """
    try:
        goal = goal_dao.get_by_id(goal_id)
        if not goal:
            return jsonify({'error': '目标不存在'}), 404

        return jsonify({
            'code': 0,
            'message': '获取目标详情成功',
            'goal': goal_to_response(goal)
        }), 200

    except Exception as e:
        logger.error(f"获取目标失败: {e}")
        return jsonify({'error': f'获取目标失败: {str(e)}'}), 500


@goal_bp.route('/<goal_id>', methods=['PUT'])
@require_auth
def update_goal_api(goal_id):
    """
    更新目标

    路径参数:
    - goal_id: 目标ID

    请求参数:
    - name: 目标名称（可选）
    - subject: 科目（可选）
    - status: 目标状态（可选）
    - ai_prompt: AI提示词（可选）
    """
    try:
        data = request.get_json()

        # 获取现有目标
        goal = goal_dao.get_by_id(goal_id)
        if not goal:
            return jsonify({'error': '目标不存在'}), 404

        # 更新字段
        if 'name' in data:
            goal.name = data['name']
        if 'subject' in data:
            goal.subject = data['subject']
        if 'status' in data:
            goal.status = data['status']
        if 'ai_prompt' in data:
            goal.ai_prompt = data['ai_prompt']

        # 更新修改时间
        goal.updated_at = datetime.now()

        # 保存到数据库
        updated_goal = goal_dao.update(goal)

        logger.info(f"更新目标成功: {goal_id}")
        return jsonify({
            'code': 0,
            'message': '目标更新成功',
            'goal': goal_to_response(updated_goal)
        }), 200

    except Exception as e:
        logger.error(f"更新目标失败: {e}")
        return jsonify({'error': f'更新目标失败: {str(e)}'}), 500


@goal_bp.route('/<goal_id>', methods=['DELETE'])
@require_auth
def delete_goal_api(goal_id):
    """
    删除目标（软删除）

    路径参数:
    - goal_id: 目标ID
    """
    try:
        # 获取目标
        goal = goal_dao.get_by_id(goal_id)
        if not goal:
            return jsonify({'error': '目标不存在'}), 404

        # 软删除
        goal_dao.delete(goal)

        logger.info(f"删除目标成功: {goal_id}")
        return jsonify({
            'code': 0,
            'message': '目标删除成功',
            'goal_id': goal_id
        }), 200

    except Exception as e:
        logger.error(f"删除目标失败: {e}")
        return jsonify({'error': f'删除目标失败: {str(e)}'}), 500


@goal_bp.route('/list', methods=['GET'])
@require_auth
def list_goals_api():
    """
    获取目标列表，支持筛选和分页

    查询参数:
    - name: 目标名称过滤（可选）
    - subject: 科目过滤（可选）
    - status: 状态过滤（可选）
    - creator_id: 创建人ID过滤（可选）
    - page: 页码，默认1
    - size: 每页数量，默认10
    """
    try:
        # 获取查询参数
        name = request.args.get('name')
        subject = request.args.get('subject')
        creator_id = request.args.get('creator_id')
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))

        # 计算分页参数
        skip = (page - 1) * size
        limit = size

        # 构建筛选条件
        filters = {}
        if name is not None:
            filters["name"] = name
        if subject is not None:
            filters["subject"] = subject
        if creator_id is not None:
            filters["creator_id"] = creator_id

        goals = goal_dao.search_by_kwargs(filters, skip=skip, limit=limit)
        total = goal_dao.count_by_kwargs(filters)

        # 转换为响应格式
        goal_responses = [goal_to_response(g) for g in goals]

        return jsonify({
            'code': 0,
            'message': '获取目标列表成功',
            'data': {
                'goals': goal_responses,
                'total': total,
                'page': page,
                'size': size,
                'pages': (total + size - 1) // size
            }
        }), 200

    except Exception as e:
        logger.error(f"获取目标列表失败: {e}")
        return jsonify({'error': f'获取目标列表失败: {str(e)}'}), 500
