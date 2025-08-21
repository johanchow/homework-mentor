"""
考试API模块 - 处理考试相关的HTTP请求 - FastAPI异步版本
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from entity.exam import Exam, ExamStatus, create_exam
from dao.question_dao import question_dao
from dao.exam_dao import exam_dao
from utils.jwt_utils import verify_token, get_current_user_id
from utils.exceptions import DataNotFoundException, ValidationException, BusinessException
import json
import logging

logger = logging.getLogger(__name__)

exam_router = APIRouter(prefix="/exam", tags=["考试管理"])


# 请求模型
class CreateExamRequest(BaseModel):
    goal_id: str
    examinee_id: str
    question_ids: List[str]
    plan_starttime: str
    plan_duration: int


class FinishExamRequest(BaseModel):
    id: str
    answer_json: Dict[str, Any]


class ExamResponse(BaseModel):
    code: int = 0
    message: str
    data: Optional[Dict[str, Any]] = None

class UpdateExamRequest(BaseModel):
    id: str
    plan_starttime: Optional[str] = None
    plan_duration: Optional[int] = None
    status: Optional[ExamStatus] = None
    material: Optional[str] = None
    question_ids: Optional[List[str]] = None




@exam_router.post("/create", response_model=ExamResponse)
async def create_exam_api(request: CreateExamRequest, current_user_id: str = Depends(get_current_user_id)):
    """创建考试"""
    try:
        # 创建考试
        exam = create_exam(**request.dict())

        # 保存到数据库
        saved_exam = await exam_dao.create(exam)
        print(saved_exam.to_dict())

        return ExamResponse(
            message='考试创建成功',
            data=saved_exam.to_dict()
        )

    except Exception as e:
        logger.exception(f"创建考试失败: {e}")
        raise HTTPException(status_code=500, detail="创建考试失败，请稍后重试")


@exam_router.post("/finish", response_model=ExamResponse)
async def finish_exam(request: FinishExamRequest, current_user_id: str = Depends(get_current_user_id)):
    """提交考试答卷（只能修改answer_json字段）"""
    try:
        # 验证考试是否存在
        exam = await exam_dao.get_by_id(request.id)
        if not exam:
            raise DataNotFoundException("考试", request.id)

        # 更新答案
        exam.answer_json = json.dumps(request.answer_json)
        exam.status = ExamStatus.completed
        updated_exam = await exam_dao.update(exam)

        return ExamResponse(
            message='答卷更新成功',
            data=updated_exam.to_dict()
        )

    except BusinessException:
        raise

    except Exception as e:
        logger.exception(f"更新考试答卷失败: {e}")
        raise HTTPException(status_code=500, detail="更新答卷失败，请稍后重试")


@exam_router.delete("/delete")
async def delete_exam(id: str = Query(..., description="考试ID"), current_user_id: str = Depends(get_current_user_id)):
    """删除考试（软删除）"""
    try:
        # 验证考试是否存在
        exam = await exam_dao.get_by_id(id)
        if not exam:
            raise DataNotFoundException("考试", id)

        # 软删除
        exam.is_deleted = True
        await exam_dao.update(exam)

        return ExamResponse(message='考试删除成功')

    except BusinessException:
        raise

    except Exception as e:
        logger.exception(f"删除考试失败: {e}")
        raise HTTPException(status_code=500, detail="删除考试失败，请稍后重试")


@exam_router.get("/get")
async def get_exam(id: str = Query(..., description="考试ID"), current_user_id: str = Depends(get_current_user_id)):
    """获取单个考试详情"""
    try:
        # 获取考试详细信息
        exam = await exam_dao.get_by_id(id)
        if not exam:
            raise DataNotFoundException("考试", id)

        # 构建返回数据
        exam_data = exam.to_dict()
        if exam.question_ids and len(exam.question_ids) > 0:
            question_id_list = exam.question_ids.split(',')
            questions = await question_dao.search_by_kwargs({'id': {'$in': question_id_list}})
            exam_data['questions'] = [q.to_dict() for q in questions]

    except BusinessException:
        raise

    except Exception as e:
        logger.exception(f"获取考试详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取考试详情失败，请稍后重试")

    exam_data['questions'].sort(key=lambda x: question_id_list.index(x['id']))
    return ExamResponse(
        message='获取考试详情成功',
        data=exam_data
    )


@exam_router.get("/list")
async def list_exams(
    plan_starttime_from: Optional[str] = Query(None, description="开始时间（大于等于）"),
    plan_starttime_to: Optional[str] = Query(None, description="结束时间（小于等于）"),
    goal_id: Optional[str] = Query(None, description="目标ID"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    current_user_id: str = Depends(get_current_user_id)
):
    """获取考试列表"""
    try:
        # 计算分页参数
        skip = (page - 1) * page_size
        limit = page_size

        # 构建查询条件
        kwargs = {'is_deleted': False, 'examinee_id': current_user_id}
        
        if goal_id:
            kwargs['goal_id'] = goal_id
        # 添加时间过滤条件
        if plan_starttime_from and plan_starttime_to:
            # 如果同时有开始和结束时间，使用between
            kwargs['plan_starttime'] = {"$between": [plan_starttime_from, plan_starttime_to]}
        elif plan_starttime_from:
            # 只有开始时间
            kwargs['plan_starttime'] = {"$gte": plan_starttime_from}
        elif plan_starttime_to:
            # 只有结束时间
            kwargs['plan_starttime'] = {"$lte": plan_starttime_to}

        # 查询考试列表
        exams = await exam_dao.search_by_kwargs(kwargs, skip, limit)
        total = await exam_dao.count_by_kwargs(kwargs)

        # 转换为字典格式
        exam_list = [exam.to_dict() for exam in exams]

        return ExamResponse(
            message='获取考试列表成功',
            data={
                'exams': exam_list,
                'total': total,
                'page': page,
                'page_size': page_size,
                'pages': (total + page_size - 1) // page_size
            }
        )

    except Exception as e:
        logger.exception(f"获取考试列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取考试列表失败，请稍后重试")


@exam_router.put("/update", response_model=ExamResponse)
async def update_exam(request: UpdateExamRequest, current_user_id: str = Depends(get_current_user_id)):
    """更新考试"""
    try:
        # 验证考试是否存在
        exam = await exam_dao.get_by_id(request.id)
        if not exam:
            raise DataNotFoundException("考试", request.id)

        # 更新考试
        request_exam = Exam.from_dict(request.dict())
        for key, value in request_exam.model_dump().items():
            if value is not None:
                setattr(exam, key, value)
        updated_exam = await exam_dao.update(exam)


        return ExamResponse(
            message='更新考试成功',
            data=updated_exam.to_dict()
        )

    except Exception as e:
        logger.exception(f"更新考试失败: {e}")
        raise HTTPException(status_code=500, detail="更新考试失败，请稍后重试")
