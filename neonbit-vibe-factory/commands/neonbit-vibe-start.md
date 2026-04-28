---
name: neonbit-vibe-start
description: 启动新的开发任务工作流
argument-hint: <任务描述>
allowed-tools: ["Read", "Write", "Bash", "Skill"]
---

# /neonbit-vibe-start

启动一个新的开发任务工作流。

## 使用方式

```
/neonbit-vibe-start 开发一个用户管理模块，包含增删改查功能
```

## 执行流程

1. **调用 `orchestrator` skill** — 开始协调完整工作流
2. **创建 feat 目录** — 通过 `artifact-manager` skill 初始化
3. **进入需求收集阶段** — 解析任务描述
4. **按阶段执行** — 架构设计 → 详细设计 → 执行计划 → 开发 → 测试

## 参数

- `任务描述`: 简洁描述需要开发的功能，包括：
  - 功能范围
  - 涉及页面（如果有）
  - 涉及接口（如果有）
  - 技术栈偏好（如果有）

## 示例

```
/neonbit-vibe-start 开发商品展示页面，支持分类筛选和搜索
/neonbit-vibe-start 实现用户认证模块，JWT 方式
/neonbit-vibe-start 订单管理模块，包含下单、支付、取消流程
```

## 约束

- 每次 `/neonbit-vibe-start` 创建一个新的 feat 目录
- 已有 feat 正在执行时，新命令会创建新的 feat-{N+1}
- 使用 `current-state.json` 追踪全局状态