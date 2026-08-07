#!/usr/bin/env bash

# ============================================
# {{PROJECT_NAME}} Docker 镜像构建 + 推送
#
# 依赖环境变量:
#   REGISTRY_URL        私有 Registry 地址
#   REGISTRY_IMAGE_NAME 镜像名称
#   BUILD_CONTEXT       docker build 上下文路径
# ============================================

set -e

IMAGE_NAME="${REGISTRY_IMAGE_NAME:?缺少 REGISTRY_IMAGE_NAME}"
REGISTRY="${REGISTRY_URL:?缺少 REGISTRY_URL}"
BUILD_CTX="${BUILD_CONTEXT:-.}"

FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}"

echo "========================================="
echo "Docker 镜像构建"
echo "========================================="
echo "镜像: ${FULL_IMAGE_NAME}"
echo "上下文: ${BUILD_CTX}"
echo "========================================="

docker build -t "${FULL_IMAGE_NAME}" "${BUILD_CTX}"

docker tag "${FULL_IMAGE_NAME}" "${FULL_IMAGE_NAME}:latest"

echo "推送镜像到 Registry..."
docker push "${FULL_IMAGE_NAME}"

echo "========================================="
echo "推送完成: ${FULL_IMAGE_NAME}"
echo "========================================="
