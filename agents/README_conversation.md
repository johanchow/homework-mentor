# 多轮对话系统使用说明

## 概述

本系统基于 LangGraph 构建，支持多轮对话，能够根据用户问题自动路由到相应的专业 Agent 进行处理。**最新版本已支持完整的上下文传递，确保多轮对话的连贯性。**

## 主要特性

- ✅ 多轮对话支持
- ✅ **完整上下文传递** - 解决上下文丢失问题
- ✅ 自动路由到专业 Agent
- ✅ 对话历史管理
- ✅ 会话状态持久化
- ✅ 错误处理
- ✅ 对话导出功能

## 核心改进

### 上下文传递机制

之前的版本每次调用 `process_query` 只传递最新的消息，导致上下文丢失。现在系统通过以下方式解决：

1. **`process_query_with_context` 方法**: 新增支持传递完整上下文的方法
2. **对话历史构建**: 将历史对话构建成结构化的消息列表
3. **智能上下文管理**: 自动限制历史对话数量，避免token过多
4. **回退机制**: 当主方法失败时，自动回退到基础方法

### 工作流程

```
用户消息 → 路由节点 → Agent(带完整上下文) → 返回回复 → 更新状态
    ↑                                                    ↓
    ←────────── 多轮对话循环 ←──────────────────────────┘
```

## 快速开始

### 1. 基础使用

```python
from agents.agent_graph import create_workflow, create_conversation_session
from langchain_core.messages import HumanMessage

# 创建工作流
app = create_workflow()

# 创建会话
session = create_conversation_session()

# 第一轮对话
resp1 = app.invoke({
    "messages": [HumanMessage(content="你好，我想学习中文。")],
    "session_id": session["session_id"],
    "conversation_history": session["conversation_history"],
    "subject": session["subject"]
})

# 第二轮对话 - 系统会自动传递完整上下文
resp2 = app.invoke({
    "messages": [HumanMessage(content="我想学习写作，有什么建议吗？")],
    "session_id": session["session_id"],
    "conversation_history": resp1.get("conversation_history", []),
    "subject": resp1.get("subject", "")
})

# 第三轮对话 - 可以引用前面的内容
resp3 = app.invoke({
    "messages": [HumanMessage(content="刚才你提到的那个方法能再详细说说吗？")],
    "session_id": session["session_id"],
    "conversation_history": resp2.get("conversation_history", []),
    "subject": resp2.get("subject", "")
})
```

### 2. 使用对话管理器

```python
from agents.conversation_example import ConversationManager

# 创建对话管理器
manager = ConversationManager()

# 发送消息 - 自动处理上下文
response = manager.send_message("你好，我想学习中文。")
print(response)

# 继续对话 - 系统会记住前面的内容
response = manager.send_message("我想学习写作，有什么建议吗？")
print(response)

# 引用前面的内容 - 系统能理解上下文
response = manager.send_message("刚才你提到的那个方法能再详细说说吗？")
print(response)

# 获取对话历史
history = manager.get_conversation_history()
```

### 3. 使用高级对话管理器

```python
from agents.advanced_conversation import AdvancedConversationManager

# 创建高级对话管理器
manager = AdvancedConversationManager()

# 发送消息
result = manager.send_message("你好，我想学习中文。", user_id="user_001")
if result["success"]:
    print(f"AI回复: {result['response']}")
    print(f"会话ID: {result['session_id']}")
else:
    print(f"错误: {result['error']}")

# 继续对话 - 自动保持上下文
result = manager.send_message("我想学习写作，有什么建议吗？", user_id="user_001")
if result["success"]:
    print(f"AI回复: {result['response']}")

# 获取会话信息
session_info = manager.get_session_info()
print(session_info)

# 导出对话历史
exported_json = manager.export_conversation("json")
exported_txt = manager.export_conversation("txt")
```

## 系统架构

### 工作流程图

