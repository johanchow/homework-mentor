"""
动态路由模块 - 使用LLM进行智能任务分配
"""

from typing import Dict, Any, List, Optional
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import asyncio
from agents import ResearchAgent, AnalysisAgent, SummaryAgent, ChineseTeacherAgent


class TaskRouter:
    """智能任务路由器 - 使用LLM动态分配任务"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3
        )
        
        # 初始化可用的Agent
        self.available_agents = {
            "research": ResearchAgent(),
            "analysis": AnalysisAgent(),
            "summary": SummaryAgent(),
            "chinese_teacher": ChineseTeacherAgent()
        }
        
        # Agent能力映射
        self.agent_capabilities = {
            "research": [
                "信息收集", "调研", "搜索", "数据收集", "市场研究",
                "research", "investigate", "search", "collect", "gather"
            ],
            "analysis": [
                "数据分析", "深度分析", "评估", "检查", "洞察发现",
                "analyze", "evaluate", "assess", "examine", "insight"
            ],
            "summary": [
                "总结", "概括", "提炼", "归纳", "报告生成",
                "summarize", "condense", "extract", "synthesize", "report"
            ],
            "chinese_teacher": [
                "中文教学", "语文指导", "写作指导", "阅读理解", "语法分析",
                "作文指导", "诗词鉴赏", "文言文", "现代文", "语言表达",
                "chinese", "teaching", "guidance", "writing", "reading"
            ]
        }
    
    async def route_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """使用LLM进行智能任务路由"""
        
        # 构建路由提示
        system_prompt = """你是一个智能任务路由器，负责将任务分配给最合适的Agent。

可用的Agent类型：
1. ResearchAgent (研究Agent)
   - 能力：信息收集、调研、搜索、数据收集
   - 适用：需要收集新信息、调研市场、查找资料的任务

2. AnalysisAgent (分析Agent)  
   - 能力：数据分析、深度分析、评估、洞察发现
   - 适用：需要分析数据、评估情况、发现洞察的任务

3. SummaryAgent (总结Agent)
   - 能力：总结、概括、提炼、报告生成
   - 适用：需要总结内容、生成报告、提炼要点的任务

4. ChineseTeacherAgent (中文老师Agent)
   - 能力：中文教学、语文指导、写作指导、阅读理解、语法分析
   - 适用：中文学习问题、作文指导、阅读理解、语法学习、诗词鉴赏等

请根据任务内容，选择最合适的Agent类型，并说明理由。
返回格式：
{
    "selected_agent": "agent_type",
    "confidence": 0.95,
    "reasoning": "选择理由",
    "estimated_time": "预计完成时间",
    "priority": "high/medium/low"
}
"""
        
        user_message = f"""
请为以下任务选择最合适的Agent：

任务：{task}
上下文：{context or '无'}

请分析任务需求，选择最合适的Agent类型。
"""
        
        # 调用LLM进行路由决策
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        # 解析LLM响应（这里简化处理，实际应用中需要更复杂的解析）
        routing_decision = self._parse_routing_response(response.content, task)
        
        return routing_decision
    
    def _parse_routing_response(self, response: str, task: str) -> Dict[str, Any]:
        """解析LLM的路由响应"""
        # 简化的解析逻辑，实际应用中可以使用更复杂的NLP处理
        
        # 基于关键词的备选路由逻辑
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["研究", "调研", "搜索", "收集", "research", "search", "investigate"]):
            selected_agent = "research"
            reasoning = "任务涉及信息收集和调研"
        elif any(word in task_lower for word in ["分析", "评估", "检查", "analyze", "evaluate", "assess"]):
            selected_agent = "analysis"
            reasoning = "任务需要深度分析和评估"
        elif any(word in task_lower for word in ["总结", "概括", "提炼", "summarize", "summary", "extract"]):
            selected_agent = "summary"
            reasoning = "任务需要内容总结和提炼"
        elif any(word in task_lower for word in ["中文", "语文", "作文", "写作", "阅读", "语法", "诗词", "文言文", "chinese", "teaching", "guidance"]):
            selected_agent = "chinese_teacher"
            reasoning = "任务涉及中文教学和指导"
        else:
            # 默认选择分析Agent
            selected_agent = "analysis"
            reasoning = "任务性质不明确，选择通用分析Agent"
        
        return {
            "selected_agent": selected_agent,
            "confidence": 0.85,
            "reasoning": reasoning,
            "estimated_time": "5-10分钟",
            "priority": "medium",
            "llm_response": response
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """获取所有Agent的状态"""
        status = {}
        for agent_type, agent in self.available_agents.items():
            status[agent_type] = {
                "status": agent.get_status(),
                "capabilities": self.agent_capabilities[agent_type],
                "workload": agent.get_workload()
            }
        return status
    
    def get_best_agent(self, task: str) -> Optional[str]:
        """基于工作负载选择最佳Agent"""
        best_agent = None
        min_workload = float('inf')
        
        for agent_type, agent in self.available_agents.items():
            if agent.can_handle(task):
                workload = agent.get_workload()
                if workload < min_workload:
                    min_workload = workload
                    best_agent = agent_type
        
        return best_agent 