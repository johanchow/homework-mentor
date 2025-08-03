#!/bin/bash

set -e

APP_NAME="fastapi-app"
GHCR_REPO="ghcr.io/johanchow/your-repo-name"
CONTAINER_NAME="fastapi_container"
PORT=8000
ROLLBACK_TAG_FILE="rollback_tag.txt"

function deploy() {
    TAG=${1:-latest}

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
        -p $PORT:8000 \
        $GHCR_REPO:$TAG
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
    *)
        echo "Usage: $0 {deploy [<tag>]|status|rollback|restart}"
        exit 1
        ;;
esac
