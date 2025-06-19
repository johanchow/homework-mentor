"""
Flask应用主文件
"""

from flask import Flask
from flask_cors import CORS
from config.settings import settings
from utils.helpers import setup_logging
from .routes import api_bp


def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 配置CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册蓝图
    app.register_blueprint(api_bp)
    
    # 设置日志
    logger = setup_logging()
    
    @app.route('/')
    def index():
        """根路径"""
        return {
            "service": "LangGraph Multi-Agent System",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "health": "/api/health",
                "submit_task": "/api/task",
                "task_status": "/api/task/<task_id>/status",
                "task_result": "/api/task/<task_id>/result",
                "cancel_task": "/api/task/<task_id>",
                "sync_task": "/api/task/sync",
                "system_status": "/api/status",
                "agents_info": "/api/agents",
                "chinese_teaching": "/api/chinese/teach",
                "start_conversation": "/api/chinese/conversation/start",
                "conversation_chat": "/api/chinese/conversation/chat",
                "conversation_summary": "/api/chinese/conversation/<session_id>/summary"
            },
            "agents": {
                "research": "研究Agent - 信息收集和调研",
                "analysis": "分析Agent - 数据分析和洞察",
                "summary": "总结Agent - 内容总结和报告",
                "chinese_teacher": "中文老师Agent - 中文教学和指导"
            }
        }
    
    @app.errorhandler(404)
    def not_found(error):
        """404错误处理"""
        return {
            "success": False,
            "error": "接口不存在",
            "message": "请检查API路径是否正确"
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500错误处理"""
        logger.error(f"服务器内部错误: {str(error)}")
        return {
            "success": False,
            "error": "服务器内部错误",
            "message": "请稍后重试"
        }, 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    print(f"🚀 启动LangGraph多Agent服务...")
    print(f"📍 服务地址: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"🔧 调试模式: {settings.API_DEBUG}")
    print(f"📊 健康检查: http://{settings.API_HOST}:{settings.API_PORT}/api/health")
    print(f"📚 中文教学: http://{settings.API_HOST}:{settings.API_PORT}/api/chinese/teach")
    
    app.run(
        host=settings.API_HOST,
        port=settings.API_PORT,
        debug=settings.API_DEBUG
    ) 