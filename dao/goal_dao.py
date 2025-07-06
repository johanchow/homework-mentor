from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, update
from entity.goal import Goal
from dao.database import get_engine
from dao.base_dao import BaseDao
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GoalDAO(BaseDao):
    def get_by_id(self, id: str) -> Optional[Goal]:
        return self._get_by_id(Goal, id)

    def search_by_kwargs(self, kwargs: dict, skip: int = 0, limit: int = 100) -> List[Goal]:
        # 定义需要模糊匹配的字段
        fuzzy_fields = ['name']
        return self._search_by_kwargs(Goal, kwargs, skip, limit, fuzzy_fields)

    def count_by_kwargs(self, kwargs: dict) -> int:
        # 定义需要模糊匹配的字段
        fuzzy_fields = ['name']
        return self._count_by_kwargs(Goal, kwargs, fuzzy_fields)

# 全局DAO实例
goal_dao = GoalDAO()
