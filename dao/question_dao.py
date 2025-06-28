from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, update
from entity.question import Question
from dao.database import get_engine
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class QuestionDAO:
    def __init__(self):
        self.engine = get_engine()

    def create_question(self, question: Question) -> Question:
        try:
            with Session(self.engine) as session:
                session.add(question)
                session.commit()
                session.refresh(question)
                return question
        except Exception as e:
            logger.error(f"创建问题失败: {e}")
            raise

    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        try:
            with Session(self.engine) as session:
                statement = select(Question).where(Question.id == question_id, Question.is_deleted == False)
                return session.exec(statement).first()
        except Exception as e:
            logger.error(f"获取问题失败: {e}")
            raise

    def search_questions_by_creator_id(self, creator_id: str, skip: int = 0, limit: int = 100) -> List[Question]:
        try:
            with Session(self.engine) as session:
                statement = select(Question).where(Question.is_deleted == False, Question.creator_id == creator_id).offset(skip).limit(limit)
                return session.exec(statement).all()
        except Exception as e:
            logger.error(f"获取问题列表失败: {e}")
            raise

    def update_question(self, question_id: str, update_data: Dict[str, Any]) -> Optional[Question]:
        try:
            with Session(self.engine) as session:
                update_data['updated_at'] = datetime.now()
                statement = (
                    update(Question)
                    .where(Question.id == question_id, Question.is_deleted == False)
                    .values(**update_data)
                )
                session.exec(statement)
                session.commit()
                return self.get_question_by_id(question_id)
        except Exception as e:
            logger.error(f"更新问题失败: {e}")
            raise

    def delete_question(self, question_id: str) -> bool:
        try:
            with Session(self.engine) as session:
                statement = (
                    update(Question)
                    .where(Question.id == question_id)
                    .values(is_deleted=True, updated_at=datetime.now())
                )
                session.exec(statement)
                session.commit()
                return True
        except Exception as e:
            logger.error(f"删除问题失败: {e}")
            raise

# 全局DAO实例
question_dao = QuestionDAO()