# Homework Mentor - 智能学习管理系统

一个基于FastAPI和LangGraph的智能学习管理系统，提供目标导向的学习、AI辅助问题生成和考试创建功能。

## 🎯 项目特性

- 🤖 **多Agent协同工作流** - 基于LangGraph的智能Agent协作
- 🧠 **LLM动态路由决策** - 智能任务分配和负载均衡
- 📚 **目标导向学习** - 用户自定义学习目标，AI分解学习计划
- ❓ **智能问题生成** - 基于学习目标自动生成练习题
- 📝 **考试系统** - 完整的在线考试和评分功能
- 🔍 **OCR识别** - 支持图片文字识别和题目提取
- 📊 **RESTful API** - 完整的API接口，支持前后端分离
- 🚀 **异步架构** - 基于FastAPI的高性能异步处理
- 🐳 **容器化部署** - 支持Docker一键部署

## 🏗️ 项目结构

```
homework-mentor/
├── api/                    # API接口层
│   ├── app.py             # FastAPI主应用
│   ├── goal_api.py        # 目标管理API
│   ├── exam_api.py        # 考试管理API
│   ├── question_api.py    # 问题管理API
│   ├── user_api.py        # 用户管理API
│   └── ai_api.py          # AI服务API
├── agents/                 # LangGraph Agent定义
│   ├── base_agent.py      # 基础Agent类
│   ├── chinese_agent.py   # 中文处理Agent
│   ├── gossip_agent.py    # 对话Agent
│   └── parse_image_agent.py # 图像解析Agent
├── config/                # 配置文件
│   └── settings.py        # 应用配置
├── dao/                   # 数据访问层
│   ├── base_dao.py        # 基础DAO类
│   ├── database.py        # 数据库连接
│   ├── user_dao.py        # 用户DAO
│   ├── goal_dao.py        # 目标DAO
│   ├── exam_dao.py        # 考试DAO
│   └── question_dao.py    # 问题DAO
├── entity/                # 数据实体
│   ├── base.py           # 基础实体类
│   ├── user.py           # 用户实体
│   ├── goal.py           # 目标实体
│   ├── exam.py           # 考试实体
│   └── question.py       # 问题实体
├── service/               # 业务服务层
│   ├── ocr_service.py    # OCR服务
│   ├── detection_service.py # 图像检测服务
│   └── vector_service.py # 向量服务
├── utils/                 # 工具函数
│   ├── helpers.py        # 辅助函数
│   ├── exceptions.py     # 异常处理
│   ├── jwt_utils.py      # JWT工具
│   └── llm.py           # LLM工具
├── workflows/             # 工作流定义
│   ├── coordinator.py    # 工作流协调器
│   └── router.py         # 动态路由
├── main.py               # 主程序入口
├── Dockerfile            # Docker构建文件
├── docker-compose.yml    # Docker编排文件
├── requirements.txt      # Python依赖
└── README.md            # 项目文档
```

## 🚀 快速开始

### 方式一：本地开发环境

#### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd homework-mentor

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 2. 环境配置

```bash
# 创建环境配置文件
cp .env.example .env

# 编辑配置文件，添加必要的API密钥
nano .env
```

**必需的环境变量：**
```bash
# API配置
API_HOST=0.0.0.0
API_PORT=5556
API_DEBUG=true

# 数据库配置（可选）
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/database

# LLM配置（必需）
OPENAI_API_KEY=your_openai_api_key_here
DASHSCOPE_API_KEY=your_dashscope_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
```

#### 3. 启动服务

```bash
# 方式1：使用完整启动脚本（推荐）
python main.py

# 方式2：直接启动FastAPI
uvicorn api.app:app --host 0.0.0.0 --port 5556 --reload
```

#### 4. 验证服务

```bash
# 健康检查
curl http://localhost:5556/api/health

# 查看API文档
open http://localhost:5556/docs
```

### 方式二：Docker部署

#### 1. 环境准备

```bash
# 确保已安装Docker
docker --version
```

#### 2. 使用部署脚本（推荐）

```bash
# 给脚本添加执行权限
chmod +x deploy.sh

# 构建镜像:  Git action会执行ci/cd流程，把镜像推送到远程

# 部署: 耗时比较久，用nohup忽略挂断信号，后台自动持续执行
nohup ./deploy.sh deploy > deploy.log 2>&1 &

# 启动服务
./deploy.sh start

# 查看状态
./deploy.sh status

# 查看日志
./deploy.sh logs

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 进入容器
./deploy.sh shell

# 清理资源
./deploy.sh clean
```

#### 3. 手动Docker命令

