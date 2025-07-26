#!/bin/bash

# Homework Mentor 部署脚本
# 使用方法: ./deploy.sh [start|stop|restart|build|logs|status|clean]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目名称
PROJECT_NAME="homework-mentor"
CONTAINER_NAME="homework-mentor-api"
IMAGE_NAME="homework-mentor:latest"
PORT=5556

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    log_success "Docker 环境检查通过"
}

# 检查环境文件
check_env() {
    if [ ! -f ".env" ]; then
        log_warning ".env 文件不存在，正在创建示例文件..."
        cat > .env << EOF
# API配置
API_HOST=0.0.0.0
API_PORT=5556
API_DEBUG=false

# LLM配置
OPENAI_API_KEY=your_openai_api_key_here
DASHSCOPE_API_KEY=your_dashscope_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# 日志配置
LOG_LEVEL=INFO
EOF
        log_warning "请编辑 .env 文件，添加你的 API 密钥"
    fi
}

# 构建镜像
build() {
    log_info "开始构建 Docker 镜像..."
    docker build -t $IMAGE_NAME .
    log_success "镜像构建完成"
}

# 启动服务
start() {
    log_info "启动 Homework Mentor 服务..."
    
    # 检查是否已经运行
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        log_warning "服务已经在运行中"
        return
    fi
    
    # 停止旧容器（如果存在）
    if docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        log_info "停止旧容器..."
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
    fi
    
    # 启动新容器
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:$PORT \
        --env-file .env \
        -v $(pwd)/data:/app/data \
        -v $(pwd)/logs:/app/logs \
        --restart unless-stopped \
        $IMAGE_NAME
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        log_success "服务启动成功"
        log_info "API 地址: http://localhost:$PORT"
        log_info "健康检查: http://localhost:$PORT/api/health"
        log_info "API 文档: http://localhost:$PORT/docs"
    else
        log_error "服务启动失败"
        docker logs $CONTAINER_NAME
        exit 1
    fi
}

# 停止服务
stop() {
    log_info "停止 Homework Mentor 服务..."
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
        log_success "服务已停止"
    else
        log_warning "服务未在运行"
    fi
}

# 重启服务
restart() {
    log_info "重启 Homework Mentor 服务..."
    stop
    start
    log_success "服务重启完成"
}

# 查看日志
logs() {
    log_info "查看服务日志..."
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        docker logs -f $CONTAINER_NAME
    else
        log_error "服务未在运行"
        exit 1
    fi
}

# 查看状态
status() {
    log_info "服务状态:"
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        docker ps --filter "name=$CONTAINER_NAME"
        echo ""
        log_info "容器资源使用情况:"
        docker stats --no-stream $CONTAINER_NAME
    else
        log_warning "服务未在运行"
        echo ""
        log_info "所有容器状态:"
        docker ps -a --filter "name=$CONTAINER_NAME"
    fi
}

# 清理
clean() {
    log_warning "清理所有容器和镜像..."
    
    # 停止并删除容器
    if docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        docker stop $CONTAINER_NAME 2>/dev/null || true
        docker rm $CONTAINER_NAME 2>/dev/null || true
    fi
    
    # 删除镜像
    if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "^${IMAGE_NAME}$"; then
        docker rmi $IMAGE_NAME 2>/dev/null || true
    fi
    
    log_success "清理完成"
}

# 进入容器
shell() {
    log_info "进入容器..."
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        docker exec -it $CONTAINER_NAME bash
    else
        log_error "服务未在运行"
        exit 1
    fi
}

# 备份数据
backup() {
    log_info "备份数据..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="backup_${timestamp}"
    
    mkdir -p "$backup_dir"
    
    # 备份数据目录
    if [ -d "data" ]; then
        cp -r data "$backup_dir/"
        log_success "数据目录备份完成"
    fi
    
    # 备份配置文件
    if [ -f ".env" ]; then
        cp .env "$backup_dir/"
        log_success "配置文件备份完成"
    fi
    
    log_success "备份完成: $backup_dir"
}

# 主函数
main() {
    case "${1:-start}" in
        "build")
            check_docker
            build
            ;;
        "start")
            check_docker
            check_env
            start
            ;;
        "stop")
            stop
            ;;
        "restart")
            check_docker
            restart
            ;;
        "logs")
            logs
            ;;
        "status")
            status
            ;;
        "shell")
            shell
            ;;
        "clean")
            clean
            ;;
        "backup")
            backup
            ;;
        "help"|"-h"|"--help")
            echo "Homework Mentor 部署脚本"
            echo ""
            echo "使用方法: $0 [命令]"
            echo ""
            echo "命令:"
            echo "  build    构建 Docker 镜像"
            echo "  start    启动服务 (默认)"
            echo "  stop     停止服务"
            echo "  restart  重启服务"
            echo "  logs     查看日志"
            echo "  status   查看状态"
            echo "  shell    进入容器"
            echo "  clean    清理所有容器和镜像"
            echo "  backup   备份数据"
            echo "  help     显示帮助信息"
            ;;
        *)
            log_error "未知命令: $1"
            echo "使用 '$0 help' 查看帮助信息"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 