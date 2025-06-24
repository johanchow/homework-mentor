"""
闲聊Agent - 专门负责闲聊
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from langchain.schema import HumanMessage, SystemMessage, AIMessage

class GossipAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def process_query(self, query: str) -> str:
        return self.llm.invoke(query)

    def process_query_with_context(self, query: str, context: Dict[str, Any] = None) -> str:
        """处理用户查询 - 支持完整上下文"""
        if not context:
            # 如果没有上下文，使用原来的方法
            return self.process_query(query)

        # 获取对话历史
        conversation_history = context.get("conversation_history", [])

        # 构建消息列表
        messages = [
            SystemMessage(content="你是一个友好的AI助手，可以进行轻松的闲聊对话。请保持友好、幽默和自然的语气。")
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
        try:
            response = self.llm.invoke(messages)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return "抱歉，我现在有点忙，稍后再聊吧！"


def get_gossip_agent():
    return GossipAgent()
