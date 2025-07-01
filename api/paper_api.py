"""
试卷API - 提供试卷相关的RESTful接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from entity.paper import Paper, create_paper
from entity.question import Question
from dao.paper_dao import paper_dao
from dao.user_dao import user_dao
from dao.question_dao import question_dao
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/papers", tags=["papers"])


# 请求模型
class PaperCreateRequest(BaseModel):
    """创建试卷的请求模型"""
    title: str
    description: Optional[str] = None
    creator_id: str
    question_ids: Optional[List[str]] = None


class PaperUpdateRequest(BaseModel):
    """更新试卷的请求模型 - 只能修改answer_json"""
    answer_json: str


# 响应模型
class QuestionResponse(BaseModel):
    """问题响应模型"""
    id: str
    subject: str
    type: str
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


class PaperResponse(BaseModel):
    """试卷响应模型"""
    id: str
    title: str
    description: Optional[str] = None
    question_ids: str
    creator_id: str
    created_at: str
    updated_at: str
    is_deleted: bool

    class Config:
        from_attributes = True


class PaperDetailResponse(BaseModel):
    """试卷详情响应模型（包含问题信息）"""
    id: str
    title: str
    description: Optional[str] = None
    question_ids: str
    questions: List[QuestionResponse]
    creator_id: str
    creator_name: Optional[str] = None
    created_at: str
    updated_at: str
    is_deleted: bool


class PaperListResponse(BaseModel):
    """试卷列表响应模型"""
    papers: List[PaperResponse]
    total: int
    skip: int
    limit: int


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


def paper_to_response(paper: Paper) -> PaperResponse:
    """将Paper实体转换为响应模型"""
    return PaperResponse(
        id=paper.id,
        title=paper.title,
        description=paper.description,
        question_ids=paper.question_ids,
        creator_id=paper.creator_id,
        created_at=paper.created_at.isoformat(),
        updated_at=paper.updated_at.isoformat(),
        is_deleted=paper.is_deleted
    )


def paper_to_detail_response(paper: Paper) -> PaperDetailResponse:
    """将Paper实体转换为详情响应模型"""
    # 获取创建人信息
    creator_name = None
    if paper.creator_id:
        creator = user_dao.get_by_id(paper.creator_id)
        if creator:
            creator_name = creator.name
    
    # 获取问题列表
    questions = []
    if paper.question_ids:
        question_id_list = [qid.strip() for qid in paper.question_ids.split(',') if qid.strip()]
        for qid in question_id_list:
            question = question_dao.get_by_id(qid)
            if question:
                questions.append(question_to_response(question))
    
    return PaperDetailResponse(
        id=paper.id,
        title=paper.title,
        description=paper.description,
        question_ids=paper.question_ids,
        questions=questions,
        creator_id=paper.creator_id,
        creator_name=creator_name,
        created_at=paper.created_at.isoformat(),
        updated_at=paper.updated_at.isoformat(),
        is_deleted=paper.is_deleted
    )


def validate_creator_exists(creator_id: str) -> bool:
    """验证创建人是否存在"""
    creator = user_dao.get_by_id(creator_id)
    return creator is not None


def validate_questions_exist(question_ids: List[str]) -> bool:
    """验证问题是否都存在"""
    if not question_ids:
        return True
    
    for qid in question_ids:
        question = question_dao.get_by_id(qid)
        if not question:
            return False
    return True


# API接口

@router.post("/", response_model=PaperResponse, summary="创建试卷")
async def create_paper_api(request: PaperCreateRequest):
    """
    创建试卷
    
    - **title**: 试卷标题
    - **description**: 试卷描述（可选）
    - **creator_id**: 创建人ID
    - **question_ids**: 问题ID列表（可选）
    """
    try:
        # 验证创建人是否存在
        if not validate_creator_exists(request.creator_id):
            raise HTTPException(status_code=400, detail="创建人不存在")
        
        # 验证问题是否都存在
        if request.question_ids and not validate_questions_exist(request.question_ids):
            raise HTTPException(status_code=400, detail="部分问题不存在")
        
        # 创建试卷
        paper = create_paper(
            title=request.title,
            description=request.description,
            creator_id=request.creator_id,
            question_ids=request.question_ids
        )
        
        # 保存到数据库
        created_paper = paper_dao.create(paper)
        
        logger.info(f"创建试卷成功: {created_paper.id}")
        return paper_to_response(created_paper)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建试卷失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建试卷失败: {str(e)}")


@router.get("/{paper_id}", response_model=PaperDetailResponse, summary="获取试卷详情")
async def get_paper_api(paper_id: str):
    """
    根据ID获取试卷详情（包含问题信息）
    
    - **paper_id**: 试卷ID
    """
    try:
        paper = paper_dao.get_by_id(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="试卷不存在")
        
        return paper_to_detail_response(paper)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取试卷失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取试卷失败: {str(e)}")


@router.get("/", response_model=PaperListResponse, summary="获取试卷列表")
async def list_papers_api(
    creator_id: Optional[str] = Query(None, description="创建人ID筛选"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量")
):
    """
    获取试卷列表，支持筛选和分页
    
    - **creator_id**: 创建人ID筛选（可选）
    - **skip**: 跳过数量，默认0
    - **limit**: 返回数量，默认100，最大1000
    """
    try:
        # 构建筛选条件
        filters = {}
        if creator_id is not None:
            filters["creator_id"] = creator_id
        
        # 查询试卷列表
        papers = paper_dao.search_by_kwargs(filters, skip=skip, limit=limit)
        
        # 统计总数
        total = paper_dao.count_by_kwargs(filters)
        
        # 转换为响应格式
        paper_responses = [paper_to_response(p) for p in papers]
        
        return PaperListResponse(
            papers=paper_responses,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"获取试卷列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取试卷列表失败: {str(e)}")


@router.put("/{paper_id}/answer", response_model=PaperResponse, summary="更新试卷答案")
async def update_paper_answer_api(paper_id: str, request: PaperUpdateRequest):
    """
    更新试卷答案（只能修改answer_json）
    
    - **paper_id**: 试卷ID
    - **answer_json**: 答案JSON字符串
    """
    try:
        # 获取现有试卷
        paper = paper_dao.get_by_id(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="试卷不存在")
        
        # 注意：根据要求，这里只能修改answer_json
        # 但是Paper实体中没有answer_json字段，这里可能需要根据实际需求调整
        # 暂时返回错误，因为Paper实体中没有answer_json字段
        
        raise HTTPException(status_code=400, detail="Paper实体中没有answer_json字段，请检查实体定义")
        
        # 如果Paper实体中有answer_json字段，可以这样更新：
        # paper.answer_json = request.answer_json
        # updated_paper = paper_dao.update(paper)
        # return paper_to_response(updated_paper)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新试卷答案失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新试卷答案失败: {str(e)}")


@router.delete("/{paper_id}", summary="删除试卷")
async def delete_paper_api(paper_id: str):
    """
    删除试卷（软删除）
    
    - **paper_id**: 试卷ID
    """
    try:
        # 获取试卷
        paper = paper_dao.get_by_id(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="试卷不存在")
        
        # 软删除
        paper_dao.delete(paper)
        
        logger.info(f"删除试卷成功: {paper_id}")
        return {"message": "试卷删除成功", "paper_id": paper_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除试卷失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除试卷失败: {str(e)}")


# 额外的查询接口

@router.get("/by-creator/{creator_id}", response_model=PaperListResponse, summary="根据创建人获取试卷列表")
async def get_papers_by_creator_api(
    creator_id: str,
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量")
):
    """
    根据创建人获取试卷列表
    
    - **creator_id**: 创建人ID
    - **skip**: 跳过数量，默认0
    - **limit**: 返回数量，默认100，最大1000
    """
    try:
        papers = paper_dao.search_by_kwargs({"creator_id": creator_id}, skip=skip, limit=limit)
        total = paper_dao.count_by_kwargs({"creator_id": creator_id})
        
        paper_responses = [paper_to_response(p) for p in papers]
        
        return PaperListResponse(
            papers=paper_responses,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"根据创建人获取试卷列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"根据创建人获取试卷列表失败: {str(e)}")
