"""
主程序入口 - LangGraph多Agent协同服务
"""

import asyncio
import sys
from api.app import create_app
from config.settings import settings
from utils.helpers import setup_logging


def main():
    """主函数"""
    logger = setup_logging()

    try:
        # 创建Flask应用
        app = create_app()

        # 配置
        app.config['SECRET_KEY'] = 'your-secret-key-here'
        app.config['JSON_AS_ASCII'] = False  # 支持中文

        logger.info("🚀 启动Homework Mentor API...")
        logger.info(f"📍 服务地址: http://{settings.API_HOST}:{settings.API_PORT}")
        logger.info(f"🔧 调试模式: {settings.API_DEBUG}")
        logger.info(f"📊 健康检查: http://{settings.API_HOST}:{settings.API_PORT}/api/health")

        # 启动Flask应用
        app.run(
            host=settings.API_HOST,
            port=settings.API_PORT,
            debug=settings.API_DEBUG
        )

    except KeyboardInterrupt:
        logger.info("🛑 服务被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()