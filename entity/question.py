"""
问题实体类 - 定义问题的基本结构和属性
"""

from typing import List, Optional, Union
from sqlmodel import SQLModel, Field, Session, select, Relationship
from enum import Enum
from datetime import datetime
from entity.base import BaseModel
import json
from utils.helpers import random_uuid
from entity.message import Message, MessageRole
from entity.user import User


class QuestionType(str, Enum):
    """问题类型枚举"""
    JUDGE = "judge"                     # 判断题
    CHOICE = "choice"                   # 选择题
    QA = "qa"                           # 问答题
    ORAL = "oral"                       # 口述题
    PERFORMANCE = "performance"         # 表演题


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

    # 媒体资源 - 使用JSON字符串存储
    images: Optional[str] = Field(default=None, description="图片文件列表字符串(以逗号分割)")
    audios: Optional[str] = Field(default=None, description="音频文件列表字符串(以逗号分割)")
    videos: Optional[str] = Field(default=None, description="视频文件列表字符串(以逗号分割)")

    # 选项（用于选择题）- 使用JSON字符串存储
    options: Optional[str] = Field(default=None, description="选项列表字符串(选择题专用,以逗号分割)")

    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 创建人信息
    creator_id: str = Field(..., description="创建人ID", foreign_key="user.id")
    creator: User = Relationship(back_populates="questions")

    # 状态信息
    is_active: bool = Field(default=True, description="是否激活")
    is_deleted: bool = Field(default=False, description="是否已删除")

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
def create_question(
    subject: Subject,
    type: QuestionType,
    title: str,
    creator_id: str,
    options: Optional[List[str]] = None,
    images: Optional[List[str]] = None,
    audios: Optional[List[str]] = None,
    videos: Optional[List[str]] = None,
) -> Question:
    """创建问题实例的工厂函数"""
    question = Question(
        id=random_uuid(),
        subject=subject,
        type=type,
        title=title,
        creator_id=creator_id,
    )
    if options:
        question.options = json.dumps(options)
    if images:
        question.images = ",".join(images)
    if audios:
        question.audios = ",".join(audios)
    if videos:
        question.videos = ",".join(videos)

    return question


# 示例用法
if __name__ == "__main__":
    # 创建一个选择题示例
    question = create_question(
        subject=Subject.CHINESE,
        type=QuestionType.CHOICE,
        title="下列词语中加点字的读音完全正确的一项是",
        creator_id="user123",
        options=["A. 正确", "B. 错误", "C. 不确定", "D. 以上都不是"],
        images=["https://example.com/image1.jpg"],
    )

    print(question)
    print(f"选项: {question.get_options_list()}")
    print(f"图片: {question.get_images_list()}")
