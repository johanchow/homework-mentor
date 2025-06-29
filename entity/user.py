"""
用户实体类 - 定义用户的基本信息
"""

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import datetime

class User(SQLModel, table=True):
    """用户实体类"""

    # 基本信息
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, description="用户唯一标识")
    name: str = Field(..., description="用户姓名")

    # 可选信息
    email: Optional[str] = Field(default=None, description="邮箱")
    phone: Optional[str] = Field(default=None, description="手机号")
    avatar: Optional[str] = Field(default=None, description="头像URL")

    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 状态信息
    is_active: bool = Field(default=True, description="是否激活")
    is_deleted: bool = Field(default=False, description="是否已删除")

    questions: List['Question'] = Relationship(back_populates="creator")
    papers: List['Paper'] = Relationship(back_populates="creator")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# 创建用户的工厂函数
def create_user(
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    avatar: Optional[str] = None
) -> User:
    """创建用户实例的工厂函数"""
    return User(
        name=name,
        email=email,
        phone=phone,
        avatar=avatar
    )


# 示例用法
if __name__ == "__main__":
    # 创建一个用户示例
    user = create_user(
        name="张三",
        email="zhangsan@example.com",
        phone="13800138000"
    )

    print(user)
    print(f"用户ID: {user.id}")
    print(f"用户姓名: {user.name}")
    print(f"创建时间: {user.created_at}")
