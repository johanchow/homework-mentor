# 中文老师Agent使用示例

## 概述

中文老师Agent是一个专门负责中文教学指导和答疑的智能代理，支持：
- 写作指导（记叙文、议论文、说明文等）
- 阅读理解指导
- 语法学习指导
- 诗词鉴赏指导
- 文言文学习指导
- 多轮对话教学

## API接口

### 1. 中文教学指导

**接口**: `POST /api/chinese/teach`

**请求示例**:
```bash
curl -X POST http://localhost:5000/api/chinese/teach \
  -H "Content-Type: application/json" \
  -d '{
    "question": "如何写好一篇记叙文？",
    "student_level": "初中生",
    "learning_goal": "提高记叙文写作水平"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "task": "如何写好一篇记叙文？",
    "assigned_agent": "chinese_teacher",
    "routing_decision": {
      "selected_agent": "chinese_teacher",
      "reasoning": "任务涉及中文教学和指导"
    },
    "result": {
      "task_type": "chinese_teaching",
      "teaching_type": "writing",
      "guidance": "详细的写作指导内容...",
      "teaching_methods": ["思维导图法", "五步写作法", "范文分析法"],
      "learning_principles": ["多读多写", "观察生活", "积累素材"],
      "practice_suggestions": ["每天写一篇日记", "阅读优秀范文"]
    }
  }
}
```

### 2. 开始对话会话

**接口**: `POST /api/chinese/conversation/start`

**请求示例**:
```bash
curl -X POST http://localhost:5000/api/chinese/conversation/start \
  -H "Content-Type: application/json" \
  -d '{
    "student_info": {
      "student_name": "小明",
      "grade": "初三",
      "weakness": "作文写作"
    }
  }'
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "session_id": "session_20241201_143022"
  }
}
```

### 3. 对话聊天

**接口**: `POST /api/chinese/conversation/chat`

**请求示例**:
```bash
curl -X POST http://localhost:5000/api/chinese/conversation/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "老师，我写作文总是不知道写什么，怎么办？",
    "session_id": "session_20241201_143022",
    "conversation_history": []
  }'
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "task_type": "chinese_conversation",
    "session_id": "session_20241201_143022",
    "response": "亲切的教师回复内容...",
    "conversation_history": [
      {
        "role": "user",
        "content": "老师，我写作文总是不知道写什么，怎么办？",
        "timestamp": "2024-12-01T14:30:22"
      },
      {
        "role": "assistant",
        "content": "亲切的教师回复内容...",
        "timestamp": "2024-12-01T14:30:23"
      }
    ],
    "turn_count": 1
  }
}
```

### 4. 获取对话总结

**接口**: `GET /api/chinese/conversation/{session_id}/summary`

**请求示例**:
```bash
curl http://localhost:5000/api/chinese/conversation/session_20241201_143022/summary
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "session_id": "session_20241201_143022",
    "total_turns": 3,
    "user_messages_count": 3,
    "assistant_messages_count": 3,
    "main_topics": ["写作指导"],
    "learning_progress": "根据对话内容分析学习进展"
  }
}
```

## Python客户端示例

### 基本教学指导

```python
import requests

# 中文教学指导
response = requests.post('http://localhost:5000/api/chinese/teach', 
                        json={
                            'question': '如何提高阅读理解能力？',
                            'student_level': '高中生',
                            'learning_goal': '提高阅读理解准确率'
                        })

if response.status_code == 200:
    result = response.json()
    print(f"教学指导: {result['data']['result']['guidance']}")
    print(f"教学方法: {result['data']['result']['teaching_methods']}")
    print(f"练习建议: {result['data']['result']['practice_suggestions']}")
```

### 多轮对话教学

```python
import requests

# 开始对话会话
start_response = requests.post('http://localhost:5000/api/chinese/conversation/start',
                              json={
                                  'student_info': {
                                      'student_name': '小红',
                                      'grade': '初二',
                                      'weakness': '语法学习'
                                  }
                              })

session_id = start_response.json()['data']['session_id']
conversation_history = []

# 第一轮对话
chat_response = requests.post('http://localhost:5000/api/chinese/conversation/chat',
                             json={
                                 'message': '老师，我语法总是学不好，有什么好方法吗？',
                                 'session_id': session_id,
                                 'conversation_history': conversation_history
                             })

result = chat_response.json()['data']
print(f"老师回复: {result['response']}")
conversation_history = result['conversation_history']

# 第二轮对话
chat_response2 = requests.post('http://localhost:5000/api/chinese/conversation/chat',
                              json={
                                  'message': '那具体应该怎么练习呢？',
                                  'session_id': session_id,
                                  'conversation_history': conversation_history
                              })

result2 = chat_response2.json()['data']
print(f"老师回复: {result2['response']}")

# 获取对话总结
summary_response = requests.get(f'http://localhost:5000/api/chinese/conversation/{session_id}/summary')
summary = summary_response.json()['data']
print(f"对话总结: 共{summary['total_turns']}轮对话，主要话题: {summary['main_topics']}")
```

## 支持的教学类型

### 1. 写作指导 (writing)
- 记叙文写作
- 议论文写作
- 说明文写作
- 应用文写作
- 作文修改指导

### 2. 阅读理解 (reading)
- 现代文阅读
- 文章中心思想分析
- 段落大意概括
- 写作手法分析
- 阅读技巧指导

### 3. 语法学习 (grammar)
- 现代汉语语法
- 文言文语法
- 句式分析
- 修辞手法
- 语言表达

### 4. 诗词鉴赏 (poetry)
- 古诗词鉴赏
- 现代诗欣赏
- 意象分析
- 情感体验
- 创作指导

### 5. 文言文学习 (classical)
- 文言文翻译
- 字词解释
- 句式分析
- 文化背景
- 古今对比

## 教学特点

1. **方法指导**: 不仅给出答案，更教会学生思考方法
2. **原则性指导**: 帮助学生建立正确的学习思维
3. **实例讲解**: 用具体例子说明抽象概念
4. **个性化建议**: 根据学生水平提供针对性指导
5. **多轮对话**: 支持连续问答，深入探讨问题
6. **练习建议**: 提供具体的练习和巩固方法

## 测试运行

运行中文老师Agent测试：

```bash
python test_chinese_agent.py
```

这将测试：
- 教学指导功能
- 多轮对话功能
- 不同主题的教学能力 