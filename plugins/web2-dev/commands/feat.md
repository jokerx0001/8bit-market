---
name: web2-dev:feat
description: |
  启动新功能开发工作流。产出模块级需求文档、架构设计（含领域模型）、
  详细设计（按模块），然后进入 TDD 实现循环。

  <example>
  user: "/web2-dev:feat 在用户模块中增加手机号绑定功能"
  assistant: "启动新功能开发。检测技术栈 → grill → 模块级需求 → 架构 → 详细设计 → plan → exec"
  </example>

  <example>
  user: "/web2-dev:feat 增加文件上传接口 --auto"
  assistant: "全自动模式。跳过人工审查点。"
  </example>
argument-hint: <task description> [--auto]
allowed-tools: ["Skill"]
---

# Feature Development Workflow

启动新功能开发全流程。

## 参数解析

- `--auto`：全自动模式，跳过 plan 审查点
- 其他所有内容 → 任务描述，原样传给 orchestrator

## 执行

```
Skill({skill: "web2-dev:feat-orchestrator", args: "<用户输入原文>"})
```
