from openai import OpenAI
from langchain_community.chat_models import ChatOpenAI
from utils.env import EnvUtils
import numpy as np

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


class Embedding:
    client = OpenAI(
        api_key=EnvUtils.get_required_env("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    @staticmethod
    def get_embeddings(text_list):
        response = Embedding.client.embeddings.create(
            model="text-embedding-v4",
            input=text_list,
            dimensions=1024,  # 可选，建议使用默认或统一
            encoding_format="float"
        )
        vectors = [np.array(record.embedding, dtype='float32') for record in response.data]
        return vectors