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

    def add_image(self, file_name: str, file_url: str, file_size: Optional[int] = None) -> str:
        """添加图片文件"""
        file_id = str(uuid.uuid4())
        image = MediaFile(
            file_id=file_id,
            file_name=file_name,
            file_url=file_url,
            file_type="image",
            file_size=file_size
        )
        self.images.append(image)
        self.updated_at = datetime.now()
        return file_id
    
    def add_audio(self, file_name: str, file_url: str, duration: Optional[float] = None, 
                  file_size: Optional[int] = None) -> str:
        """添加音频文件"""
        file_id = str(uuid.uuid4())
        audio = MediaFile(
            file_id=file_id,
            file_name=file_name,
            file_url=file_url,
            file_type="audio",
            file_size=file_size,
            duration=duration
        )
        self.audios.append(audio)
        self.updated_at = datetime.now()
        return file_id
    
    def add_video(self, file_name: str, file_url: str, duration: Optional[float] = None,
                  file_size: Optional[int] = None, thumbnail_url: Optional[str] = None) -> str:
        """添加视频文件"""
        file_id = str(uuid.uuid4())
        video = MediaFile(
            file_id=file_id,
            file_name=file_name,
            file_url=file_url,
            file_type="video",
            file_size=file_size,
            duration=duration,
            thumbnail_url=thumbnail_url
        )
        self.videos.append(video)
        self.updated_at = datetime.now()
        return file_id
    
    def remove_media(self, file_id: str) -> bool:
        """移除媒体文件"""
        # 从图片中移除
        for i, image in enumerate(self.images):
            if image.file_id == file_id:
                self.images.pop(i)
                self.updated_at = datetime.now()
                return True
        
        # 从音频中移除
        for i, audio in enumerate(self.audios):
            if audio.file_id == file_id:
                self.audios.pop(i)
                self.updated_at = datetime.now()
                return True
        
        # 从视频中移除
        for i, video in enumerate(self.videos):
            if video.file_id == file_id:
                self.videos.pop(i)
                self.updated_at = datetime.now()
                return True
        
        return False
    
    def get_media_count(self) -> dict:
        """获取媒体文件统计"""
        return {
            "images": len(self.images),
            "audios": len(self.audios),
            "videos": len(self.videos),
            "total": len(self.images) + len(self.audios) + len(self.videos)
        }
    
    def is_multiple_choice(self) -> bool:
        """判断是否为选择题"""
        return self.question_type == QuestionType.MULTIPLE_CHOICE
    
    def has_media(self) -> bool:
        """判断是否包含媒体文件"""
        return bool(self.images or self.audios or self.videos)

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


# 创建问题的工厂函数
def create_question(
    subject: Subject,
    question_type: QuestionType,
    title: str,
    content: Optional[str] = None,
    options: Optional[List[str]] = None,
    correct_answer: Optional[Union[str, List[str]]] = None,
    difficulty: Optional[int] = None,
    points: Optional[int] = None,
    tags: Optional[List[str]] = None
) -> Question:
    """创建问题实例的工厂函数"""
    return Question(
        subject=subject,
        question_type=question_type,
        title=title,
        options=options,
        correct_answer=correct_answer,
        difficulty=difficulty,
        points=points,
        tags=tags or []
    )


# 示例用法
if __name__ == "__main__":
    # 创建一个选择题示例
    question = create_question(
        subject=Subject.CHINESE,
        question_type=QuestionType.MULTIPLE_CHOICE,
        title="下列词语中加点字的读音完全正确的一项是",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        difficulty=3,
        points=5,
        tags=["语文", "字音", "选择题"]
    )
    
    # 添加图片
    question.add_image("题目图片.jpg", "https://example.com/image1.jpg", 1024000)
    
    # 添加音频
    question.add_audio("朗读音频.mp3", "https://example.com/audio1.mp3", 30.5, 2048000)
    
    print(question)
    print(f"媒体文件统计: {question.get_media_count()}")
    print(f"是否为选择题: {question.is_multiple_choice()}")
    print(f"是否包含媒体: {question.has_media()}")
