from fastapi import APIRouter, Depends, Query, Body, Request
from dao.session_dao import session_dao
from utils.jwt_utils import get_current_user_id
from utils.exceptions import DataNotFoundException
from api.question_api import BaseResponse
import logging

logger = logging.getLogger(__name__)

session_router = APIRouter(prefix="/session", tags=["Session服务"])

@session_router.get("/get")
async def get_session(id: str, current_user_id: str = Depends(get_current_user_id)):
    session = await session_dao.get_by_id(id)
    if not session:
        raise DataNotFoundException(data_type="session", data_id=id)

    return BaseResponse(
        message="success",
        data=session.to_dict()
    )
