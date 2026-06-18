---
name: unity-dev:plan
description: "Plan a Unity feature following AI-safe architecture. Use when asked to 'implement/design/plan a Unity feature'. 规划 Unity 功能开发，生成实现计划文档。"
argument-hint: <功能描述>
---

# Unity AI-Safe 开发 — 规划阶段

分析 Unity 开发需求，生成严格遵守 AI-Safe 模式的实现计划文档。

## 核心原则
**铁律 此 skill **只做分析和规划并输出文档**，不写实现代码。

---

## 工作流

### 1. 加载安全原则

读取安全原则参考文件：
- `plugins/unity-dev/references/unity-safety-principles.md`

所有规划必须遵守这些不可协商的约束。

### 2. 加载输出格式规范

读取格式契约文件：
- `plugins/unity-dev/references/plan-format.md`

plan 输出必须严格遵守此格式，exec skill 依赖此格式解析。

### 3. 检测项目环境

#### 渲染管线检测

```bash
# 检查 URP
find . -path "*/UniversalRenderPipelineAsset*.asset" -not -path "*/Library/*" | head -1
# 检查 HDRP
find . -path "*/HDRenderPipelineAsset*.asset" -not -path "*/Library/*" | head -1
# 检查 Packages/manifest.json
grep -o "com.unity.render-pipelines\.[a-z]*" Packages/manifest.json 2>/dev/null
```

判定规则：
- 含 `com.unity.render-pipelines.universal` → URP
- 含 `com.unity.render-pipelines.high-definition` → HDRP
- 都没有 → Built-in

#### Unity 版本检测

```bash
grep "m_EditorVersion:" ProjectSettings/ProjectVersion.txt 2>/dev/null
```

#### 命名空间检测

```bash
grep -r "^namespace " --include="*.cs" --max-count=5 | head -10
```

### 4. 理解需求

调用 `superpowers:brainstorming` 分析用户需求。分析时关注：

- 要构建什么游戏功能/系统
- 映射到推荐架构的哪个层级（Core / Systems / Entities / Data / Events）
- 哪些现有系统会受影响
- 需要新建哪些 Systems、Events、Entities、Data
- 哪些工作**人类**必须在 Unity Editor 完成（prefabs, scenes, animators）

### 5. 生成计划文档

按 `references/plan-format.md` 定义的格式生成计划。关键要求：

- 每个 AI 任务必须有 `[AI-N]` 编号 + 输出文件路径 + 依赖标注
- 每个 HUMAN 任务必须有具体操作步骤
- 数据定义中 ScriptableObject 只有字段
- 事件流用箭头链描述完整流转

### 6. 格式自检

输出前对照 `plan-format.md` 中的"格式校验清单"逐项确认。

### 7. 创建任务目录

调用 `unity-dev:artifact-manager` skill 创建任务目录：

```
调用 unity-dev:artifact-manager：
- 操作: create_task
- kind: feat
```

记录返回的 `feat-{N}` 编号。当前任务的所有文档都存储于 `.unity-dev/feat-{N}/` 下。

### 8. 保存计划文档

调用 `unity-dev:artifact-manager` skill 保存计划：

```
调用 unity-dev:artifact-manager：
- 操作: save_document
- task: feat-{N}
- doc_type: plan
- content: <生成的计划内容（完整 Markdown）>
```

然后更新阶段：

```
调用 unity-dev:artifact-manager：
- 操作: update_state
- phase: plan_generated
```

### 9. 审批确认

**必须等待用户确认后才能继续，不能自动推进到 exec。**

输出计划摘要并请求审批：

```
## Plan: {feature-name}

**存储位置：** `.unity-dev/feat-{N}/plan.md`

**渲染管线：** {URP/HDRP/Built-in}
**新建 Systems：** N 个
**新建 Events：** N 个
**新建 Entities：** N 个
**人工任务：** N 个

**AI 任务概览：**
{逐条列出 [AI-N] 任务简述}

---

### 审批确认

请审阅以上计划：
- 回复 **"approve"**（或 **"yes"**）批准计划并进入可执行状态
- 回复 **具体修改意见**，将据此修改计划后重新提交审批
- 回复 **"cancel"** 放弃此计划
```

**收到用户回复后：**

- **approve / yes：**
  ```
  调用 unity-dev:artifact-manager：
  - 操作: update_state
  - phase: plan_approved
  ```
  输出：`Plan approved. 运行 /unity-dev:exec 开始 TDD 实现。`

- **修改意见：** 根据用户反馈修改 plan 内容，回到步骤 8 重新保存（覆盖），再次等待审批。

- **cancel：** 不更新状态，输出 `Plan cancelled. 可运行 /unity-dev:plan 重新开始。`

### 10. Completion Gate

Never claim the plan step is complete unless:

1. 执行了工作流的所有步骤
2. plan.md 成功保存到 `.unity-dev/feat-{N}/plan.md`
3. 用户已回复 "approve" 且 state 已更新为 `plan_approved`
4. 向用户输出了确认信息和下一步指令（/unity-dev:exec）

