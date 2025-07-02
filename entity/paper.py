"""
试卷实体类 - 定义试卷的基本结构和属性
"""

from typing import List, Optional, ClassVar
from sqlmodel import SQLModel, Field, Relationship
from entity.base import BaseModel
from datetime import datetime
from pydantic import PrivateAttr
from .question import Question
from .user import User
from utils.helpers import random_uuid


class Paper(BaseModel, table=True):
    """试卷实体类"""

    # 基本信息
    id: Optional[str] = Field(default_factory=lambda: random_uuid(), primary_key=True, description="试卷唯一标识")
    title: str = Field(..., description="试卷标题")
    description: Optional[str] = Field(default=None, description="试卷描述")

    # 问题列表
    question_ids: str = Field(default='', description="问题ID列表,以逗号分割")
    # 声明一个私有实例属性，不被 ORM、验证、导出影响，不被当成数据库字段处理
    _questions: list = PrivateAttr(default_factory=list)

    # 创建人信息
    creator_id: str = Field(..., description="创建人ID", foreign_key="user.id")
    creator: User = Relationship(back_populates="papers")

    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 状态信息
    is_deleted: bool = Field(default=False, description="是否已删除")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._questions = []

    def get_questions_list(self) -> List[Question]:
        """获取问题列表"""
        if not self.question_ids:
            return []
        if self._questions and len(self._questions) > 0:
            return self._questions
        else:
            return [Question.get_by_id(qid.strip()) for qid in self.question_ids.split(',') if qid.strip()]

# 创建试卷的工厂函数
def create_paper(
    title: str,
    creator_id: str,
    description: Optional[str] = None,
    question_ids: Optional[List[str]] = None,
) -> Paper:
    """创建试卷实例的工厂函数"""
    paper = Paper(
        title=title,
        creator_id=creator_id,
        description=description,
    )

    if question_ids:
        paper.question_ids = ','.join(question_ids)

    return paper
