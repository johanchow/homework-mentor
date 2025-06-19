"""
中文老师Agent - 专门负责中文教学指导和答疑
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import asyncio
from datetime import datetime


class ChineseTeacherAgent(BaseAgent):
    """中文老师Agent - 负责中文教学指导和答疑"""
    
    def __init__(self, agent_id: Optional[str] = None, **kwargs):
        super().__init__(agent_id, **kwargs)
        # 存储对话历史，支持多轮问答
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_session_id: Optional[str] = None
    
    async def process_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理中文教学任务"""
        
        # 检查是否是对话任务
        if context and context.get("is_conversation", False):
            return await self._handle_conversation(task, context)
        else:
            return await self._handle_teaching_guidance(task, context)
    
    async def _handle_teaching_guidance(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理教学指导任务"""
        
        # 构建系统提示
        system_prompt = """你是一位经验丰富的中文老师，擅长语文教学和指导。

你的教学特点：
1. 注重方法指导，不仅给出答案，更要教会学生思考方法
2. 提供原则性的指导，帮助学生建立正确的学习思维
3. 结合具体例子，让抽象的概念变得具体易懂
4. 鼓励学生独立思考，培养自主学习能力
5. 关注学生的个体差异，提供个性化的建议

教学指导原则：
- 启发式教学：引导学生自己发现答案
- 循序渐进：从简单到复杂，逐步深入
- 联系实际：将抽象知识与生活实际结合
- 培养兴趣：激发学生对中文学习的兴趣
- 注重实践：提供具体的练习方法和建议

请根据学生的具体问题，提供：
1. 问题分析：理解问题的核心和难点
2. 方法指导：提供解决问题的思路和方法
3. 原则说明：解释相关的语文学习原则
4. 实例讲解：用具体例子说明
5. 练习建议：提供相关的练习和巩固方法
"""
        
        # 构建用户消息
        user_message = f"""
请为以下中文学习问题提供指导：

问题：{task}

学生背景：{context.get('student_level', '中等水平') if context else '中等水平'}
学习目标：{context.get('learning_goal', '提高语文能力') if context else '提高语文能力'}

请提供详细的教学指导，包括方法、原则和具体建议。
"""
        
        # 调用LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        # 分析任务类型
        task_type = self._analyze_task_type(task)
        
        return {
            "task_type": "chinese_teaching",
            "teaching_type": task_type,
            "guidance": response.content,
            "teaching_methods": self._get_teaching_methods(task_type),
            "learning_principles": self._get_learning_principles(task_type),
            "practice_suggestions": self._generate_practice_suggestions(task_type),
            "confidence": 0.92,
            "completion_time": "3-5分钟",
            "session_id": self.current_session_id
        }
    
    async def _handle_conversation(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理多轮对话任务"""
        
        # 获取或创建会话ID
        session_id = context.get("session_id") if context else None
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.current_session_id = session_id
        
        # 获取对话历史
        conversation_history = context.get("conversation_history", []) if context else []
        
        # 构建系统提示
        system_prompt = """你是一位亲切耐心的中文老师，正在进行与学生的对话交流。

对话指导原则：
1. 保持耐心和鼓励的态度
2. 根据学生的理解程度调整回答的深度
3. 适时提出问题，引导学生思考
4. 结合具体例子，让抽象概念更易理解
5. 鼓励学生表达自己的想法
6. 在适当时候总结和归纳要点

回答要求：
- 语言亲切自然，符合师生对话的语气
- 内容准确专业，体现中文教学的专业性
- 结构清晰，便于学生理解和记忆
- 适时鼓励，增强学生的学习信心
"""
        
        # 构建对话历史
        messages = [SystemMessage(content=system_prompt)]
        
        # 添加历史对话
        for turn in conversation_history[-5:]:  # 保留最近5轮对话
            if turn.get("role") == "user":
                messages.append(HumanMessage(content=turn.get("content", "")))
            elif turn.get("role") == "assistant":
                messages.append(AIMessage(content=turn.get("content", "")))
        
        # 添加当前问题
        messages.append(HumanMessage(content=task))
        
        # 调用LLM
        response = await self.llm.ainvoke(messages)
        
        # 更新对话历史
        new_turn = {
            "role": "user",
            "content": task,
            "timestamp": datetime.now().isoformat()
        }
        conversation_history.append(new_turn)
        
        assistant_turn = {
            "role": "assistant", 
            "content": response.content,
            "timestamp": datetime.now().isoformat()
        }
        conversation_history.append(assistant_turn)
        
        return {
            "task_type": "chinese_conversation",
            "session_id": session_id,
            "response": response.content,
            "conversation_history": conversation_history,
            "turn_count": len(conversation_history) // 2,
            "confidence": 0.90,
            "completion_time": "1-2分钟"
        }
    
    def _analyze_task_type(self, task: str) -> str:
        """分析任务类型"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["作文", "写作", "写", "文章"]):
            return "writing"
        elif any(word in task_lower for word in ["阅读", "理解", "文章", "段落"]):
            return "reading"
        elif any(word in task_lower for word in ["语法", "句式", "修辞", "表达"]):
            return "grammar"
        elif any(word in task_lower for word in ["诗词", "古诗", "现代诗", "鉴赏"]):
            return "poetry"
        elif any(word in task_lower for word in ["文言文", "古文", "翻译"]):
            return "classical"
        else:
            return "general"
    
    def start_conversation(self, student_info: Dict[str, Any] = None) -> str:
        """开始新的对话会话"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session_id = session_id
        
        # 记录学生信息
        if student_info:
            self.conversation_history.append({
                "type": "student_info",
                "data": student_info,
                "timestamp": datetime.now().isoformat()
            })
        
        return session_id
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """获取对话总结"""
        if not self.conversation_history:
            return {"error": "没有对话历史"}
        
        # 统计对话信息
        user_messages = [msg for msg in self.conversation_history if msg.get("role") == "user"]
        assistant_messages = [msg for msg in self.conversation_history if msg.get("role") == "assistant"]
        
        return {
            "session_id": session_id,
            "total_turns": len(user_messages),
            "user_messages_count": len(user_messages),
            "assistant_messages_count": len(assistant_messages),
            "conversation_duration": "根据时间戳计算",
            "main_topics": self._extract_main_topics(),
            "learning_progress": "根据对话内容分析学习进展"
        }
    