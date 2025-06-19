"""
研究Agent - 专门负责信息收集、搜索和调研任务
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from langchain.schema import HumanMessage, SystemMessage
import asyncio


class ResearchAgent(BaseAgent):
    """研究Agent - 负责信息收集和调研"""
    
    def _define_capabilities(self) -> List[str]:
        return [
            "research", "search", "investigate", "collect", "gather",
            "调研", "搜索", "收集", "查找", "研究"
        ]
    
    async def process_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理研究任务"""
        
        # 构建系统提示
        system_prompt = """你是一个专业的研究员，擅长信息收集和调研工作。
        
你的任务包括：
1. 分析任务需求，确定需要收集的信息类型
2. 制定研究计划和方法
3. 模拟信息收集过程
4. 整理和总结收集到的信息
5. 提供详细的研究报告

请确保你的回答结构清晰，包含：
- 研究目标
- 研究方法
- 主要发现
- 结论和建议
"""
        
        # 构建用户消息
        user_message = f"""
请帮我完成以下研究任务：

任务：{task}

额外上下文：{context or '无'}

请提供详细的研究报告，包括研究过程、主要发现和结论。
"""
        
        # 调用LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        # 模拟研究过程（在实际应用中，这里会调用真实的搜索API）
        research_steps = [
            "分析任务需求",
            "确定研究范围",
            "收集相关信息",
            "整理和分析数据",
            "形成研究报告"
        ]
        
        return {
            "task_type": "research",
            "research_steps": research_steps,
            "report": response.content,
            "sources": self._simulate_sources(task),
            "confidence": 0.85,
            "completion_time": "5-10分钟"
        }
    
    def _simulate_sources(self, task: str) -> List[Dict[str, str]]:
        """模拟信息来源"""
        return [
            {
                "title": f"关于{task}的最新研究报告",
                "url": "https://example.com/research1",
                "type": "research_paper",
                "relevance": "high"
            },
            {
                "title": f"{task}相关技术文档",
                "url": "https://example.com/tech-doc",
                "type": "technical_documentation",
                "relevance": "medium"
            },
            {
                "title": f"{task}行业分析报告",
                "url": "https://example.com/industry-report",
                "type": "industry_report",
                "relevance": "high"
            }
        ] 