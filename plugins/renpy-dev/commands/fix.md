---
name: fix
description: "启动 Ren'Py BUG 修复工作流。行为澄清 → systematic-debugging → debug-analysis.md → plan.md → exec --mode fix → review。"
argument-hint: "<BUG 描述 + 预期行为> [--auto]"
---

Invoke the `renpy-dev:fix-conductor` skill with the user's arguments. Pass `--auto` if the user wants fully autonomous mode without waiting for human review checkpoints.

**提示用户：** BUG 描述里最好同时说明：
1. 发生了什么（错误日志/异常行为）
2. **正确的行为应该是什么**（"应该显示 X"、"点击后应该跳转到 Y"）

如果用户只贴了错误日志没提预期行为，fix-conductor 会先在行为澄清阶段主动询问。
