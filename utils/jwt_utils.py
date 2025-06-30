"""
JWT工具模块 - 处理token的生成和验证
"""

import jwt
import datetime
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

# JWT配置
JWT_SECRET_KEY = "your-secret-key-here"  # 在生产环境中应该从环境变量获取
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7天


def generate_token(user_id: str, user_email: str) -> str:
    """生成JWT token"""
    try:
        payload = {
            'user_id': user_id,
            'email': user_email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    except Exception as e:
        logger.error(f"生成token失败: {e}")
        raise


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """验证JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token已过期")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"无效的token: {e}")
        return None
    except Exception as e:
        logger.error(f"验证token失败: {e}")
        return None


def get_token_from_header() -> Optional[str]:
    """从请求头中获取token"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None


def require_auth(f):
    """认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()

        if not token:
            return jsonify({'error': '缺少认证token'}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({'error': '无效或过期的token'}), 401

        # 将用户信息添加到请求上下文
        request.user_id = payload.get('user_id')
        request.user_email = payload.get('email')

        return f(*args, **kwargs)

    return decorated_function


def get_current_user_id() -> Optional[str]:
    """获取当前用户ID"""
    return getattr(request, 'user_id', None)

