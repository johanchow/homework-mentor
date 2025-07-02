"""
问题API - 提供问题相关的RESTful接口
"""

from flask import Blueprint, request, jsonify
from pydantic import BaseModel
from typing import List, Optional
import json
import logging
from dao.question_dao import question_dao
from dao.user_dao import user_dao
from entity.question import Question, QuestionType, Subject, create_question
from utils.jwt_utils import require_auth

logger = logging.getLogger(__name__)

question_bp = Blueprint('question', __name__, url_prefix='/question')


# 请求模型
class QuestionCreateRequest(BaseModel):
    """创建问题的请求模型"""
    subject: Subject
    type: QuestionType
    title: str
    creator_id: str
    options: Optional[List[str]] = None
    images: Optional[List[str]] = None
    audios: Optional[List[str]] = None
    videos: Optional[List[str]] = None


class QuestionUpdateRequest(BaseModel):
    """更新问题的请求模型"""
    subject: Optional[Subject] = None
    type: Optional[QuestionType] = None
    title: Optional[str] = None
    options: Optional[List[str]] = None
    images: Optional[List[str]] = None
    audios: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    is_active: Optional[bool] = None


class QuestionBatchCreateRequest(BaseModel):
    """批量创建问题的请求模型"""
    questions: List[QuestionCreateRequest]


# 响应模型
class QuestionResponse(BaseModel):
    """问题响应模型"""
    id: str
    subject: Subject
    type: QuestionType
    title: str
    options: Optional[str] = None
    images: Optional[str] = None
    audios: Optional[str] = None
    videos: Optional[str] = None
    creator_id: str
    created_at: str
    updated_at: str
    is_active: bool
    is_deleted: bool

    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    """问题列表响应模型"""
    questions: List[QuestionResponse]
    total: int
    skip: int
    limit: int


class QuestionBatchCreateResponse(BaseModel):
    """批量创建问题响应模型"""
    created_count: int
    failed_count: int
    questions: List[QuestionResponse]
    errors: List[str]


# 工具函数
def question_to_response(question: Question) -> dict:
    """将Question实体转换为响应格式"""
    try:
        options = json.loads(question.options) if question.options else []
    except Exception as e:
        logger.exception(f"转换问题选项失败: {e}")
        options = ["__invalid__"]

    return {
        "id": question.id,
        "subject": question.subject,
        "type": question.type,
        "title": question.title,
        "options": options,
        "images": question.images.split(',') if question.images else [],
        "audios": question.audios.split(',') if question.audios else [],
        "videos": question.videos.split(',') if question.videos else [],
        "creator_id": question.creator_id,
        "created_at": question.created_at.isoformat(),
        "updated_at": question.updated_at.isoformat(),
        "is_active": question.is_active,
        "is_deleted": question.is_deleted
    }


def validate_creator_exists(creator_id: str) -> bool:
    """验证创建人是否存在"""
    creator = user_dao.get_by_id(creator_id)
    return creator is not None


# API接口

@question_bp.route('/create', methods=['POST'])
@require_auth
def create_question_api():
    """
    创建单个问题

    请求参数:
    - subject: 科目
    - type: 问题类型
    - title: 题干
    - creator_id: 创建人ID
    - options: 选项列表（可选）
    - images: 图片列表（可选）
    - audios: 音频列表（可选）
    - videos: 视频列表（可选）
    """
    try:
        data = request.get_json()

        # 验证必需字段
        required_fields = ['subject', 'type', 'title', 'creator_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必需字段: {field}'}), 400

        # 验证创建人是否存在
        if not validate_creator_exists(data['creator_id']):
            return jsonify({'error': '创建人不存在'}), 400

        # 创建问题
        question = create_question(
            subject=data['subject'],
            type=data['type'],
            title=data['title'],
            creator_id=data['creator_id'],
            options=data.get('options'),
            images=data.get('images'),
            audios=data.get('audios'),
            videos=data.get('videos')
        )

        # 保存到数据库
        created_question = question_dao.create(question)

        logger.info(f"创建问题成功: {created_question.id}")
        return jsonify({
            'code': 0,
            'message': '问题创建成功',
            'question': question_to_response(created_question)
        }), 201

    except Exception as e:
        logger.error(f"创建问题失败: {e}")
        return jsonify({'error': f'创建问题失败: {str(e)}'}), 500


@question_bp.route('/<question_id>', methods=['GET'])
@require_auth
def get_question_api(question_id):
    """
    根据ID获取问题详情

    路径参数:
    - question_id: 问题ID
    """
    try:
        question = question_dao.get_by_id(question_id)
        if not question:
            return jsonify({'error': '问题不存在'}), 404

        return jsonify({
            'code': 0,
            'message': '获取问题详情成功',
            'question': question_to_response(question)
        }), 200

    except Exception as e:
        logger.error(f"获取问题失败: {e}")
        return jsonify({'error': f'获取问题失败: {str(e)}'}), 500


