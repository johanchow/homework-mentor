"""
FastAPI应用主文件
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config.settings import settings
from utils.helpers import setup_logging

# 导入所有路由
from .exam_api import exam_router
from .user_api import user_router
from .question_api import question_router
from .goal_api import goal_router
from .ai_api import ai_router

# 创建FastAPI应用
app = FastAPI(
    title="Homework Mentor API",
    description="学习管理系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 注册路由
app.include_router(exam_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(question_router, prefix="/api")
app.include_router(goal_router, prefix="/api")
app.include_router(ai_router, prefix="/api")

# 设置日志
logger = setup_logging()


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "Homework Mentor API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "Homework Mentor API",
        "version": "1.0.0"
    }


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """404错误处理"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "接口不存在",
            "message": "请检查API路径是否正确"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """500错误处理"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "服务器内部错误",
            "message": "请稍后重试"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
