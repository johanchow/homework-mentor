# 用户API使用说明

## 概述

本项目实现了基于JWT token的用户认证系统，包括用户注册、登录、信息管理等功能。

## 功能特性

- ✅ 用户注册（邮箱/手机号）
- ✅ 用户登录（邮箱/手机号）
- ✅ JWT Token认证
- ✅ 用户信息管理
- ✅ 密码修改
- ✅ 邮箱/手机号唯一性检查

## 快速开始

### 1. 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动

### 2. 测试API

```bash
python test_user_api.py
```

## API接口文档

### 用户注册

**POST** `/user/register`

请求体：
```json
{
    "name": "张三",
    "password": "123456",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
    "avatar": "https://example.com/avatar.jpg"
}
```

响应：
```json
{
    "message": "注册成功",
    "user": {
        "id": "user-id",
        "name": "张三",
        "email": "zhangsan@example.com",
        "phone": "13800138000",
        "avatar": "https://example.com/avatar.jpg",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "is_active": true,
        "is_deleted": false
    },
    "token": "jwt-token-here"
}
```

### 用户登录

**POST** `/user/login`

请求体：
```json
{
    "email": "zhangsan@example.com",
    "password": "123456"
}
```

响应：
```json
{
    "message": "登录成功",
    "user": {
        "id": "user-id",
        "name": "张三",
        "email": "zhangsan@example.com",
        "phone": "13800138000",
        "avatar": "https://example.com/avatar.jpg",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "is_active": true,
        "is_deleted": false
    },
    "token": "jwt-token-here"
}
```

### 手机号登录

**POST** `/user/login/phone`

请求体：
```json
{
    "phone": "13800138000",
    "password": "123456"
}
```

### 获取用户信息

**GET** `/user/profile`

请求头：
```
Authorization: Bearer jwt-token-here
```

响应：
```json
{
    "user": {
        "id": "user-id",
        "name": "张三",
        "email": "zhangsan@example.com",
        "phone": "13800138000",
        "avatar": "https://example.com/avatar.jpg",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "is_active": true,
        "is_deleted": false
    }
}
```

### 更新用户信息

**PUT** `/user/profile`

请求头：
```
Authorization: Bearer jwt-token-here
```

请求体：
```json
{
    "name": "张三（已更新）",
    "phone": "13800138001",
    "avatar": "https://example.com/new-avatar.jpg"
}
```

### 修改密码

**PUT** `/user/password`

请求头：
```
Authorization: Bearer jwt-token-here
```

请求体：
```json
{
    "old_password": "123456",
    "new_password": "654321"
}
```

### 检查邮箱是否存在

**POST** `/user/check-email`

请求体：
```json
{
    "email": "zhangsan@example.com"
}
```

响应：
```json
{
    "exists": true
}
```

### 检查手机号是否存在

**POST** `/user/check-phone`

请求体：
```json
{
    "phone": "13800138000"
}
```

响应：
```json
{
    "exists": true
}
```

### 用户登出

**POST** `/user/logout`

请求头：
```
Authorization: Bearer jwt-token-here
```

响应：
```json
{
    "message": "登出成功"
}
```

## 认证说明

### JWT Token

- Token有效期：7天
- 算法：HS256
- 包含信息：用户ID、邮箱、过期时间

### 使用方式

在需要认证的请求中，在请求头中添加：

```
Authorization: Bearer your-jwt-token-here
```

## 错误处理

### 常见错误码

- `400` - 请求参数错误
- `401` - 认证失败
- `404` - 资源不存在
- `409` - 资源冲突（如邮箱已存在）
- `500` - 服务器内部错误

### 错误响应格式

```json
{
    "error": "错误描述信息"
}
```

## 安全特性

- 密码使用PBKDF2加密存储
- JWT Token包含过期时间
- 软删除用户数据
- 输入验证和过滤

## 开发说明

### 项目结构

```
├── api/
│   └── user_api.py          # 用户API接口
├── dao/
│   ├── base_dao.py          # 基础DAO类
│   ├── user_dao.py          # 用户DAO
│   └── database.py          # 数据库连接
├── entity/
│   └── user.py              # 用户实体类
├── utils/
│   └── jwt_utils.py         # JWT工具
├── app.py                   # Flask应用主文件
├── test_user_api.py         # API测试脚本
└── README_API.md            # 本文档
```

### 依赖包

- Flask
- SQLModel
- PyJWT
- requests (测试用)

### 环境变量

在 `.env` 文件中配置数据库连接信息：

```
DATABASE_URL=sqlite:///./homework_mentor.db
JWT_SECRET_KEY=your-secret-key-here
``` 
