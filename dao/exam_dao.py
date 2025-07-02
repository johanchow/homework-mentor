"""
考试数据访问对象 (DAO) - 处理考试相关的数据库操作
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, update, delete
from dao.base_dao import BaseDao
from entity.exam import Exam, Answer
from entity.paper import Paper
from entity.user import User
import json

logger = logging.getLogger(__name__)


class ExamDAO(BaseDao):
    """考试数据访问对象"""

    def get_by_id(self, exam_id: str) -> Optional[Exam]:
        """根据ID获取考试"""
        return self._get_by_id(Exam, exam_id)

    def search_by_kwargs(self, kwargs: dict, skip: int = 0, limit: int = 100) -> List[Exam]:
        """根据关键字搜索考试"""
        return self._search_by_kwargs(Exam, kwargs, skip, limit)

    def count_by_kwargs(self, kwargs: dict) -> int:
        """根据关键字统计考试数量"""
        return self._count_by_kwargs(Exam, kwargs)

    def list_exams_by_paper_id(self, paper_id: str, skip: int = 0, limit: int = 100) -> List[Exam]:
        """根据试卷ID获取考试列表"""
        return self.search_by_kwargs({"paper_id": paper_id}, skip, limit)

    def list_exams_by_examinee_id(self, examinee_id: str, skip: int = 0, limit: int = 100) -> List[Exam]:
        """根据考生ID获取考试列表"""
        return self.search_by_kwargs({"examinee_id": examinee_id}, skip, limit)

    def get_exam_with_details(self, exam_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取考试详细信息（包括试卷和考生信息）"""
        try:
            exam = self.get_by_id(exam_id)
            if not exam:
                return None

            # 获取试卷信息
            from dao.paper_dao import paper_dao
            paper = paper_dao.get_by_id(exam.paper_id)

            # 获取考生信息
            from dao.user_dao import user_dao
            examinee = user_dao.get_by_id(exam.examinee_id)

            # 解析答卷
            answer = exam.get_answer()

            return {
                "exam": exam,
                "paper": paper,
                "examinee": examinee,
                "answer": answer
            }
        except Exception as e:
            logger.error(f"获取考试详细信息失败 (ID: {exam_id}): {e}")
            raise

# 创建全局DAO实例
exam_dao = ExamDAO()
