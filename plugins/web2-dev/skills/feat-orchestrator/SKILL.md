---
name: web2-dev:feat-orchestrator
description: |
  新功能开发工作流状态机。在已有项目上增加新功能：
  技术栈检测 → grill 前置采访 → 模块级需求 → 架构(含领域模型) → 详细设计(按模块)
  → [frontend-design] → [设计审查] → plan(任务分解) → [审查] → exec。

  与 new-orchestrator 唯一区别：产出模块级文档（新增/修改的模块），而非项目级全量文档。

  <example>
  Context: 用户通过 /web2-dev:feat 启动新功能
  user: "/web2-dev:feat 在用户模块中增加手机号绑定功能"
  assistant: "检测技术栈 → grill → 模块级需求 → 架构 → 详细设计 → plan → exec。"
  </example>

  <example>
  Context: 全自动模式
  user: "/web2-dev:feat 增加文件上传接口 --auto"
  assistant: "全自动模式。跳过人工审查点。"
  </example>
---

# Feature Orchestrator

新功能开发工作流状态机。产出模块级设计文档。

## 工作流

```
idle → [检测技术栈] → 保存用户原语 → grill → requirements → architecture → design
     → [frontend-design] → [设计审查] → plan → [审查] → exec → completed
```

## 两种模式

### 正常模式（默认）
plan → 审查 → 用户批准 → exec

### 全自动模式（`--auto`）
跳过人工审查点。

---

## 阶段执行

### 阶段 0：前置检查 + 检测技术栈 + 解析模式

**前置检查（硬门）：** 同 new-orchestrator 阶段 0 Step 0a。检查项目根目录 `ops-local.md` 存在且非空，不满足则终止。

`--auto` 来源必须从 `user-prompt.md` 中 grep 验证。

回显确认：
```
## 运行模式
模式: {normal / auto}
{normal → "正常模式 — 将在 plan 完成后暂停等待审查"}
{auto → "全自动模式 — 不在审查点暂停，全流程自动执行"}
```

### 阶段 1：创建任务目录

```
Skill({skill: "web2-dev:artifact-manager", args: "--kind feat --dev-dir {dev_dir}"})
```

返回 `task_dir`。

### 阶段 2：保存用户原语 + Grill 前置采访

同 new-orchestrator 阶段 2（完整流程：保存 user-prompt.md → grilling → 硬门验证）。

**不可跳过，auto 模式也不例外。**

### 阶段 3：Requirements 需求管理

mode 为 `update`（已有项目追加需求）：
```
Skill({skill: "web2-dev:requirements", args: "--task-dir {task_dir} --tech {tech} --mode update"})
```

在项目级 `{dev_dir}/requirements.md` 中追加新功能需求。产出 per-task `{task_dir}/.work/requirements.md`。

### 阶段 4：Architecture 架构设计（含领域模型）

```
Skill({skill: "web2-dev:architecture", args: "--task-dir {task_dir} --tech {tech}"})
```

产出模块级架构：新增/修改的模块、新增的实体/关系、数据流变更。

### 阶段 5：Design 详细设计（按模块）

```
Skill({skill: "web2-dev:design", args: "--task-dir {task_dir} --tech {tech}"})
```

产出：新增模块的 DB 设计、API 设计、与已有模块的交互方式。

### 阶段 5b：Frontend Design（条件触发）

**硬门判定：** "这次任务完成后，用户会看到原来不存在的画面或控件吗？" → 是 → 调用：
```
Skill({skill: "frontend-design:frontend-design"})
```

产出保存到 `{task_dir}/.work/layouts/`。**宁误判不漏判。**

**设计审查（normal 模式硬门，auto 模式跳过）：**

frontend-design 产出设计稿后，normal 模式必须暂停等待用户审查：

```
AskUserQuestion({
  questions: [{
    question: "UI 设计稿已生成，请审查 {task_dir}/.work/layouts/。是否满意？",
    header: "Design Review",
    options: [
      {label: "满意", description: "设计稿通过，进入 plan 任务分解"},
      {label: "需要修改", description: "描述修改意见，重新生成设计稿"}
    ]
  }])
```

- 用户选择"满意" → 进入阶段 6
- 用户选择"需要修改" → 收集修改意见，重新调用 frontend-design（携带反馈）更新 layouts/，再次提交审查。**循环直到用户满意，才允许进入 plan。**
- auto 模式跳过此审查点，直接进入阶段 6。

### 阶段 6：Plan — 任务分解

```
Skill({skill: "web2-dev:plan", args: "--task-dir {task_dir} --tech {tech}"})
```

产出：`{task_dir}/plan.md` — 本次新增/修改的模块清单。

### 阶段 7：审查（normal 模式）

同 new-orchestrator 阶段 7。`AskUserQuestion` 询问批准/修改。auto 模式跳过。

### 阶段 8：Exec — 实现

```
Skill({skill: "web2-dev:exec", args: "--mode feat --task-dir {task_dir}"})
```

### 阶段 9：Completed

```
## 新功能开发完成

**feat-{N}**
**技术栈**: {tech}
**设计文档：** {task_dir}/
**测试：** ✅ 全部通过
```

---

## Red Flags — STOP

所有 new-orchestrator 的 Red Flags 均适用。
