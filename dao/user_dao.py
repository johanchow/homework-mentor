"""
用户数据访问对象 (DAO) - 处理用户相关的数据库操作
"""

from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, update, delete
from entity.user import User
from dao.database import get_engine
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class UserDAO:
    """用户数据访问对象"""

    def __init__(self):
        self.engine = get_engine()

    def create_user(self, user: User) -> User:
        """创建用户"""
        try:
            with Session(self.engine) as session:
                session.add(user)
                session.commit()
                session.refresh(user)
                logger.info(f"创建用户成功: {user.id}")
                return user
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            raise

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        try:
            with Session(self.engine) as session:
                statement = select(User).where(User.id == user_id, User.is_deleted == False)
                user = session.exec(statement).first()
                return user
        except Exception as e:
            logger.error(f"获取用户失败 (ID: {user_id}): {e}")
            raise

    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        try:
            with Session(self.engine) as session:
                statement = select(User).where(User.email == email, User.is_deleted == False)
                user = session.exec(statement).first()
                return user
        except Exception as e:
            logger.error(f"获取用户失败 (Email: {email}): {e}")
            raise

    def search_users(self, name: str = None, email: str = None, phone: str = None) -> List[User]:
        """搜索用户"""
        try:
            with Session(self.engine) as session:
                statement = select(User).where(User.is_deleted == False)

                if name:
                    statement = statement.where(User.name.contains(name))
                if email:
                    statement = statement.where(User.email.contains(email))
                if phone:
                    statement = statement.where(User.phone.contains(phone))

                users = session.exec(statement).all()
                return users
        except Exception as e:
            logger.error(f"搜索用户失败: {e}")
            raise

    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """更新用户信息"""
        try:
            with Session(self.engine) as session:
                # 添加更新时间
                update_data['updated_at'] = datetime.now()

                statement = (
                    update(User)
                    .where(User.id == user_id, User.is_deleted == False)
                    .values(**update_data)
                )
                session.exec(statement)
                session.commit()

                # 返回更新后的用户
                return self.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"更新用户失败 (ID: {user_id}): {e}")
            raise

    def delete_user(self, user_id: str) -> bool:
        """软删除用户"""
        try:
            with Session(self.engine) as session:
                statement = (
                    update(User)
                    .where(User.id == user_id)
                    .values(is_deleted=True, updated_at=datetime.now())
                )
                result = session.exec(statement)
                session.commit()
                logger.info(f"删除用户成功: {user_id}")
                return True
        except Exception as e:
            logger.error(f"删除用户失败 (ID: {user_id}): {e}")
            raise

    def activate_user(self, user_id: str) -> Optional[User]:
        """激活用户"""
        return self.update_user(user_id, {"is_active": True})

    def deactivate_user(self, user_id: str) -> Optional[User]:
        """停用用户"""
        return self.update_user(user_id, {"is_active": False})


# 创建全局DAO实例
user_dao = UserDAO()
