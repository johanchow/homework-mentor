# 使用Python 3.11作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# # 设置 pip 源为清华的镜像源
# RUN mkdir -p /root/.config/pip && \
#     echo "[global]" >> /root/.config/pip/pip.conf && \
#     echo "index-url = https://pypi.tuna.tsinghua.edu.cn/simple" >> /root/.config/pip/pip.conf && \
#     echo "trusted-host = pypi.tuna.tsinghua.edu.cn" >> /root/.config/pip/pip.conf

# 复制requirements.txt
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p logs data uploads

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# 暴露端口
EXPOSE 5556

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5556/api/health')" || exit 1

# 启动命令
CMD ["python", "main.py"] 