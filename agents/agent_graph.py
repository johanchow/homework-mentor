from typing import TypedDict, List, Any
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.graph.graph import CompiledGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.llm import LLM
from entity.question import Question, Subject
from .chinese_agent import get_chinese_agent
from .gossip_agent import get_gossip_agent
class AgentState(TypedDict):
    # 题目
    question: Question
    messages: List[Any]

def decide_route(state: AgentState):
    print('decide_route: ', state["question"].subject)
    return {"subject": state["question"].subject}


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


def create_workflow() -> CompiledGraph:
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
    app = graph.compile(checkpointer=memory)
    return app


if __name__ == "__main__":
    from dotenv import load_dotenv
    print('----------- load_dotenv -----------')
    load_dotenv('.env')
    app = create_workflow()
    resp = app.invoke({
        "messages": ["你好，我是小明，我想学习中文。"]},
        config={"configurable": {"thread_id": "1234567890"}})
    print('resp', resp)