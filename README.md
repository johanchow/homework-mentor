# LangGraph 多Agent协同服务

这是一个基于LangGraph和Flask的多Agent协同系统，支持LLM动态驱动路由和智能任务分配。

## 项目特性

- 🤖 多Agent协同工作流
- 🧠 LLM动态路由决策
- 🔄 智能任务分配和负载均衡
- 📊 RESTful API接口
- 🚀 可扩展的Agent架构

## 项目结构

```
myapp/
├── agents/                 # Agent定义
│   ├── __init__.py
│   ├── base_agent.py      # 基础Agent类
│   ├── research_agent.py  # 研究Agent
│   ├── analysis_agent.py  # 分析Agent
│   └── summary_agent.py   # 总结Agent
├── workflows/             # 工作流定义
│   ├── __init__.py
│   ├── router.py         # 动态路由逻辑
│   └── coordinator.py    # 协调器
├── config/               # 配置文件
│   ├── __init__.py
│   └── settings.py
├── utils/                # 工具函数
│   ├── __init__.py
│   └── helpers.py
├── api/                  # Flask API接口
│   ├── __init__.py
│   ├── routes.py        # API路由
│   └── app.py           # Flask应用
├── tests/                # 测试文件
│   └── __init__.py
├── .env.example          # 环境变量示例
├── main.py              # 主程序入口
└── requirements.txt     # 依赖包
```

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，添加你的API密钥
```

3. 运行服务：
```bash
python main.py
```

4. 或者直接运行Flask应用：
```bash
python api/app.py
```

## API使用示例

### 启动任务
```bash
curl -X POST http://localhost:5000/api/task \
  -H "Content-Type: application/json" \
  -d '{"task": "分析最新的AI技术趋势", "priority": "high"}'
```

### 查询任务状态
```bash
curl http://localhost:5000/api/task/{task_id}/status
```

### 获取任务结果
```bash
curl http://localhost:5000/api/task/{task_id}/result
```

## Python客户端示例

```python
import requests

# 创建协调器
response = requests.post('http://localhost:5000/api/task', 
                        json={'task': '分析最新的AI技术趋势'})
task_id = response.json()['task_id']

# 查询结果
result = requests.get(f'http://localhost:5000/api/task/{task_id}/result')
print(result.json())
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License 