"""
用户数据访问对象 (DAO) - 处理用户相关的数据库操作
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, update, delete
from dao.base_dao import BaseDao
from entity.user import User

logger = logging.getLogger(__name__)


class UserDAO(BaseDao):
    """用户数据访问对象"""
    def get_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        return self._get_by_id(User, user_id)

    def search_by_kwargs(self, kwargs: dict, skip: int = 0, limit: int = 100) -> List[User]:
        """搜索用户"""
        return self._search_by_kwargs(User, kwargs, skip, limit)

    def count_by_kwargs(self, kwargs: dict) -> int:
        return self._count_by_kwargs(User, kwargs)


# 创建全局DAO实例
user_dao = UserDAO()
