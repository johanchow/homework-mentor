"""
数据库连接和会话管理 - 异步版本
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# 异步数据库引擎
async_engine = None
async_session_maker = None


def get_database_url() -> str:
    """获取数据库URL"""
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    else:
        # 默认使用SQLite
        return "sqlite+aiosqlite:///./homework_mentor.db"


async def create_async_database_engine():
    """创建异步数据库引擎"""
    global async_engine, async_session_maker
    database_url = get_database_url()
    
    # 转换为异步URL
    if database_url.startswith("sqlite://"):
        database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    elif database_url.startswith("mysql://"):
        database_url = database_url.replace("mysql://", "mysql+aiomysql://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    logger.info(f"连接异步数据库: {database_url}")
    
    async_engine = create_async_engine(
        database_url,
        echo=settings.API_DEBUG,  # 在调试模式下显示SQL语句
        pool_pre_ping=True,
        pool_recycle=300,
    )
    
    async_session_maker = async_sessionmaker(
        async_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    return async_engine


async def get_async_engine():
    """获取异步数据库引擎"""
    global async_engine
    if async_engine is None:
        async_engine = await create_async_database_engine()
    return async_engine


async def get_async_session_maker():
    """获取异步会话工厂"""
    global async_session_maker
    if async_session_maker is None:
        await get_async_engine()
    return async_session_maker


async def create_db_and_tables():
    """创建数据库和表"""
    engine = await get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("数据库表创建完成")


async def get_async_session():
    """获取异步数据库会话"""
    session_maker = await get_async_session_maker()
    async with session_maker() as session:
        yield session


# 初始化数据库
async def init_database():
    """初始化数据库"""
    try:
        await create_db_and_tables()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


# 兼容性函数 - 保持向后兼容
def get_engine():
    """获取同步数据库引擎（兼容性函数）"""
    raise NotImplementedError("请使用异步版本 get_async_engine()")


def get_session():
    """获取同步数据库会话（兼容性函数）"""
    raise NotImplementedError("请使用异步版本 get_async_session()")
