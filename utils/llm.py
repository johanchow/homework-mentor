from langchain_community.chat_models import ChatTongyi

class LLM:
    @staticmethod
    def get_text_llm(temperature: float = 0.0):
        return ChatTongyi(model="qwen-plus", temperature=temperature)

    @staticmethod
    def get_image_llm(temperature: float = 0.0):
        return ChatTongyi(model="qwen-vl-plus", temperature=temperature)
