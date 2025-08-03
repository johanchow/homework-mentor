#!/bin/bash

# Homework Mentor 部署脚本
# 自动拉取最新镜像并启动服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="homework-mentor"
CONTAINER_NAME="homework-mentor-api"
IMAGE_NAME="ghcr.io/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/')"
PORT=5556
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

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

# 检查Docker环境
check_docker() {
    log_info "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker服务未运行，请启动Docker服务"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 获取最新镜像标签
get_latest_tag() {
    log_info "获取最新镜像标签..."
    
    # 尝试从GitHub获取最新标签
    LATEST_TAG=$(curl -s "https://api.github.com/repos/$(echo $IMAGE_NAME | sed 's/ghcr.io\///')/tags" | jq -r '.[0].name' 2>/dev/null || echo "latest")
    
    if [ "$LATEST_TAG" = "null" ] || [ -z "$LATEST_TAG" ]; then
        LATEST_TAG="latest"
    fi
    
    log_success "使用镜像标签: $LATEST_TAG"
    echo $LATEST_TAG
}

# 拉取最新镜像
pull_image() {
    local tag=$1
    log_info "拉取最新镜像: $IMAGE_NAME:$tag"
    
    if docker pull $IMAGE_NAME:$tag; then
        log_success "镜像拉取成功"
    else
        log_error "镜像拉取失败"
        exit 1
    fi
}

# 备份当前数据
backup_data() {
    log_info "备份当前数据..."
    
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        mkdir -p $BACKUP_DIR
        
        # 备份容器数据
        docker cp $CONTAINER_NAME:/app/data $BACKUP_DIR/ 2>/dev/null || true
        docker cp $CONTAINER_NAME:/app/logs $BACKUP_DIR/ 2>/dev/null || true
        
        log_success "数据备份完成: $BACKUP_DIR"
    else
        log_warning "没有运行中的容器，跳过备份"
    fi
}

# 停止旧容器
stop_container() {
    log_info "停止旧容器..."
    
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
        log_success "旧容器已停止并删除"
    else
        log_warning "没有运行中的容器"
    fi
}

# 启动新容器
start_container() {
    local tag=$1
    log_info "启动新容器..."
    
    # 创建必要的目录
    mkdir -p ./data ./logs
    
    # 启动容器
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:$PORT \
        -v $(pwd)/data:/app/data \
        -v $(pwd)/logs:/app/logs \
        --restart unless-stopped \
        $IMAGE_NAME:$tag
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        log_success "容器启动成功"
    else
        log_error "容器启动失败"
        docker logs $CONTAINER_NAME
        exit 1
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:$PORT/api/health" > /dev/null; then
            log_success "服务健康检查通过"
            return 0
        fi
        
        log_info "等待服务就绪... (尝试 $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "服务健康检查失败"
    docker logs $CONTAINER_NAME
    return 1
}

# 显示服务信息
show_service_info() {
    log_success "部署完成！"
    echo ""
    echo "📋 服务信息:"
    echo "  服务名称: $CONTAINER_NAME"
    echo "  镜像: $IMAGE_NAME:$1"
    echo "  端口: $PORT"
    echo "  健康检查: http://localhost:$PORT/api/health"
    echo "  API文档: http://localhost:$PORT/docs"
    echo "  数据目录: $(pwd)/data"
    echo "  日志目录: $(pwd)/logs"
    echo ""
    echo "🔧 常用命令:"
    echo "  查看日志: docker logs $CONTAINER_NAME"
    echo "  停止服务: docker stop $CONTAINER_NAME"
    echo "  重启服务: docker restart $CONTAINER_NAME"
    echo "  进入容器: docker exec -it $CONTAINER_NAME bash"
}

# 主部署函数
deploy() {
    log_info "开始部署 Homework Mentor..."
    
    # 检查Docker环境
    check_docker
    
    # 获取最新标签
    LATEST_TAG=$(get_latest_tag)
    
    # 备份数据
    backup_data
    
    # 拉取最新镜像
    pull_image $LATEST_TAG
    
    # 停止旧容器
    stop_container
    
    # 启动新容器
    start_container $LATEST_TAG
    
    # 健康检查
    if health_check; then
        show_service_info $LATEST_TAG
    else
        log_error "部署失败，请检查日志"
        exit 1
    fi
}

# 回滚函数
rollback() {
    log_info "开始回滚..."
    
    # 停止当前容器
    stop_container
    
    # 恢复备份数据
    if [ -d "$BACKUP_DIR" ]; then
        log_info "恢复备份数据..."
        cp -r $BACKUP_DIR/* ./ 2>/dev/null || true
        log_success "数据恢复完成"
    fi
    
    # 启动上一个版本
    local previous_tag="latest"
    if [ -f "./.previous_tag" ]; then
        previous_tag=$(cat ./.previous_tag)
    fi
    
    start_container $previous_tag
    
    if health_check; then
        log_success "回滚完成"
    else
        log_error "回滚失败"
        exit 1
    fi
}

# 查看服务状态
status() {
    log_info "服务状态:"
    
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        echo "✅ 服务正在运行"
        docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
        
        echo ""
        echo "📊 资源使用情况:"
        docker stats $CONTAINER_NAME --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
        
        echo ""
        echo "🔍 健康检查:"
        if curl -s "http://localhost:$PORT/api/health" > /dev/null; then
            echo "✅ 服务健康"
        else
            echo "❌ 服务不健康"
        fi
    else
        echo "❌ 服务未运行"
    fi
}

# 查看日志
logs() {
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        docker logs -f $CONTAINER_NAME
    else
        log_error "服务未运行"
        exit 1
    fi
}

# 停止服务
stop() {
    log_info "停止服务..."
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
    log_info "重启服务..."
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        docker restart $CONTAINER_NAME
        log_success "服务已重启"
    else
        log_warning "服务未在运行"
    fi
}

# 清理函数
cleanup() {
    log_info "清理资源..."
    
    # 清理未使用的镜像
    docker image prune -f
    
    # 清理未使用的容器
    docker container prune -f
    
    # 清理未使用的网络
    docker network prune -f
    
    log_success "清理完成"
}

# 显示帮助信息
show_help() {
    echo "Homework Mentor 部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  deploy    部署最新版本 (默认)"
    echo "  rollback  回滚到上一个版本"
    echo "  status    查看服务状态"
    echo "  logs      查看服务日志"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  cleanup   清理Docker资源"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 deploy    # 部署最新版本"
    echo "  $0 status    # 查看服务状态"
    echo "  $0 logs      # 查看日志"
}

# 主程序
main() {
    case "${1:-deploy}" in
        deploy)
            deploy
            ;;
        rollback)
            rollback
            ;;
        status)
            status
            ;;
        logs)
            logs
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主程序
main "$@" 