from abc import ABC, abstractmethod
from dao.database import get_engine
from typing import List, Union, Dict, Any
from sqlalchemy import func
from sqlmodel import Session, select, update, delete
from datetime import datetime
import logging
import re

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

    def batch_create(self, models: List['BaseModel']):
        try:
            with Session(self.engine) as session:
                session.add_all(models)
                session.commit()
                for model in models:
                    session.refresh(model)
                return models
        except Exception as e:
            logger.error(f"批量创建{models[0].__class__.__name__}失败: {e}")
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

    def _parse_filter_value(self, value: Any) -> tuple:
        """
        解析过滤值，支持简化的比较操作符
        
        Args:
            value: 过滤值，可以是：
                - 普通值: 表示相等比较 (key=value)
                - 字典: 如 {"$gt": 5}, {"$like": "abc"}, {"$in": [1,2,3]}
        
        Returns:
            tuple: (操作符, 值)
        """
        if isinstance(value, dict):
            # 字典格式: {"$gt": 5}, {"$like": "abc"}
            if len(value) != 1:
                raise ValueError(f"过滤条件字典只能包含一个键值对: {value}")
            op, val = next(iter(value.items()))
            return op, val
        else:
            # 普通值，默认为相等比较
            return '$eq', value

    def _build_filter_condition(self, attr, op: str, value: Any):
        """
        根据操作符构建过滤条件
        
        Args:
            attr: SQLModel字段属性
            op: 操作符
            value: 比较值
        
        Returns:
            SQLAlchemy过滤条件
        """
        if op == '$eq':
            return attr == value
        elif op == '$ne':
            return attr != value
        elif op == '$gt':
            return attr > value
        elif op == '$gte':
            return attr >= value
        elif op == '$lt':
            return attr < value
        elif op == '$lte':
            return attr <= value
        elif op == '$like':
            return attr.contains(value)
        elif op == '$in':
            return attr.in_(value)
        elif op == '$nin':
            return ~attr.in_(value)
        elif op == '$between':
            if len(value) != 2:
                raise ValueError("between条件需要两个值")
            return attr.between(value[0], value[1])
        else:
            raise ValueError(f"不支持的操作符: {op}")

    def _search_by_kwargs(self, Clazz: 'BaseModel', kwargs: dict, skip: int = 0, limit: int = 100) -> List['BaseModel']:
        """
        根据关键字搜索，支持多种比较操作符
        
        Args:
            Clazz: 实体类
            kwargs: 过滤条件字典
            skip: 跳过数量
            limit: 返回数量限制
        """
        filters = [Clazz.is_deleted == False]
        
        for key, value in kwargs.items():
            attr = getattr(Clazz, key, None)
            if attr is not None:
                try:
                    op, val = self._parse_filter_value(value)
                    condition = self._build_filter_condition(attr, op, val)
                    filters.append(condition)
                except Exception as e:
                    logger.warning(f"解析过滤条件失败 {key}={value}: {e}")
                    # 如果解析失败，尝试作为普通相等条件处理
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
        """
        根据关键字统计数量，支持多种比较操作符
        
        Args:
            Clazz: 实体类
            kwargs: 过滤条件字典
        """
        filters = [Clazz.is_deleted == False]
        
        for key, value in kwargs.items():
            attr = getattr(Clazz, key, None)
            if attr is not None:
                try:
                    op, val = self._parse_filter_value(value)
                    condition = self._build_filter_condition(attr, op, val)
                    filters.append(condition)
                except Exception as e:
                    logger.warning(f"解析过滤条件失败 {key}={value}: {e}")
                    # 如果解析失败，尝试作为普通相等条件处理
                    filters.append(attr == value)
            else:
                raise ValueError(f"Invalid filter column: {key}")
        
        try:
            with Session(self.engine) as session:
                statement = select(func.count()).select_from(Clazz).where(*filters)
                num = session.exec(statement).one()
                return num
        except Exception as e:
            logger.error(f"统计数量失败: {e}")
            raise
