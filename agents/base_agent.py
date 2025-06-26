"""
基础Agent类 - 定义所有Agent的通用接口和功能
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
import asyncio
import uuid
from datetime import datetime
from langchain.chat_models.base import init_chat_model
from langchain_community.chat_models import ChatTongyi
from entity.session import Session
from entity.message import Message

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
        self.agent_id = agent_id or str(uuid.uuid4())
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
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @abstractmethod
    def process_ask(self, session: Session, latest_message: Message) -> str:
        """处理用户查询"""
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
        self.state.updated_at = datetime.now()

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
