---
name: renpy-dev:artifact-manager
description: |
  管理 .renpy-dev/ 下的任务目录创建和全局状态。三个 conductor（orchestrator / refactor-conductor / fix-conductor）通过本 skill 统一创建任务目录，消除样板代码重复。
---

# Ren'Py Artifact Manager

管理 `.renpy-dev/` 下的目录创建和 `current-state.json`。

## 核心功能

### 1. create_task — 创建任务目录

**入参：**
- `kind`: `feat` / `refactor` / `fix`
- `phase`（可选）: 初始阶段名，不传则用默认值：
  - feat → `"plan"`
  - refactor → `"analyze"`
  - fix → `"clarification"`

**执行：**

1. 读取 `.renpy-dev/current-state.json`
   - **文件不存在** → 初始化为 `{"current_task": "", "current_kind": "", "counters": {"feat": 0, "refactor": 0, "fix": 0}}`
   - **旧格式**（有 `current_feat` 无 `counters`）→ 按 `counters = {"feat": N, "refactor": 0, "fix": 0}` 转换
2. 从 `counters.{kind}` 取值，+1 得到 N
3. 创建目录：`mkdir -p .renpy-dev/{kind}-{N}`
4. 写回 `current-state.json`：
   ```json
   {
     "current_task": "{kind}-{N}",
     "current_kind": "{kind}",
     "phase": "{phase}",
     "counters": { "...原有值不变...", "{kind}": N }
   }
   ```
5. 输出 `task_dir = .renpy-dev/{kind}-{N}`

**输出：**
```
已创建任务目录：.renpy-dev/{kind}-{N}/
```

**约束：** 三种 kind 的计数器互相独立。`feat-1`、`refactor-1`、`fix-1` 可同时存在。

---

## 使用方式

conductor 中这样调用：

```
Skill({skill: "renpy-dev:artifact-manager", args: "create_task kind=feat"})
```

返回 `task_dir` 后，conductor 继续执行其专属流程。
