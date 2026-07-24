---
name: start
description: "启动游戏项目新功能开发工作流。自动检测技术栈（Ren'Py / Godot），使用 orchestrator 协调 plan → [resources] → exec → completed 全流程。"
argument-hint: "<任务描述> [--auto]"
---

Invoke the `game-dev:orchestrator` skill with the user's arguments passed through verbatim.

**CRITICAL — `--auto` passthrough rule:**
- If the user's original input contains `--auto` → forward it to the orchestrator
- If the user's original input does NOT contain `--auto` → do NOT add it
- NEVER fabricate `--auto`. The orchestrator's Step 0e determines mode by checking the user's original input for `--auto`. Adding it when the user didn't include it bypasses the human review checkpoint that the user explicitly chose (normal mode).
