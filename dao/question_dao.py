from typing import List, Optional, Dict, Any
from sqlmodel import select, update
from entity.question import Question
from dao.base_dao import BaseDao
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class QuestionDAO(BaseDao):
    async def get_by_id(self, id: str) -> Optional[Question]:
        return await self._get_by_id(Question, id)

    async def search_by_kwargs(self, kwargs: dict, skip: int = 0, limit: int = 100) -> List[Question]:
        # 定义需要模糊匹配的字段
        return await self._search_by_kwargs(Question, kwargs, skip, limit)

    async def count_by_kwargs(self, kwargs: dict) -> int:
        # 定义需要模糊匹配的字段
        return await self._count_by_kwargs(Question, kwargs)

# 全局DAO实例
question_dao = QuestionDAO()