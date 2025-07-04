from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, update
from entity.question import Question
from dao.database import get_engine
from dao.base_dao import BaseDao
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class QuestionDAO(BaseDao):
    def get_by_id(self, id: str) -> Optional[Question]:
        return self._get_by_id(Question, id)

    def search_by_kwargs(self, kwargs: dict, skip: int = 0, limit: int = 100) -> List[Question]:
        return self._search_by_kwargs(Question, kwargs, skip, limit)

    def count_by_kwargs(self, kwargs: dict) -> int:
        return self._count_by_kwargs(Question, kwargs)

# 全局DAO实例
question_dao = QuestionDAO()