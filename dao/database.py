"""
数据库连接和会话管理
"""

from sqlmodel import SQLModel, create_engine, Session
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# 数据库引擎
engine = None


def get_database_url() -> str:
    """获取数据库URL"""
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    else:
        # 默认使用SQLite
        return "sqlite:///./homework_mentor.db"


def create_database_engine():
    """创建数据库引擎"""
    global engine
    database_url = get_database_url()
    logger.info(f"连接数据库: {database_url}")
    engine = create_engine(
        database_url,
        echo=settings.API_DEBUG,  # 在调试模式下显示SQL语句
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
    )
    return engine


def get_engine():
    """获取数据库引擎"""
    global engine
    if engine is None:
        engine = create_database_engine()
    return engine


def create_db_and_tables():
    """创建数据库和表"""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    logger.info("数据库表创建完成")


def get_session():
    """获取数据库会话"""
    engine = get_engine()
    with Session(engine) as session:
        yield session


# 初始化数据库
def init_database():
    """初始化数据库"""
    try:
        create_db_and_tables()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
