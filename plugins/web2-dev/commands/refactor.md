---
name: web2-dev:refactor
description: |
  启动代码重构工作流。分析现有代码影响范围 → 变更计划 → TDD 重构循环。

  <example>
  user: "/web2-dev:refactor 将文件解析从同步改为异步处理"
  assistant: "分析影响范围 → impact.md → plan → exec 重构循环。"
  </example>
argument-hint: <target> [--auto]
allowed-tools: ["Skill"]
---

# Refactor Workflow

启动代码重构全流程。

## 参数解析

- `--auto`：全自动模式
- 其他所有内容 → 重构目标和约束，原样传给 orchestrator

## 执行

```
Skill({skill: "web2-dev:refactor-orchestrator", args: "<用户输入原文>"})
```
