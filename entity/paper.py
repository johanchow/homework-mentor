"""
试卷实体类 - 定义试卷的基本结构和属性
"""

from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from .question import Question
from .user import User


class Paper(BaseModel):
    """试卷实体类"""
    
    # 基本信息
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="试卷唯一标识")
    title: str = Field(..., description="试卷标题")
    description: Optional[str] = Field(None, description="试卷描述")
    
    # 问题列表
    questions: List[Question] = Field(default_factory=list, description="问题列表")
    
    # 创建人信息
    creator: User = Field(..., description="创建人")
    
    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # 状态信息
    is_deleted: bool = Field(default=False, description="是否已删除")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_question(self, question: Question) -> None:
        """添加问题到试卷"""
        self.questions.append(question)
        self.updated_at = datetime.now()
    
    def remove_question(self, question_id: str) -> bool:
        """从试卷中移除问题"""
        for i, question in enumerate(self.questions):
            if question.id == question_id:
                self.questions.pop(i)
                self.updated_at = datetime.now()
                return True
        return False
    
    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """根据ID获取问题"""
        for question in self.questions:
            if question.id == question_id:
                return question
        return None
    
    def get_questions_by_subject(self, subject: str) -> List[Question]:
        """根据科目获取问题列表"""
        return [q for q in self.questions if q.subject == subject]
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Paper':
        """从字典创建试卷实例"""
        return cls(**data)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Paper(id={self.id}, title='{self.title}', questions={len(self.questions)})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()
