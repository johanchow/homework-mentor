"""
问题实体类 - 定义问题的基本结构和属性
"""

from typing import List, Optional, Union
from sqlmodel import SQLModel, Field, Session, select, Relationship
import logging
from enum import Enum
from datetime import datetime
from entity.base import BaseModel
import json
from utils.helpers import random_uuid
from entity.message import Message, MessageRole
from entity.user import User
from utils.transformer import iso_to_mysql_datetime, mysql_datetime_to_iso

logger = logging.getLogger(__name__)

class QuestionType(str, Enum):
    """问题类型枚举"""
    judge = "judge"                     # 判断题
    choice = "choice"                   # 选择题
    qa = "qa"                           # 问答题
    reading = "reading"                 # 阅读题
    summary = "summary"                 # 总结题
    show = "show"                       # 展示题


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


class Question(BaseModel, table=True):
    """问题实体类"""

    # 基本信息
    id: Optional[str] = Field(default_factory=lambda: random_uuid(), primary_key=True, description="问题唯一标识")
    subject: Subject = Field(..., description="科目")
    type: QuestionType = Field(..., description="问题类型")
    title: str = Field(..., description="题干")
    tip: Optional[str] = Field(default=None, description="提示")

    # 媒体资源 - 使用JSON字符串存储
    links: Optional[str] = Field(default=None, description="链接列表字符串(以逗号分割)")
    attachments: Optional[str] = Field(default=None, description="附件列表字符串(以逗号分割)")
    images: Optional[str] = Field(default=None, description="图片文件列表字符串(以逗号分割)")
    audios: Optional[str] = Field(default=None, description="音频文件列表字符串(以逗号分割)")
    videos: Optional[str] = Field(default=None, description="视频文件列表字符串(以逗号分割)")

    # 选项（用于选择题）- 使用JSON字符串存储
    options: Optional[str] = Field(default=None, description="选项列表字符串(选择题专用,以逗号分割)")

    # 材料内容，可能是文件中提取的，可能是题目中提取的
    material: Optional[str] = Field(default=None, description="内容dict字符串")

    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 创建人信息
    creator_id: str = Field(..., description="创建人ID", foreign_key="user.id")
    creator: User = Relationship(back_populates="questions")

    # 状态信息
    is_active: bool = Field(default=True, description="是否激活")
    is_deleted: bool = Field(default=False, description="是否已删除")

    sessions: List['Session'] = Relationship(back_populates="question")


    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True

    def to_message(self, belong_role: MessageRole = MessageRole.USER) -> Message:
        """转换为消息格式"""
        images_list = self.get_images_list()
        if len(images_list) == 0:
            # 如果是纯文字的题目
            return Message(
                role=belong_role,
                content=self.title
            )
        else:
            # 如果是包含图片的题目
            return Message(
                role=belong_role,
                content=[{
                    "type": "text",
                    "text": self.title
                }, {
                    "type": "image_url",
                    "image_url": {
                        "url": images_list[0]
                    }
                }]
            )

    @classmethod
    def from_dict(cls, data: dict) -> 'BaseModel':
        """从字典创建"""
        for field in ['options', 'images', 'audios', 'videos', 'attachments', 'links']:
            if isinstance(data.get(field), list):
                data[field] = ','.join(data[field])
        for field in ['created_at', 'updated_at']:
            if data.get(field):
                data[field] = iso_to_mysql_datetime(data[field])
        return cls(**data)

    def to_dict(self) -> dict:
        """转换为字典格式"""
        result = {}
        for field in self.__fields__:
            value = getattr(self, field)
            if field in ['images', 'audios', 'videos', 'options', 'attachments', 'links']:
                result[field] = value.split(',') if value else []
            elif field in ['created_at', 'updated_at']:
                result[field] = mysql_datetime_to_iso(value)
            else:
                result[field] = value
        return result

    def get_images_list(self) -> List[str]:
        """获取图片列表"""
        if self.images:
            return [img.strip() for img in self.images.split(',') if img.strip()]
        return []

    def get_audios_list(self) -> List[str]:
        """获取音频列表"""
        if self.audios:
            return [audio.strip() for audio in self.audios.split(',') if audio.strip()]
        return []

    def get_videos_list(self) -> List[str]:
        """获取视频列表"""
        if self.videos:
            return [video.strip() for video in self.videos.split(',') if video.strip()]
        return []

    def get_options_list(self) -> List[str]:
        """获取选项列表"""
        if self.options:
            return json.loads(self.options)
        return []


# 创建问题的工厂函数
def create_question(**kwargs) -> Question:
    """创建问题实例的工厂函数"""
    question = Question.from_dict(kwargs)
    return question


# 示例用法
if __name__ == "__main__":
    # 创建一个选择题示例
    question = create_question(
        subject=Subject.CHINESE,
        type=QuestionType.choice,
        title="下列词语中加点字的读音完全正确的一项是",
        creator_id="user123",
        options=["A. 正确", "B. 错误", "C. 不确定", "D. 以上都不是"],
        images=["https://example.com/image1.jpg"],
    )

    print(question)
    print(f"选项: {question.get_options_list()}")
    print(f"图片: {question.get_images_list()}")
