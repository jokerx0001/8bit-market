---
name: web2-dev:new-orchestrator
description: |
  新项目开发工作流状态机。从零开始构建项目：
  技术栈检测 → grill 前置采访 → 项目级需求 → 架构(含领域模型) → 详细设计(按模块)
  → [frontend-design] → plan(任务分解) → [审查] → exec。

  <example>
  Context: 用户通过 /web2-dev:new 启动新项目
  user: "/web2-dev:new 做一个电商平台"
  assistant: "检测技术栈 → grill → 项目级需求 → 架构 → 详细设计 → plan → exec。"
  </example>

  <example>
  Context: 全自动模式
  user: "/web2-dev:new 开发一个博客系统 --auto"
  assistant: "全自动模式。跳过人工审查点，plan 完成后直接进入 exec。"
  </example>
---

# New Project Orchestrator

新项目开发工作流状态机。产出项目级设计文档。

## 工作流

```
idle → [检测技术栈] → 保存用户原语 → grill → requirements → architecture → design
     → [frontend-design] → plan → [审查] → exec → completed
```

## 两种模式

### 正常模式（默认）
plan → 输出设计文档 → 等待用户审查
  ├── 用户批准 → 进入 exec
  └── 用户拒绝 → 修改 plan，重新提交

### 全自动模式（`--auto`）
plan → 直接进入 exec → 完成

---

## 阶段执行

### 阶段 0：前置检查 + 检测技术栈

**Step 0a — 运维配置检查（硬门，不可跳过）：**

```
1. 检查项目根目录 ops-local.md 是否存在
2. 检查文件非空（test -s ops-local.md）
3. 任一条件不满足 → 输出：

   ❌ 运维配置缺失

   项目根目录缺少 ops-local.md。
   后续 exec 阶段需要此文件进行基础设施部署和服务部署。
   请创建并填写后重新运行此命令。

   → 终止，不继续后续阶段。

4. 存在且非空 → 继续
```

**Step 0b — 解析运行模式：**

检查用户输入是否包含 `--auto`。

**硬门 — `--auto` 来源验证：**
1. 从 `{task_dir}/.work/user-prompt.md` 中 grep `--auto`
2. 如果 user-prompt.md 中不含 `--auto` 但 mode 被判定为 auto → **报错：`--auto` 来源不明，回退为 normal 模式**
3. 此检查防止上游节点错误地编造 `--auto`

回显确认后才能进入阶段 1：

```
## 运行模式
模式: {normal / auto}
{normal → "正常模式 — 将在 plan 完成后暂停等待审查"}
{auto → "全自动模式 — 不在审查点暂停，全流程自动执行"}
```

**Step 0c — 调用 stack-detector：**
```
Skill({skill: "web2-dev:stack-detector"})
```

stack-detector 产出 `{dev_dir}/stack.json`。**不猜测技术栈——不确定时向用户确认。**

### 阶段 1：创建任务目录

```
Skill({skill: "web2-dev:artifact-manager", args: "--kind new --dev-dir {dev_dir}"})
```

artifact-manager 读取 `current-state.json`、递增计数器、创建 `{dev_dir}/new-{N}/`、写回状态。返回 `task_dir`。

### 阶段 2：保存用户原语 + Grill 前置采访

**Grill 的目的是防止 AI 偏差，不是产出需求文档。** 通过 grilling（relentless interview）确保 AI 理解用户真正想要什么，避免自作主张跑偏。

**不可跳过，auto 模式也不例外。** grill 的目的不是用户审查——是防止 AI 误解用户意图后一路跑偏。`--auto` 跳过的是人工审查点（plan review），不是意图澄清。

**Step 2a — 保存用户原语：**

将用户的原始任务描述（触发 `/web2-dev:new` 的完整输入）原样写入：
```
{task_dir}/.work/user-prompt.md
```

这是用户的"原语"——未经任何加工。后续所有设计环节在综合理解任务时，必须回到这个原始输入。

**Step 2b — 运行 Grilling 采访：**
```
Skill({skill: "mattpocock-skills:grilling"})
```

**铁律：grill-interview.md 只能由 grilling skill 的返回内容写入。orchestrator 绝不自己创建、自己整理、自己补写此文件。**

grilling 返回什么就保存什么。**不分类、不整理、不转化。** 直接将完整输出写入：
```
{task_dir}/.work/grill-interview.md
```

**硬门 — 产出验证（不可跳过）：**

```
bash
test -s {task_dir}/.work/grill-interview.md && echo "GRILL_OK" || echo "GRILL_MISSING"
```

- `GRILL_MISSING` → **报告阻塞，不继续后续阶段。禁止自己写文件代替。**
- `GRILL_OK` → 读回文件前 20 行，确认内容是对话/采访格式（有 `?` 或 `？`）。**零问句 → 不是采访 → STOP，回到 Step 2b 重新 grill。**

**Step 2c — Domain Modeling 归档：**
```
Skill({skill: "mattpocock-skills:domain-modeling"})
```

domain-modeling 自行维护 `CONTEXT.md`（术语表）和 `docs/adr/`（架构决策记录）。**此步骤是补充性归档，返回空或失败不阻塞流程。**

**Step 2d — 传递规则：**

后面的所有设计环节（requirements、architecture、design、plan）**必须自己读取以下两份文件，综合理解去完成任务**：

