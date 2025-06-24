"""
中文老师Agent - 专门负责中文教学指导和答疑
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import asyncio
from datetime import datetime


class ChineseTeacherAgent(BaseAgent):
    """中文老师Agent - 负责中文教学指导和答疑"""

    def __init__(self, agent_id: Optional[str] = None, **kwargs):
        super().__init__(agent_id, **kwargs)
        # 存储对话历史，支持多轮问答
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_session_id: Optional[str] = None

        # 初始化AgentExecutor
        self._init_agent()

    def _init_agent(self):
        """初始化AgentExecutor"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位经验丰富的中文老师，擅长语文教学和指导。

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

当学生提出语文题目或问题时，你需要：
1. 仔细分析题目内容和学生问题
2. 理解问题的核心和难点
3. 提供解决问题的思路和方法
4. 解释相关的语文学习原则
5. 用具体例子说明
6. 提供相关的练习和巩固方法

请根据语文题目和用户问题，进行详细的解答讲解。"""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_functions_agent(self.llm, tools=[], prompt=prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=[])

    def _define_capabilities(self) -> List[str]:
        """定义Agent的能力"""
        return [
            "中文教学", "语文指导", "写作指导", "阅读理解", "语法分析",
            "作文指导", "诗词鉴赏", "文言文", "现代文", "语言表达",
            "chinese", "teaching", "guidance", "writing", "reading"
        ]

    def _analyze_task_type(self, task: str) -> str:
        """分析任务类型"""
        task_lower = task.lower()

        if any(word in task_lower for word in ["写作", "作文", "写", "writing"]):
            return "writing"
        elif any(word in task_lower for word in ["阅读", "理解", "reading", "comprehension"]):
            return "reading"
        elif any(word in task_lower for word in ["语法", "grammar", "句式", "修辞"]):
            return "grammar"
        elif any(word in task_lower for word in ["诗词", "诗歌", "poetry", "古诗词"]):
            return "poetry"
        elif any(word in task_lower for word in ["文言文", "古文", "classical", "ancient"]):
            return "classical"
        else:
            return "general"

    def _get_teaching_methods(self, task_type: str) -> List[str]:
        """获取教学方法"""
        methods_map = {
            "writing": ["思维导图法", "五步写作法", "范文分析法", "修改指导法"],
            "reading": ["精读法", "略读法", "批注法", "复述法", "概括法"],
            "grammar": ["对比法", "归纳法", "演绎法", "练习法"],
            "poetry": ["意象分析法", "情感体验法", "背景了解法", "诵读法"],
            "classical": ["字词解释法", "句式分析法", "翻译法", "文化背景法"],
            "general": ["启发式教学", "实例讲解", "练习巩固", "总结归纳"]
        }
        return methods_map.get(task_type, methods_map["general"])

    def _get_learning_principles(self, task_type: str) -> List[str]:
        """获取学习原则"""
        principles_map = {
            "writing": ["多读多写", "观察生活", "积累素材", "反复修改"],
            "reading": ["理解为主", "速度与准确并重", "联系实际", "培养语感"],
            "grammar": ["理解规律", "多练习", "对比分析", "实际运用"],
            "poetry": ["感受意境", "理解情感", "了解背景", "诵读品味"],
            "classical": ["字词为本", "句式为要", "文化为根", "古今对比"],
            "general": ["循序渐进", "理论联系实际", "多练习", "独立思考"]
        }
        return principles_map.get(task_type, principles_map["general"])

    def _generate_practice_suggestions(self, task_type: str) -> List[str]:
        """生成练习建议"""
        suggestions_map = {
            "writing": [
                "每天写日记，记录生活感悟",
                "阅读优秀范文，学习写作技巧",
                "练习不同体裁的写作",
                "请老师或同学帮忙修改作文"
            ],
            "reading": [
                "每天阅读一定量的文章",
                "练习概括段落大意",
                "分析文章结构和写作手法",
                "做阅读理解练习题"
            ],
            "grammar": [
                "系统学习语法知识",
                "多做语法练习题",
                "在实际写作中运用语法",
                "对比分析不同句式"
            ],
            "poetry": [
                "背诵经典诗词",
                "分析诗词的意象和情感",
                "了解诗人的生平和时代背景",
                "尝试创作简单的诗歌"
            ],
            "classical": [
                "背诵经典文言文段落",
                "练习文言文翻译",
                "了解古代文化背景",
                "对比古今语言差异"
            ],
            "general": [
                "制定学习计划",
                "多做练习题",
                "及时复习巩固",
                "寻求老师指导"
            ]
        }
        return suggestions_map.get(task_type, suggestions_map["general"])

    def _extract_main_topics(self) -> List[str]:
        """提取主要话题"""
        # 简化的实现，实际应用中可以使用更复杂的NLP处理
        topics = []
        for msg in self.conversation_history:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if "写作" in content:
                    topics.append("写作指导")
                elif "阅读" in content:
                    topics.append("阅读理解")
                elif "语法" in content:
                    topics.append("语法学习")
                elif "诗词" in content:
                    topics.append("诗词鉴赏")
                elif "文言文" in content:
                    topics.append("文言文学习")
        return list(set(topics)) if topics else ["中文学习"]

    def process_query(self, query: str) -> str:
        """处理用户查询 - 使用AgentExecutor"""
        result = self.agent_executor.invoke({"input": query})
        return result.get("output", result.get("result", ""))

    def process_query_with_context(self, query: str, context: Dict[str, Any] = None) -> str:
        """处理用户查询 - 支持完整上下文"""
        if not context:
            # 如果没有上下文，使用原来的方法
            return self.process_query(query)

        # 获取对话历史
        conversation_history = context.get("conversation_history", [])
        session_id = context.get("session_id", "")

        # 构建包含历史对话的提示
        if conversation_history:
            # 有对话历史，构建上下文
            context_prompt = "以下是我们的对话历史：\n\n"
            for i, turn in enumerate(conversation_history[-6:], 1):  # 保留最近6轮对话
                role = "用户" if turn.get("role") == "user" else "AI助手"
                content = turn.get("content", "")
                context_prompt += f"{i}. {role}: {content}\n"
            context_prompt += f"\n当前问题: {query}\n\n请基于以上对话历史回答当前问题。"
        else:
            # 没有对话历史，直接使用原问题
            context_prompt = query

        # 使用AgentExecutor处理
        try:
            result = self.agent_executor.invoke({"input": context_prompt})
            return result.get("output", result.get("result", ""))
        except Exception as e:
            print(f"AgentExecutor处理失败: {e}")
            # 回退到基础方法
            return self._fallback_process_query_with_context(query, context)

    def _fallback_process_query_with_context(self, query: str, context: Dict[str, Any] = None) -> str:
        """回退的带上下文查询处理方法"""
        conversation_history = context.get("conversation_history", []) if context else []

        # 构建消息列表
        messages = [
            SystemMessage(content="你是一位经验丰富的中文老师，请根据学生的问题和对话历史提供详细的解答和指导。")
        ]

        # 添加历史对话（限制数量避免token过多）
        for turn in conversation_history[-4:]:  # 保留最近4轮对话
            if turn.get("role") == "user":
                messages.append(HumanMessage(content=turn.get("content", "")))
            elif turn.get("role") == "assistant":
                messages.append(AIMessage(content=turn.get("content", "")))

        # 添加当前问题
        messages.append(HumanMessage(content=query))

        # 调用LLM
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果已经在异步环境中，使用线程池
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(lambda: asyncio.run(self.llm.ainvoke(messages)))
                    response = future.result()
            else:
                response = asyncio.run(self.llm.ainvoke(messages))
            return response.content
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return "抱歉，处理您的问题时出现了错误，请稍后再试。"

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


def get_chinese_agent():
    return ChineseTeacherAgent()
