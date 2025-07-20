"""
目标实体类 - 定义学习目标的基本结构和属性
"""

from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from datetime import datetime
from entity.base import BaseModel
from utils.helpers import random_uuid
from entity.user import User


class GoalStatus(str, Enum):
    """目标状态枚举"""
    PREPARING = 'preparing'  # 准备中
    DOING = 'doing'  # 进行中
    PASSED = 'passed'  # 已通过
    cancelled = "cancelled"  # 已取消


class Subject(str, Enum):
    """科目枚举"""
    CHINESE = "chinese"     # 语文
    ENGLISH = "english"     # 英语
    MATH = "math"          # 数学
    PHYSICS = "physics"    # 物理
    CHEMISTRY = "chemistry" # 化学
    BIOLOGY = "biology"    # 生物
    HISTORY = "history"    # 历史
    GEOGRAPHY = "geography" # 地理
    POLITICS = "politics"  # 政治
    OTHER = "other"        # 其他


class Goal(BaseModel, table=True):
    """目标实体类"""

    # 基本信息
    id: Optional[str] = Field(default_factory=lambda: random_uuid(), primary_key=True, description="目标唯一标识")
    name: str = Field(..., description="目标名称")
    subject: Subject = Field(..., description="科目")
    status: GoalStatus = Field(default=GoalStatus.PREPARING, description="目标状态")
    ai_prompt: Optional[str] = Field(default=None, description="AI提示词")

    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 创建人信息
    creator_id: str = Field(..., description="创建人ID", foreign_key="user.id")
    creator: User = Relationship(back_populates="goals")

    # 状态信息
    is_deleted: bool = Field(default=False, description="是否已删除")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True


# 创建目标的工厂函数
def create_goal(
    name: str,
    subject: Subject,
    ai_prompt: str,
    creator_id: str,
    status: GoalStatus = GoalStatus.PREPARING,
) -> Goal:
    """创建目标实例的工厂函数"""
    goal = Goal(
        name=name,
        subject=subject,
        ai_prompt=ai_prompt,
        creator_id=creator_id,
        status=status,
    )
    return goal


# 示例用法
if __name__ == "__main__":
    # 创建一个学习目标示例
    goal = create_goal(
        name="掌握初中数学函数概念",
        subject=Subject.MATH,
        ai_prompt="请帮助我理解初中数学中的函数概念，包括定义、性质和应用",
        creator_id="user123",
        status=GoalStatus.pending,
    )

    print(goal)
    print(f"目标名称: {goal.name}")
    print(f"科目: {goal.subject}")
    print(f"状态: {goal.status}")
    print(f"AI提示词: {goal.ai_prompt}")
