# PaperDAO 使用说明

## 概述

PaperDAO是基于SqlModel实现的试卷数据访问对象，提供了完整的试卷数据库CRUD操作功能。

## 文件结构

```
dao/
├── paper_dao.py          # 试卷DAO实现
├── database.py           # 数据库连接管理
└── README_PAPER.md      # 使用说明

entity/
└── paper.py             # 试卷实体类（已修改为继承SqlModel）

examples/
├── test_paper.py        # 测试文件
└── paper_dao_example.py # 使用示例
```

## 主要功能

### 1. 试卷实体类 (`entity/paper.py`)

- 继承SqlModel，支持数据库表映射
- 包含完整的试卷信息字段
- 支持JSON序列化和反序列化
- 提供工厂函数创建试卷实例

### 2. 试卷DAO (`dao/paper_dao.py`)

提供以下数据库操作：

#### 创建操作
- `create_paper(paper: Paper) -> Paper` - 创建新试卷

#### 查询操作
- `get_paper_by_id(paper_id: str) -> Optional[Paper]` - 根据ID查询试卷
- `get_papers_by_creator_id(creator_id: str, skip: int = 0, limit: int = 100) -> List[Paper]` - 根据创建者ID查询试卷
- `get_all_papers(skip: int = 0, limit: int = 100) -> List[Paper]` - 获取所有试卷（分页）
- `search_papers(title: str = None, description: str = None) -> List[Paper]` - 搜索试卷

#### 更新操作
- `update_paper(paper_id: str, update_data: Dict[str, Any]) -> Optional[Paper]` - 更新试卷信息

#### 删除操作
- `delete_paper(paper_id: str) -> bool` - 软删除试卷
- `hard_delete_paper(paper_id: str) -> bool` - 硬删除试卷

#### 统计操作
- `count_papers() -> int` - 统计试卷总数
- `count_papers_by_creator(creator_id: str) -> int` - 统计指定创建者的试卷数量

## 使用方法

### 1. 创建试卷

```python
from entity.paper import create_paper
from dao.paper_dao import paper_dao

# 创建试卷
paper = create_paper(
    title="2024年春季数学期中考试",
    creator_id="user123",
    description="包含代数、几何、统计等内容的综合试卷"
)

# 保存到数据库
saved_paper = paper_dao.create_paper(paper)
```

### 2. 查询试卷

```python
# 根据ID查询
paper = paper_dao.get_paper_by_id("paper_id")

# 根据创建者查询
creator_papers = paper_dao.get_papers_by_creator_id("user123")

# 搜索试卷
search_results = paper_dao.search_papers(title="数学")

# 分页获取所有试卷
all_papers = paper_dao.get_all_papers(skip=0, limit=10)
```

### 3. 更新试卷

```python
update_data = {
    "title": "2024年春季数学期中考试（修订版）",
    "description": "已修订的试卷描述"
}
updated_paper = paper_dao.update_paper("paper_id", update_data)
```

### 4. 删除试卷

```python
# 软删除
paper_dao.delete_paper("paper_id")

# 硬删除
paper_dao.hard_delete_paper("paper_id")
```

### 5. 统计功能

```python
# 统计总数
total_count = paper_dao.count_papers()

# 统计创建者的试卷数
creator_count = paper_dao.count_papers_by_creator("user123")
```

## 特性

### 1. 软删除支持
- 默认使用软删除，不会真正删除数据
- 提供硬删除方法用于彻底删除数据

### 2. 自动时间戳
- 创建时自动设置 `created_at`
- 更新时自动更新 `updated_at`

### 3. 分页查询
- 支持分页获取试卷列表
- 可设置偏移量和限制数量

### 4. 搜索功能
- 支持按标题、描述搜索
- 使用模糊匹配

### 5. 错误处理
- 完整的异常处理和日志记录
- 提供详细的错误信息

### 6. 关联关系
- 支持与User实体的关联关系
- 通过外键关联创建者信息

## 运行示例

### 运行测试
```bash
python examples/test_paper.py
```

### 运行使用示例
```bash
python examples/paper_dao_example.py
```

## 注意事项

1. **数据库初始化**：首次使用前需要调用 `init_database()` 创建表结构
2. **事务管理**：DAO层自动管理数据库事务，无需手动处理
3. **连接池**：使用SQLAlchemy的连接池，提高性能
4. **日志记录**：所有数据库操作都有详细的日志记录
5. **类型安全**：使用类型注解，提供更好的IDE支持

## 扩展

如需添加新的查询方法或业务逻辑，可以在 `PaperDAO` 类中添加新的方法。建议遵循现有的命名规范和错误处理模式。 
