"""
用户API模块 - 处理用户相关的HTTP请求
"""

from flask import Blueprint, request, jsonify
from entity.user import User, create_user
from dao.user_dao import user_dao
from utils.jwt_utils import generate_token, require_auth, get_current_user_id
import logging

logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        mode = data.get('mode')
        if mode != 'name' and mode != 'phone':
            return jsonify({'error': '无效的注册模式'}), 400

        # 验证必需字段
        required_fields = ['name', 'password'] if mode == 'name' else ['phone', 'verify_code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必需字段: {field}'}), 400

        name, password, phone = None, None, None
        if mode == 'name':
            name = data.get('name')
            password = data.get('password')
            # 验证密码长度
            if len(password) < 8:
                return jsonify({'error': '密码长度至少8位'}), 400
            if user_dao.get_by_name(name) is not None:
                return jsonify({'error': '用户名已被注册'}), 409
        else:
            phone = data.get('phone')
            verify_code = data.get('verify_code')
            # 检查手机号是否已存在（如果提供）
            if user_dao.get_by_phone(phone) is not None:
                return jsonify({'error': '手机号已被注册'}), 409

        # 创建用户
        user = create_user(
            name=name,
            password=password,
            phone=phone,
        )

        # 保存到数据库
        saved_user = user_dao.create(user)

        # 生成token
        token = generate_token(saved_user.id, saved_user.name)

        return jsonify({
            'code': 0,
            'message': '注册成功',
            'data': {
                'user': saved_user.to_dict(),
                'token': token
            }
        }), 201

    except Exception as e:
        logger.exception(f"用户注册失败: {e}")
        return jsonify({'error': '注册失败，请稍后重试'}), 500


@user_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        mode = data.get('mode')
        if mode != 'name' and mode != 'phone':
            return jsonify({'error': '无效的登录模式'}), 400

        # 验证必需字段
        required_fields = ['name', 'password'] if mode == 'name' else ['phone', 'verify_code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必需字段: {field}'}), 400

        if mode == 'name':
            name = data.get('name')
            password = data.get('password')
            user = user_dao.authenticate_user_by_name(name, password)
        else:
            phone = data.get('phone')
            verify_code = data.get('verify_code')
            user = user_dao.authenticate_user_by_phone(phone, verify_code)

        if not user:
            error_message = '用户名或密码错误' if mode == 'name' else '手机号或验证码错误'
            return jsonify({'error': error_message}), 401

        # 生成token
        token = generate_token(user.id, user.name)

        return jsonify({
            'code': 0,
            'message': '登录成功',
            'data': {
                'user': user.to_dict(),
                'token': token
            }
        }), 200

    except Exception as e:
        logger.error(f"用户登录失败: {e}")
        return jsonify({'error': '登录失败，请稍后重试'}), 500


@user_bp.route('/profile', methods=['GET'])
@require_auth
def get_user_profile():
    """获取当前用户信息"""
    try:
        user_id = get_current_user_id()
        user = user_dao.get_by_id(user_id)

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        return jsonify({
            'code': 0,
            'message': '获取用户信息成功',
            'data': user.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        return jsonify({'error': '获取用户信息失败'}), 500


@user_bp.route('/check-phone', methods=['POST'])
def check_phone_exists():
    """检查手机号是否已存在"""
    try:
        data = request.get_json()

        if not data.get('phone'):
            return jsonify({'error': '缺少手机号'}), 400

        phone = data.get('phone')
        exists = user_dao.check_phone_exists(phone)

        return jsonify({
            'code': 0,
            'message': '检查手机号成功',
            'data': {
                'exists': exists
            }
        }), 200

    except Exception as e:
        logger.error(f"检查手机号失败: {e}")
        return jsonify({'error': '检查失败，请稍后重试'}), 500


@user_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """用户登出（客户端删除token即可）"""
    return jsonify({
        'code': 0,
        'message': '登出成功'
    }), 200
