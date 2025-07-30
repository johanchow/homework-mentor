"""
问题API - 提供问题相关的RESTful接口 - FastAPI异步版本
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import logging
from dao.question_dao import question_dao
from dao.user_dao import user_dao
from entity.question import Question, QuestionType, Subject, create_question
from utils.jwt_utils import verify_token, get_current_user_id
from utils.exceptions import DataNotFoundException, ValidationException, BusinessException

logger = logging.getLogger(__name__)

question_router = APIRouter(prefix="/question", tags=["问题管理"])


# 统一响应模型
class BaseResponse(BaseModel):
    code: int = 0
    message: str
    data: Optional[Dict[str, Any]] = None


# 请求模型
class QuestionCreateRequest(BaseModel):
    """创建问题的请求模型"""
    subject: Subject
    type: QuestionType
    title: str
    creator_id: str
    options: Optional[List[str]] = None
    images: Optional[List[str]] = None
    audios: Optional[List[str]] = None
    videos: Optional[List[str]] = None


class QuestionUpdateRequest(BaseModel):
    """更新问题的请求模型"""
    subject: Optional[Subject] = None
    type: Optional[QuestionType] = None
    title: Optional[str] = None
    options: Optional[List[str]] = None
    images: Optional[List[str]] = None
    audios: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    is_active: Optional[bool] = None


class QuestionBatchCreateRequest(BaseModel):
    """批量创建问题的请求模型"""
    questions: List[QuestionCreateRequest]


# 响应模型
class QuestionResponse(BaseModel):
    """问题响应模型"""
    id: str
    subject: Subject
    type: QuestionType
    title: str
    options: Optional[str] = None
    images: Optional[str] = None
    audios: Optional[str] = None
    videos: Optional[str] = None
    creator_id: str
    created_at: str
    updated_at: str
    is_active: bool
    is_deleted: bool

    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    """问题列表响应模型"""
    questions: List[QuestionResponse]
    total: int
    skip: int
    limit: int


class QuestionBatchCreateResponse(BaseModel):
    """批量创建问题响应模型"""
    questions: List[QuestionResponse]


async def validate_creator_exists(creator_id: str) -> bool:
    """验证创建人是否存在"""
    creator = await user_dao.get_by_id(creator_id)
    return creator is not None


# API接口

@question_router.post("/create", response_model=BaseResponse)
async def create_question_api(request: QuestionCreateRequest, current_user_id: str = Depends(get_current_user_id)):
    """
    创建单个问题

    请求参数:
    - subject: 科目
    - type: 问题类型
    - title: 题干
    - creator_id: 创建人ID
    - options: 选项列表（可选）
    - images: 图片列表（可选）
    - audios: 音频列表（可选）
    - videos: 视频列表（可选）
    """
    try:
        # 验证创建人是否存在
        creator = await user_dao.get_by_id(request.creator_id)
        if not creator:
            raise DataNotFoundException("创建人", request.creator_id)

        # 创建问题
        question = create_question(
            subject=request.subject,
            type=request.type,
            title=request.title,
            creator_id=request.creator_id,
            options=request.options,
            images=request.images,
            audios=request.audios,
            videos=request.videos
        )

        # 保存到数据库
        created_question = await question_dao.create(question)

        logger.info(f"创建问题成功: {created_question.id}")
        return BaseResponse(
            message='问题创建成功',
            data=created_question.to_dict()
        )

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"创建问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建问题失败: {str(e)}")





@question_router.put("/{question_id}", response_model=BaseResponse)
async def update_question_api(question_id: str, request: QuestionUpdateRequest, current_user_id: str = Depends(get_current_user_id)):
    """
    更新问题信息

    路径参数:
    - question_id: 问题ID

    请求参数:
    - subject: 科目（可选）
    - type: 问题类型（可选）
    - title: 题干（可选）
    - options: 选项列表（可选）
    - images: 图片列表（可选）
    - audios: 音频列表（可选）
    - videos: 视频列表（可选）
    - is_active: 是否激活（可选）
    """
    try:
        # 获取现有问题
        question = await question_dao.get_by_id(question_id)
        if not question:
            raise DataNotFoundException("问题", question_id)

        # 更新字段
        if request.subject is not None:
            question.subject = request.subject
        if request.type is not None:
            question.type = request.type
        if request.title is not None:
            question.title = request.title
        if request.options is not None:
            question.options = ",".join(request.options) if request.options else None
        if request.images is not None:
            question.images = ",".join(request.images) if request.images else None
        if request.audios is not None:
            question.audios = ",".join(request.audios) if request.audios else None
        if request.videos is not None:
            question.videos = ",".join(request.videos) if request.videos else None
        if request.is_active is not None:
            question.is_active = request.is_active

        # 保存更新
        updated_question = await question_dao.update(question)

        logger.info(f"更新问题成功: {updated_question.id}")
        return BaseResponse(
            message='问题更新成功',
            data=updated_question.to_dict()
        )

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"更新问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新问题失败: {str(e)}")


@question_router.delete("/{question_id}", response_model=BaseResponse)
async def delete_question_api(question_id: str, current_user_id: str = Depends(get_current_user_id)):
    """
    删除问题（软删除）

    路径参数:
    - question_id: 问题ID
    """
    try:
        # 获取问题
        question = await question_dao.get_by_id(question_id)
        if not question:
            raise DataNotFoundException("问题", question_id)

        # 软删除
        await question_dao.delete(question)

        logger.info(f"删除问题成功: {question_id}")
        return BaseResponse(
            message='问题删除成功',
            data={"question_id": question_id}
        )

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"删除问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除问题失败: {str(e)}")


@question_router.get("/list", response_model=BaseResponse)
async def list_questions_api(
    subject: Optional[str] = Query(None, description="科目筛选"),
    question_type: Optional[str] = Query(None, description="问题类型筛选"),
    creator_id: Optional[str] = Query(None, description="创建人ID筛选"),
    is_active: Optional[bool] = Query(None, description="是否激活筛选"),
    page: int = Query(1, description="页码，默认1"),
    page_size: int = Query(10, description="每页数量，默认10"),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    获取问题列表，支持筛选和分页

    查询参数:
    - subject: 科目筛选（可选）
    - type: 问题类型筛选（可选）
    - creator_id: 创建人ID筛选（可选）
    - is_active: 是否激活筛选（可选）
    - page: 页码，默认1
    - page_size: 每页数量，默认10
    """
    try:
        # 计算分页参数
        skip = (page - 1) * page_size
        limit = page_size

        # 构建筛选条件
        filters = {}
        if subject is not None:
            filters["subject"] = subject
        if question_type is not None:
            filters["type"] = question_type
        if creator_id is not None:
            filters["creator_id"] = creator_id
        if is_active is not None:
            filters["is_active"] = is_active

        # 查询问题列表
        questions = await question_dao.search_by_kwargs(filters, skip=skip, limit=limit)

        # 统计总数
        total = await question_dao.count_by_kwargs(filters)

        # 转换为响应格式
        question_responses = [q.to_dict() for q in questions]

        return BaseResponse(
            message='获取问题列表成功',
            data={
                'questions': question_responses,
                'total': total,
                'page': page,
                'page_size': page_size,
                'pages': (total + page_size - 1) // page_size
            }
        )

    except Exception as e:
        logger.exception(f"获取问题列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取问题列表失败: {str(e)}")


