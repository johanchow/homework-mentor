from fastapi import APIRouter, HTTPException, Depends, Query, Body, Request
from dao.session_dao import session_dao
from utils.jwt_utils import get_current_user_id
from utils.exceptions import AuthenticationException, DataNotFoundException, PermissionException
import logging

logger = logging.getLogger(__name__)

session_router = APIRouter(prefix="/session", tags=["Session服务"])

@session_router.get("/get")
async def get_session(session_id: str, current_user_id: str = Depends(get_current_user_id)):
    session = await session_dao.get_by_id(session_id)
    if not session:
        raise DataNotFoundException(data_type="session", data_id=session_id)
    if session.user_id != current_user_id:
        raise PermissionException(message="无权限访问")
    return session.to_dict()
