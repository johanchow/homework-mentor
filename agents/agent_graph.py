from typing import TypedDict, List, Any
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from .chinese_agent import get_chinese_agent
from .gossip_agent import get_gossip_agent
class AgentState(TypedDict):
    messages: List[Any]
    # 学科
    subject: str

def decide_route(state: AgentState):
    return "chinese"

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
    graph.add_edge(START, "chinese")
    graph.add_node("route", decide_route)
    graph.add_node("chinese", call_chinese_teacher)
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