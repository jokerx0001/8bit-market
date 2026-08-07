#!/usr/bin/env bash

# ============================================
# {{PROJECT_NAME}} 启动脚本
#
# 依赖环境变量:
#   IMAGE            完整镜像名 (registry/name:tag)
#   CONTAINER_NAME   容器名
#   NACOS_ADDR       Nacos 地址
#   NACOS_NAMESPACE  Nacos 命名空间
#   NACOS_USERNAME   Nacos 用户名
#   NACOS_PASSWORD   Nacos 密码
# ============================================

set -e

CONTAINER_NAME="{{CONTAINER_NAME}}"

docker pull "${IMAGE:?缺少 IMAGE}"

docker run -d \
  --network=host \
  --restart always \
  --name "${CONTAINER_NAME}" \
  -v /data/deploy/logs:/data/deploy/logs \
  -v "/data/deploy/${CONTAINER_NAME}:/data/deploy/${CONTAINER_NAME}" \
  -e {{ENV_PREFIX}}_NACOS_ADDR="${NACOS_ADDR}" \
  -e {{ENV_PREFIX}}_NACOS_NAMESPACE="${NACOS_NAMESPACE}" \
  -e {{ENV_PREFIX}}_NACOS_USERNAME="${NACOS_USERNAME}" \
  -e {{ENV_PREFIX}}_NACOS_PASSWORD="${NACOS_PASSWORD}" \
  "${IMAGE}"
