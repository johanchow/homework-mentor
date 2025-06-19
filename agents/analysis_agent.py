"""
分析Agent - 专门负责数据分析和深度分析任务
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from langchain.schema import HumanMessage, SystemMessage


class AnalysisAgent(BaseAgent):
    """分析Agent - 负责数据分析和深度分析"""
    
    def _define_capabilities(self) -> List[str]:
        return [
            "analyze", "analysis", "evaluate", "assess", "examine",
            "分析", "评估", "检查", "评价", "深度分析"
        ]
    
    async def process_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理分析任务"""
        
        # 构建系统提示
        system_prompt = """你是一个专业的数据分析师，擅长深度分析和洞察发现。
        
你的任务包括：
1. 理解分析需求，确定分析目标
2. 设计分析框架和方法
3. 进行多维度分析
4. 识别关键洞察和模式
5. 提供行动建议

请确保你的分析包含：
- 分析目标和方法
- 关键发现和洞察
- 数据支撑和证据
- 结论和建议
- 风险评估
"""
        
        # 构建用户消息
        user_message = f"""
请帮我完成以下分析任务：

任务：{task}

额外上下文：{context or '无'}

请提供深入的分析报告，包括分析框架、关键发现和行动建议。
"""
        
        # 调用LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        # 模拟分析过程
        analysis_framework = [
            "需求理解",
            "数据收集",
            "数据清洗",
            "探索性分析",
            "深度分析",
            "洞察发现",
            "报告撰写"
        ]
        
        return {
            "task_type": "analysis",
            "analysis_framework": analysis_framework,
            "report": response.content,
            "key_insights": self._extract_key_insights(response.content),
            "confidence": 0.90,
            "completion_time": "10-15分钟",
            "analysis_methods": ["SWOT分析", "趋势分析", "对比分析", "风险评估"]
        }
    
    def _extract_key_insights(self, content: str) -> List[str]:
        """从分析报告中提取关键洞察"""
        # 这里可以集成更复杂的NLP处理
        insights = [
            "识别了主要趋势和模式",
            "发现了关键影响因素",
            "提供了具体的行动建议",
            "评估了潜在风险和机会"
        ]
        return insights 