"""
闲聊Agent - 专门负责闲聊
"""

from .base_agent import BaseAgent
from entity.session import Session
from entity.message import Message
from typing import Dict, Any

class GossipAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def _process_guide(self, session: Session, latest_message: Message) -> str:
        """处理闲聊查询"""
        # 构建消息
        messages = [
            Message(role="system", content="你是一个友好的AI助手，擅长闲聊和日常对话。"),
            latest_message
        ]
        llm_messages = [msg.to_llm_message() for msg in messages]
        result = await self.llm.ainvoke(llm_messages)
        return result.content

    async def _process_raise(self, session: Session, latest_message: Message) -> str:
        pass

    async def process_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理任务的核心方法"""
        pass

def get_gossip_agent():
    return GossipAgent()
