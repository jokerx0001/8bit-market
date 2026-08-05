---
name: web2-dev:refactor-orchestrator
description: |
  代码重构工作流状态机。先分析影响范围写入 impact.md 约束设计范围，
  再调用 plan 在约束内设计，最后 exec 执行 TDD 重构循环。

  <example>
  Context: 用户通过 /web2-dev:refactor 启动重构
  user: "/web2-dev:refactor 将文件解析从同步改为异步处理"
  assistant: "分析影响范围 → impact.md → plan(带约束) → exec 重构循环。"
  </example>

  <example>
  Context: 全自动模式
  user: "/web2-dev:refactor 统一所有接口的错误响应格式 --auto"
  assistant: "全自动模式。跳过人工审查点。"
  </example>
---

# Refactor Orchestrator

重构工作流状态机。与 new/feat 的区别：先分析影响范围并写入 impact.md，再调用 plan（plan 读取 impact.md 约束设计范围）。

## 工作流

```
idle → [检测技术栈] → 保存用户原语 → grill
     → 分析影响范围 → impact.md
     → architecture + design → plan → [审查] → exec → completed
```

## 两种模式

### 正常模式（默认）
plan → 审查 → 用户批准 → exec

### 全自动模式（`--auto`）
跳过人工审查点。

---

## 阶段执行

### 阶段 0：检测技术栈 + 解析模式

同 new-orchestrator 阶段 0。

**硬门 — `--auto` 来源验证：** 从 `user-prompt.md` 中 grep `--auto`。来源不明 → 回退 normal。

回显确认：
```
## 技术栈确认
检测到: {tech}
dev_dir: {dev_dir}（从 config.md 产物目录节原样读取）
任务目录: {dev_dir}/refactor-{N}

## 运行模式
模式: {normal / auto}
```

**不猜测不缩写。**

### 阶段 1：创建任务目录

```
Skill({skill: "web2-dev:artifact-manager", args: "--kind refactor --dev-dir {dev_dir}"})
```

### 阶段 2：保存用户原语 + Grill 前置采访

同 new-orchestrator 阶段 2。**不可跳过，auto 模式也不例外。**

### 阶段 3：分析影响范围

充分阅读现有代码，结合用户原语和 grill 输出中的重构目标：

1. 读取 `user-prompt.md` 和 `grill-interview.md` 了解重构目标
2. 读取受影响的源文件
3. 使用 Glob/Grep 发现关联文件（共享接口、数据依赖、import 链）
4. 识别当前实现模式和公共接口
5. 查找已有测试文件
6. 评估级联影响和风险

### 阶段 4：写入 impact.md

产出 `{task_dir}/impact.md`，包含：
- **修改范围**（硬约束，plan 不得超出）
- **排除范围**（plan 不得触碰）
- **已有测试**（plan 必须在测试策略中保护）
- **风险点**（plan 必须在设计中应对）
- **特殊约束**（用户指定的限制）

### 阶段 5：Architecture + Design（在约束内设计）

```
Skill({skill: "web2-dev:architecture", args: "--task-dir {task_dir} --tech {tech}"})
Skill({skill: "web2-dev:design", args: "--task-dir {task_dir} --tech {tech}"})
```

architecture 和 design 必须读取 `impact.md` 获取约束，在约束范围内设计。

### 阶段 6：Plan — 任务分解

```
Skill({skill: "web2-dev:plan", args: "--task-dir {task_dir} --tech {tech}"})
```

产出 `{task_dir}/plan.md` — 需要重构的模块清单。

### 阶段 7：审查（normal 模式）

**必须**调用 `AskUserQuestion` 暂停等待用户审查：
```
AskUserQuestion({
  questions: [{
    question: "Plan 已生成，请审查 {task_dir}/plan.md。是否批准进入 exec 重构阶段？",
    header: "Plan Review",
    options: [
      {label: "批准", description: "plan.md 审查通过"},
      {label: "需要修改", description: "plan.md 有问题，描述需要改什么"}
    ]
  }]
})
```

- 用户选择"批准" → 进入阶段 8
- 用户选择"需要修改" → 用户描述修改意见，重新进入阶段 5-6 调整设计后重新提交

**auto 模式：** 跳过 AskUserQuestion，直接进入阶段 8。

### 阶段 8：Exec — TDD 重构循环

```
Skill({skill: "web2-dev:exec", args: "--mode refactor --task-dir {task_dir}"})
```

支持断点续跑（读取 progress.json）。

**重构额外约束：**
- coding agent 必须保证所有已有测试继续通过
- 已有测试被破坏 → 立即反馈修复，最高优先级
- 重构范围不得超出 impact.md 的硬约束

### 阶段 9：Completed

```
## 重构完成

**refactor-{N}**
**技术栈**: {tech}
**影响范围：** {task_dir}/impact.md
**设计文档：** {task_dir}/plan.md
**任务完成：** {done}/{total}
**测试：** ✅ 全部通过
**已有测试：** ✅ 无回归
```

---

## 状态存储

状态由 `web2-dev:artifact-manager` 统一管理。conductor 不直接操作 `current-state.json`。

## 错误处理

- **技术栈检测失败**：根据文件特征推断，向用户确认
- **plan 阶段失败**：输出具体错误，等待用户指示
- **exec 阶段任务失败**：不限重试，连续 5 轮无进展才报告
- **已有测试被破坏**：立即反馈 coding agent 修复，最高优先级
- **用户中断**：progress.json 保存当前状态，下次启动可继续

## Red Flags — STOP

- "dev_dir 大概就是 .web2-dev 吧，不用读 config"
- 没有回显 dev_dir 值就直接调用 artifact-manager
- "用户没加 --auto 但我可以跳过审查直接进入 exec，反正都一样"
- "plan 完成后不需要 AskUserQuestion，用户肯定批准"
- 没有回显 mode 确认就直接进入阶段执行

**以上任一条 → STOP。**
