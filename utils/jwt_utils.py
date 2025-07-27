"""
JWT工具模块 - 处理token的生成和验证 - FastAPI版本
"""

import jwt
import datetime
from typing import Optional, Dict, Any
from fastapi import Request
from utils.exceptions import AuthenticationException
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


def get_token_from_header(request: Request) -> Optional[str]:
    """从请求头中获取token"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None


async def get_current_user_id(request: Request) -> str:
    """获取当前用户ID - FastAPI依赖注入函数"""
    token = get_token_from_header(request)
    
    if not token:
        raise AuthenticationException("缺少认证token")
    
    payload = verify_token(token)
    if not payload:
        raise AuthenticationException("无效或过期的token")
    
    return payload.get('user_id')


async def get_current_user_payload(request: Request) -> Dict[str, Any]:
    """获取当前用户完整信息 - FastAPI依赖注入函数"""
    token = get_token_from_header(request)
    
    if not token:
        raise AuthenticationException("缺少认证token")
    
    payload = verify_token(token)
    if not payload:
        raise AuthenticationException("无效或过期的token")
    
    return payload


# 为了向后兼容，保留原有的函数名
require_auth = get_current_user_id

