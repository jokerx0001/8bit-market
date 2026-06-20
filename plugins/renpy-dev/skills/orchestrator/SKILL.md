---
name: renpy-dev:orchestrator
description: |
  工作流状态机，协调 Ren'Py 新功能开发的完整周期：plan → exec → review。
  用户可以通过 --auto 标志控制是全自动运行还是在审查点暂停。

  <example>
  Context: 用户提出新的 Ren'Py 开发需求
  user: "/renpy-dev:start 开发一个角色选择界面，包含角色头像、名称和选择按钮"
  assistant: "我将使用 orchestrator 协调开发流程。plan → exec → review。"
  <commentary>
  新功能开发，需要完整的 plan→exec→review 流程。
  </commentary>
  </example>

  <example>
  Context: 用户想要全自动模式
  user: "/renpy-dev:start 开发存档界面 --auto"
  assistant: "全自动模式启动。将完成 plan → exec → review 全流程，不在中间暂停。"
  <commentary>
  --auto 标志表示全自主模式，不等人工审查。
  </commentary>
  </example>
---

# Ren'Py Orchestrator — 工作流状态机

协调从需求到完成的完整开发周期。

## 工作流状态

```
idle → plan → [human_review] → exec → review → completed
                   ↑                              ↓
                   └── 人工拒绝 → 修改 plan ──────→
```

## 两种模式

### 正常模式（默认）

```
plan → 输出设计文档 → 等待用户审查
  ├── 用户批准 → 自动进入 exec
  └── 用户拒绝 → 修改 plan，重新提交
```

### 全自动模式（`--auto`）

```
plan → 直接进入 exec → review → 完成
（无人工审查点，全部自动）
```

---

## 阶段执行

### 阶段 1：Plan — 设计阶段

1. 确定 N：
   - 读取 `.renpy-dev/current-state.json`
   - **文件不存在** → 初始化 `{"current_task": "", "current_kind": "", "counters": {"feat": 0, "refactor": 0, "fix": 0}}`
   - **旧格式**（有 `current_feat` 无 `counters`）→ 按 `counters = {"feat": N, "refactor": 0, "fix": 0}` 转换
   - 从 `counters.feat` 取值，+1 得到 N
2. 加载 `renpy-dev:plan` skill，传入 `task_dir = .renpy-dev/feat-{N}`
3. 执行设计全流程：
   - 创建 `{task_dir}/.work/` 目录
   - 中间产物 → `.work/`（requirements, architecture, design）
   - 自包含计划 → `plan.md`（人类审查此文件）
4. 写回 `current-state.json`，`counters.feat = N`
5. 输出 plan.md 路径

**正常模式：** 暂停，等待用户审查 plan.md。
**全自动模式：** 直接进入阶段 2。

状态记录：
```json
{
  "current_task": "feat-1",
  "current_kind": "feat",
  "phase": "plan",
  "mode": "manual",
  "counters": {
    "feat": 1,
    "refactor": 0,
    "fix": 0
  },
  "started_at": "..."
}
```

保存到 `.renpy-dev/current-state.json`。

### 阶段 2：Exec — 实现阶段

**触发条件：**
- 全自动模式：plan 完成后直接进入
- 正常模式：用户明确批准后进入（如 "审查通过，开始实现"）

1. 确定 `task_dir` = `.renpy-dev/feat-{N}`（N 从 current-state.json 的 counters.feat 获取）
2. 加载 `renpy-dev:exec` skill，传入参数：
   ```
   Skill({skill: "renpy-dev:exec", args: "--mode feat --task-dir .renpy-dev/feat-{N}"})
   ```
3. exec 按 TDD 循环逐任务执行：
   - RED: spawn test agent
   - GREEN: spawn coding agent
   - VERIFY: 运行 `renpy.sh project test`
   - REFACTOR: 主会话审查
4. 支持断点续跑（读取 progress.json）
5. 全部 AI 任务完成后输出完成报告

### 阶段 3：Review — 审查阶段

**触发条件：** exec 全部任务完成

1. 加载 `renpy-dev:review` skill
2. 审查 agent 产出合规性
3. 提醒 `[HUMAN]` 任务
4. 输出最终报告

### 阶段 4：Completed — 完成

```
## 开发完成

**Feat: feat-{N}**
**设计文档：** .renpy-dev/feat-{N}/plan.md
**中间产物：** .renpy-dev/feat-{N}/.work/
**任务完成：** {done}/{total}
**测试：** ✅ 全部通过
**人工任务：** {count} 项待完成
```

---

## 状态存储

`.renpy-dev/current-state.json`：

```json
{
  "current_task": "feat-1",
  "current_kind": "feat",
  "phase": "exec",
  "mode": "manual",
  "counters": {
    "feat": 1,
    "refactor": 0,
    "fix": 0
  },
  "started_at": "2026-06-18T10:00:00Z"
}
```

> **向后兼容**：旧版使用 `current_feat` 字段。读取时如发现旧字段而无 `current_task`/`counters`，按 `current_task = current_feat`、`current_kind = "feat"`、`counters = {"feat": N, "refactor": 0, "fix": 0}` 转换。

## 错误处理

- **plan 阶段失败**：输出具体错误，等待用户指示
- **exec 阶段任务失败**：不限重试，连续 5 轮无进展才报告
- **review 阶段违规**：反馈给对应 agent 修复，重新审查
- **用户中断**：progress.json 保存当前状态，下次启动可继续

## 约束

- plan 输出的设计文档是实现的唯一真相来源
- exec 只允许 spawn agent 进行代码工作，主会话负责协调和审查
- coding agent 绝不修改测试代码
- 所有测试通过才算任务完成
