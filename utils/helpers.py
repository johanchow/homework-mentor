"""
工具函数模块
"""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from config.settings import settings


def setup_logging(name: str = "langgraph_agents") -> logging.Logger:
    """设置日志配置"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.LOG_LEVEL))

        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))

        # 创建格式化器
        formatter = logging.Formatter(settings.LOG_FORMAT)
        console_handler.setFormatter(formatter)

        # 添加处理器
        logger.addHandler(console_handler)

    return logger


def validate_task_input(task: str, priority: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """验证任务输入"""
    errors = []

    # 验证任务描述
    if not task or not task.strip():
        errors.append("任务描述不能为空")
    elif len(task.strip()) < 5:
        errors.append("任务描述至少需要5个字符")
    elif len(task.strip()) > 1000:
        errors.append("任务描述不能超过1000个字符")

    # 验证优先级
    if priority and priority not in ["low", "medium", "high"]:
        errors.append("优先级必须是 low、medium 或 high")

    # 验证上下文
    if context and not isinstance(context, dict):
        errors.append("上下文必须是字典格式")

    if errors:
        return {
            "valid": False,
            "errors": errors
        }

    return {
        "valid": True,
        "task": task.strip(),
        "priority": priority or "medium",
        "context": context or {}
    }


def format_response(success: bool, data: Any = None, message: str = "", error: str = "") -> Dict[str, Any]:
    """格式化API响应"""
    response = {
        "success": success,
        "timestamp": datetime.now().isoformat(),
        "message": message
    }

    if success and data is not None:
        response["data"] = data

    if not success and error:
        response["error"] = error

    return response


def sanitize_task_id(task_id: str) -> str:
    """清理任务ID"""
    # 移除可能的危险字符
    return task_id.replace("..", "").replace("/", "").replace("\\", "")


def estimate_task_complexity(task: str) -> str:
    """估算任务复杂度"""
    task_lower = task.lower()

    # 简单的复杂度估算逻辑
    if len(task) < 50:
        return "simple"
    elif len(task) < 200:
        return "medium"
    else:
        return "complex"


def extract_keywords(task: str) -> list:
    """从任务中提取关键词"""
    # 简单的关键词提取（实际应用中可以使用更复杂的NLP）
    stop_words = {"的", "是", "在", "有", "和", "与", "或", "但", "而", "如果", "那么", "因为", "所以"}

    words = task.lower().split()
    keywords = [word for word in words if word not in stop_words and len(word) > 1]

    return list(set(keywords))[:10]  # 返回前10个关键词


def create_task_summary(task_id: str, task: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """创建任务摘要"""
    return {
        "task_id": task_id,
        "task": task,
        "summary": {
            "agent_type": result.get("agent_type", "unknown"),
            "task_type": result.get("task_type", "unknown"),
            "confidence": result.get("confidence", 0.0),
            "completion_time": result.get("completion_time", "unknown"),
            "key_points": result.get("key_points", []),
            "status": "completed"
        },
        "timestamp": datetime.now().isoformat()
    }

def random_uuid(length: int = 10) -> str:
    return uuid.uuid4().hex[:length]