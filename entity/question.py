"""
问题实体类 - 定义问题的基本结构和属性
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
import uuid
from datetime import datetime


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
    file_name: str = Field(..., description="文件名")
    file_url: str = Field(..., description="文件URL")
    file_type: str = Field(..., description="文件类型")
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
    content: Optional[str] = Field(None, description="问题详细内容")
    
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
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return self.dict()
    
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
        content=content,
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
        content="A. 憧憬(chōng jǐng) B. 憧憬(chōng jìng) C. 憧憬(chōng jīng) D. 憧憬(chōng jīng)",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        difficulty=3,
        points=5,
        tags=["语文", "字音", "选择题"]
    )
    
    print(question)
    print(f"媒体文件统计: {question.get_media_count()}")
    print(f"是否为选择题: {question.is_multiple_choice()}")
    print(f"是否包含媒体: {question.has_media()}")
