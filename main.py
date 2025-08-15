#!/usr/bin/env python3
"""
Homework Mentor - 主程序入口
提供完整的启动前检查和服务启动功能
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from utils.helpers import setup_logging


class StartupChecker:
    """启动前检查器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.errors = []
        self.warnings = []
        
    def log_error(self, message: str):
        """记录错误"""
        self.errors.append(message)
        self.logger.error(f"❌ {message}")
        
    def log_warning(self, message: str):
        """记录警告"""
        self.warnings.append(message)
        self.logger.warning(f"⚠️  {message}")
        
    def log_success(self, message: str):
        """记录成功"""
        self.logger.info(f"✅ {message}")
        
    def check_python_version(self) -> bool:
        """检查Python版本"""
        self.logger.info("🔍 检查Python版本...")
        
        if sys.version_info < (3, 8):
            self.log_error(f"Python版本过低: {sys.version}. 需要Python 3.8或更高版本")
            return False
        else:
            self.log_success(f"Python版本: {sys.version}")
            
        return True
    
    def check_environment_variables(self) -> bool:
        """检查环境变量"""
        self.logger.info("🔍 检查环境变量...")
        
        # 必需的环境变量
        required_vars = []
        
        # 可选但重要的环境变量
        important_vars = [
            ("OPENAI_API_KEY", settings.OPENAI_API_KEY),
            ("DASHSCOPE_API_KEY", settings.DASHSCOPE_API_KEY),
            ("DATABASE_URL", settings.DATABASE_URL)
        ]
        
        # 检查必需变量
        for var in required_vars:
            if not os.getenv(var):
                self.log_error(f"缺少必需环境变量: {var}")
                
        # 检查重要变量
        for var_name, var_value in important_vars:
            if not var_value:
                self.log_warning(f"缺少重要环境变量: {var_name}")
            else:
                self.log_success(f"环境变量已设置: {var_name}")
                
        return len([var for var in required_vars if not os.getenv(var)]) == 0
    
    def run_all_checks(self) -> bool:
        """运行所有检查"""
        self.logger.info("🚀 开始启动前检查...")
        self.logger.info("=" * 50)
        
        checks = [
            ("Python版本", self.check_python_version),
            ("环境变量", self.check_environment_variables),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                if not check_func():
                    all_passed = False
            except Exception as e:
                self.log_error(f"{check_name}检查异常: {str(e)}")
                all_passed = False
                
        self.logger.info("=" * 50)
        
        if self.warnings:
            self.logger.warning(f"⚠️  发现 {len(self.warnings)} 个警告")
            for warning in self.warnings:
                self.logger.warning(f"  - {warning}")
                
        if self.errors:
            self.logger.error(f"❌ 发现 {len(self.errors)} 个错误")
            for error in self.errors:
                self.logger.error(f"  - {error}")
            self.logger.error("❌ 启动前检查失败，请解决上述问题后重试")
        else:
            self.logger.info("✅ 所有检查通过，准备启动服务")
            
        return all_passed


def print_startup_banner():
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    Homework Mentor API                       ║
║                                                              ║
║  🎯 智能学习管理系统 - 基于FastAPI和LangGraph                ║
║  🚀 版本: 1.0.0                                              ║
║  📅 启动时间: {timestamp}                                    ║
╚══════════════════════════════════════════════════════════════╝
"""
    from datetime import datetime
    print(banner.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def main():
    """主函数"""
    # 设置日志
    logger = setup_logging()
    
    try:
        # 打印启动横幅
        print_startup_banner()
        
        # 运行启动前检查
        checker = StartupChecker()
        if not checker.run_all_checks():
            logger.error("❌ 启动前检查失败，服务无法启动")
            sys.exit(1)
        
        # 导入并启动FastAPI应用
        logger.info("🚀 启动Homework Mentor API...")
        logger.info(f"📍 服务地址: http://{settings.API_HOST}:{settings.API_PORT}")
        logger.info(f"🔧 调试模式: {settings.API_DEBUG}")
        logger.info(f"📊 健康检查: http://{settings.API_HOST}:{settings.API_PORT}/api/health")
        logger.info(f"📚 API文档: http://{settings.API_HOST}:{settings.API_PORT}/docs")
        
        # 启动uvicorn服务器
        import uvicorn
        uvicorn.run(
            "api.app:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=settings.API_DEBUG,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 服务被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {str(e)}")
        logger.exception("详细错误信息:")
        sys.exit(1)


if __name__ == "__main__":
    main()
