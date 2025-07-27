"""
测试JWT工具模块 - FastAPI版本
"""

import pytest
import jwt
import datetime
from unittest.mock import Mock, patch
from utils.exceptions import AuthenticationException
from utils.jwt_utils import (
    generate_token, 
    verify_token, 
    get_token_from_header,
    get_current_user_id,
    get_current_user_email,
    get_current_user_payload
)


class TestJWTUtils:
    """JWT工具模块测试类"""

    def test_generate_token(self):
        """测试生成token"""
        user_id = "test_user_123"
        user_email = "test@example.com"
        
        token = generate_token(user_id, user_email)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(self):
        """测试验证有效token"""
        user_id = "test_user_123"
        user_email = "test@example.com"
        
        # 生成token
        token = generate_token(user_id, user_email)
        
        # 验证token
        payload = verify_token(token)
        
        assert payload is not None
        assert payload['user_id'] == user_id
        assert payload['email'] == user_email
        assert 'exp' in payload
        assert 'iat' in payload

    def test_verify_token_invalid(self):
        """测试验证无效token"""
        invalid_token = "invalid.token.here"
        
        payload = verify_token(invalid_token)
        
        assert payload is None

    def test_verify_token_expired(self):
        """测试验证过期token"""
        # 创建一个过期的payload
        expired_payload = {
            'user_id': 'test_user',
            'email': 'test@example.com',
            'exp': datetime.datetime.utcnow() - datetime.timedelta(hours=1),
            'iat': datetime.datetime.utcnow() - datetime.timedelta(hours=2)
        }
        
        # 手动编码过期token
        expired_token = jwt.encode(expired_payload, "your-secret-key-here", algorithm="HS256")
        
        payload = verify_token(expired_token)
        
        assert payload is None

    def test_get_token_from_header_valid(self):
        """测试从请求头获取有效token"""
        mock_request = Mock()
        mock_request.headers = {'Authorization': 'Bearer test.token.here'}
        
        token = get_token_from_header(mock_request)
        
        assert token == "test.token.here"

    def test_get_token_from_header_invalid_format(self):
        """测试从请求头获取无效格式token"""
        mock_request = Mock()
        mock_request.headers = {'Authorization': 'InvalidFormat test.token.here'}
        
        token = get_token_from_header(mock_request)
        
        assert token is None

    def test_get_token_from_header_missing(self):
        """测试从请求头获取缺失的token"""
        mock_request = Mock()
        mock_request.headers = {}
        
        token = get_token_from_header(mock_request)
        
        assert token is None

    @pytest.mark.asyncio
    async def test_get_current_user_id_success(self):
        """测试成功获取当前用户ID"""
        # 生成有效token
        user_id = "test_user_123"
        user_email = "test@example.com"
        token = generate_token(user_id, user_email)
        
        # 模拟请求
        mock_request = Mock()
        mock_request.headers = {'Authorization': f'Bearer {token}'}
        
        result = await get_current_user_id(mock_request)
        
        assert result == user_id

    @pytest.mark.asyncio
    async def test_get_current_user_id_missing_token(self):
        """测试获取当前用户ID时缺少token"""
        mock_request = Mock()
        mock_request.headers = {}
        
        with pytest.raises(AuthenticationException) as exc_info:
            await get_current_user_id(mock_request)
        
        assert exc_info.value.code == 401
        assert "缺少认证token" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_get_current_user_id_invalid_token(self):
        """测试获取当前用户ID时无效token"""
        mock_request = Mock()
        mock_request.headers = {'Authorization': 'Bearer invalid.token'}
        
        with pytest.raises(AuthenticationException) as exc_info:
            await get_current_user_id(mock_request)
        
        assert exc_info.value.code == 401
        assert "无效或过期的token" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_get_current_user_email_success(self):
        """测试成功获取当前用户邮箱"""
        # 生成有效token
        user_id = "test_user_123"
        user_email = "test@example.com"
        token = generate_token(user_id, user_email)
        
        # 模拟请求
        mock_request = Mock()
        mock_request.headers = {'Authorization': f'Bearer {token}'}
        
        result = await get_current_user_email(mock_request)
        
        assert result == user_email

    @pytest.mark.asyncio
    async def test_get_current_user_payload_success(self):
        """测试成功获取当前用户完整信息"""
        # 生成有效token
        user_id = "test_user_123"
        user_email = "test@example.com"
        token = generate_token(user_id, user_email)
        
        # 模拟请求
        mock_request = Mock()
        mock_request.headers = {'Authorization': f'Bearer {token}'}
        
        result = await get_current_user_payload(mock_request)
        
        assert result['user_id'] == user_id
        assert result['email'] == user_email
        assert 'exp' in result
        assert 'iat' in result


if __name__ == "__main__":
    pytest.main([__file__]) 