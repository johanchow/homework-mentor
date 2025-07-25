"""
通用异常处理模块
"""

from typing import Optional


class BusinessException(Exception):
    """业务异常基类"""
    
    def __init__(self, code: int, message: str, details: Optional[str] = None):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(self.message)


class DataNotFoundException(BusinessException):
    """数据不存在异常"""
    
    def __init__(self, data_type: str, data_id: str, details: Optional[str] = None):
        self.data_type = data_type
        self.data_id = data_id
        message = f"{data_type}不存在: {data_id}"
        super().__init__(code=404, message=message, details=details)


class ValidationException(BusinessException):
    """数据验证异常"""
    
    def __init__(self, field: str, message: str, details: Optional[str] = None):
        self.field = field
        message = f"字段'{field}'验证失败: {message}"
        super().__init__(code=400, message=message, details=details)


class PermissionException(BusinessException):
    """权限异常"""
    
    def __init__(self, message: str = "权限不足", details: Optional[str] = None):
        super().__init__(code=403, message=message, details=details)


class AuthenticationException(BusinessException):
    """认证异常"""
    
    def __init__(self, message: str = "认证失败", details: Optional[str] = None):
        super().__init__(code=401, message=message, details=details)


class DatabaseException(BusinessException):
    """数据库异常"""
    
    def __init__(self, message: str = "数据库操作失败", details: Optional[str] = None):
        super().__init__(code=500, message=message, details=details)


class ExternalServiceException(BusinessException):
    """外部服务异常"""
    
    def __init__(self, service_name: str, message: str, details: Optional[str] = None):
        self.service_name = service_name
        message = f"{service_name}服务异常: {message}"
        super().__init__(code=502, message=message, details=details)