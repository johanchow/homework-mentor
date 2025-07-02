"""
试卷API - 提供试卷相关的RESTful接口
"""

from flask import Blueprint, request, jsonify
from typing import List, Optional
import logging
from entity.paper import Paper, create_paper
from entity.question import Question
from dao.paper_dao import paper_dao
from dao.user_dao import user_dao
from dao.question_dao import question_dao
from utils.jwt_utils import require_auth
from .question_api import question_to_response

logger = logging.getLogger(__name__)

paper_bp = Blueprint('paper', __name__, url_prefix='/paper')


# # 工具函数
# def question_to_response(question: Question) -> dict:
#     """将Question实体转换为响应格式"""
#     return {
#         "id": question.id,
#         "subject": question.subject,
#         "type": question.type,
#         "title": question.title,
#         "options": question.options,
#         "images": question.images,
#         "audios": question.audios,
#         "videos": question.videos,
#         "creator_id": question.creator_id,
#         "created_at": question.created_at.isoformat(),
#         "updated_at": question.updated_at.isoformat(),
#         "is_active": question.is_active,
#         "is_deleted": question.is_deleted
#     }


def paper_to_response(paper: Paper) -> dict:
    """将Paper实体转换为响应格式"""
    return {
        "id": paper.id,
        "title": paper.title,
        "description": paper.description,
        "question_ids": paper.question_ids.split(',') if paper.question_ids else [],
        "creator_id": paper.creator_id,
        "created_at": paper.created_at.isoformat(),
        "updated_at": paper.updated_at.isoformat(),
        "is_deleted": paper.is_deleted
    }


def paper_to_detail_response(paper: Paper) -> dict:
    """将Paper实体转换为详情响应格式"""
    # 获取创建人信息
    creator_name = None
    if paper.creator_id:
        creator = user_dao.get_by_id(paper.creator_id)
        if creator:
            creator_name = creator.name

    # 获取问题列表
    questions = []
    if paper.question_ids:
        question_id_list = [qid.strip() for qid in paper.question_ids.split(',') if qid.strip()]
        for qid in question_id_list:
            question = question_dao.get_by_id(qid)
            if question:
                questions.append(question_to_response(question))

    return {
        "id": paper.id,
        "title": paper.title,
        "description": paper.description,
        "question_ids": paper.question_ids,
        "questions": questions,
        "creator_id": paper.creator_id,
        "creator_name": creator_name,
        "created_at": paper.created_at.isoformat(),
        "updated_at": paper.updated_at.isoformat(),
        "is_deleted": paper.is_deleted
    }


def validate_creator_exists(creator_id: str) -> bool:
    """验证创建人是否存在"""
    creator = user_dao.get_by_id(creator_id)
    return creator is not None


def validate_questions_exist(question_ids: List[str]) -> bool:
    """验证问题是否都存在"""
    if not question_ids:
        return True

    for qid in question_ids:
        question = question_dao.get_by_id(qid)
        if not question:
            return False
    return True


# API接口

@paper_bp.route('/create', methods=['POST'])
@require_auth
def create_paper_api():
    """
    创建试卷

    请求参数:
    - title: 试卷标题
    - description: 试卷描述（可选）
    - creator_id: 创建人ID
    - question_ids: 问题ID列表（可选）
    """
    try:
        data = request.get_json()

        # 验证必需字段
        required_fields = ['title', 'creator_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必需字段: {field}'}), 400

        # 验证创建人是否存在
        if not validate_creator_exists(data['creator_id']):
            return jsonify({'error': '创建人不存在'}), 400

        # 验证问题是否都存在
        question_ids = data.get('question_ids')
        if question_ids and not validate_questions_exist(question_ids):
            return jsonify({'error': '部分问题不存在'}), 400

        # 创建试卷
        paper = create_paper(
            title=data['title'],
            description=data.get('description'),
            creator_id=data['creator_id'],
            question_ids=question_ids
        )

        # 保存到数据库
        created_paper = paper_dao.create(paper)

        logger.info(f"创建试卷成功: {created_paper.id}")
        return jsonify({
            'code': 0,
            'message': '试卷创建成功',
            'paper': paper_to_response(created_paper)
        }), 201

    except Exception as e:
        logger.error(f"创建试卷失败: {e}")
        return jsonify({'error': f'创建试卷失败: {str(e)}'}), 500


@paper_bp.route('/<paper_id>', methods=['GET'])
@require_auth
def get_paper_api(paper_id):
    """
    根据ID获取试卷详情（包含问题信息）

    路径参数:
    - paper_id: 试卷ID
    """
    try:
        paper = paper_dao.get_by_id(paper_id)
        if not paper:
            return jsonify({'error': '试卷不存在'}), 404

        return jsonify({
            'code': 0,
            'message': '获取试卷详情成功',
            'paper': paper_to_detail_response(paper)
        }), 200

    except Exception as e:
        logger.error(f"获取试卷失败: {e}")
        return jsonify({'error': f'获取试卷失败: {str(e)}'}), 500


@paper_bp.route('/list', methods=['GET'])
@require_auth
def list_papers_api():
    """
    获取试卷列表，支持筛选和分页

    查询参数:
    - creator_id: 创建人ID筛选（可选）
    - page: 页码，默认1
    - size: 每页数量，默认10
    """
    try:
        # 获取查询参数
        creator_id = request.args.get('creator_id')
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))

        # 计算分页参数
        skip = (page - 1) * size
        limit = size

        # 构建筛选条件
        filters = {}
        if creator_id is not None:
            filters["creator_id"] = creator_id

        # 查询试卷列表
        papers = paper_dao.search_by_kwargs(filters, skip=skip, limit=limit)

        # 统计总数
        total = paper_dao.count_by_kwargs(filters)

        # 转换为响应格式
        paper_responses = [paper_to_response(p) for p in papers]

        return jsonify({
            'code': 0,
            'message': '获取试卷列表成功',
            'data': {
                'papers': paper_responses,
                'total': total,
                'page': page,
                'size': size,
                'pages': (total + size - 1) // size
            }
        }), 200

    except Exception as e:
        logger.error(f"获取试卷列表失败: {e}")
        return jsonify({'error': f'获取试卷列表失败: {str(e)}'}), 500


@paper_bp.route('/<paper_id>', methods=['DELETE'])
@require_auth
def delete_paper_api(paper_id):
    """
    删除试卷（软删除）

    路径参数:
    - paper_id: 试卷ID
    """
    try:
        # 获取试卷
        paper = paper_dao.get_by_id(paper_id)
        if not paper:
            return jsonify({'error': '试卷不存在'}), 404

        # 软删除
        paper_dao.delete(paper)

        logger.info(f"删除试卷成功: {paper_id}")
        return jsonify({
            'code': 0,
            'message': '试卷删除成功',
            'paper_id': paper_id
        }), 200

    except Exception as e:
        logger.error(f"删除试卷失败: {e}")
        return jsonify({'error': f'删除试卷失败: {str(e)}'}), 500