```
用户消息 → 路由节点 → 专业Agent(带上下文) → 返回回复 → 更新状态
    ↑                                                    ↓
    ←────────── 多轮对话循环 ←──────────────────────────┘
```

### 状态结构

```python
class AgentState(TypedDict):
    messages: List[Any]           # 当前消息
    subject: str                  # 学科分类
    conversation_history: List[Dict[str, Any]]  # 对话历史
    session_id: str               # 会话ID
```

### 上下文传递机制

```python
# 构建上下文信息
context = {
    "session_id": state.get("session_id", ""),
    "conversation_history": conversation_history,
    "is_conversation": True,
    "subject": state.get("subject", "chinese")
}

# 调用带上下文的方法
response = agent.process_query_with_context(query, context)
```

### 路由逻辑

系统会根据用户问题自动路由到相应的 Agent：

- **语文问题** → `chinese_agent`
- **英语问题** → `english_agent` (暂未实现，路由到 gossip)
- **数学问题** → `math_agent` (暂未实现，路由到 gossip)
- **其他问题** → `gossip_agent`

## 文件说明

- `agent_graph.py` - 核心工作流定义（已更新支持上下文）
- `conversation_example.py` - 基础对话管理器
- `advanced_conversation.py` - 高级对话管理器（推荐使用）
- `chinese_agent.py` - 中文教学 Agent（已更新支持上下文）
- `gossip_agent.py` - 闲聊 Agent（已更新支持上下文）
- `test_context.py` - 上下文传递测试脚本

## 配置要求

确保在 `.env` 文件中配置了必要的环境变量：

```env
# LLM 配置
OPENAI_API_KEY=your_openai_api_key
# 或其他 LLM 配置
```

## 运行示例

```bash
# 运行基础示例
python agents/agent_graph.py

# 运行对话示例
python agents/conversation_example.py

# 运行高级示例
python agents/advanced_conversation.py

# 运行上下文测试
python agents/test_context.py
```

## 扩展指南

### 添加新的 Agent

1. 在 `agents/` 目录下创建新的 Agent 文件
2. 继承 `BaseAgent` 类
3. 实现必要的方法，包括 `process_query_with_context`
4. 在 `agent_graph.py` 中添加路由逻辑

### 自定义路由逻辑

修改 `decide_route` 函数中的提示词和路由规则。

### 添加新的状态字段

在 `AgentState` 中添加新字段，并在相应的处理函数中更新状态。

### 自定义上下文处理

可以修改 `process_query_with_context` 方法来自定义上下文处理逻辑：

```python
def process_query_with_context(self, query: str, context: Dict[str, Any] = None) -> str:
    # 自定义上下文处理逻辑
    conversation_history = context.get("conversation_history", [])
    
    # 构建自定义提示
    custom_prompt = self._build_custom_prompt(query, conversation_history)
    
    # 处理查询
    return self._process_with_prompt(custom_prompt)
```

## 注意事项

1. 确保所有依赖包已正确安装
2. 对话历史会自动保存到 `conversations/` 目录
3. 每个会话都有唯一的 ID，可以用于恢复对话
4. 系统支持 JSON 和 TXT 格式的对话导出
5. **上下文会自动限制在最近6轮对话内，避免token过多**
6. **系统会自动处理上下文传递，无需手动管理**

## 故障排除

### 常见问题

1. **路由失败**: 检查 LLM 配置和网络连接
2. **状态丢失**: 检查存储路径权限
3. **Agent 无响应**: 检查 Agent 实现和依赖
4. **上下文丢失**: 确保使用 `process_query_with_context` 方法

### 调试模式

在代码中添加更多 `print` 语句来调试：

```python
print('用户问题:', message)
print('对话历史长度:', len(conversation_history))
print('路由结果:', route_result)
print('Agent 回复:', agent_response)
```

### 测试上下文功能

使用提供的测试脚本验证上下文传递：

```bash
python agents/test_context.py
```

这将运行多个测试用例，验证：
- 上下文保持功能
- 学科切换功能
- 对话管理器功能 
