# 考试API文档

## 接口列表

### 1. 创建考试
- **POST** `/exam/`
- 创建新的考试记录

### 2. 获取考试详情  
- **GET** `/exam/{exam_id}`
- 获取指定考试的详细信息

### 3. 更新考试答卷
- **PUT** `/exam/{exam_id}`
- 只能修改answer_json字段

### 4. 删除考试
- **DELETE** `/exam/{exam_id}`
- 软删除考试记录

### 5. 获取考试列表
- **GET** `/exam/`
- 支持分页和筛选

### 6. 根据试卷获取考试
- **GET** `/exam/paper/{paper_id}`

### 7. 根据考生获取考试
- **GET** `/exam/examinee/{examinee_id}`

## 认证
所有接口都需要JWT token: `Authorization: Bearer <token>`

## 概述

考试API提供了考试相关的完整CRUD操作，包括创建、查询、修改和删除考试记录。

## 基础URL

```
http://localhost:5000/exam
```

## API接口

### 1. 创建考试

**POST** `/exam/`

创建新的考试记录。

#### 请求参数

```json
{
  "paper_id": "试卷ID",
  "examinee_id": "考生ID",
  "answer": {
    "question": [
      {
        "id": "问题ID",
        "subject": "科目",
        "type": "问题类型",
        "title": "题目内容",
        "creator_id": "创建者ID",
        "options": "选项列表（逗号分隔）"
      }
    ],
    "messages": {
      "问题ID": [
        {
          "id": "消息ID",
          "role": "角色",
          "content": "消息内容",
          "message_type": "消息类型",
          "timestamp": "时间戳"
        }
      ]
    },
    "answer": {
      "问题ID": "答案"
    }
  }
}
```

#### 响应示例

```json
{
  "code": 0,
  "message": "考试创建成功",
  "exam": {
    "id": "考试ID",
    "paper_id": "试卷ID",
    "examinee_id": "考生ID",
    "answer_json": "答卷JSON字符串",
    "created_at": "创建时间",
    "updated_at": "更新时间",
    "is_deleted": false
  }
}
```

### 2. 获取考试详情

**GET** `/exam/{exam_id}`

获取指定考试的详细信息，包括试卷和考生信息。

#### 响应示例

```json
{
  "code": 0,
  "message": "获取考试详情成功",
  "exam": {
    "id": "考试ID",
    "paper_id": "试卷ID",
    "examinee_id": "考生ID",
    "answer_json": "答卷JSON字符串",
    "created_at": "创建时间",
    "updated_at": "更新时间",
    "is_deleted": false,
    "paper": {
      "试卷详细信息"
    },
    "examinee": {
      "考生详细信息"
    },
    "answer": {
      "答卷详细信息"
    }
  }
}
```

### 3. 更新考试答卷

**PUT** `/exam/{exam_id}`

更新指定考试的答卷内容（只能修改answer_json字段）。

#### 请求参数

```json
{
  "answer": {
    "question": [
      {
        "id": "问题ID",
        "subject": "科目",
        "type": "问题类型",
        "title": "题目内容",
        "creator_id": "创建者ID",
        "options": "选项列表"
      }
    ],
    "messages": {
      "问题ID": [
        {
          "id": "消息ID",
          "role": "角色",
          "content": "消息内容",
          "message_type": "消息类型",
          "timestamp": "时间戳"
        }
      ]
    },
    "answer": {
      "问题ID": "答案"
    }
  }
}
```

#### 响应示例

```json
{
  "code": 0,
  "message": "答卷更新成功",
  "exam": {
    "考试更新后的信息"
  }
}
```

### 4. 获取考试列表

**GET** `/exam/`

获取考试列表，支持分页和筛选。

#### 查询参数

- `paper_id`: 试卷ID（可选）
- `examinee_id`: 考生ID（可选）
- `page`: 页码，默认1
- `size`: 每页数量，默认10

#### 响应示例

```json
{
  "code": 0,
  "message": "获取考试列表成功",
  "data": {
    "exams": [
      {
        "考试信息"
      }
    ],
    "total": 总数量,
    "page": 当前页码,
    "size": 每页数量,
    "pages": 总页数
  }
}
```

### 5. 根据试卷获取考试列表

**GET** `/exam/paper/{paper_id}`

获取指定试卷的所有考试记录。

#### 查询参数

- `page`: 页码，默认1
- `size`: 每页数量，默认10

### 6. 根据考生获取考试列表

**GET** `/exam/examinee/{examinee_id}`

获取指定考生的所有考试记录。

#### 查询参数

- `page`: 页码，默认1
- `size`: 每页数量，默认10

### 7. 删除考试

**DELETE** `/exam/{exam_id}`

删除指定的考试记录（软删除）。

#### 响应示例

```json
{
  "code": 0,
  "message": "考试删除成功"
}
```

## 错误处理

所有API都遵循统一的错误响应格式：

```json
{
  "error": "错误描述"
}
```

### 常见HTTP状态码

- `200`: 请求成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 认证失败
- `404`: 资源不存在
- `500`: 服务器内部错误

## 使用示例

### Python示例

```python
import requests

# 创建考试
exam_data = {
    "paper_id": "paper-123",
    "examinee_id": "user-456"
}

response = requests.post(
    "http://localhost:5000/exam/",
    json=exam_data,
    headers={"Authorization": "Bearer your-token"}
)

if response.status_code == 201:
    exam = response.json()['exam']
    print(f"考试创建成功，ID: {exam['id']}")
```

### JavaScript示例

```javascript
// 创建考试
const examData = {
    paper_id: "paper-123",
    examinee_id: "user-456"
};

fetch('http://localhost:5000/exam/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-token'
    },
    body: JSON.stringify(examData)
})
.then(response => response.json())
.then(data => {
    if (data.code === 0) {
        console.log('考试创建成功:', data.exam);
    }
});
```

## 注意事项

1. 所有请求都需要有效的JWT token
2. 删除操作是软删除，不会真正删除数据
3. 更新操作只能修改答卷内容，不能修改其他字段
4. 答卷数据需要符合Answer类的格式要求
5. 分页参数page从1开始计数 
