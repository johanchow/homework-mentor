
"""
录入题目Agent - 专门负责录入题目
"""

from abc import ABC
import json
from typing import Dict, Any, List, Optional
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import asyncio
from utils.llm import LLM
from entity.message import Message, MessageRole
from entity.question import Question
from utils.transformer import markdown_to_json

class TypistAgent(ABC):
    """录入题目Agent - 负责录入题目"""

    def __init__(self, agent_id: Optional[str] = None, **kwargs):
        # super().__init__(agent_id, **kwargs)
        self.system_prompt: Message = Message(role=MessageRole.SYSTEM, content="""
	用户会可能会传入一段文字、或者若干个图片，里面都应该是多个小学题目。也可能会包含一点杂乱无用的信息。

题目的全部类型有： 选择题(choice)、判断题(judge)、填空题(fill)、问答题(qa)
题目的全部学科有: chinese、math、english、science、social、other

请你帮我提取出全部文字和全部图片中的所有题目。每道题请用以下 JSON 格式输出.

举例1:
[题目] 小明有3个苹果，给了小红1个，下面哪个说法正确？ A. 小明还剩2个 B. 小明还剩1个 C. 小红拥有2个 D. 小红拥有3个
[输出] { "title": "小明有3个苹果，给了小红1个，下面哪个说法正确？", "subject": "math",
  "images_coords": [{ "coords_2d": [] }],
  "type": "choice", "options": ["小明还剩2个", "小明还剩1个", "小红拥有2个","小红拥有3个"] }

举例2:
[题目] 请看下面的图，然后数一数，填一填。
[输出] { "title": "请看下面的图，然后数一数，填一填", "subject": "math",
  "images_coords": [{ "coords_2d": [ [ x1, y1 ], [ x2, y1 ], [ x1, y2 ], [ x2, y2 ] ] }],
  "type": "qa" }

说明：
每道题目是一组编号、文字，可能还有图的组合。如果题目中包含图片，请把相关图像转为 坐标形式（以左上角为原点）
忽略可能有的广告、页眉页脚等无关内容; 尽可能完整识别题干，保留题号、选项等
请返回所有题目的 JSON 列表。
""")
        self.llm = LLM.get_image_llm()

        # 初始化AgentExecutor
        self._init_agent()

    def _init_agent(self):
        """初始化AgentExecutor"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位经验丰富的中文老师，擅长语文教学和指导。
请针对用户的问题，进行解答提示。"""),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder("agent_scratchpad"),  # 必须有这个，LangChain内部把执行记录写入到这个变量
        ])

        agent = create_openai_functions_agent(self.llm, tools=[], prompt=prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=[])

    def process_input(self, latest_message: Message) -> List[Question]:
        """处理用户查询 - 使用AgentExecutor"""
        all_messages = [self.system_prompt] + [latest_message]
        llm_chat_messages = [msg.to_llm_message() for msg in all_messages]
        result = self.llm.invoke(llm_chat_messages)
        print('get ask result: ', result.content)
        print(type(result.content))  # 应该是 <class 'str'>
        try:
            question_dicts = json.loads(markdown_to_json(result.content))
        except Exception as e:
            print('json.loads ask result error: ', e)
            return []
        questions = [Question.from_dict(question) for question in question_dicts]
        return questions

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