@question_router.get("/get", response_model=BaseResponse)
async def get_question_api(id: str = Query(..., description="问题ID"), current_user_id: str = Depends(get_current_user_id)):
    """
    根据ID获取问题详情

    路径参数:
    - question_id: 问题ID
    """
    try:
        question = await question_dao.get_by_id(id)
        if not question:
            raise DataNotFoundException("问题", id)

        return BaseResponse(
            message='获取问题详情成功',
            data=question.to_dict()
        )

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"获取问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取问题失败: {str(e)}")



@question_router.post("/batch-create", response_model=BaseResponse)
async def batch_create_questions_api(request: QuestionBatchCreateRequest, current_user_id: str = Depends(get_current_user_id)):
    """
    批量创建问题

    请求参数:
    - questions: 问题列表
    """
    try:
        if not request.questions:
            raise ValidationException("questions", "缺少问题列表")

        questions = []
        errors = []

        for index, question_data in enumerate(request.questions):
            # 验证创建人是否存在
            creator = await user_dao.get_by_id(question_data.creator_id)
            if not creator:
                raise DataNotFoundException(f"第{index+1}个问题创建人", question_data.creator_id)

            # 创建问题
            question = create_question(
                subject=question_data.subject,
                type=question_data.type,
                title=question_data.title,
                creator_id=question_data.creator_id,
                options=question_data.options,
                images=question_data.images,
                audios=question_data.audios,
                videos=question_data.videos
            )
            questions.append(question)

        # 批量保存到数据库
        created_questions: List[Question] = await question_dao.batch_create(questions)
        logger.info(f"批量创建问题成功: {created_questions}")

        # 转换为响应格式
        question_responses = [q.to_dict() for q in created_questions]

        return BaseResponse(
            message='批量创建问题完成',
            data={
                'questions': question_responses,
            }
        )

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"批量创建问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量创建问题失败: {str(e)}")

