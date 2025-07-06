from typing import TypedDict, List, Any, Annotated, Sequence
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import BaseMessage
from langgraph.graph.graph import CompiledGraph
from utils.llm import LLM
from entity.question import Question, Subject, QuestionType
from entity.message import Message, MessageRole, create_message
from entity.session import Session, TopicType
from .chinese_agent import get_chinese_agent
from .gossip_agent import get_gossip_agent
class AgentState(TypedDict):
    # 会话
    session: Session
    # 最新消息
    latest_message: Message
    # 出题列表
    questions: List[Question]
    # messages: Annotated[Sequence[BaseMessage], add_messages]

def decide_route(state: AgentState):
    if state["session"].topic == TopicType.QUESTION:
        subject = state["session"]._question.subject
        return f"{subject}-topic-question"
    else:
        subject = state["session"]._goal.subject
        return f"{subject}-topic-goal"


# Define the function that calls the model
def call_chinese_teacher(state: AgentState):
    print('call_chinese_teacher', state)
    chinese_agent = get_chinese_agent()
    session = state["session"]
    resp_content = chinese_agent.process_ask(state["session"], state["latest_message"])
    session.add_message(Message(role=MessageRole.ASSISTANT, content=resp_content))
    return {"session": session}

def call_chinese_questioner(state: AgentState):
    chinese_agent = get_chinese_agent()
    session = state["session"]
    questions = chinese_agent.generate_questions(state["session"], state["latest_message"])
    return {"session": session, "questions": questions}

def call_gossip_agent(state: AgentState):
    gossip_agent = get_gossip_agent()
    response = gossip_agent.process_ask(state["session"], state["latest_message"])
    return {"messages": response}


def create_workflow() -> CompiledGraph:
    # Define a new graph
    graph = StateGraph(state_schema=AgentState)

    # Define the (single) node in the graph
    graph.add_node("chinese-topic-question", call_chinese_teacher)
    graph.add_node("chinese-topic-goal", call_chinese_questioner)
    graph.add_node("gossip", call_gossip_agent)
    graph.add_conditional_edges(
        START,
        decide_route,
    )

    # Add memory
    memory = MemorySaver()
    app = graph.compile()
    return app


agent_graph = create_workflow()


if __name__ == "__main__":
    from dotenv import load_dotenv
    print('----------- load_dotenv -----------')
    load_dotenv('.env')

    question = Question(
        subject=Subject.CHINESE,
        question_type=QuestionType.MULTIPLE_CHOICE,
        title="请描述下面图片内容",
        images=[
            "https://gips2.baidu.com/it/u=1651586290,17201034&fm=3028&app=3028&f=JPEG&fmt=auto&q=100&size=f600_800",
        ]
    )
    session = Session(session_id="1234567890", question=question)
    message1 = Message.from_dict({
        "role": "user",
        "content":  "一般可以从哪些角度描述图片？",
    })
    resp1 = agent_graph.invoke({
        "session": session,
        "latest_message": message1,
    }, config={"configurable": {"thread_id": "1234567890"}})
    print('resp1', resp1)

    message2 = Message.from_dict({
        "role": "user",
        "content": "我刚刚问了什么问题?"
    })
    resp2 = agent_graph.invoke({
        "session": session,
        "latest_message": message2,
    }, config={"configurable": {"thread_id": "1234567890"}})
    print('resp2', resp2)

