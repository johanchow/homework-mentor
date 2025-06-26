"""
用户实体类 - 定义用户的基本信息
"""

from typing import Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class User(BaseModel):
    """用户实体类"""
    
    # 基本信息
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="用户唯一标识")
    name: str = Field(..., description="用户姓名")
    
    # 可选信息
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    avatar: Optional[str] = Field(None, description="头像URL")
    
    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # 状态信息
    is_active: bool = Field(default=True, description="是否激活")
    is_deleted: bool = Field(default=False, description="是否已删除")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """从字典创建用户实例"""
        return cls(**data)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"User(id={self.id}, name='{self.name}')"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()


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