```bash
# 构建镜像
docker build -t homework-mentor:latest .

# 启动容器
docker run -d \
  --name homework-mentor-api \
  -p 5556:5556 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  homework-mentor:latest

# 查看容器状态
docker ps

# 查看日志
docker logs -f homework-mentor-api

# 停止容器
docker stop homework-mentor-api
docker rm homework-mentor-api
```

#### 4. 环境变量配置

创建 `.env` 文件：
```bash
# API配置
API_HOST=0.0.0.0
API_PORT=5556
API_DEBUG=false
LOG_LEVEL=INFO

# LLM配置
OPENAI_API_KEY=your_openai_api_key_here
DASHSCOPE_API_KEY=your_dashscope_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
```

## 📚 API接口

### 核心功能

- **目标管理** - 创建、查询、更新学习目标
- **考试系统** - 创建考试、提交答案、自动评分
- **问题生成** - AI智能生成练习题
- **用户管理** - 用户注册、登录、权限管理
- **AI服务** - OCR识别、图像分析、智能对话

### 主要端点

```
GET  /api/health          # 健康检查
GET  /api/docs           # API文档

# 用户管理
POST /api/user/register  # 用户注册
POST /api/user/login     # 用户登录
GET  /api/user/profile   # 获取用户信息

# 目标管理
POST   /api/goal/create  # 创建学习目标
GET    /api/goal/list    # 获取目标列表
GET    /api/goal/get     # 获取目标详情
PUT    /api/goal/update  # 更新目标
DELETE /api/goal/delete  # 删除目标

# 考试管理
POST   /api/exam/create  # 创建考试
GET    /api/exam/list    # 获取考试列表
GET    /api/exam/get     # 获取考试详情
POST   /api/exam/finish  # 提交考试答案
DELETE /api/exam/delete  # 删除考试

# 问题管理
POST   /api/question/create      # 创建问题
GET    /api/question/list        # 获取问题列表
GET    /api/question/get         # 获取问题详情
PUT    /api/question/update      # 更新问题
DELETE /api/question/delete      # 删除问题
POST   /api/question/batch-create # 批量创建问题

# AI服务
POST /api/ai/generate-questions           # 生成问题
POST /api/ai/parse-questions-from-images  # 图片解析
POST /api/ai/analyze-question             # 问题分析
```

## 🔧 开发指南

### 代码结构说明

- **API层** (`api/`) - 处理HTTP请求，参数验证，响应格式化
- **服务层** (`service/`) - 业务逻辑处理，外部服务调用
- **DAO层** (`dao/`) - 数据访问对象，数据库操作封装
- **实体层** (`entity/`) - 数据模型定义，ORM映射
- **Agent层** (`agents/`) - LangGraph Agent实现，AI任务处理
- **工具层** (`utils/`) - 通用工具函数，异常处理

### 开发规范

1. **异常处理** - 使用统一的异常类 (`utils/exceptions.py`)
2. **响应格式** - 统一的API响应格式
3. **日志记录** - 使用结构化日志记录
4. **类型注解** - 完整的类型注解支持
5. **文档注释** - 详细的函数和类文档

### 测试

```bash
# 运行测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_api.py
```

## 🐳 Docker部署

### 生产环境部署

```bash
# 1. 构建生产镜像
docker build -t homework-mentor:latest .

# 2. 运行容器
docker run -d \
  --name homework-mentor-api \
  -p 5556:5556 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  homework-mentor:latest

# 3. 使用部署脚本（推荐）
./deploy.sh start
```

### 环境变量配置

生产环境建议配置以下环境变量：

```bash
# 必需配置
OPENAI_API_KEY=your_openai_api_key
DASHSCOPE_API_KEY=your_dashscope_api_key

# API配置
API_DEBUG=false
LOG_LEVEL=INFO

# 可选：数据库配置
DATABASE_URL=mysql+pymysql://user:password@host:3306/database
```

### 监控和日志

```bash
# 查看容器状态
./deploy.sh status

# 查看日志
./deploy.sh logs

# 健康检查
curl http://localhost:5556/api/health

# 进入容器调试
./deploy.sh shell
```

## 🔍 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   # 升级pip
   pip install --upgrade pip
   
   # 清理缓存重新安装
   pip cache purge
   pip install -r requirements.txt
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库服务
   docker ps | grep mysql
   
   # 检查网络连接
   docker network ls
   ```

3. **端口被占用**
   ```bash
   # 查看端口占用
   lsof -i :5556
   
   # 修改端口
   export API_PORT=5557
   ```

4. **权限问题**
   ```bash
   # 检查目录权限
   ls -la logs/ data/
   
   # 修复权限
   chmod 755 logs/ data/
   ```

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看Docker日志
./deploy.sh logs

# 查看错误日志
grep ERROR logs/app.log
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📞 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 邮箱: [your-email@example.com]

---

**Happy Learning! 🎓**
