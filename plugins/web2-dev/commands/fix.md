---
name: web2-dev:fix
description: |
  启动 BUG 修复工作流。行为澄清 → BUG 复现测试 → 修复循环 → 验证。

  <example>
  user: "/web2-dev:fix 用户注册时邮箱验证未生效"
  assistant: "行为澄清 → BUG 复现测试 → coding agent 修复循环 → code-review。"
  </example>
argument-hint: <bug description> [--auto]
allowed-tools: ["Skill"]
---

# Bug Fix Workflow

启动 BUG 修复全流程。

## 参数解析

- `--auto`：全自动模式
- 其他所有内容 → BUG 描述，原样传给 orchestrator

## 执行

```
Skill({skill: "web2-dev:fix-orchestrator", args: "<用户输入原文>"})
```
