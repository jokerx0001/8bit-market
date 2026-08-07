#!/usr/bin/env bash

# ============================================
# {{PROJECT_NAME}} 停止脚本
# ============================================

set -e

CONTAINER_NAME="{{CONTAINER_NAME}}"

docker rm -f "${CONTAINER_NAME}"
