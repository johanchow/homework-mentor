from typing import TypedDict, List, Any, Annotated, Sequence
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import BaseMessage
from langgraph.graph.graph import CompiledGraph
from utils.llm import LLM
from entity.question import Question, Subject, QuestionType, MediaFile
from entity.message import Message
from entity.session import Session
from .chinese_agent import get_chinese_agent
from .gossip_agent import get_gossip_agent
class AgentState(TypedDict):
    # 题目
    session: Session
    # 最新消息
    latest_message: Message
    # messages: Annotated[Sequence[BaseMessage], add_messages]

def decide_route(state: AgentState):
    return state["session"].question.subject


# Define the function that calls the model
def call_chinese_teacher(state: AgentState):
    print('call_chinese_teacher', state)
    chinese_agent = get_chinese_agent()
    response = chinese_agent.process_ask(state["session"], state["latest_message"])
    return {"messages": response}

def call_gossip_agent(state: AgentState):
    gossip_agent = get_gossip_agent()
    response = gossip_agent.process_ask(state["session"], state["latest_message"])
    return {"messages": response}


def create_workflow() -> CompiledGraph:
    # Define a new graph
    graph = StateGraph(state_schema=AgentState)

    # Define the (single) node in the graph
    graph.add_node("chinese", call_chinese_teacher)
    graph.add_node("gossip", call_gossip_agent)
    graph.add_conditional_edges(
        START,
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

    question = Question(
        subject=Subject.CHINESE,
        question_type=QuestionType.MULTIPLE_CHOICE,
        title="请描述下面图片内容",
        images=[MediaFile(
            file_id="123",
            file_url="https://gips2.baidu.com/it/u=1651586290,17201034&fm=3028&app=3028&f=JPEG&fmt=auto&q=100&size=f600_800",
        )]
    )
    session = Session(session_id="1234567890", question=question)
    message1 = Message.from_dict({
        "role": "user",
        "content":  "一般可以从哪些角度描述图片？",
    })
    app = create_workflow()
    resp1 = app.invoke({
        "session": session,
        "latest_message": message1,
    }, config={"configurable": {"thread_id": "1234567890"}})
    print('resp1', resp1)

    message2 = Message.from_dict({
        "role": "user",
        "content": "我刚刚问了什么问题?"
    })
    resp2 = app.invoke({
        "session": session,
        "latest_message": message2,
    }, config={"configurable": {"thread_id": "1234567890"}})
    print('resp2', resp2)

