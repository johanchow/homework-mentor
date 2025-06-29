"""
数据访问对象 (DAO) 包
"""

from .user_dao import UserDAO, user_dao
from .question_dao import QuestionDAO, question_dao
from .paper_dao import PaperDAO, paper_dao

__all__ = ['UserDAO', 'user_dao', 'QuestionDAO', 'question_dao', 'PaperDAO', 'paper_dao']
