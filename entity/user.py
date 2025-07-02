"""
用户实体类 - 定义用户的基本信息
"""

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import datetime
import hashlib
import os
from utils.helpers import random_uuid

class User(SQLModel, table=True):
    """用户实体类"""

    # 基本信息
    id: Optional[str] = Field(default_factory=lambda: random_uuid(), primary_key=True, description="用户唯一标识")
    name: str = Field(..., description="用户姓名")
    password: str = Field(..., description="密码")

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

    def set_password(self, password: str):
        """设置密码（加密）"""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        self.password = salt.hex() + key.hex()

    def check_password(self, password: str) -> bool:
        """验证密码"""
        try:
            salt = bytes.fromhex(self.password[:64])
            key = bytes.fromhex(self.password[64:])
            new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            return key == new_key
        except:
            return False

    def to_dict(self, include_password: bool = False) -> dict:
        """转换为字典，可选择是否包含密码"""
        user_dict = self.model_dump()
        if not include_password:
            user_dict.pop('password', None)
        return user_dict

# 创建用户的工厂函数
def create_user(
    name: str,
    password: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    avatar: Optional[str] = None
) -> User:
    """创建用户实例的工厂函数"""
    user = User(
        name=name,
        email=email,
        phone=phone,
        avatar=avatar
    )
    user.set_password(password)
    return user


# 示例用法
if __name__ == "__main__":
    # 创建一个用户示例
    user = create_user(
        name="张三",
        password="123456",
        email="zhangsan@example.com",
        phone="13800138000"
    )

    print(user)
    print(f"用户ID: {user.id}")
    print(f"用户姓名: {user.name}")
    print(f"创建时间: {user.created_at}")
    print(f"密码验证: {user.check_password('123456')}")
