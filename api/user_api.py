"""
用户API模块 - 处理用户相关的HTTP请求 - FastAPI异步版本
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from entity.user import User, create_user
from dao.user_dao import user_dao
from utils.jwt_utils import generate_token, verify_token, get_current_user_id
from utils.exceptions import DataNotFoundException, ValidationException, BusinessException
import logging

logger = logging.getLogger(__name__)

user_router = APIRouter(prefix="/user", tags=["用户管理"])


# 请求模型
class RegisterRequest(BaseModel):
    mode: str  # 'name' or 'phone'
    name: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    verify_code: Optional[str] = None


class LoginRequest(BaseModel):
    mode: str  # 'name' or 'phone'
    name: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    verify_code: Optional[str] = None


class CheckPhoneRequest(BaseModel):
    phone: str


# 响应模型
class UserResponse(BaseModel):
    code: int = 0
    message: str
    data: Optional[Dict[str, Any]] = None


@user_router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest):
    """用户注册"""
    try:
        mode = request.mode
        if mode != 'name' and mode != 'phone':
            raise ValidationException("mode", "无效的注册模式")

        # 验证必需字段
        if mode == 'name':
            if not request.name or not request.password:
                raise ValidationException("credentials", "用户名和密码不能为空")
            # 验证密码长度
            if len(request.password) < 8:
                raise ValidationException("password", "密码长度至少8位")
            if await user_dao.get_by_name(request.name) is not None:
                raise ValidationException("username", "用户名已被注册")
        else:
            if not request.phone or not request.verify_code:
                raise ValidationException("credentials", "手机号和验证码不能为空")
            # 检查手机号是否已存在
            if await user_dao.get_by_phone(request.phone) is not None:
                raise ValidationException("phone", "手机号已被注册")

        # 创建用户
        user = create_user(
            name=request.name,
            password=request.password,
            phone=request.phone,
        )

        # 保存到数据库
        saved_user = await user_dao.create(user)

        # 生成token
        token = generate_token(saved_user.id, saved_user.name)

        return UserResponse(
            message='注册成功',
            data={
                'user': saved_user.to_dict(),
                'token': token
            }
        )

    except BusinessException:
        raise
    except Exception as e:
        logger.exception(f"用户注册失败: {e}")
        raise HTTPException(status_code=500, detail="注册失败，请稍后重试")


@user_router.post("/login", response_model=UserResponse)
async def login(request: LoginRequest):
    """用户登录"""
    try:
        mode = request.mode
        if mode != 'name' and mode != 'phone':
            raise ValidationException("mode", "无效的登录模式")

        # 验证必需字段
        if mode == 'name':
            if not request.name or not request.password:
                raise ValidationException("credentials", "用户名和密码不能为空")
            user = await user_dao.authenticate_user_by_name(request.name, request.password)
        else:
            if not request.phone or not request.verify_code:
                raise ValidationException("credentials", "手机号和验证码不能为空")
            user = await user_dao.authenticate_user_by_phone(request.phone, request.verify_code)

        if not user:
            error_message = '用户名或密码错误' if mode == 'name' else '手机号或验证码错误'
            raise AuthenticationException(error_message)

        # 生成token
        token = generate_token(user.id, user.name)

        return UserResponse(
            message='登录成功',
            data={
                'user': user.to_dict(),
                'token': token
            }
        )

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {e}")
        raise HTTPException(status_code=500, detail="登录失败，请稍后重试")


@user_router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user_id: str = Depends(get_current_user_id)):
    """获取当前用户信息"""
    try:
        user = await user_dao.get_by_id(current_user_id)

        if not user:
            raise DataNotFoundException("用户", current_user_id)

        return UserResponse(
            message='获取用户信息成功',
            data=user.to_dict()
        )

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取用户信息失败")


@user_router.post("/check-phone", response_model=UserResponse)
async def check_phone_exists(request: CheckPhoneRequest):
    """检查手机号是否已存在"""
    try:
        exists = await user_dao.check_phone_exists(request.phone)

        return UserResponse(
            message='检查手机号成功',
            data={
                'exists': exists
            }
        )

    except Exception as e:
        logger.error(f"检查手机号失败: {e}")
        raise HTTPException(status_code=500, detail="检查失败，请稍后重试")


@user_router.post("/logout", response_model=UserResponse)
async def logout(current_user_id: str = Depends(get_current_user_id)):
    """用户登出（客户端删除token即可）"""
    return UserResponse(message='登出成功')
