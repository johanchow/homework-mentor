from typing import TypedDict, List, Any
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.llm import LLM
from .chinese_agent import get_chinese_agent
from .gossip_agent import get_gossip_agent

class AgentState(TypedDict):
    messages: List[Any]
    # 学科
    subject: str

def decide_route(state: AgentState):
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
    print('user question', state["messages"][-1])
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"question": state["messages"][-1]})
    print('decide_route response', response)
    return {"subject": response}

# Define the function that calls the model
def call_chinese_teacher(state: AgentState):
    print('call_chinese_teacher', state)
    chinese_agent = get_chinese_agent()
    response = chinese_agent.process_query(state["messages"])
    return {"messages": response}

def call_gossip_agent(state: AgentState):
    gossip_agent = get_gossip_agent()
    response = gossip_agent.process_query(state["messages"])
    return {"messages": response}


def create_workflow():
    # Define a new graph
    graph = StateGraph(state_schema=AgentState)

    # Define the (single) node in the graph
    graph.add_node("route", decide_route)
    graph.add_node("chinese", call_chinese_teacher)
    graph.add_edge(START, "route")
    graph.add_conditional_edges(
        "route",
        decide_route,
    )

    # Add memory
    memory = MemorySaver()
    app = graph.compile()
    return app


if __name__ == "__main__":
    from dotenv import load_dotenv
    print('----------- load_dotenv -----------')
    load_dotenv('.env')
    app = create_workflow()
    resp = app.invoke({"messages": ["你好，我是小明，我想学习中文。"]})
    print('resp', resp)