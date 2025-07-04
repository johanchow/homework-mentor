"""
中文老师Agent - 专门负责中文教学指导和答疑
"""

import json
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import asyncio
from datetime import datetime
from utils.llm import LLM
from entity.session import Session
from entity.message import Message, MessageRole

class ChineseTeacherAgent(BaseAgent):
    """中文老师Agent - 负责中文教学指导和答疑"""

    def __init__(self, agent_id: Optional[str] = None, **kwargs):
        super().__init__(agent_id, **kwargs)
        # 存储对话历史，支持多轮问答
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_session_id: Optional[str] = None
        self.llm = LLM.get_image_llm()

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

当学生提出语文题目或问题时，你需要：
1. 仔细分析题目内容和学生问题
2. 理解问题的核心和难点
3. 提供解决问题的思路和方法
4. 解释相关的语文学习原则
5. 用具体例子说明

请针对用户的问题，进行解答提示。"""),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder("agent_scratchpad"),  # 必须有这个，LangChain内部把执行记录写入到这个变量
            {
                "role": "human",
                "content": [{
                    "type": "image",
                    "image_url": {
                        "url": "https://gips2.baidu.com/it/u=1651586290,17201034&fm=3028&app=3028&f=JPEG&fmt=auto&q=100&size=f600_800"
                    }
                }, {
                    "type": "text",
                    "text": "{input}"
                }]
            }
        ])

        agent = create_openai_functions_agent(self.llm, tools=[], prompt=prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=[])

    def process_ask(self, session: Session, latest_message: Message) -> str:
        """处理用户查询 - 使用AgentExecutor"""
        prompt_message = Message(role=MessageRole.SYSTEM, content="你是一位经验丰富的中文老师，擅长语文教学和指导。")
        question_message = session.question.to_message()
        history_messages = session.get_messages()
        all_messages = [prompt_message] + [question_message] + history_messages + [latest_message]
        llm_chat_messages = [msg.to_llm_message() for msg in all_messages]
        result = self.llm.invoke(llm_chat_messages)
        print('get ask result', result.content)
        return result.content

    def _fallback_process_ask(self, query: str) -> str:
        """回退的查询处理方法"""
        messages = [
            SystemMessage(content="你是一位经验丰富的中文老师，请根据学生的问题提供详细的解答和指导。"),
            HumanMessage(content=query)
        ]

        # 这里需要同步调用，因为这是回退方法
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
        except:
            return "抱歉，处理您的问题时出现了错误，请稍后再试。"

    async def process_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理中文教学任务"""

        # 检查是否是对话任务
        if context and context.get("is_conversation", False):
            return await self._handle_conversation(task, context)

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
