"""
目标API - 提供目标相关的RESTful接口 - FastAPI异步版本
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
from entity.goal import Goal, GoalStatus, Subject, create_goal
from dao.goal_dao import goal_dao
from dao.user_dao import user_dao
from utils.jwt_utils import verify_token
from utils.exceptions import DataNotFoundException, ValidationException, BusinessException

logger = logging.getLogger(__name__)

goal_router = APIRouter(prefix="/goal", tags=["目标管理"])


# 统一响应模型
class BaseResponse(BaseModel):
    code: int = 0
    message: str
    data: Optional[Dict[str, Any]] = None


# 请求模型
class CreateGoalRequest(BaseModel):
    name: str
    subject: Subject
    ai_prompt: Optional[str] = None
    creator_id: str
    status: Optional[GoalStatus] = GoalStatus.PREPARING


class UpdateGoalRequest(BaseModel):
    name: Optional[str] = None
    subject: Optional[Subject] = None
    status: Optional[GoalStatus] = None
    ai_prompt: Optional[str] = None


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


def goal_to_response(goal: Goal) -> dict:
    """将Goal实体转换为响应格式"""
    return {
        "id": goal.id,
        "name": goal.name,
        "subject": goal.subject,
        "status": goal.status,
        "ai_prompt": goal.ai_prompt,
        "creator_id": goal.creator_id,
        "created_at": goal.created_at.isoformat(),
        "updated_at": goal.updated_at.isoformat(),
        "is_deleted": goal.is_deleted
    }


async def validate_creator_exists(creator_id: str) -> bool:
    """验证创建人是否存在"""
    creator = await user_dao.get_by_id(creator_id)
    return creator is not None


# API接口

@goal_router.post("/create", response_model=BaseResponse)
async def create_goal_api(request: CreateGoalRequest, current_user_id: str = Depends(get_current_user_id)):
    """
    创建目标

    请求参数:
    - name: 目标名称
    - subject: 科目
    - ai_prompt: AI提示词
    - creator_id: 创建人ID
    - status: 目标状态（可选，默认为pending）
    """
    try:
        # 验证创建人是否存在
        creator = await user_dao.get_by_id(request.creator_id)
        if not creator:
            raise DataNotFoundException("创建人", request.creator_id)

        # 创建目标
        goal = create_goal(
            name=request.name,
            subject=request.subject,
            ai_prompt=request.ai_prompt,
            creator_id=request.creator_id,
            status=request.status
        )

        # 保存到数据库
        created_goal = await goal_dao.create(goal)

        logger.info(f"创建目标成功: {created_goal.id}")
        return BaseResponse(
            message='目标创建成功',
            data=goal_to_response(created_goal)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建目标失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建目标失败: {str(e)}")


@goal_router.get("/list", response_model=BaseResponse)
async def list_goals_api(
    name: Optional[str] = Query(None, description="目标名称过滤"),
    subject: Optional[str] = Query(None, description="科目过滤"),
    creator_id: Optional[str] = Query(None, description="创建人ID过滤"),
    page: int = Query(1, description="页码，默认1"),
    page_size: int = Query(10, description="每页数量，默认10"),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    获取目标列表，支持筛选和分页

    查询参数:
    - name: 目标名称过滤（可选）
    - subject: 科目过滤（可选）
    - status: 状态过滤（可选）
    - creator_id: 创建人ID过滤（可选）
    - page: 页码，默认1
    - page_size: 每页数量，默认10
    """
    try:
        # 计算分页参数
        skip = (page - 1) * page_size
        limit = page_size

        # 构建筛选条件
        filters = {}
        if name is not None:
            filters["name"] = name
        if subject is not None:
            filters["subject"] = subject
        if creator_id is not None:
            filters["creator_id"] = creator_id

        goals = await goal_dao.search_by_kwargs(filters, skip=skip, limit=limit)
        total = await goal_dao.count_by_kwargs(filters)

        # 转换为响应格式
        goal_responses = [goal_to_response(g) for g in goals]

        return BaseResponse(
            message='获取目标列表成功',
            data={
                'goals': goal_responses,
                'total': total,
                'page': page,
                'page_size': page_size,
                'pages': (total + page_size - 1) // page_size
            }
        )

    except Exception as e:
        logger.error(f"获取目标列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取目标列表失败: {str(e)}")


@goal_router.get("/get", response_model=BaseResponse)
async def get_goal_api(id: str = Query(..., description="目标ID"), current_user_id: str = Depends(get_current_user_id)):
    """
    根据ID获取目标详情

    路径参数:
    - goal_id: 目标ID
    """
    try:
        goal = await goal_dao.get_by_id(id)
        if not goal:
            raise DataNotFoundException("目标", id)

        return BaseResponse(
            message='获取目标详情成功',
            data=goal_to_response(goal)
        )

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"获取目标失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取目标失败: {str(e)}")


@goal_router.put("/{goal_id}", response_model=BaseResponse)
async def update_goal_api(goal_id: str, request: UpdateGoalRequest, current_user_id: str = Depends(get_current_user_id)):
    """
    更新目标

    路径参数:
    - goal_id: 目标ID

    请求参数:
    - name: 目标名称（可选）
    - subject: 科目（可选）
    - status: 目标状态（可选）
    - ai_prompt: AI提示词（可选）
    """
    try:
        # 获取现有目标
        goal = await goal_dao.get_by_id(goal_id)
        if not goal:
            raise DataNotFoundException("目标", goal_id)

        # 更新字段
        if request.name is not None:
            goal.name = request.name
        if request.subject is not None:
            goal.subject = request.subject
        if request.status is not None:
            goal.status = request.status
        if request.ai_prompt is not None:
            goal.ai_prompt = request.ai_prompt

        # 更新修改时间
        goal.updated_at = datetime.now()

        # 保存到数据库
        updated_goal = await goal_dao.update(goal)

        logger.info(f"更新目标成功: {goal_id}")
        return BaseResponse(
            message='目标更新成功',
            data=goal_to_response(updated_goal)
        )

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"更新目标失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新目标失败: {str(e)}")


@goal_router.delete("/delete", response_model=BaseResponse)
async def delete_goal_api(id: str = Query(..., description="目标ID"), current_user_id: str = Depends(get_current_user_id)):
    """
    删除目标（软删除）

    路径参数:
    - goal_id: 目标ID
    """
    try:
        # 获取目标
        goal = await goal_dao.get_by_id(id)
        if not goal:
            raise DataNotFoundException("目标", id)

        # 软删除
        await goal_dao.delete(goal)

        logger.info(f"删除目标成功: {id}")
        return BaseResponse(
            message='目标删除成功',
            data={"id": id}
        )

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"删除目标失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除目标失败: {str(e)}")
