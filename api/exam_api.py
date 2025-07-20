"""
考试API模块 - 处理考试相关的HTTP请求
"""

from flask import Blueprint, request, jsonify
from entity.exam import Exam, ExamStatus, create_exam
from dao.question_dao import question_dao
from dao.exam_dao import exam_dao
from utils.jwt_utils import require_auth, get_current_user_id
import json
import logging

logger = logging.getLogger(__name__)

exam_bp = Blueprint('exam', __name__, url_prefix='/exam')


@exam_bp.route('/create', methods=['POST'])
@require_auth
def create_exam_api():
    """创建考试"""
    try:
        data = request.get_json()

        # 验证必需字段
        required_fields = ['goal_id', 'examinee_id', 'question_ids', 'plan_starttime', 'plan_duration']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必需字段: {field}'}), 400

        # 创建考试
        exam = create_exam(**data)

        # 保存到数据库
        saved_exam = exam_dao.create(exam)
        print(saved_exam.to_dict())

        return jsonify({
            'code': 0,
            'message': '考试创建成功',
            'data': saved_exam.to_dict()
        }), 201

    except Exception as e:
        logger.exception(f"创建考试失败: {e}")
        return jsonify({'error': '创建考试失败，请稍后重试'}), 500


@exam_bp.route('/finish', methods=['POST'])
@require_auth
def finish_exam():
    """提交考试答卷（只能修改answer_json字段）"""
    data = request.get_json()
    # 验证必需字段
    required_fields = ['id', 'answer_json']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'缺少必需字段: {field}'}), 400

    exam_id = data.get('id')
    answer_json = data.get('answer_json')
    try:
        # 验证考试是否存在
        exam = exam_dao.get_by_id(exam_id)
        if not exam:
            return jsonify({'error': '考试不存在'}), 404

        # 解析答卷数据
        # try:
        #     answer = Answer(**answer_json)
        # except Exception as e:
        #     logger.exception(f"答卷数据格式错误: {e}")
        #     return jsonify({'error': f'答卷数据格式错误'}), 400

        # 更新答案
        exam.answer_json = json.dumps(answer_json)
        exam.status = ExamStatus.completed
        updated_exam = exam_dao.update(exam)

        return jsonify({
            'code': 0,
            'message': '答卷更新成功',
            'exam': updated_exam.to_dict()
        }), 200

    except Exception as e:
        logger.exception(f"更新考试答卷失败: {e}")
        return jsonify({'error': '更新答卷失败，请稍后重试'}), 500


@exam_bp.route('/delete', methods=['DELETE'])
@require_auth
def delete_exam():
    """删除考试（软删除）"""
    exam_id = request.args.get('id')
    try:
        # 验证考试是否存在
        exam = exam_dao.get_by_id(exam_id)
        if not exam:
            return jsonify({'error': '考试不存在'}), 404

        # 软删除
        exam.is_deleted = True
        exam_dao.update(exam)

        return jsonify({
            'code': 0,
            'message': '考试删除成功'
        }), 200

    except Exception as e:
        logger.exception(f"删除考试失败: {e}")
        return jsonify({'error': '删除考试失败，请稍后重试'}), 500


@exam_bp.route('/get', methods=['GET'])
@require_auth
def get_exam():
    exam_id = request.args.get('id')  # 小于某时间
    """获取单个考试详情"""
    try:
        # 获取考试详细信息
        exam = exam_dao.get_by_id(exam_id)
        if not exam:
            return jsonify({'error': '考试不存在'}), 404

        # 构建返回数据
        exam_data = exam.to_dict()
        if exam.question_ids and len(exam.question_ids) > 0:
            question_id_list = exam.question_ids.split(',')
            exam_data['questions'] = [q.to_dict() for q in question_dao.search_by_kwargs({'id': {'$in': question_id_list}}) ]

        return jsonify({
            'code': 0,
            'message': '获取考试详情成功',
            'data': exam_data
        }), 200

    except Exception as e:
        logger.exception(f"获取考试详情失败: {e}")
        return jsonify({'error': '获取考试详情失败，请稍后重试'}), 500


@exam_bp.route('/list', methods=['GET'])
@require_auth
def list_exams():
    """获取考试列表"""
    try:
        # 获取查询参数
        plan_starttime_from = request.args.get('plan_starttime_from')  # 大于某时间
        plan_starttime_to = request.args.get('plan_starttime_to')  # 小于某时间
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))

        # 计算分页参数
        skip = (page - 1) * size
        limit = size

        # 构建查询条件
        kwargs = {'is_deleted': False, 'examinee_id': get_current_user_id()}
        
        # 添加时间过滤条件
        if plan_starttime_from:
            kwargs['plan_starttime'] = {"$gte": plan_starttime_from}
        if plan_starttime_to:
            kwargs['plan_starttime'] = {"$lte": plan_starttime_to}

        # 查询考试列表
        exams = exam_dao.search_by_kwargs(kwargs, skip, limit)
        total = exam_dao.count_by_kwargs(kwargs)

        # 转换为字典格式
        exam_list = [exam.to_dict() for exam in exams]

        return jsonify({
            'code': 0,
            'message': '获取考试列表成功',
            'data': {
                'exams': exam_list,
                'total': total,
                'page': page,
                'size': size,
                'pages': (total + size - 1) // size
            }
        }), 200

    except Exception as e:
        logger.exception(f"获取考试列表失败: {e}")
        return jsonify({'error': '获取考试列表失败，请稍后重试'}), 500

