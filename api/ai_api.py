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
from agents.parse_image_agent import ParseImageAgent
from entity.session import create_session, TopicType
from dao.session_dao import session_dao
from entity.message import create_message, MessageRole, MessageType
from entity.question import create_question
from utils.jwt_utils import verify_token

logger = logging.getLogger(__name__)

ai_router = APIRouter(prefix="/ai", tags=["AI服务"])


# 统一响应模型
class BaseResponse(BaseModel):
    code: int = 0
    message: str
    data: Optional[Dict[str, Any]] = None


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


# 认证依赖
async def get_current_user_id(request: Request) -> str:
    """获取当前用户ID"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="缺少认证token")
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效或过期的token")
    
    return payload.get('user_id')

logger = logging.getLogger(__name__)



@ai_router.post("/generate-questions", response_model=BaseResponse)
async def generate_questions(request: GenerateQuestionsRequest, current_user_id: str = Depends(get_current_user_id)):
    """创建AI"""
    try:
        if not session_id:
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
        state = agent_graph.invoke({
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
            raise HTTPException(status_code=400, detail="images is required")
        
        # 调用AI解析题目
        parse_image_agent = ParseImageAgent()
        # 创建包含图片的消息
        image_contents = [{"type": "image_url", "image_url": {"url": image}} for image in request.image_urls]
        message = create_message(
            role=MessageRole.USER,
            content=image_contents
        )
        questions = parse_image_agent.process_input(message)
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


