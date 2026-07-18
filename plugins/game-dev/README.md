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
| `/game-dev:start <任务> [--auto]` | 启动新功能开发全流程 |
| `/game-dev:refactor <目标> [--auto]` | 启动重构工作流 |
| `/game-dev:fix <BUG 描述> [--auto]` | 启动 BUG 修复工作流 |

`--auto` 启用全自动模式，不在审查点暂停。

## 架构

```
orchestrator (新功能)        refactor-conductor (重构)        fix-conductor (修BUG)
  ├── plan (brainstorming)     ├── 分析 → impact.md           ├── behavior clarification
  ├── exec --mode feat         ├── plan (受impact约束)         ├── test agent BUG复现测试
  │   ├── test-agent (RED)     ├── exec --mode refactor       ├── fix-agent (fix-loop)
  │   └── coding (GREEN)       │   ├── test-agent (RED)       │   ├── debug-root-cause
  └── review (合规审查)        │   └── coding (GREEN)         │   └── fix + verify loop
                               └── review (合规审查)           ├── VERIFY (test-agent)
                                                               └── review (合规审查)
```

## 测试

使用 Ren'Py 原生 `testcase` / `testsuite` 框架。完整参考见 `references/renpy-testing.md`。

```bash
renpy.sh <project> test                           # 运行全部测试
renpy.sh <project> test <testsuite_name>          # 运行指定 testsuite
renpy.sh <project> test <testsuite>::<testcase>   # 运行单个 testcase
renpy.sh <project> test --report-detailed         # 详细输出
```

## 前置要求

- Ren'Py SDK（通过 `RENPY_SDK` 环境变量配置）

## 设计文档

所有设计文档存储在 `.renpy-dev/{kind}-{N}/`（feat/refactor/fix）：

```
.renpy-dev/{kind}-{N}/
├── plan.md             # 自包含设计文档 (exec 唯一读取)
├── progress.json       # 任务追踪 (断点续跑)
├── impact.md           # (refactor) 修改范围约束
└── .work/              # 中间产物
    ├── requirements.md
    ├── architecture.md
    ├── design.md
    └── debug-analysis.md  # (fix) 根因分析
```

## 许可

Apache License 2.0
