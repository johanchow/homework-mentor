from abc import ABC, abstractmethod
from dao.database import get_engine
from typing import List
from sqlalchemy import func
from sqlmodel import Session, select, update, delete
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseDao(ABC):
    def __init__(self):
        self.engine = get_engine()

    def create(self, model: 'BaseModel'):
        try:
          with Session(self.engine) as session:
              session.add(model)
              session.commit()
              session.refresh(model)
              return model
        except Exception as e:
            logger.error(f"创建{model.__class__.__name__}失败: {e}")
            raise

    def update(self, model: 'BaseModel'):
        try:
          with Session(self.engine) as session:
              # 添加更新时间
              model.updated_at = datetime.now()
              statement = (
                  update(model.__class__)
                  .where(model.__class__.id == model.id, model.is_deleted == False)
                  .values(**model.dict())
              )
              session.exec(statement)
              session.commit()
              return self.get_by_id(model.id)
        except Exception as e:
            logger.error(f"更新{model.__class__.__name__}失败: {e}")
            raise

    def delete(self, model: 'BaseModel'):
        try:
          with Session(self.engine) as session:
              statement = (
                  update(model.__class__)
                  .where(model.__class__.id == model.id)
                  .values(is_deleted=True, updated_at=datetime.now())
              )
              session.exec(statement)
              session.commit()
              return True
        except Exception as e:
            logger.error(f"删除{model.__class__.__name__}失败: {e}")
            raise

    @abstractmethod
    def get_by_id(self, id: str) -> 'BaseModel':
        pass

    @abstractmethod
    def search_by_kwargs(self, kwargs: dict, skip: int = 0, limit: int = 100) -> List['BaseModel']:
        pass

    @abstractmethod
    def count_by_kwargs(self, kwargs: dict) -> int:
        pass

    def _get_by_id(self, Clazz: 'BaseModel', id: str) -> 'BaseModel':
        try:
            with Session(self.engine) as session:
                statement = select(Clazz).where(Clazz.id == id, Clazz.is_deleted == False)
                result = session.exec(statement).first()
                return result
        except Exception as e:
            logger.error(f"获取{Clazz.__name__}的id={id}失败: {e}")
            raise

    def _search_by_kwargs(self, Clazz: 'BaseModel', kwargs: dict, skip: int = 0, limit: int = 100) -> List['BaseModel']:
        """根据关键字搜索"""
        filters = [Clazz.is_deleted == False]
        for key, value in kwargs.items():
            attr = getattr(Clazz, key, None)
            if attr is not None:
                filters.append(attr == value)
            else:
                raise ValueError(f"Invalid filter column: {key}")
        try:
            with Session(self.engine) as session:
                statement = select(Clazz).where(*filters).offset(skip).limit(limit)
                results = session.exec(statement).all()
                return results
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            raise

    def _count_by_kwargs(self, Clazz: 'BaseModel', kwargs: dict) -> int:
        """根据关键字统计数量"""
        filters = []
        for key, value in kwargs.items():
            attr = getattr(Clazz, key, None)
            if attr is not None:
                filters.append(attr == value)
            else:
                raise ValueError(f"Invalid filter column: {key}")
        try:
            with Session(self.engine) as session:
                statement = select(func.count()).select_from(Clazz).where(Clazz.is_deleted == False, *filters)
                num = session.exec(statement).one()
                return num
        except Exception as e:
            logger.error(f"统计数量失败: {e}")
            raise