| 文件 | 内容 | 用途 |
|------|------|------|
| `{task_dir}/.work/user-prompt.md` | 用户原始输入 | 检查用户是否直接指示了工作内容、技术约束 |
| `{task_dir}/.work/grill-interview.md` | grilling 采访记录 | 理解用户确认过的意图，防止 AI 跑偏 |

**各环节不得假设 grill-interview.md 有固定结构。** 它是什么格式就是什么格式，自己去读。

### 阶段 3：Requirements 需求管理

requirements skill 自行读取 `user-prompt.md` 和 `grill-interview.md`，综合理解用户意图后产出需求文档。

mode 为 `init`（新项目）：
```
Skill({skill: "web2-dev:requirements", args: "--task-dir {task_dir} --tech {tech} --mode init"})
```

产出：
- 项目级：`{dev_dir}/requirements.md`（跨任务持久的全量需求文档）
- per-task：`{task_dir}/.work/requirements.md`（本次需求，含行为确认清单）

### 阶段 4：Architecture 架构设计（含领域模型）

```
Skill({skill: "web2-dev:architecture", args: "--task-dir {task_dir} --tech {tech}"})
```

产出：`{task_dir}/.work/architecture.md` — 模块划分、实体关系和领域模型、数据流、技术选型。

### 阶段 5：Design 详细设计（按模块）

```
Skill({skill: "web2-dev:design", args: "--task-dir {task_dir} --tech {tech}"})
```

产出：`{task_dir}/.work/design.md` — 按模块组织：数据库设计、API 接口设计、模块间交互。

### 阶段 5b：Frontend Design（条件触发）

**硬门 — 判定流程（不可跳过）：**

1. 分析用户原语，**只要有任何一个行为描述了原来不存在的界面 → 调用 frontend-design**
2. 判定时问一个问题：**"这次任务完成后，用户会看到原来不存在的画面或控件吗？"** 答案是"是" → 调用
3. 不自行判定"可以跳过"。**宁可误判多调，也不要漏判。**

**涉及 UI →** 调用：
```
Skill({skill: "frontend-design:frontend-design"})
```

产出保存到 `{task_dir}/.work/layouts/`。

### 阶段 6：Plan — 任务分解

```
Skill({skill: "web2-dev:plan", args: "--task-dir {task_dir} --tech {tech}"})
```

产出：`{task_dir}/plan.md` — 简洁任务清单（模块名 + 文件路径）。

### 阶段 7：审查（normal 模式）

**正常模式 — 必须暂停等待用户审查：**
```
AskUserQuestion({
  questions: [{
    question: "Plan 已生成，请审查 {task_dir}/plan.md。是否批准进入 exec 实现阶段？",
    header: "Plan Review",
    options: [
      {label: "批准", description: "plan.md 审查通过，进入实现"},
      {label: "需要修改", description: "plan.md 有问题，描述需要改什么"}
    ]
  }]
})
```

- 用户选择"批准" → 进入阶段 8
- 用户选择"需要修改" → 用户描述修改意见，重新进入阶段 4-6 调整设计后重新提交审查

**全自动模式（mode=auto）：** 跳过 AskUserQuestion，直接进入阶段 8。

### 阶段 8：Exec — 实现

```
Skill({skill: "web2-dev:exec", args: "--mode new --task-dir {task_dir}"})
```

支持断点续跑（读取 progress.json）。

### 阶段 9：Completed

```
## 新项目开发完成

**new-{N}**
**技术栈**: {tech}
**设计文档：** {task_dir}/
**测试：** ✅ 全部通过
```

---

## 状态存储

状态由 `web2-dev:artifact-manager` 统一管理。conductor 不直接操作 `current-state.json`。

## 错误处理

- **技术栈检测失败**：根据文件特征推断，向用户确认
- **grill 输出缺失**：报告阻塞，不继续
- **plan 阶段失败**：输出具体错误，等待用户指示
- **exec 阶段任务失败**：exec 内部处理（重试 + 阻塞报告）
- **用户中断**：progress.json 保存当前状态，下次启动可继续

## Red Flags — STOP

- "dev_dir 大概就是 .web2-dev 吧，不用读 config"
- 没有回显 mode 确认就直接进入阶段执行
- "用户没加 --auto 但我可以跳过审查直接进入 exec，反正都一样"
- "plan 完成后不需要 AskUserQuestion，用户肯定批准"
- "--auto 模式下 grill 也可以跳过" → STOP。grill 不可跳过，auto 模式也不例外
- "--auto 模式下我可以自己完成 grill 采访（self-directed grilling）" → STOP。grill 的核心价值是向用户提问获取真实反馈。AI 自我分析不是 grill
- "grilling 什么都没返回，我自己整理一份 grill-interview.md 就行" → STOP。grill-interview.md 只能由 grilling 的返回内容写入
- "grill-interview.md 已经存在了，不用再调 grilling" → STOP。没经过 grilling 返回的文件不能信任
- "这个任务不需要 frontend-design，虽然有新界面但是标准控件" → STOP。有没有新界面是客观事实，不是风格判断
- "问号检测太机械了，内容明显是对话格式" → STOP。硬门就是硬门——没有问号 = 不是采访

**以上任一条 → STOP。**
