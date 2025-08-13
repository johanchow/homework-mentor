"""
基础Agent类 - 定义所有Agent的通用接口和功能
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
import asyncio
from datetime import datetime, timezone
from langchain.chat_models.base import init_chat_model
from langchain_community.chat_models import ChatTongyi
from entity.session import Session
from entity.message import Message, create_message, MessageRole
from entity.question import Question
from utils.transformer import markdown_to_json
from utils.helpers import random_uuid
from service.vector_service import vector_service
from agents.prompt import get_import_prompt

class AgentState(BaseModel):
    """Agent状态模型"""
    agent_id: str
    agent_type: str
    status: str = "idle"  # idle, busy, completed, error
    current_task: Optional[str] = None
    task_history: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}


class BaseAgent(ABC):
    """基础Agent抽象类"""

    def __init__(self, agent_id: Optional[str] = None, **kwargs):
        self.agent_id = agent_id or random_uuid()
        # 出题prompt - 用于生成题目的系统提示
        self.system_raise_prompt_template: Message = create_message(
            role=MessageRole.SYSTEM,
            content="你是一个教育类AI题库生成器。请根据用户的要求生成题目。"
        )
        # 答疑prompt - 用于回答问题的系统提示
        self.ask_prompt: Message = create_message(
            role=MessageRole.SYSTEM,
            content="你是一个经验丰富的老师，请根据学生的问题提供详细的解答和指导。"
        )
        # 导入题prompt
        self.system_import_prompt_template: Message = create_message(
            role=MessageRole.SYSTEM,
            content="你是一个教育老师。请根据题目基础信息，进行完善题目"
        )
        self.agent_type = self.__class__.__name__
        self.llm = ChatTongyi()
        # self.llm = init_chat_model("deepseek-r1", model_provider="deepseek")
        # self.llm = init_chat_model(model="gemini-1.5-flash", temperature=0.7, **kwargs)
        # self.llm = ChatOpenAI(
        #     model="gpt-3.5-turbo",
        #     temperature=0.7,
        #     **kwargs
        # )
        self.state = AgentState(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    async def process_guide(self, session: Session, latest_message: Message) -> str:
        """处理用户查询"""
        resp_content = await self._process_guide(session, latest_message)
        session.add_message(Message(role=MessageRole.USER, content=latest_message.content))
        session.add_message(Message(role=MessageRole.ASSISTANT, content=resp_content))
        return resp_content

    @abstractmethod
    async def _process_guide(self, session: Session, latest_message: Message) -> str:
        """处理用户查询"""
        pass

    async def process_raise(self, session: Session, latest_message: Message) -> List['Question']:
        """出题"""
        content = await self._process_raise(session, latest_message)
        try:
            question_dicts = json.loads(markdown_to_json(content))
        except Exception as e:
            print('json.loads generate questions result error: ', e)
            return []
        questions = [Question.from_dict(question) for question in question_dicts]
        return questions

    def process_import(self, session: Session, latest_message: Message) -> 'Question':
        """导入题目"""
        messages = get_import_prompt(session.question)
        llm_chat_messages = [msg.to_llm_message() for msg in messages]
        result = self.llm.invoke(llm_chat_messages)
        result = {
            "content": json.dumps({
                "material": "It's sunny today, I want to go to the park"
            })
        }
        print('process_import result: ', result)
        question_dict = json.loads(markdown_to_json(result['content']))
        question = session.question
        question.material = question_dict['material']
        return question

    def get_system_raise_prompt(self, session: Session, latest_message: Message) -> Message:
        """获取系统提示"""
        # 根据科目找到全部题目，并且向量化；然后根据用户的问题，找到最相似的题目，然后生成系统提示
        near_questions: List[Question] = vector_service.list_sematic_near_questions(session._goal.subject, latest_message.content)
        system_raise_prompt = self.system_raise_prompt_template.content
        if len(near_questions) > 0:
            system_raise_prompt += "\n\n例如: "
            for question in near_questions:
                # 构建选项字符串
                options_str = f'"options": {question.options},' if question.type == 'choice' and question.options else ""
                images_str = f'"images": {question.images},' if question.images else ""
                audios_str = f'"audios": {question.audios},' if question.audios else ""
                videos_str = f'"videos": {question.videos},' if question.videos else ""
                
                # 过滤掉空字符串，避免产生空行
                non_empty_fields = [field for field in [options_str, images_str, audios_str, videos_str] if field]
                
                # 构建JSON内容
                json_content = f'  "title": "{question.title}",\n  "subject": "{question.subject.value}",\n  "type": "{question.type.value}"'
                if non_empty_fields:
                    json_content += f',\n  {chr(10).join(non_empty_fields)}'
                
                system_raise_prompt += f"""
{{
{json_content}
}}
                """
        return create_message(role=MessageRole.SYSTEM, content=system_raise_prompt)

    @abstractmethod
    async def _process_raise(self, session: Session, latest_message: Message) -> str:
        pass

    @abstractmethod
    async def process_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理任务的核心方法"""
        pass

    def can_handle(self, task: str) -> bool:
        """判断是否能处理指定任务"""
        # 简单的关键词匹配，可以扩展为更复杂的逻辑
        task_lower = task.lower()
        for capability in self.capabilities:
            if capability.lower() in task_lower:
                return True
        return False

    def get_workload(self) -> float:
        """获取当前工作负载 (0-1)"""
        if self.state.status == "idle":
            return 0.0
        elif self.state.status == "busy":
            return 0.7
        else:
            return 1.0

    def update_state(self, status: str, task: Optional[str] = None, metadata: Dict[str, Any] = None):
        """更新Agent状态"""
        self.state.status = status
        self.state.updated_at = datetime.now(timezone.utc)

        if task:
            self.state.current_task = task

        if metadata:
            self.state.metadata.update(metadata)

        # 记录任务历史
        if task:
            self.state.task_history.append({
                "task": task,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            })

    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行任务的主方法"""
        try:
            self.update_state("busy", task)

            # 执行具体任务
            result = await self.process_task(task, context)

            self.update_state("completed", task, {"result": result})
            return {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "status": "completed",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.update_state("error", task, {"error": str(e)})
            return {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态信息"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.state.status,
            "current_task": self.state.current_task,
            "workload": self.get_workload(),
            "capabilities": self.capabilities,
            "created_at": self.state.created_at.isoformat(),
            "updated_at": self.state.updated_at.isoformat(),
            "task_count": len(self.state.task_history)
        }
