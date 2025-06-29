"""
试卷数据访问对象 (DAO) - 处理试卷相关的数据库操作
"""

from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, update, delete
from sqlalchemy import func
from dao.base_dao import BaseDao
from dao.database import get_engine
from dao.question_dao import question_dao
from entity.paper import Paper
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PaperDAO(BaseDao):
    """试卷数据访问对象"""

    def create(self, paper: Paper) -> Paper:
        """创建试卷"""
        try:
            with Session(self.engine) as session:
                session.add(paper)
                session.commit()
                session.refresh(paper)
                logger.info(f"创建试卷成功: {paper.id}")
                return paper
        except Exception as e:
            logger.error(f"创建试卷失败: {e}")
            raise

    def update(self, paper: Paper) -> Paper:
        """更新试卷"""
        try:
            with Session(self.engine) as session:
                session.add(paper)
                session.commit()
                session.refresh(paper)
                logger.info(f"更新试卷成功: {paper.id}")
                return paper
        except Exception as e:
            logger.error(f"更新试卷失败: {e}")
            raise

    def delete(self, paper: Paper) -> Paper:
        """删除试卷"""
        try:
            with Session(self.engine) as session:
                session.delete(paper)
                session.commit()
                logger.info(f"删除试卷成功: {paper.id}")
                return paper
        except Exception as e:
            logger.error(f"删除试卷失败: {e}")
            raise

    def get_by_id(self, paper_id: str) -> Optional[Paper]:
        """根据ID获取试卷"""
        return self._get_by_id(Paper, paper_id)

    def search_by_kwargs(self, kwargs: dict, skip: int = 0, limit: int = 100) -> List[Paper]:
        """根据关键字搜索试卷"""
        return self._search_by_kwargs(Paper, kwargs, skip, limit)

    def count_by_kwargs(self, kwargs: dict) -> int:
        """根据关键字统计试卷数量"""
        return self._count_by_kwargs(Paper, kwargs)

    def get_paper_with_questions(self, paper_id: str) -> Optional[Paper]:
        """根据ID获取试卷并加载问题列表"""
        try:
            paper = self.get_by_id(paper_id)
            if paper:
                # 加载问题列表
                questions = []
                for qid in paper.question_ids:
                    question = question_dao.get_by_id(qid)
                    if question:
                        questions.append(question)
                paper._questions = questions
            return paper
        except Exception as e:
            logger.error(f"获取试卷及问题失败 (ID: {paper_id}): {e}")
            raise


# 创建全局DAO实例
paper_dao = PaperDAO()
