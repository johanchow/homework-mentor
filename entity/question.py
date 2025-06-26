"""
问题实体类 - 定义问题的基本结构和属性
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
import uuid
from datetime import datetime
from entity.message import Message, MessageRole

class QuestionType(str, Enum):
    """问题类型枚举"""
    MULTIPLE_CHOICE = "multiple_choice"  # 选择题
    FILL_BLANK = "fill_blank"           # 填空题
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


class MediaFile(BaseModel):
    """媒体文件模型"""
    file_id: str = Field(..., description="文件唯一标识")
    file_url: str = Field(..., description="文件URL")
    file_name: Optional[str] = Field(None, description="文件名")
    file_type: Optional[str] = Field(None, description="文件类型")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    duration: Optional[float] = Field(None, description="音频/视频时长(秒)")
    thumbnail_url: Optional[str] = Field(None, description="缩略图URL")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Question(BaseModel):
    """问题实体类"""

    # 基本信息
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="问题唯一标识")
    subject: Subject = Field(..., description="科目")
    question_type: QuestionType = Field(..., description="问题类型")
    title: str = Field(..., description="题干")

    # 媒体资源
    images: List[MediaFile] = Field(default_factory=list, description="图片文件列表")
    audios: List[MediaFile] = Field(default_factory=list, description="音频文件列表")
    videos: List[MediaFile] = Field(default_factory=list, description="视频文件列表")

    # 选项（用于选择题）
    options: Optional[List[str]] = Field(None, description="选项列表（选择题专用）")
    correct_answer: Optional[Union[str, List[str]]] = Field(None, description="正确答案")

    # 元数据
    difficulty: Optional[int] = Field(None, ge=1, le=5, description="难度等级(1-5)")
    points: Optional[int] = Field(None, description="分值")
    tags: List[str] = Field(default_factory=list, description="标签列表")

    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 状态信息
    is_active: bool = Field(default=True, description="是否激活")
    is_deleted: bool = Field(default=False, description="是否已删除")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.images = kwargs.get("images", [])
        self.audios = kwargs.get("audios", [])
        self.videos = kwargs.get("videos", [])

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return self.dict()

    def to_message(self, belong_role: MessageRole = MessageRole.USER) -> Message:
        """转换为消息格式"""
        if len(self.images) == 0:
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
                        "url": self.images[0].file_url
                    }
                }]
            )

    @classmethod
    def from_dict(cls, data: dict) -> 'Question':
        """从字典创建问题实例"""
        return cls(**data)

    def __str__(self) -> str:
        """字符串表示"""
        return f"Question(id={self.id}, subject={self.subject}, type={self.question_type}, title='{self.title[:50]}...')"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()
