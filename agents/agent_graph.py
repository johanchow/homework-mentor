from typing import TypedDict, List, Any, Dict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from utils.llm import LLM
from .chinese_agent import get_chinese_agent
from .gossip_agent import get_gossip_agent

class AgentState(TypedDict):
    messages: List[Any]
    # 学科
    subject: str
    # 对话历史
    conversation_history: List[Dict[str, Any]]
    # 当前会话ID
    session_id: str

def decide_route(state: AgentState):
    """决定路由到哪个agent"""
    llm = LLM.get_text_llm()
    prompt = ChatPromptTemplate.from_template("""
    你是一个AI助手，根据用户的问题，判断用户的问题是否属于以下学科：
    1. 语文
    2. 英语
    3. 数学
    4. 闲谈(包括其他类问题和非问题)
    只需要返回学科名称，不需要其他内容
    如果是语文，返回"chinese"，如果是英语，返回"english"，如果是数学，返回"math"，如果是其他，返回"gossip"
    用户的问题是：{question}
    """)

    # 获取最新的用户消息
    latest_message = state["messages"][-1]
    if isinstance(latest_message, dict):
        question = latest_message.get("content", str(latest_message))
    elif hasattr(latest_message, 'content'):
        question = latest_message.content
    else:
        question = str(latest_message)

    print('user question', question)
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"question": question})
    print('decide_route response', response)

    # 清理响应，确保返回正确的路由
    response = response.strip().lower()
    if "chinese" in response or "语文" in response:
        return "chinese"
    elif "english" in response or "英语" in response:
        return "english"
    elif "math" in response or "数学" in response:
        return "math"
    else:
        return "gossip"

def call_chinese_teacher(state: AgentState):
    """调用中文老师agent"""
    print('call_chinese_teacher', state)
    chinese_agent = get_chinese_agent()

    # 获取最新的用户消息
    latest_message = state["messages"][-1]
    if isinstance(latest_message, dict):
        query = latest_message.get("content", str(latest_message))
    elif hasattr(latest_message, 'content'):
        query = latest_message.content
    else:
        query = str(latest_message)

    # 获取对话历史
    conversation_history = state.get("conversation_history", [])

    # 构建上下文信息
    context = {
        "session_id": state.get("session_id", ""),
        "conversation_history": conversation_history,
        "is_conversation": True,
        "subject": state.get("subject", "chinese")
    }

    # 处理查询 - 传递完整上下文
    response = chinese_agent.process_query_with_context(query, context)

    # 创建AI回复消息
    ai_message = AIMessage(content=response)

    # 更新对话历史
    conversation_history.append({
        "role": "user",
        "content": query,
        "timestamp": "2024-01-01T00:00:00Z"  # 实际应用中应该使用真实时间戳
    })
    conversation_history.append({
        "role": "assistant",
        "content": response,
        "timestamp": "2024-01-01T00:00:00Z"
    })

    return {
        "messages": [ai_message],
        "conversation_history": conversation_history
    }

def call_gossip_agent(state: AgentState):
    """调用闲聊agent"""
    print('call_gossip_agent', state)
    gossip_agent = get_gossip_agent()

    # 获取最新的用户消息
    latest_message = state["messages"][-1]
    if isinstance(latest_message, dict):
        query = latest_message.get("content", str(latest_message))
    elif hasattr(latest_message, 'content'):
        query = latest_message.content
    else:
        query = str(latest_message)

    # 获取对话历史
    conversation_history = state.get("conversation_history", [])

    # 构建上下文信息
    context = {
        "session_id": state.get("session_id", ""),
        "conversation_history": conversation_history,
        "is_conversation": True,
        "subject": state.get("subject", "gossip")
    }

    # 处理查询 - 传递完整上下文
    response = gossip_agent.process_query_with_context(query, context)

    # 创建AI回复消息
    ai_message = AIMessage(content=response)

    # 更新对话历史
    conversation_history.append({
        "role": "user",
        "content": query,
        "timestamp": "2024-01-01T00:00:00Z"
    })
    conversation_history.append({
        "role": "assistant",
        "content": response,
        "timestamp": "2024-01-01T00:00:00Z"
    })

    return {
        "messages": [ai_message],
        "conversation_history": conversation_history
    }

def create_workflow():
    """创建工作流"""
    # 定义状态图
    graph = StateGraph(state_schema=AgentState)

    # 添加节点
    graph.add_node("route", decide_route)
    graph.add_node("chinese", call_chinese_teacher)
    graph.add_node("gossip", call_gossip_agent)

    # 添加边
    graph.add_edge(START, "route")

    # 添加条件边
    graph.add_conditional_edges(
        "route",
        lambda x: x,  # 直接返回路由结果
        {
            "chinese": "chinese",
            "gossip": "gossip",
            "english": "gossip",  # 暂时路由到gossip
            "math": "gossip"      # 暂时路由到gossip
        }
    )

    # 从各个agent节点回到开始，支持多轮对话
    graph.add_edge("chinese", START)
    graph.add_edge("gossip", START)

    # 添加内存
    memory = MemorySaver()
    app = graph.compile(checkpointer=memory)
    return app

def create_conversation_session():
    """创建新的对话会话"""
    import uuid
    return {
        "session_id": str(uuid.uuid4()),
        "conversation_history": [],
        "subject": "",
        "messages": []
    }

if __name__ == "__main__":
    from dotenv import load_dotenv
    print('----------- load_dotenv -----------')
    load_dotenv('.env')

    app = create_workflow()

    # 创建会话
    session = create_conversation_session()

    # 第一轮对话
    print("=== 第一轮对话 ===")
    resp1 = app.invoke({
        "messages": [HumanMessage(content="你好，我是小明，我想学习中文。")],
        "session_id": session["session_id"],
        "conversation_history": session["conversation_history"],
        "subject": session["subject"]
    })
    print('第一轮回复:', resp1["messages"][-1].content if resp1["messages"] else "无回复")

    # 第二轮对话
    print("\n=== 第二轮对话 ===")
    resp2 = app.invoke({
        "messages": [HumanMessage(content="我想学习写作，有什么建议吗？")],
        "session_id": session["session_id"],
        "conversation_history": resp1.get("conversation_history", []),
        "subject": resp1.get("subject", "")
    })
    print('第二轮回复:', resp2["messages"][-1].content if resp2["messages"] else "无回复")

    # 第三轮对话
    print("\n=== 第三轮对话 ===")
    resp3 = app.invoke({
        "messages": [HumanMessage(content="今天天气怎么样？")],
        "session_id": session["session_id"],
        "conversation_history": resp2.get("conversation_history", []),
        "subject": resp2.get("subject", "")
    })
    print('第三轮回复:', resp3["messages"][-1].content if resp3["messages"] else "无回复")