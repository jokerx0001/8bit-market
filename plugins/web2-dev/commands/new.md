---
name: web2-dev:new
description: |
  启动新项目开发工作流。产出项目级需求文档、架构设计（含领域模型）、
  详细设计（按模块），然后进入 TDD 实现循环。

  <example>
  user: "/web2-dev:new 做一个电商平台，支持用户注册、商品管理、订单处理"
  assistant: "启动新项目开发。检测技术栈 → grill → 项目级需求 → 架构 → 详细设计 → plan → exec"
  </example>

  <example>
  user: "/web2-dev:new 开发一个博客系统 --auto"
  assistant: "全自动模式。跳过人工审查点，plan 完成后直接进入 exec。"
  </example>
argument-hint: <task description> [--auto]
allowed-tools: ["Skill"]
---

# New Project Workflow

启动新项目开发全流程。

## 参数解析

- `--auto`：全自动模式，跳过 plan 审查点
- 其他所有内容 → 任务描述，原样传给 orchestrator

## 执行

```
Skill({skill: "web2-dev:new-orchestrator", args: "<用户输入原文>"})
```
