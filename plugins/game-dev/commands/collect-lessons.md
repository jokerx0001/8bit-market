---
name: collect-lessons
description: "手动触发经验收集。回顾最近完成的游戏项目开发任务上下文，提取测试和编码经验，按技术栈分类后记录。"
argument-hint: "[task-dir] (可选，不填则使用 current-state.json 中的当前任务)"
---

Invoke the `game-dev:collect-lessons` skill. If the user provided a task directory, pass it as `task_dir`. Otherwise, read the current-state.json to determine the current task.
