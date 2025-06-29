"""
抽象类 - 定义基础模型
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class BaseModel(SQLModel):
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return self.dict()

    @classmethod
    def from_dict(cls, data: dict) -> 'BaseModel':
        """从字典创建"""
        return cls(**data)

    def __str__(self) -> str:
        """字符串表示"""
        class_name = self.__class__.__name__
        return f"{class_name}(id={self.id})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()