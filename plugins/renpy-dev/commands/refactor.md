---
name: refactor
description: "启动 Ren'Py 重构工作流。plan → 分析现有代码 → 影响评估 → 综合设计 → 变更计划 → TDD 重构。"
argument-hint: "<重构目标> [约束条件] [--auto]"
---

Invoke the `renpy-dev:refactor-conductor` skill with the user's arguments. Pass `--auto` if the user wants fully autonomous mode without waiting for human review checkpoints.
