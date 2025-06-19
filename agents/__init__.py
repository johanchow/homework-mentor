"""
Agent模块 - 定义各种类型的智能代理
"""

from .base_agent import BaseAgent
from .research_agent import ResearchAgent
from .analysis_agent import AnalysisAgent
from .summary_agent import SummaryAgent
from .chinese_agent import ChineseTeacherAgent

__all__ = [
    'BaseAgent',
    'ResearchAgent', 
    'AnalysisAgent',
    'SummaryAgent',
    'ChineseTeacherAgent'
] 