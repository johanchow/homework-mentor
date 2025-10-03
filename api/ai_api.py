"""
AI API模块 - 处理AI相关的HTTP请求 - FastAPI异步版本
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import json
from agents.agent_graph import agent_graph
from agents.summary_agent import SummaryAgent
from entity.session import create_session, TopicType
from dao.session_dao import session_dao
from dao.question_dao import question_dao
from entity.message import create_message, MessageRole, MessageType
from entity.question import create_question
import service.ocr_service as ocr_service
from utils.exceptions import DataNotFoundException, ValidationException
from utils.jwt_utils import get_current_user_id
from service.extract_file_word import extract_text_from_file_url

logger = logging.getLogger(__name__)

ai_router = APIRouter(prefix="/ai", tags=["AI服务"])


# 统一响应模型
class BaseResponse(BaseModel):
    code: int = 0
    message: str
    data: Optional[Dict[str, Any]] = None

class UserChatMessage(BaseModel):
    text: str
    image_url: Optional[str] = None

# 请求模型
class GenerateQuestionsRequest(BaseModel):
    ai_prompt: str
    subject: str
    count: int
    session_id: Optional[str] = None

class ParseQuestionsRequest(BaseModel):
    image_urls: List[str]

class AnalyzeQuestionRequest(BaseModel):
    question: Dict[str, Any]

class GuideQuestionRequest(BaseModel):
    question_id: str
    new_message: UserChatMessage
    session_id: Optional[str] = None

class GossipChatRequest(BaseModel):
    new_message: UserChatMessage
    session_id: Optional[str] = None


@ai_router.post("/guide-question", response_model=BaseResponse)
async def guide_question(request: GuideQuestionRequest, current_user_id: str = Depends(get_current_user_id)):
    """引导用户分析题目"""
    logger.info(f"/guide-question收到请求: {request.new_message}")
    print(f"/guide-question收到请求: {request.new_message}")
    if request.new_message.image_url:
        content = [
            {"type": "text", "text": request.new_message.text},
            {"type": "image_url", "image_url": {"url": request.new_message.image_url}}
        ]
    else:
        content = request.new_message.text

    try:
        question = await question_dao.get_by_id(request.question_id)
        if not question:
            raise DataNotFoundException(data_type="question", data_id=request.question_id)
        
        is_new_session = False
        if not request.session_id:
            session = create_session(TopicType.GUIDE, question)
            is_new_session = True
        else:
            session = await session_dao.get_by_id(request.session_id)
            if not session:
                session = create_session(TopicType.GUIDE, question)
                is_new_session = True
            else:
                session.question = question

        state = await agent_graph.ainvoke({
            "session": session,
            "latest_message": create_message(
                role=MessageRole.USER,
                content=content,
            )
        })
        if is_new_session:
            await session_dao.create(session)
        else:
            await session_dao.update(session)

        ai_resp_message = session.get_messages()[-1].content
        return BaseResponse(
            message="success",
            data={
                "session_id": session.id,
                "ai_message": ai_resp_message
            }
        )
        
    except DataNotFoundException:
        raise
    except Exception as e:
        logger.exception(f"引导题目分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"引导题目分析失败: {str(e)}")

@ai_router.post("/gossip-chat", response_model=BaseResponse)
async def gossip_chat(request: GossipChatRequest, current_user_id: str = Depends(get_current_user_id)):
    """闲聊"""
    logger.info(f"/gossip-chat收到请求: {request.new_message}")
    print(f"/gossip-chat收到请求: {request.new_message}")
    if request.new_message.image_url:
        content = [
            {"type": "text", "text": request.new_message.text},
            {"type": "image_url", "image_url": {"url": request.new_message.image_url}}
        ]
    else:
        content = request.new_message.text

    try:
        if not request.session_id:
            session = create_session(TopicType.GOSSIP, None)
        else:
            session = await session_dao.get_by_id(request.session_id)
            if not session:
                session = create_session(TopicType.GOSSIP, None)

        state = await agent_graph.ainvoke({
            "session": session,
            "latest_message": create_message(
                role=MessageRole.USER,
                content=content,
            )
        })
    except Exception as e:
        logger.error(f"分析问题失败了: {e}")
        raise e

    ai_resp_message = session.get_messages()[-1].content
    logger.info(f"/gossip-chat返回结果: {ai_resp_message}")
    return BaseResponse(
        message="success",
        data={
            "session_id": session.id,
            "ai_message": ai_resp_message
        }
    )


@ai_router.post("/generate-questions", response_model=BaseResponse)
async def generate_questions(request: GenerateQuestionsRequest, current_user_id: str = Depends(get_current_user_id)):
    """创建AI"""
    try:
        if not request.session_id:
            session = create_session(TopicType.RAISE, '')
        else:
            session = await session_dao.get_full_by_id(request.session_id)

        # 创建goal流程，需要一并出题，这时候并没有已存在goal
        if not session._goal:
            from entity.goal import create_goal
            session._goal = create_goal(name='', subject=request.subject, ai_prompt=request.ai_prompt, creator_id='')

        new_message = create_message(
            role=MessageRole.USER,
            content=f"{request.ai_prompt}\n请根据提示生成{request.count}个题目",
            message_type=MessageType.TEXT
        )
        state = await agent_graph.ainvoke({
            "session": session,
            "latest_message": new_message,
        }, config={"configurable": {"thread_id": request.session_id}})
        questions = state.get('questions')

        # 添加用户消息
        session.add_message(create_message(
            role=MessageRole.USER,
            content=request.ai_prompt,
            message_type=MessageType.TEXT
        ))
        if request.session_id:
            await session_dao.update(session)
        else:
            await session_dao.create(session)

        return BaseResponse(
            message="success",
            data={
                "questions": [q.to_dict() for q in questions],
                "session_id": session.id
            }
        )

    except Exception as e:
        logger.error(f"生成问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成问题失败: {str(e)}")


@ai_router.post("/parse-questions-from-images", response_model=BaseResponse)
async def parse_questions_from_images(request: ParseQuestionsRequest, current_user_id: str = Depends(get_current_user_id)):
    """从图片中解析题目"""
    try:
        logger.info(f'开始从图片中提取题目，图片数量: {len(request.image_urls)}')
        if not request.image_urls:
            raise ValidationException("image_urls", "图片列表不能为空")
        
        results = ocr_service.read_text_from_image(request.image_urls[0])
        all_text = '\n'.join([result.text for result in results])
        logger.info(f'从图片中提取的全部文字: {all_text}')
        print(f'从图片中提取的全部文字: {all_text}')

        # 调用AI解析题目
        summary_agent = SummaryAgent()        
        questions = await summary_agent.process_input(all_text)
        logger.info(f'完成从图片中提取题目，题目数量: {len(questions)}')
        
        return BaseResponse(
            message='success',
            data={
                'questions': [q.to_dict() for q in questions]
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"解析图片失败: {e}")
        raise HTTPException(status_code=500, detail=f"解析图片失败: {str(e)}")

@ai_router.post("/analyze-question", response_model=BaseResponse)
async def analyze_question(request: AnalyzeQuestionRequest, current_user_id: str = Depends(get_current_user_id)):
    """分析题目和答案"""
    try:
        question = create_question(**request.question)
        question.refresh_material()
        
        return BaseResponse(
            message="success",
            data={
                "question": question.to_dict()
            }
        )

    except Exception as e:
        logger.error(f"分析题目失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析题目失败: {str(e)}")

class ExtractWordsRequest(BaseModel):
    file_url: str

@ai_router.post("/extract-words", response_model=BaseResponse)
async def extract_words(request: ExtractWordsRequest, current_user_id: str = Depends(get_current_user_id)):
    """提取图片中的文字"""
    image_text = extract_text_from_file_url(request.file_url)
    return BaseResponse(
        message="success",
        data={
            "words": image_text
        }
    )
