"""
工具函数模块
"""

import logging
import uuid
import requests
from io import BytesIO
from typing import Dict, Any, Optional
from datetime import datetime
from config.settings import settings


def setup_logging(name: str = "langgraph_agents") -> logging.Logger:
    """设置日志配置"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.LOG_LEVEL))


        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))

        # 创建格式化器
        formatter = logging.Formatter(settings.LOG_FORMAT)
        console_handler.setFormatter(formatter)

        # 添加处理器
        logger.addHandler(console_handler)

    return logger

def random_uuid(length: int = 10) -> str:
    return uuid.uuid4().hex[:length]

def download_bytes_from_url(url: str) -> BytesIO:
    resp = requests.get(url)
    resp.raise_for_status()
    return BytesIO(resp.content)
