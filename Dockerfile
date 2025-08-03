# 使用 Alpine Linux 作为基础镜像（更小）
FROM python:3.11-alpine as builder

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 复制requirements.txt
COPY requirements.txt .

# 创建虚拟环境并安装依赖
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 生产阶段
FROM python:3.11-alpine as production

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 只安装运行时必需的系统依赖
RUN apk add --no-cache \
    libjpeg \
    zlib \
    curl \
    jq

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 创建必要的目录
RUN mkdir -p logs data uploads

# 创建非root用户
RUN adduser -D -s /bin/sh app && \
    chown -R app:app /app
USER app

# 复制应用代码
COPY --chown=app:app . .

# 暴露端口
EXPOSE 5556

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5556/api/health')" || exit 1

# 启动命令
CMD ["python", "main.py"] 