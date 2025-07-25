"""
用户数据访问对象 (DAO) - 处理用户相关的数据库操作 - 异步版本
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import select, update, delete
from dao.base_dao import BaseDao
from entity.user import User

logger = logging.getLogger(__name__)


class UserDAO(BaseDao):
    """用户数据访问对象"""
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        return await self._get_by_id(User, user_id)

    async def search_by_kwargs(self, kwargs: dict, skip: int = 0, limit: int = 100) -> List[User]:
        """搜索用户"""
        return await self._search_by_kwargs(User, kwargs, skip, limit)

    async def count_by_kwargs(self, kwargs: dict) -> int:
        return await self._count_by_kwargs(User, kwargs)

    async def get_by_name(self, name: str) -> Optional[User]:
        """根据用户名获取用户"""
        try:
            session_maker = await self._get_session_maker()
            async with session_maker() as session:
                statement = select(User).where(User.name == name, User.is_deleted == False)
                result = await session.execute(statement)
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"根据用户名获取用户失败 (name: {name}): {e}")
            raise

    async def get_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        try:
            session_maker = await self._get_session_maker()
            async with session_maker() as session:
                statement = select(User).where(User.phone == phone, User.is_deleted == False)
                result = await session.execute(statement)
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"根据手机号获取用户失败 (phone: {phone}): {e}")
            raise

    async def authenticate_user_by_name(self, name: str, password: str) -> Optional[User]:
        """用户认证"""
        try:
            user = await self.get_by_name(name)
            if user and user.check_password(password) and user.is_active:
                return user
            return None
        except Exception as e:
            logger.error(f"用户认证失败 (email: {name}): {e}")
            raise

    async def authenticate_user_by_phone(self, phone: str, password: str) -> Optional[User]:
        """通过手机号+验证码认证用户"""
        try:
            user = await self.get_by_phone(phone)
            if user and user.check_password(password) and user.is_active:
                return user
            return None
        except Exception as e:
            logger.error(f"用户认证失败 (phone: {phone}): {e}")
            raise


# 创建全局DAO实例
user_dao = UserDAO()
