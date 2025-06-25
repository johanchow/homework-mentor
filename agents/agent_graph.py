from typing import TypedDict, List, Any, Annotated, Sequence
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph.graph import CompiledGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.llm import LLM
from entity.question import Question, Subject, QuestionType, create_question
from .chinese_agent import get_chinese_agent
from .gossip_agent import get_gossip_agent
class AgentState(TypedDict):
    # 题目
    question: Question
    messages: Annotated[Sequence[BaseMessage], add_messages]

def decide_route(state: AgentState):
    return state["question"].subject


# Define the function that calls the model
def call_chinese_teacher(state: AgentState):
    print('call_chinese_teacher', state)
    chinese_agent = get_chinese_agent()
    response = chinese_agent.process_ask(state["question"], state["messages"])
    return {"messages": response}

def call_gossip_agent(state: AgentState):
    gossip_agent = get_gossip_agent()
    response = gossip_agent.process_ask(state["question"], state["messages"])
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

    question = create_question(
        subject=Subject.CHINESE,
        question_type=QuestionType.MULTIPLE_CHOICE,
        title="下列词语中加点字的读音完全正确的一项是",
        content="A. 憧憬(chōng jǐng) B. 憧憬(chōng jìng) C. 憧憬(chōng jīng) D. 憧憬(chōng jīng)",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        difficulty=3,
        points=5,
        tags=["语文", "字音", "选择题"]
    )

    app = create_workflow()
    resp1 = app.invoke({
        "messages": ["这个题目有几个选项呢？"],
        "question": question,
    }, config={"configurable": {"thread_id": "1234567890"}})
    print('resp1', resp1)

    resp2 = app.invoke({
        "messages": ["我刚刚问了什么问题？"],
        "question": question,
    }, config={"configurable": {"thread_id": "1234567890"}})
    print('resp2', resp2)

