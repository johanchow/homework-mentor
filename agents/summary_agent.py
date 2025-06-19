"""
总结Agent - 专门负责内容总结和报告生成任务
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from langchain.schema import HumanMessage, SystemMessage
import asyncio


class SummaryAgent(BaseAgent):
    """总结Agent - 负责内容总结和报告生成"""
    
    def _define_capabilities(self) -> List[str]:
        return [
            "summarize", "summary", "summarize", "condense", "extract",
            "总结", "概括", "提炼", "归纳", "报告生成"
        ]
    
    async def process_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理总结任务"""
        
        # 构建系统提示
        system_prompt = """你是一个专业的总结专家，擅长内容提炼和报告生成。
        
你的任务包括：
1. 理解总结需求，确定重点内容
2. 提取关键信息和要点
3. 组织逻辑结构
4. 生成清晰简洁的总结
5. 提供可执行的建议

请确保你的总结包含：
- 核心要点提炼
- 关键数据支撑
- 逻辑清晰的结论
- 具体的行动建议
- 简洁明了的表达
"""
        
        # 构建用户消息
        user_message = f"""
请帮我完成以下总结任务：

任务：{task}

额外上下文：{context or '无'}

请提供结构化的总结报告，突出关键信息并提供清晰的结论。
"""
        
        # 调用LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        # 模拟总结过程
        summary_structure = [
            "内容理解",
            "要点提取",
            "逻辑组织",
            "总结撰写",
            "质量检查"
        ]
        
        return {
            "task_type": "summary",
            "summary_structure": summary_structure,
            "report": response.content,
            "key_points": self._extract_key_points(response.content),
            "confidence": 0.88,
            "completion_time": "3-5分钟",
            "summary_methods": ["要点提取", "逻辑归纳", "重点突出", "简洁表达"]
        }
    
    def _extract_key_points(self, content: str) -> List[str]:
        """从总结中提取关键要点"""
        # 这里可以集成更复杂的NLP处理
        points = [
            "核心观点和结论",
            "关键数据和事实",
            "主要趋势和变化",
            "重要建议和行动项"
        ]
        return points 