@question_bp.route('/<question_id>', methods=['PUT'])
@require_auth
def update_question_api(question_id):
    """
    更新问题信息

    路径参数:
    - question_id: 问题ID

    请求参数:
    - subject: 科目（可选）
    - type: 问题类型（可选）
    - title: 题干（可选）
    - options: 选项列表（可选）
    - images: 图片列表（可选）
    - audios: 音频列表（可选）
    - videos: 视频列表（可选）
    - is_active: 是否激活（可选）
    """
    try:
        data = request.get_json()

        # 获取现有问题
        question = question_dao.get_by_id(question_id)
        if not question:
            return jsonify({'error': '问题不存在'}), 404

        # 更新字段
        if 'subject' in data:
            question.subject = data['subject']
        if 'type' in data:
            question.type = data['type']
        if 'title' in data:
            question.title = data['title']
        if 'options' in data:
            question.options = ",".join(data['options']) if data['options'] else None
        if 'images' in data:
            question.images = ",".join(data['images']) if data['images'] else None
        if 'audios' in data:
            question.audios = ",".join(data['audios']) if data['audios'] else None
        if 'videos' in data:
            question.videos = ",".join(data['videos']) if data['videos'] else None
        if 'is_active' in data:
            question.is_active = data['is_active']

        # 保存更新
        updated_question = question_dao.update(question)

        logger.info(f"更新问题成功: {updated_question.id}")
        return jsonify({
            'code': 0,
            'message': '问题更新成功',
            'question': question_to_response(updated_question)
        }), 200

    except Exception as e:
        logger.error(f"更新问题失败: {e}")
        return jsonify({'error': f'更新问题失败: {str(e)}'}), 500


@question_bp.route('/<question_id>', methods=['DELETE'])
@require_auth
def delete_question_api(question_id):
    """
    删除问题（软删除）

    路径参数:
    - question_id: 问题ID
    """
    try:
        # 获取问题
        question = question_dao.get_by_id(question_id)
        if not question:
            return jsonify({'error': '问题不存在'}), 404

        # 软删除
        question_dao.delete(question)

        logger.info(f"删除问题成功: {question_id}")
        return jsonify({
            'code': 0,
            'message': '问题删除成功',
            'question_id': question_id
        }), 200

    except Exception as e:
        logger.error(f"删除问题失败: {e}")
        return jsonify({'error': f'删除问题失败: {str(e)}'}), 500


@question_bp.route('/list', methods=['GET'])
@require_auth
def list_questions_api():
    """
    获取问题列表，支持筛选和分页

    查询参数:
    - subject: 科目筛选（可选）
    - type: 问题类型筛选（可选）
    - creator_id: 创建人ID筛选（可选）
    - is_active: 是否激活筛选（可选）
    - page: 页码，默认1
    - size: 每页数量，默认10
    """
    try:
        # 获取查询参数
        subject = request.args.get('subject')
        question_type = request.args.get('type')
        creator_id = request.args.get('creator_id')
        is_active = request.args.get('is_active')
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))

        # 计算分页参数
        skip = (page - 1) * size
        limit = size

        # 构建筛选条件
        filters = {}
        if subject is not None:
            filters["subject"] = subject
        if question_type is not None:
            filters["type"] = question_type
        if creator_id is not None:
            filters["creator_id"] = creator_id
        if is_active is not None:
            filters["is_active"] = is_active.lower() == 'true'

        # 查询问题列表
        questions = question_dao.search_by_kwargs(filters, skip=skip, limit=limit)

        # 统计总数
        total = question_dao.count_by_kwargs(filters)

        # 转换为响应格式
        question_responses = [question_to_response(q) for q in questions]

        return jsonify({
            'code': 0,
            'message': '获取问题列表成功',
            'data': {
                'questions': question_responses,
                'total': total,
                'page': page,
                'size': size,
                'pages': (total + size - 1) // size
            }
        }), 200

    except Exception as e:
        logger.exception(f"获取问题列表失败: {e}")
        return jsonify({'error': f'获取问题列表失败: {str(e)}'}), 500


@question_bp.route('/batch', methods=['POST'])
@require_auth
def batch_create_questions_api():
    """
    批量创建问题

    请求参数:
    - questions: 问题列表
    """
    try:
        data = request.get_json()

        if not data.get('questions'):
            return jsonify({'error': '缺少问题列表'}), 400

        created_questions = []
        errors = []
        created_count = 0
        failed_count = 0

        for question_data in data['questions']:
            try:
                # 验证必需字段
                required_fields = ['subject', 'type', 'title', 'creator_id']
                for field in required_fields:
                    if not question_data.get(field):
                        errors.append(f'缺少必需字段: {field}')
                        failed_count += 1
                        continue

                # 验证创建人是否存在
                if not validate_creator_exists(question_data['creator_id']):
                    errors.append(f"创建人不存在: {question_data['creator_id']}")
                    failed_count += 1
                    continue

                # 创建问题
                question = create_question(
                    subject=question_data['subject'],
                    type=question_data['type'],
                    title=question_data['title'],
                    creator_id=question_data['creator_id'],
                    options=question_data.get('options'),
                    images=question_data.get('images'),
                    audios=question_data.get('audios'),
                    videos=question_data.get('videos')
                )

                # 保存到数据库
                created_question = question_dao.create(question)
                created_questions.append(created_question)
                created_count += 1

                logger.info(f"批量创建问题成功: {created_question.id}")

            except Exception as e:
                error_msg = f"创建问题失败: {str(e)}"
                errors.append(error_msg)
                failed_count += 1
                logger.error(f"批量创建问题失败: {error_msg}")

        # 转换为响应格式
        question_responses = [question_to_response(q) for q in created_questions]

        return jsonify({
            'code': 0,
            'message': '批量创建问题完成',
            'data': {
                'created_count': created_count,
                'failed_count': failed_count,
                'questions': question_responses,
                'errors': errors
            }
        }), 200

    except Exception as e:
        logger.error(f"批量创建问题失败: {e}")
        return jsonify({'error': f'批量创建问题失败: {str(e)}'}), 500

