"""
闲聊Agent - 专门负责闲聊
"""

from .base_agent import BaseAgent

class GossipAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def process_guide(self, query: str) -> str:
        return self.llm.invoke(query)


def get_gossip_agent():
    return GossipAgent()
