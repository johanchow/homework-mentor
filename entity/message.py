from typing import Dict, List, Optional, Union, Any
from enum import Enum
import json
import base64
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from utils.helpers import random_uuid


class MessageType(Enum):
    """消息类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"


class MessageRole(Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """绘画消息类，支持多种媒体类型"""

    # 消息ID
    id: Optional[str] = Field(default_factory=lambda: random_uuid(), primary_key=True, description="消息唯一标识")

    # 消息角色
    role: MessageRole = Field(..., description="消息角色")

    # 消息内容
    content: Union[str, List[Dict[str, Any]]] = Field(..., description="消息内容")

    # 消息类型
    message_type: MessageType = Field(default=MessageType.TEXT, description="消息类型")

    # 时间戳
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="时间戳")

    # 元数据
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")

    def add_text_content(self, text: str) -> None:
        """添加文本内容"""
        if isinstance(self.content, str):
            self.content = text
        elif isinstance(self.content, list):
            # 查找是否已有文本内容
            text_item = next((item for item in self.content if item.get("type") == "text"), None)
            if text_item:
                text_item["text"] = text
            else:
                self.content.append({"type": "text", "text": text})
        else:
            self.content = [{"type": "text", "text": text}]

    def add_image_content(self, image_url: str, image_data: Optional[bytes] = None) -> None:
        """添加图片内容"""
        if isinstance(self.content, str):
            self.content = []

        if not isinstance(self.content, list):
            self.content = []

        image_item = {
            "type": "image_url",
            "image_url": {"url": image_url}
        }

        if image_data:
            # 将图片数据编码为base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            image_item["image_url"]["url"] = f"data:image/jpeg;base64,{image_base64}"

        self.content.append(image_item)

    def add_video_content(self, video_url: str, video_data: Optional[bytes] = None) -> None:
        """添加视频内容"""
        if isinstance(self.content, str):
            self.content = []

        if not isinstance(self.content, list):
            self.content = []

        video_item = {
            "type": "video_url",
            "video_url": {"url": video_url}
        }

        if video_data:
            # 将视频数据编码为base64
            video_base64 = base64.b64encode(video_data).decode('utf-8')
            video_item["video_url"]["url"] = f"data:video/mp4;base64,{video_base64}"

        self.content.append(video_item)

    def add_audio_content(self, audio_url: str, audio_data: Optional[bytes] = None) -> None:
        """添加音频内容"""
        if isinstance(self.content, str):
            self.content = []

        if not isinstance(self.content, list):
            self.content = []

        audio_item = {
            "type": "audio_url",
            "audio_url": {"url": audio_url}
        }

        if audio_data:
            # 将音频数据编码为base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            audio_item["audio_url"]["url"] = f"data:audio/mpeg;base64,{audio_base64}"

        self.content.append(audio_item)

    def to_llm_message(self) -> Dict[str, Any]:
        """
        转换为LLM消息格式

        Returns:
            LLM消息格式的字典
        """
        if isinstance(self.content, str):
            llm_message = {
                "role": self.role.value,
                "content": self.content
            }
        elif isinstance(self.content, list):
            llm_content = []
            for item in self.content:
                if item.get("type") == "text":
                    llm_content.append({"type": "text", "text": item.get("text")})
                elif item.get("type") == "image_url":
                    llm_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": item.get("image_url", {}).get("url")
                        }
                    })
            llm_message = {
                "role": self.role.value,
                "content": llm_content
            }

        # llm_message = {
        #     "role": self.role.value,
        #     "content": self.content
        # }

        # 添加元数据
        if self.metadata:
            llm_message["metadata"] = self.metadata

        return llm_message

    @classmethod
    def from_llm_message(cls, llm_message: Dict[str, Any]) -> 'Message':
        """
        从LLM消息格式创建Message对象

        Args:
            llm_message: LLM消息格式的字典

        Returns:
            Message对象
        """
        role = llm_message.get("role", "user")
        content = llm_message.get("content", "")

        # 判断消息类型
        message_type = MessageType.TEXT
        if isinstance(content, list):
            for item in content:
                if item.get("type") == "image_url":
                    message_type = MessageType.IMAGE
                    break
                elif item.get("type") == "video_url":
                    message_type = MessageType.VIDEO
                    break
                elif item.get("type") == "audio_url":
                    message_type = MessageType.AUDIO
                    break

        return cls(
            role=role,
            content=content,
            message_type=message_type,
            metadata=llm_message.get("metadata", {})
        )

    def get_text_content(self) -> Optional[str]:
        """获取文本内容"""
        if isinstance(self.content, str):
            return self.content
        elif isinstance(self.content, list):
            for item in self.content:
                if item.get("type") == "text":
                    return item.get("text", "")
        return None

    def get_media_urls(self) -> Dict[str, List[str]]:
        """获取所有媒体URL"""
        urls = {"images": [], "videos": [], "audios": []}

        if isinstance(self.content, list):
            for item in self.content:
                if item.get("type") == "image_url":
                    url = item.get("image_url", {}).get("url", "")
                    if url:
                        urls["images"].append(url)
                elif item.get("type") == "video_url":
                    url = item.get("video_url", {}).get("url", "")
                    if url:
                        urls["videos"].append(url)
                elif item.get("type") == "audio_url":
                    url = item.get("audio_url", {}).get("url", "")
                    if url:
                        urls["audios"].append(url)

        return urls

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "role": self.role.value,
            "content": self.content,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """从字典创建Message对象"""
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            message_type=MessageType(data.get("message_type", "text")),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
            id=data.get("id"),
            metadata=data.get("metadata", {})
        )

    def __str__(self) -> str:
        """字符串表示"""
        text_content = self.get_text_content() or ""
        return f"Message(role={self.role.value}, content={text_content[:50]}..., type={self.message_type.value})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"Message(role={self.role.value}, content={self.content}, message_type={self.message_type.value}, timestamp={self.timestamp})"


def create_message(
    role: MessageRole,
    content: Union[str, List[Dict[str, Any]]],
    message_type: MessageType = MessageType.TEXT,
    timestamp: Optional[datetime] = datetime.now(timezone.utc),
    metadata: Optional[Dict[str, Any]] = None
) -> Message:
    """创建消息实例的工厂函数"""
    return Message(
        role=role,
        content=content,
        message_type=message_type,
        timestamp=timestamp,
        metadata=metadata)