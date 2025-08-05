"""
应用配置设置
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    """应用配置类"""

    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 5556
    API_DEBUG: bool = False

    # LLM配置
    OPENAI_API_KEY: Optional[str] = None
    DASHSCOPE_API_KEY: str = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000

    # Agent配置
    MAX_CONCURRENT_TASKS: int = 10
    TASK_TIMEOUT: int = 300  # 秒
    AGENT_POOL_SIZE: int = 3

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 数据库配置（如果需要）
    DATABASE_URL: str = None

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        load_dotenv()


# 创建全局配置实例
settings = Settings()