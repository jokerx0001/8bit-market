---
name: fix
description: "启动游戏项目 BUG 修复工作流。自动检测技术栈，行为澄清 → BUG 复现测试 → 根因分析 → plan.md → exec --mode fix。"
argument-hint: "<BUG 描述 + 预期行为> [--auto]"
---

Invoke the `game-dev:fix-conductor` skill with the user's arguments. Pass `--auto` for fully autonomous mode.
