"""
多Agent协调器 - 管理整个工作流程和任务执行
"""

from typing import Dict, Any, List, Optional
import asyncio
import uuid
from datetime import datetime
from pydantic import BaseModel
from .router import TaskRouter


class TaskStatus(BaseModel):
    """任务状态模型"""
    task_id: str
    status: str  # pending, running, completed, failed
    task: str
    assigned_agent: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    priority: str = "medium"
    estimated_time: Optional[str] = None


class MultiAgentCoordinator:
    """多Agent协调器 - 管理任务分配和执行"""
    
    def __init__(self):
        self.router = TaskRouter()
        self.tasks: Dict[str, TaskStatus] = {}
        self.task_queue: List[str] = []
        self.running_tasks: Dict[str, asyncio.Task] = {}
    
    async def submit_task(self, task: str, priority: str = "medium", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """提交新任务"""
        task_id = str(uuid.uuid4())
        
        # 创建任务状态
        task_status = TaskStatus(
            task_id=task_id,
            status="pending",
            task=task,
            priority=priority,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.tasks[task_id] = task_status
        self.task_queue.append(task_id)
        
        # 根据优先级重新排序队列
        self._sort_queue_by_priority()
        
        # 启动任务处理
        asyncio.create_task(self._process_task(task_id, context))
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "任务已提交，正在处理中"
        }
    
    async def _process_task(self, task_id: str, context: Dict[str, Any] = None):
        """处理单个任务"""
        task_status = self.tasks[task_id]
        
        try:
            # 更新任务状态
            task_status.status = "running"
            task_status.updated_at = datetime.now()
            
            # 使用路由器选择最佳Agent
            routing_result = await self.router.route_task(task_status.task, context)
            
            # 更新任务信息
            task_status.assigned_agent = routing_result["selected_agent"]
            task_status.estimated_time = routing_result["estimated_time"]
            task_status.updated_at = datetime.now()
            
            # 获取选定的Agent
            agent = self.router.available_agents[routing_result["selected_agent"]]
            
            # 执行任务
            result = await agent.execute(task_status.task, context)
            
            # 更新任务结果
            task_status.result = result
            task_status.status = "completed"
            task_status.updated_at = datetime.now()
            
        except Exception as e:
            # 处理错误
            task_status.status = "failed"
            task_status.error = str(e)
            task_status.updated_at = datetime.now()
            
        finally:
            # 从运行队列中移除
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    def _sort_queue_by_priority(self):
        """根据优先级对任务队列排序"""
        priority_order = {"high": 3, "medium": 2, "low": 1}
        
        self.task_queue.sort(
            key=lambda task_id: priority_order.get(self.tasks[task_id].priority, 1),
            reverse=True
        )
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        if task_id not in self.tasks:
            return None
        
        task_status = self.tasks[task_id]
        return {
            "task_id": task_status.task_id,
            "status": task_status.status,
            "task": task_status.task,
            "assigned_agent": task_status.assigned_agent,
            "priority": task_status.priority,
            "estimated_time": task_status.estimated_time,
            "created_at": task_status.created_at.isoformat(),
            "updated_at": task_status.updated_at.isoformat(),
            "result": task_status.result,
            "error": task_status.error
        }
    
    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务结果"""
        task_status = await self.get_task_status(task_id)
        if not task_status or task_status["status"] != "completed":
            return None
        
        return task_status["result"]
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        status_counts = {"pending": 0, "running": 0, "completed": 0, "failed": 0}
        
        for task in self.tasks.values():
            status_counts[task.status] += 1
        
        return {
            "total_tasks": len(self.tasks),
            "status_counts": status_counts,
            "queue_length": len(self.task_queue),
            "running_tasks": len(self.running_tasks),
            "agent_status": self.router.get_agent_status()
        }
    
    async def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """取消任务"""
        if task_id not in self.tasks:
            return {"success": False, "error": "任务不存在"}
        
        task_status = self.tasks[task_id]
        
        if task_status.status in ["completed", "failed"]:
            return {"success": False, "error": "任务已完成或失败，无法取消"}
        
        # 取消运行中的任务
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
        
        # 从队列中移除
        if task_id in self.task_queue:
            self.task_queue.remove(task_id)
        
        # 更新状态
        task_status.status = "cancelled"
        task_status.updated_at = datetime.now()
        
        return {"success": True, "message": "任务已取消"}
    
    async def execute_task_sync(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """同步执行任务（用于简单场景）"""
        # 直接路由和执行，不经过队列
        routing_result = await self.router.route_task(task, context)
        agent = self.router.available_agents[routing_result["selected_agent"]]
        
        result = await agent.execute(task, context)
        
        return {
            "task": task,
            "assigned_agent": routing_result["selected_agent"],
            "routing_decision": routing_result,
            "result": result
        } 