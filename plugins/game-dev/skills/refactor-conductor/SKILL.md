---
name: game-dev:refactor-conductor
description: |
  工作流状态机，协调 Ren'Py 代码重构的完整周期。与 orchestrator 唯一区别：
  先分析影响范围并写入 impact.md，再调用 plan（plan 读取 impact.md 约束设计范围）。

  <example>
  Context: 用户需要对现有 Ren'Py 代码进行重构
  user: "/game-dev:refactor 将角色选择界面的数据持久化从 persistent 迁移到自定义 save 系统"
  assistant: "分析影响范围 → 写入 impact.md → 调用 plan（带约束设计）→ exec。"
  <commentary>
  重构多一步：先分析影响范围，生成 impact.md 约束 plan 的设计范围。
  </commentary>
  </example>
---

# Ren'Py Refactor Conductor — 重构状态机

## 工作流

```
创建目录 → [UI检测] → design-ui → 分析影响范围 → 写入 impact.md → plan(读impact约束) → [审查] → exec → completed
     │        ↓           ↑                       ↑_________正常流程_________↑
     │        └── 无UI ───┘
     └── artifact-manager
```

---

### 第零步：检测技术栈 + 创建上下文

**0a — 读 CLAUDE.md 确定 tech**（同 orchestrator）。

**0b — 读 `references/{tech}/config.md`**，提取上下文字段。

**0c — 创建任务目录：**

```
Skill({skill: "game-dev:artifact-manager", args: "--task-dir {dev_dir}/refactor-{N} --kind refactor --dev-dir {dev_dir}"})
```

返回 `task_dir`。创建 `.work/` 并写入 `references/{tech}/config.md`（同 fix-conductor）。

### 第一步：UI 检测

分析用户的任务描述和重构目标，判断是否涉及 UI 视觉设计。

**Godot 项目额外判断：只对 Control UI 场景触发。**

**触发条件（满足任一即为 UI 任务）：**
- 涉及创建新模块且明显包含新界面
- 涉及现有模块的视觉重设计

**判定原则：宁可误判多调 design-ui（它会自己判断并跳过不需要的部分），也不要漏判。**

**涉及 UI 视觉设计 →** 调用 design-ui：

```
Skill({skill: "game-dev:design-ui", args: "--task-dir {task_dir}"})
```

等待 design-ui 完成后再进入 1c。

**不是 UI 任务 →** 直接进入 1c。

**1c. 分析影响范围：**

充分阅读现有代码：

1. 读取受影响的 `.rpy` 文件
2. 使用 Glob/Grep 发现关联文件（共享 screen、共用 label、数据依赖）
3. 识别当前实现模式
4. 查找已有测试文件（`{test_dir}/test_*.rpy`）
5. 检查测试基础设施状态（`{test_dir}/` 目录是否存在，`RENPY_SDK` 是否设置）
6. 评估级联影响和风险

### 第二步：写入 impact.md

按 `references/impact-format.md` 格式写入 `{task_dir}/impact.md`。关键信息：
- 修改范围（硬约束，plan 不得超出）
- 排除范围（plan 不得触碰）
- 已有测试（plan 必须在测试策略中保护）
- **测试基础设施状态**（如缺失，plan 必须添加 `[AI-0]` bootstrap 任务）
- 风险点（plan 必须在设计摘要中应对）
- 特殊约束（用户指定的限制）

### 第三步：调用 plan

调用 `game-dev:plan` skill。plan 会：
1. 读取 `impact.md` 获取约束
2. 在约束范围内用 `superpowers:brainstorming` 分析+设计
3. 自己编写自包含的 `plan.md`

### 第四步：审查

**正常模式：** 暂停，等待用户批准 plan.md。
**全自动模式（--auto）：** 直接进入 exec。

### 第五步：Exec — TDD 重构循环

调用 `game-dev:exec` skill，传入参数：

```
Skill({skill: "game-dev:exec", args: "--mode refactor --task-dir {dev_dir}/refactor-{N}"})
```

**重构额外约束：**
- coding agent 必须保证所有已有测试继续通过
- 已有测试被破坏 → 立即反馈修复，最高优先级






























