# Ren'Py Dev Plugin — Ren'Py AI Development Plugin

Plan → Exec → Review 自主循环，完整 Ren'Py 视觉小说开发流程。

## 概述

`renpy-dev` 是一个 Claude Code 插件，为 Ren'Py 视觉小说项目提供完整的 AI 辅助开发工作流：

- **plan** — 分析需求，输出设计文档，不写代码
- **exec** — 读取 plan，TDD 驱动实现（spawn 独立 agent）
- **review** — 审查 agent 产出合规性
- **自循环** — orchestrator 管理 plan→exec→review 全流程

## 命令

| 命令 | 说明 |
|------|------|
| `/renpy-dev:start <任务> [--auto]` | 启动新功能开发全流程 |
| `/renpy-dev:refactor <目标> [--auto]` | 启动重构工作流 |

`--auto` 启用全自动模式，不在审查点暂停。

## 架构

```
orchestrator (新功能)                refactor-conductor (重构)
  ├── plan (设计文档)                  ├── plan → analyze → impact
  ├── exec (TDD实现)                   ├── design → change-plan
  │   ├── test-agent (RED)            ├── exec (TDD重构)
  │   └── coding (GREEN)              │   ├── test-agent (RED)
  └── review (合规审查)                │   └── coding (GREEN)
                                      └── review (合规审查)
```

## 测试基础设施

插件提供三层自测体系（`assets/test-infra/`）：

- **Structure** — renpy lint + AST 检查 (< 5s)
- **Behavior** — headless SDK 运行 test_b_* labels (~30s)
- **Visual** — 截图 diff baselines (~60s)

单入口：`python tools/test.py`

## 前置要求

- Ren'Py SDK（通过 `RENPY_SDK` 环境变量配置）
- Python 3.x（用于 `tools/test.py`）
- PIL/Pillow + NumPy（用于 Layer 3 visual diff）

## 设计文档

所有设计文档存储在 `.renpy-dev/feat-{N}/` 或 `.renpy-dev/refactor-{N}/`：

```
.renpy-dev/feat-{N}/
├── requirements.md     # 需求摘要
├── architecture.md     # 架构设计 (Mermaid)
├── design.md           # 详细设计
├── plan.md             # 执行计划
└── progress.json       # 任务追踪 (断点续跑)
```

## 许可

Apache License 2.0
