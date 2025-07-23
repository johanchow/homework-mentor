"""
试卷数据访问对象 (DAO) - 处理试卷相关的数据库操作 - 异步版本
"""

from typing import List, Optional, Dict, Any
from sqlmodel import select, update, delete
from sqlalchemy import func
from dao.base_dao import BaseDao
from dao.question_dao import question_dao
from entity.paper import Paper
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PaperDAO(BaseDao):
    """试卷数据访问对象"""

    async def get_by_id(self, paper_id: str) -> Optional[Paper]:
        """根据ID获取试卷"""
        return await self._get_by_id(Paper, paper_id)

    async def search_by_kwargs(self, kwargs: dict, skip: int = 0, limit: int = 100) -> List[Paper]:
        """根据关键字搜索试卷"""
        return await self._search_by_kwargs(Paper, kwargs, skip, limit)

    async def count_by_kwargs(self, kwargs: dict) -> int:
        """根据关键字统计试卷数量"""
        return await self._count_by_kwargs(Paper, kwargs)

    async def get_paper_with_questions(self, paper_id: str) -> Optional[Paper]:
        """根据ID获取试卷并加载问题列表"""
        try:
            paper = await self.get_by_id(paper_id)
            if paper:
                # 加载问题列表
                questions = []
                for qid in paper.question_ids:
                    question = await question_dao.get_by_id(qid)
                    if question:
                        questions.append(question)
                paper._questions = questions
            return paper
        except Exception as e:
            logger.error(f"获取试卷及问题失败 (ID: {paper_id}): {e}")
            raise


# 创建全局DAO实例
paper_dao = PaperDAO()
