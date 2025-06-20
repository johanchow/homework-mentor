from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from .chinese_agent import get_chinese_agent

# Define the function that calls the model
def call_chinese_teacher(state: MessagesState):
    chinese_agent = get_chinese_agent()
    response = chinese_agent.process_query(state["messages"])
    return {"messages": response}


def create_workflow():
    # Define a new graph
    graph = StateGraph(state_schema=MessagesState)

    # Define the (single) node in the graph
    graph.add_edge(START, "chinese")
    graph.add_node("chinese", call_chinese_teacher)

    # Add memory
    memory = MemorySaver()
    app = graph.compile()
    return app


if __name__ == "__main__":
    from dotenv import load_dotenv
    print('----------- load_dotenv -----------')
    load_dotenv('.env')
    app = create_workflow()
    app.invoke({"messages": ["你好，我是小明，我想学习中文。"]})