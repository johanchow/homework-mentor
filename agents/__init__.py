"""
Agent模块 - 定义各种类型的智能代理
"""

from .base_agent import BaseAgent
from .chinese_agent import ChineseTeacherAgent

__all__ = [
    'BaseAgent',
    'ChineseTeacherAgent'
] 