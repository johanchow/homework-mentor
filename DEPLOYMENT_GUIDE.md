# Homework Mentor 部署指南

## 🚀 快速部署

### 方式一：本地开发环境

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd homework-mentor
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境**
   ```bash
   # 创建环境配置文件
   cp .env.example .env
   
   # 编辑配置文件，添加API密钥
   nano .env
   ```

4. **启动服务**
   ```bash
   python main.py
   ```

### 方式二：Docker部署

1. **准备环境**
   ```bash
   # 确保Docker已安装
   docker --version
   
   # 给部署脚本添加执行权限
   chmod +x deploy.sh
   ```

2. **配置环境变量**
   ```bash
   # 创建.env文件
   cat > .env << EOF
   API_HOST=0.0.0.0
   API_PORT=5556
   API_DEBUG=false
   LOG_LEVEL=INFO
   OPENAI_API_KEY=your_openai_api_key_here
   DASHSCOPE_API_KEY=your_dashscope_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   OPENAI_TEMPERATURE=0.7
   OPENAI_MAX_TOKENS=2000
   EOF
   ```

3. **构建和启动**
   ```bash
   # 构建镜像
   ./deploy.sh build
   
   # 启动服务
   ./deploy.sh start
   ```

4. **验证部署**
   ```bash
   # 查看服务状态
   ./deploy.sh status
   
   # 健康检查
   curl http://localhost:5556/api/health
   
   # 查看API文档
   open http://localhost:5556/docs
   ```

## 📋 部署脚本使用

### 可用命令

```bash
./deploy.sh build      # 构建Docker镜像
./deploy.sh start      # 启动服务
./deploy.sh stop       # 停止服务
./deploy.sh restart    # 重启服务
./deploy.sh logs       # 查看日志
./deploy.sh status     # 查看状态
./deploy.sh shell      # 进入容器
./deploy.sh clean      # 清理资源
./deploy.sh backup     # 备份数据
./deploy.sh help       # 显示帮助
```

### 环境变量说明

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| `API_HOST` | API服务主机 | 否 | 0.0.0.0 |
| `API_PORT` | API服务端口 | 否 | 5556 |
| `API_DEBUG` | 调试模式 | 否 | false |
| `LOG_LEVEL` | 日志级别 | 否 | INFO |
| `OPENAI_API_KEY` | OpenAI API密钥 | 是 | - |
| `DASHSCOPE_API_KEY` | DashScope API密钥 | 是 | - |
| `OPENAI_MODEL` | OpenAI模型 | 否 | gpt-3.5-turbo |
| `OPENAI_TEMPERATURE` | 模型温度 | 否 | 0.7 |
| `OPENAI_MAX_TOKENS` | 最大令牌数 | 否 | 2000 |

## 🔧 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查看端口占用
   lsof -i :5556
   
   # 修改端口
   export API_PORT=5557
   ./deploy.sh restart
   ```

2. **容器启动失败**
   ```bash
   # 查看详细日志
   ./deploy.sh logs
   
   # 检查环境变量
   cat .env
   ```

3. **API密钥错误**
   ```bash
   # 检查API密钥
   grep OPENAI_API_KEY .env
   grep DASHSCOPE_API_KEY .env
   ```

4. **权限问题**
   ```bash
   # 修复权限
   chmod +x deploy.sh
   chmod 755 data/ logs/
   ```

### 日志查看

```bash
# 实时查看日志
./deploy.sh logs

# 查看应用日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log
```

## 📊 监控和维护

### 健康检查

```bash
# 手动健康检查
curl http://localhost:5556/api/health

# 检查容器状态
./deploy.sh status
```

### 数据备份

```bash
# 备份数据
./deploy.sh backup

# 备份文件位置
ls -la backup_*/
```

### 更新部署

```bash
# 停止服务
./deploy.sh stop

# 清理旧镜像
./deploy.sh clean

# 重新构建和启动
./deploy.sh build
./deploy.sh start
```

## 🔒 安全建议

1. **生产环境配置**
   - 设置 `API_DEBUG=false`
   - 使用强密码的API密钥
   - 配置防火墙规则

2. **数据安全**
   - 定期备份数据
   - 加密敏感信息
   - 限制容器权限

3. **网络安全**
   - 使用HTTPS
   - 配置反向代理
   - 设置访问控制

## 📞 技术支持

如果遇到问题，请：

1. 查看日志：`./deploy.sh logs`
2. 检查状态：`./deploy.sh status`
3. 查看文档：http://localhost:5556/docs
4. 提交Issue：[GitHub Issues]

---

**Happy Deploying! 🚀** 