#!/usr/bin/env python3
"""
快速启动脚本 - LangGraph多Agent协同服务
"""

import os
import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """检查依赖是否安装"""
    try:
        import langgraph
        import langchain
        import flask
        import pydantic
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        return False


def check_env_file():
    """检查环境配置文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  未找到 .env 文件")
        print("📝 正在创建 .env 文件...")
        
        # 复制示例文件
        example_file = Path("env.example")
        if example_file.exists():
            with open(example_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ .env 文件已创建")
            print("⚠️  请编辑 .env 文件，添加你的 OpenAI API 密钥")
            return False
        else:
            print("❌ 未找到 env.example 文件")
            return False
    
    return True


def install_dependencies():
    """安装依赖"""
    print("📦 正在安装依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        return False


def start_service():
    """启动服务"""
    print("🚀 启动LangGraph多Agent协同服务...")
    
    try:
        # 导入并启动服务
        from main import main
        main()
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False


def main():
    """主函数"""
    print("🎯 LangGraph多Agent协同服务启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n📦 正在安装依赖...")
        if not install_dependencies():
            print("❌ 依赖安装失败，请手动运行: pip install -r requirements.txt")
            return
    
    # 检查环境配置
    if not check_env_file():
        print("\n⚠️  请配置 .env 文件后再启动服务")
        return
    
    # 启动服务
    print("\n🚀 启动服务...")
    start_service()


if __name__ == "__main__":
    main() 