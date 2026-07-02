---
name: game-dev:artifact-manager
description: |
  管理产物目录下的任务目录创建和全局状态。三个 conductor 通过本 skill 统一创建任务目录，消除样板代码重复。
  dev_dir 由 conductor 在检测技术栈后显式传入，不自己读 config。
---

# Game Dev Artifact Manager

管理产物目录下的 `current-state.json` 和任务目录创建。

## 核心功能

### create_task — 创建任务目录

**入参（全部必传）：**
- `kind`: `feat` / `refactor` / `fix`
- `dev_dir`: `.renpy-dev` 或 `.godot-dev`
- `phase`（可选）: 初始阶段名，不传则用默认值：
  - feat → `"plan"`
  - refactor → `"analyze"`
  - fix → `"clarification"`

**执行：**

1. 读取 `{dev_dir}/current-state.json`
   - **文件不存在** → 初始化为 `{"current_task": "", "current_kind": "", "counters": {"feat": 0, "refactor": 0, "fix": 0}}`
2. 从 `counters.{kind}` 取值，+1 得到 N
3. 创建目录：`mkdir -p {dev_dir}/{kind}-{N}`
4. 写回 `current-state.json`：
   ```json
   {
     "current_task": "{kind}-{N}",
     "current_kind": "{kind}",
     "phase": "{phase}",
     "counters": { "...原有值不变...", "{kind}": N }
   }
   ```
5. 输出 `task_dir = {dev_dir}/{kind}-{N}`

**输出：**
```
已创建任务目录：{dev_dir}/{kind}-{N}/
```

## 使用方式

conductor 中这样调用：

```
Skill({skill: "game-dev:artifact-manager", args: "--kind feat --dev-dir .godot-dev"})
```

返回 `task_dir`。后续阶段通过 `--task-dir` 参数定位任务，自行读 `references/{tech}/config.md`。
