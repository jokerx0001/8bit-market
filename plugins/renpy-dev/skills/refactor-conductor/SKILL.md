---
name: renpy-dev:refactor-conductor
description: |
  工作流状态机，协调 Ren'Py 代码重构的完整周期。与 orchestrator 唯一区别：
  先分析影响范围并写入 impact.md，再调用 plan（plan 读取 impact.md 约束设计范围）。

  <example>
  Context: 用户需要对现有 Ren'Py 代码进行重构
  user: "/renpy-dev:refactor 将角色选择界面的数据持久化从 persistent 迁移到自定义 save 系统"
  assistant: "分析影响范围 → 写入 impact.md → 调用 plan（带约束设计）→ exec。"
  <commentary>
  重构多一步：先分析影响范围，生成 impact.md 约束 plan 的设计范围。
  </commentary>
  </example>
---

# Ren'Py Refactor Conductor — 重构状态机

## 工作流

```
创建目录 → [UI检测] → design-ui → 分析影响范围 → 写入 impact.md → plan(读impact约束) → [审查] → exec → review
     │        ↓           ↑                       ↑_________正常流程_________↑
     │        └── 无UI ───┘
     └── artifact-manager
```

---

### 第一步：创建任务目录 + UI 检测

**1a. 创建目录：**

```
Skill({skill: "renpy-dev:artifact-manager", args: "create_task kind=refactor phase=analyze"})
```

artifact-manager 会读取 `current-state.json`、递增 `counters.refactor`、创建 `.renpy-dev/refactor-{N}/`、写回状态。返回 `task_dir`。

**1b. UI 检测：**

分析用户的任务描述和重构目标，判断是否涉及 UI 视觉设计：

**触发条件（满足任一即为 UI 任务）：**
- 涉及创建新模块且明显包含新界面
- 涉及现有模块的视觉重设计

**判定原则：宁可误判多调 design-ui（它会自己判断并跳过不需要的部分），也不要漏判。**

**涉及 UI 视觉设计 →** 调用 design-ui：

```
Skill({skill: "renpy-dev:design-ui", args: "--task-dir {task_dir}"})
```

等待 design-ui 完成后再进入 1c。

**不是 UI 任务 →** 直接进入 1c。

**1c. 分析影响范围：**

充分阅读现有代码：

1. 读取受影响的 `.rpy` 文件
2. 使用 Glob/Grep 发现关联文件（共享 screen、共用 label、数据依赖）
3. 识别当前实现模式
4. 查找已有测试文件（`game/tests/test_*.rpy`）
5. 检查测试基础设施状态（`game/tests/` 目录是否存在，`RENPY_SDK` 是否设置）
6. 评估级联影响和风险

### 第二步：写入 impact.md

按 `plugins/renpy-dev/references/impact-format.md` 格式写入 `{task_dir}/impact.md`。关键信息：
- 修改范围（硬约束，plan 不得超出）
- 排除范围（plan 不得触碰）
- 已有测试（plan 必须在测试策略中保护）
- **测试基础设施状态**（如缺失，plan 必须添加 `[AI-0]` bootstrap 任务）
- 风险点（plan 必须在设计摘要中应对）
- 特殊约束（用户指定的限制）

### 第三步：调用 plan

调用 `renpy-dev:plan` skill。plan 会：
1. 读取 `impact.md` 获取约束
2. 在约束范围内用 `superpowers:brainstorming` 分析+设计
3. 自己编写自包含的 `plan.md`

### 第四步：审查

**正常模式：** 暂停，等待用户批准 plan.md。
**全自动模式（--auto）：** 直接进入 exec。

### 第五步：Exec — TDD 重构循环

调用 `renpy-dev:exec` skill，传入参数：

```
Skill({skill: "renpy-dev:exec", args: "--mode refactor --task-dir .renpy-dev/refactor-{N}"})
```

**重构额外约束：**
- coding agent 必须保证所有已有测试继续通过
- 已有测试被破坏 → 立即反馈修复，最高优先级

### 第六步：Review

调用 `renpy-dev:review` skill。重构额外检查：
- 已有测试是否全部通过（无回归）
- 重构前后 jump/call 链是否一致

---

## 对比

| | orchestrator | refactor-conductor |
|--|:--:|:--:|
| 创建目录 | ✅ artifact-manager | ✅ artifact-manager |
| UI 检测 + design-ui | ✅ | ✅ |
| 分析影响范围 | — | ✅ 写 impact.md |
| plan (brainstorming → 写 plan.md) | ✅ | ✅ 读 impact.md 约束 |
| 审查 plan.md | ✅ | ✅ |
| exec | ✅ | ✅ + 已有测试保护 |
| review | ✅ | ✅ + 回归检查 |

## 约束

| 约束 | 说明 |
|------|------|
| 测试先行 | 没有测试覆盖就不修改代码 |
| 不改测试 | coding agent 不允许修改测试代码 |
| 范围纪律 | 只修改 plan.md 中列出的文件 |
| 已有测试不破坏 | 所有已有测试必须继续通过 |
| 真实代码 | 不允许空代码、假代码 |
