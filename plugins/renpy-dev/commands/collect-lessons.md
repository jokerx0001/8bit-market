---
name: collect-lessons
description: "手动触发经验收集。回顾最近完成的 Ren'Py 开发任务上下文，提取测试和编码经验，查阅 Ren'Py 文档验证后记录到 .renpy-dev/。"
argument-hint: "[task-dir] (可选，不填则使用 current-state.json 中的当前任务)"
---

Invoke the `renpy-dev:collect-lessons` skill. If the user provided a task directory (e.g. `feat-1`, `.renpy-dev/fix-2`), pass it as `task_dir`. Otherwise, read `.renpy-dev/current-state.json` to determine the current task.
