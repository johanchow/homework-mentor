"""
考试实体类 - 定义考试的基本结构和属性
"""

import json
from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import Field, Relationship
from pydantic import PrivateAttr
from entity.base import BaseModel
from entity.message import Message
from entity.question import Question
from utils.helpers import random_uuid
from entity.answer import Answer
from utils.transformer import iso_to_mysql_datetime, mysql_datetime_to_iso

class ExamStatus(str, Enum):
    """考试状态"""
    pending = "pending"  # 待开始
    ongoing = "ongoing"  # 进行中
    completed = "completed"  # 已完成
    cancelled = "cancelled"  # 已取消

class Exam(BaseModel, table=True):
    """考试实体类"""

    # 基本信息
    id: Optional[str] = Field(default_factory=lambda: random_uuid(), primary_key=True, description="试卷唯一标识")

    # 试卷ID列表
    goal_id: str = Field(..., description="试卷ID", foreign_key="goal.id")

    # 参考人
    examinee_id: str = Field(..., description="参考人ID")

    # 问题列表
    question_ids: str = Field(default='', description="问题ID列表,以逗号分割")
    # 声明一个私有实例属性，不被 ORM、验证、导出影响，不被当成数据库字段处理
    _questions: List[Question] = PrivateAttr(default_factory=list)

    # 状态
    status: ExamStatus = Field(default=ExamStatus.pending, description="状态")

    # 答卷
    answer_json: str | None = Field(default=None, description="答卷json")

    # 预计开始时间
    plan_starttime: datetime = Field(default=None, description="预计开始时间")
    # 预计耗时
    plan_duration: int = Field(default=0, description="预计耗时")
    # 实际开始时间
    actual_starttime: datetime = Field(default=None, description="实际开始时间")
    # 实际结束时间
    actual_duration: int = Field(default=0, description="实际耗时")

    # 时间信息
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="创建时间")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="更新时间")

    # 状态信息
    is_deleted: bool = Field(default=False, description="是否已删除")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def get_questions_list(self) -> List[Question]:
        """获取问题列表"""
        if not self.question_ids:
            return []
        if self._questions and len(self._questions) > 0:
            return self._questions
        else:
            return [Question.get_by_id(qid.strip()) for qid in self.question_ids.split(',') if qid.strip()]

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

    @classmethod
    def from_dict(cls, data: dict) -> 'Exam':
        """从字典创建"""
        for field in ['question_ids']:
            if data.get(field):
                data[field] = ",".join(data[field])
        for field in ['answer']:
            if isinstance(data.get(field), Answer):
                data[field] = data[field].model_dump_json()
        for field in ['plan_starttime', 'actual_starttime']:
            if data.get(field):
                data[field] = iso_to_mysql_datetime(data[field])
        return cls(**data)

    def to_dict(self) -> dict:
        """转换为字典格式"""
        result = {}
        for field in self.__fields__:
            value = getattr(self, field)
            if field in ['question_ids']:
                result[field] = value.split(',') if value else []
            elif field in ['plan_starttime', 'actual_starttime']:
                result[field] = mysql_datetime_to_iso(value)
            else:
                result[field] = value
        return result


# 创建考试的工厂函数
def create_exam(**kwargs) -> Exam:
    """创建考试实例的工厂函数"""
    return Exam.from_dict(kwargs)
