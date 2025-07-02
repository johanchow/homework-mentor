from typing import List, Optional, Dict
from sqlmodel import Field
from entity.base import BaseModel
from entity.question import Question
from entity.message import Message, create_message

class Answer(BaseModel):
    """答卷实体类"""
    # 问题
    question: List[Question] = Field(..., description="问题列表")
    # 对话信息
    messages: Dict[str, List[Message]] = Field(..., description="对话信息")
    # 答案
    answer: Dict[str, str] | None = Field(default=None, description="答案")

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "question": [q.to_dict() for q in self.question],
            "messages": {k: [m.to_dict() for m in v] for k, v in self.messages.items()},
            "answer": self.answer
        }

