import os
from langchain_community.chat_models import ChatOpenAI
from utils.env import EnvUtils

class LLM:
    @staticmethod
    def get_text_llm(temperature: float = 0.0):
        return ChatOpenAI(
            openai_api_key=EnvUtils.get_required_env("DASHSCOPE_API_KEY"),
            openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen-plus",
        )

    @staticmethod
    def get_image_llm(temperature: float = 0.0):
        return ChatOpenAI(
            openai_api_key=EnvUtils.get_required_env("DASHSCOPE_API_KEY"),
            openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen-vl-plus",
        )
