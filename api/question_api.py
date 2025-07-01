"""
问题API - 提供问题相关的RESTful接口
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from entity.question import Question, QuestionType, Subject, create_question
from dao.question_dao import question_dao
from dao.user_dao import user_dao
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/questions", tags=["questions"])


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
    created_count: int
    failed_count: int
    questions: List[QuestionResponse]
    errors: List[str]


# 工具函数
def question_to_response(question: Question) -> QuestionResponse:
    """将Question实体转换为响应模型"""
    return QuestionResponse(
        id=question.id,
        subject=question.subject,
        type=question.type,
        title=question.title,
        options=question.options,
        images=question.images,
        audios=question.audios,
        videos=question.videos,
        creator_id=question.creator_id,
        created_at=question.created_at.isoformat(),
        updated_at=question.updated_at.isoformat(),
        is_active=question.is_active,
        is_deleted=question.is_deleted
    )


def validate_creator_exists(creator_id: str) -> bool:
    """验证创建人是否存在"""
    creator = user_dao.get_by_id(creator_id)
    return creator is not None


# API接口

@router.post("/", response_model=QuestionResponse, summary="创建问题")
async def create_question_api(request: QuestionCreateRequest):
    """
    创建单个问题
    
    - **subject**: 科目
    - **type**: 问题类型
    - **title**: 题干
    - **creator_id**: 创建人ID
    - **options**: 选项列表（可选）
    - **images**: 图片列表（可选）
    - **audios**: 音频列表（可选）
    - **videos**: 视频列表（可选）
    """
    try:
        # 验证创建人是否存在
        if not validate_creator_exists(request.creator_id):
            raise HTTPException(status_code=400, detail="创建人不存在")
        
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
        created_question = question_dao.create(question)
        
        logger.info(f"创建问题成功: {created_question.id}")
        return question_to_response(created_question)
        
    except Exception as e:
        logger.error(f"创建问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建问题失败: {str(e)}")


@router.get("/{question_id}", response_model=QuestionResponse, summary="获取问题详情")
async def get_question_api(question_id: str):
    """
    根据ID获取问题详情
    
    - **question_id**: 问题ID
    """
    try:
        question = question_dao.get_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="问题不存在")
        
        return question_to_response(question)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取问题失败: {str(e)}")


@router.put("/{question_id}", response_model=QuestionResponse, summary="更新问题")
async def update_question_api(question_id: str, request: QuestionUpdateRequest):
    """
    更新问题信息
    
    - **question_id**: 问题ID
    - **subject**: 科目（可选）
    - **type**: 问题类型（可选）
    - **title**: 题干（可选）
    - **options**: 选项列表（可选）
    - **images**: 图片列表（可选）
    - **audios**: 音频列表（可选）
    - **videos**: 视频列表（可选）
    - **is_active**: 是否激活（可选）
    """
    try:
        # 获取现有问题
        question = question_dao.get_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="问题不存在")
        
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
        updated_question = question_dao.update(question)
        
        logger.info(f"更新问题成功: {updated_question.id}")
        return question_to_response(updated_question)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新问题失败: {str(e)}")


@router.delete("/{question_id}", summary="删除问题")
async def delete_question_api(question_id: str):
    """
    删除问题（软删除）
    
    - **question_id**: 问题ID
    """
    try:
        # 获取问题
        question = question_dao.get_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="问题不存在")
        
        # 软删除
        question_dao.delete(question)
        
        logger.info(f"删除问题成功: {question_id}")
        return {"message": "问题删除成功", "question_id": question_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除问题失败: {str(e)}")


@router.get("/", response_model=QuestionListResponse, summary="获取问题列表")
async def list_questions_api(
    subject: Optional[Subject] = Query(None, description="科目筛选"),
    type: Optional[QuestionType] = Query(None, description="问题类型筛选"),
    creator_id: Optional[str] = Query(None, description="创建人ID筛选"),
    is_active: Optional[bool] = Query(None, description="是否激活筛选"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量")
):
    """
    获取问题列表，支持筛选和分页
    
    - **subject**: 科目筛选（可选）
    - **type**: 问题类型筛选（可选）
    - **creator_id**: 创建人ID筛选（可选）
    - **is_active**: 是否激活筛选（可选）
    - **skip**: 跳过数量，默认0
    - **limit**: 返回数量，默认100，最大1000
    """
    try:
        # 构建筛选条件
        filters = {}
        if subject is not None:
            filters["subject"] = subject
        if type is not None:
            filters["type"] = type
        if creator_id is not None:
            filters["creator_id"] = creator_id
        if is_active is not None:
            filters["is_active"] = is_active
        
        # 查询问题列表
        questions = question_dao.search_by_kwargs(filters, skip=skip, limit=limit)
        
        # 统计总数
        total = question_dao.count_by_kwargs(filters)
        
        # 转换为响应格式
        question_responses = [question_to_response(q) for q in questions]
        
        return QuestionListResponse(
            questions=question_responses,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"获取问题列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取问题列表失败: {str(e)}")


@router.post("/batch", response_model=QuestionBatchCreateResponse, summary="批量创建问题")
async def batch_create_questions_api(request: QuestionBatchCreateRequest):
    """
    批量创建问题
    
    - **questions**: 问题列表
    """
    try:
        created_questions = []
        errors = []
        created_count = 0
        failed_count = 0
        
        for question_request in request.questions:
            try:
                # 验证创建人是否存在
                if not validate_creator_exists(question_request.creator_id):
                    errors.append(f"创建人不存在: {question_request.creator_id}")
                    failed_count += 1
                    continue
                
                # 创建问题
                question = create_question(
                    subject=question_request.subject,
                    type=question_request.type,
                    title=question_request.title,
                    creator_id=question_request.creator_id,
                    options=question_request.options,
                    images=question_request.images,
                    audios=question_request.audios,
                    videos=question_request.videos
                )
                
                # 保存到数据库
                created_question = question_dao.create(question)
                created_questions.append(created_question)
                created_count += 1
                
                logger.info(f"批量创建问题成功: {created_question.id}")
                
            except Exception as e:
                error_msg = f"创建问题失败: {str(e)}"
                errors.append(error_msg)
                failed_count += 1
                logger.error(f"批量创建问题失败: {error_msg}")
        
        # 转换为响应格式
        question_responses = [question_to_response(q) for q in created_questions]
        
        return QuestionBatchCreateResponse(
            created_count=created_count,
            failed_count=failed_count,
            questions=question_responses,
            errors=errors
        )
        
    except Exception as e:
        logger.error(f"批量创建问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量创建问题失败: {str(e)}")

