"""
考试实体类 - 定义考试的基本结构和属性
"""

import json
from datetime import datetime
from typing import Optional
from sqlmodel import Field, Relationship
from entity.base import BaseModel
from entity.message import Message
from entity.question import Question
from utils.helpers import random_uuid
from entity.answer import Answer


class Exam(BaseModel, table=True):
    """考试实体类"""

    # 基本信息
    id: Optional[str] = Field(default_factory=lambda: random_uuid(), primary_key=True, description="试卷唯一标识")

    # 试卷ID列表
    paper_id: str = Field(..., description="试卷ID", foreign_key="paper.id")

    # 参考人
    examinee_id: str = Field(..., description="参考人ID")

    # 答卷
    answer_json: str | None = Field(default=None, description="答卷json")

    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 状态信息
    is_deleted: bool = Field(default=False, description="是否已删除")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def get_answer(self) -> Answer | None:
        """获取答"""
        print(f"answer_json: {self.answer_json}")
        if self.answer_json is None:
            return None
        try:
            a = json.loads(self.answer_json)
            a['question'] = [Question.from_dict(q) for q in a['question']]
            a['messages'] = {k: [Message.from_dict(m) for m in v] for k, v in a['messages'].items()}
            return Answer(**a)
        except Exception as e:
            raise ValueError(f"答卷解析失败: {e}")


# 创建考试的工厂函数
def create_exam(
    paper_id: str,
    examinee_id: str,
    answer: Answer | None,
) -> Exam:
    """创建考试实例的工厂函数"""
    if answer is not None:
        answer_json = answer.model_dump_json()
    else:
        answer_json = None
    return Exam(
        paper_id=paper_id,
        examinee_id=examinee_id,
        answer_json=answer_json,
    )
