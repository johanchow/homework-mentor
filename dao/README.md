# 用户DAO层使用说明

## 概述

本项目使用SqlModel实现了用户实体类的DAO（数据访问对象）层，提供了完整的数据库CRUD操作功能。

## 文件结构

```
dao/
├── __init__.py          # DAO包初始化文件
├── user_dao.py          # 用户DAO实现
└── README.md           # 使用说明

config/
├── database.py         # 数据库连接管理
└── settings.py         # 配置管理

entity/
└── user.py            # 用户实体类（已修改为继承SqlModel）

examples/
└── user_dao_example.py # 使用示例
```

## 主要功能

### 1. 数据库连接管理 (`config/database.py`)

- 支持多种数据库（SQLite、MySQL、PostgreSQL等）
- 自动从环境变量读取数据库配置
- 提供会话管理和连接池

### 2. 用户实体类 (`entity/user.py`)

- 继承SqlModel，支持数据库表映射
- 包含完整的用户信息字段
- 支持JSON序列化和反序列化

### 3. 用户DAO (`dao/user_dao.py`)

提供以下数据库操作：

#### 创建操作
- `create_user(user: User) -> User` - 创建新用户

#### 查询操作
- `get_user_by_id(user_id: str) -> Optional[User]` - 根据ID查询用户
- `get_user_by_email(email: str) -> Optional[User]` - 根据邮箱查询用户
- `get_user_by_phone(phone: str) -> Optional[User]` - 根据手机号查询用户
- `get_all_users(skip: int = 0, limit: int = 100) -> List[User]` - 获取所有用户（分页）
- `search_users(name: str = None, email: str = None, phone: str = None) -> List[User]` - 搜索用户
- `get_active_users(skip: int = 0, limit: int = 100) -> List[User]` - 获取激活用户
- `count_users() -> int` - 统计用户总数

#### 更新操作
- `update_user(user_id: str, update_data: Dict[str, Any]) -> Optional[User]` - 更新用户信息
- `activate_user(user_id: str) -> Optional[User]` - 激活用户
- `deactivate_user(user_id: str) -> Optional[User]` - 停用用户

#### 删除操作
- `delete_user(user_id: str) -> bool` - 软删除用户
- `hard_delete_user(user_id: str) -> bool` - 硬删除用户

## 使用方法

### 1. 环境配置

在 `.env` 文件中配置数据库连接：

```env
# SQLite (默认)
DATABASE_URL=sqlite:///./homework_mentor.db

# MySQL
DATABASE_URL=mysql+pymysql://username:password@localhost/database_name

# PostgreSQL
DATABASE_URL=postgresql://username:password@localhost/database_name
```

### 2. 初始化数据库

```python
from config.database import init_database

# 初始化数据库和表
init_database()
```

### 3. 使用UserDAO

```python
from entity.user import User, create_user
from dao.user_dao import user_dao

# 创建用户
user = create_user(
    name="张三",
    email="zhangsan@example.com",
    phone="13800138000"
)

# 保存到数据库
saved_user = user_dao.create_user(user)

# 查询用户
found_user = user_dao.get_user_by_id(saved_user.id)

# 更新用户
update_data = {"name": "张三丰"}
updated_user = user_dao.update_user(saved_user.id, update_data)

# 删除用户
user_dao.delete_user(saved_user.id)
```

### 4. 运行示例

```bash
python examples/user_dao_example.py
```

## 特性

### 1. 软删除支持
- 默认使用软删除，不会真正删除数据
- 提供硬删除方法用于彻底删除数据

### 2. 自动时间戳
- 创建时自动设置 `created_at`
- 更新时自动更新 `updated_at`

### 3. 状态管理
- 支持用户激活/停用状态管理
- 提供状态查询方法

### 4. 分页查询
- 支持分页获取用户列表
- 可设置偏移量和限制数量

### 5. 搜索功能
- 支持按姓名、邮箱、手机号搜索
- 使用模糊匹配

### 6. 错误处理
- 完整的异常处理和日志记录
- 提供详细的错误信息

## 注意事项

1. **数据库初始化**：首次使用前需要调用 `init_database()` 创建表结构
2. **事务管理**：DAO层自动管理数据库事务，无需手动处理
3. **连接池**：使用SQLAlchemy的连接池，提高性能
4. **日志记录**：所有数据库操作都有详细的日志记录
5. **类型安全**：使用类型注解，提供更好的IDE支持

## 扩展

如需添加新的查询方法或业务逻辑，可以在 `UserDAO` 类中添加新的方法。建议遵循现有的命名规范和错误处理模式。 
