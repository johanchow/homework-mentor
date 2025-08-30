#!/bin/bash

set -e

APP_NAME="fastapi-app"
# GitHub Container Registry 仓库地址
# 格式：ghcr.io/用户名/仓库名
GHCR_REPO="ghcr.io/johanchow/homework-mentor"
CONTAINER_NAME="fastapi_container"
PORT=5556
ROLLBACK_TAG_FILE="rollback_tag.txt"
# 如果ENVIRONMENT=test，则用test镜像，否则用latest镜像
if [ "$ENVIRONMENT" = "test" ]; then
    TAG="test"
else
    TAG="latest"
fi

function deploy() {
    echo "✅ Pulling image: $GHCR_REPO:$TAG"
    docker pull $GHCR_REPO:$TAG

    echo "📦 Backing up current container (if exists)..."
    if docker ps -a | grep -q $CONTAINER_NAME; then
        CURRENT_TAG=$(docker inspect --format='{{index .Config.Image}}' $CONTAINER_NAME | cut -d':' -f2)
        echo "$CURRENT_TAG" > "$ROLLBACK_TAG_FILE"
        docker rm -f $CONTAINER_NAME
    fi

    echo "🚀 Starting new container"
    docker run -d \
        --name $CONTAINER_NAME \
        --env-file .env \
        -p $PORT:5556 \
        $GHCR_REPO:$TAG
    echo "🔄 Already started container..."
}

function status() {
    docker ps | grep $CONTAINER_NAME
}

function rollback() {
    if [ ! -f "$ROLLBACK_TAG_FILE" ]; then
        echo "❌ No rollback version found"
        exit 1
    fi

    PREV_TAG=$(cat $ROLLBACK_TAG_FILE)
    echo "🕒 Rolling back to $PREV_TAG..."
    deploy $PREV_TAG
}

function restart() {
    echo "🔁 Restarting container..."
    docker restart $CONTAINER_NAME
}

function logs() {
    if docker ps | grep -q $CONTAINER_NAME; then
        echo "📋 Showing logs for $CONTAINER_NAME..."
        docker logs -f $CONTAINER_NAME
    else
        echo "❌ Container $CONTAINER_NAME is not running"
        echo "💡 Use '$0 status' to check container status"
        exit 1
    fi
}

case "$1" in
    deploy)
        deploy "$2"
        ;;
    status)
        status
        ;;
    rollback)
        rollback
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    *)
        echo "Usage: $0 {deploy [<tag>]|status|rollback|restart|logs}"
        exit 1
        ;;
esac
