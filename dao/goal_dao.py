from typing import List, Optional, Dict, Any
from sqlmodel import select, update
from entity.goal import Goal
from dao.base_dao import BaseDao
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GoalDAO(BaseDao):
    async def get_by_id(self, id: str) -> Optional[Goal]:
        return await self._get_by_id(Goal, id)

    async def search_by_kwargs(self, kwargs: dict, skip: int = 0, limit: int = 100) -> List[Goal]:
        return await self._search_by_kwargs(Goal, kwargs, skip, limit)

    async def count_by_kwargs(self, kwargs: dict) -> int:
        return await self._count_by_kwargs(Goal, kwargs)

# 全局DAO实例
goal_dao = GoalDAO()
