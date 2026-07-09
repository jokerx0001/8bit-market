# Exec Spawn Prompt Templates

exec 在 TDD 循环每个 phase 使用以下模板组装 agent spawn prompt。`{...}` 为 exec 必须填充的变量。

## 变量来源

| 变量 | 来源 |
|------|------|
| `{project}` | 项目名称（传给 agent 用于填充 config.md 中的占位符） |
| `{task_dir}` | 任务目录路径 |
| `{tech}` | 技术栈标识（renpy / godot） |

---

## RED — test-agent

```
Agent({
  subagent_type: "game-dev:test-agent",
  prompt: `
## 模式
RED

## project
{project 名称，用于填充 config.md 中 {project} 占位符}

## task_dir
{task_dir}

## 任务
[AI-N] {任务描述}

## 要验证的行为
{从 plan.md 测试策略表提取的覆盖内容}

## 需要读取的文件
- {task_dir}/plan.md  — 设计摘要、影响范围
- {task_dir}/.work/design.md  — widget 树、变量定义、交互流程（仅 feat/refactor 模式）
- {task_dir}/impact.md  — 修改范围约束（仅 refactor 模式）
- {task_dir}/.work/debug-analysis.md  — 根因分析（仅 fix 模式）
{若任务类型为 visual，在此插入 visual 任务标记块}
{若任务类型为 ui，在此插入 UI 任务标记块}
  `
})
```

### visual 任务标记块

仅当 plan.md 中任务类型为 `visual` 时插入：

```
## visual 任务
spec: {task_dir}/{spec_path}
```

### UI 任务标记块

仅当 plan.md 中任务类型为 `ui` 时插入：

```
## UI 任务
html: {task_dir}/{html_path}
```

**exec 检查 RED 结果：**
- logic 任务：测试文件已创建、所有 testcase 失败且原因正确、无 mock/假代码
- visual/ui 任务：截图已保存到 `.work/screenshots/`、visual-compare 结果 PASS/FAIL 明确
- 合格: 全部条件达成
- 不合格: 任一条件未达到
---

## GREEN — coding-agent

```
Agent({
  subagent_type: "game-dev:coding",
  prompt: `
## 模式
GREEN

## project
{project 名称，用于填充 config.md 中 {project} 占位符}

## task_dir
{task_dir}

## 任务
[AI-N] {任务描述}

## 目标 testsuite
{从 test-agent RED report 的 "### Testsuite" 提取的 testsuite 名称}

## 目标 testcase — 每个都代表一个待实现的行为
{从 test-agent RED report 的 "### Testcases" 表格提取的 testcase 名称}
- testcase_1
- testcase_2

## 需要读取的文件
- {task_dir}/plan.md  — 设计摘要、影响范围
- {task_dir}/.work/design.md  — widget 树、变量定义、交互流程（仅 feat/refactor 模式）
- {task_dir}/impact.md  — 修改范围约束（仅 refactor 模式）
- {task_dir}/.work/debug-analysis.md  — 根因分析、预期行为（仅 fix 模式）
- game/ 下相关的源文件 — 了解已有代码模式
{若 plan.md 中任务类型为 visual，在此插入 visual 任务标记块}
{若 plan.md 中任务类型为 ui，在此插入 UI 任务标记块}
  `
})
```

### visual 任务标记块

仅当 plan.md 中任务类型为 `visual` 时，在 GREEN prompt 的 "需要读取的文件" 段后插入：

```
## visual 任务
spec: {task_dir}/{spec_path}
```

coding-agent 检测到 `## visual 任务` + `spec:` 后自动进入 visual 实现模式。

### UI 任务标记块

仅当 plan.md 中任务类型为 `ui` 时，在 GREEN prompt 的 "实现文件" 段后插入：

```
## UI 任务
html: {task_dir}/{html_path}
```

coding-agent 检测到 `## UI 任务` + `html:` 后自动进入 UI 翻译模式。

**exec 检查 GREEN 结果：**
- coding-agent 自验证报告显示目标 testsuite 全部通过
- 未修改 game/tests/ 下文件
- 无 pass / TODO / NotImplemented 残留
合格: 全部条件达成
不合格: 任一条件未达到
---

## VERIFY — test-agent

```
Agent({
  subagent_type: "game-dev:test-agent",
  prompt: `
## 模式
GREEN

## project
{project 名称}

## task_dir
{task_dir}

## 任务
独立验证 — 跑全量测试确认当前代码状态。
{若任务类型为 visual 或 ui，在此插入 visual 验证标记}

## 测试文件
{test-agent RED 阶段创建的测试文件路径}
  `
})
```

### visual 验证标记

仅当任务类型为 `visual` 或 `ui` 时插入：

```
## visual 任务
spec: {task_dir}/{spec_path}

全量测试通过后，对截图 testcase 捕获的截图调用 game-dev:visual-compare skill 做视觉验证。
```

**exec 检查 VERIFY 结果：**
- 合格: 全量测试全部通过，visual/ui 任务额外通过 visual-compare
- 不合格: 有失败时，报告是否包含具体 testcase 名称和错误行（禁止只有 Summary 数字）

---

## REFACTOR — coding-agent

**只有 VERIFY 全部通过后才执行。**

```
Agent({
  subagent_type: "game-dev:coding",
  prompt: `
## 模式
REFACTOR

## project
{project 名称，用于填充 config.md 中 {project} 占位符}

## task_dir
{task_dir}

## 任务
[AI-N] {任务描述} — 所有测试通过 ✅

## 要重构的文件
{从 coding-agent GREEN 阶段收集的已修改文件列表}

## 重构目标
- 消除重复代码/样式
- 改善命名（变量、函数、label）
- 提取可复用的公共逻辑
- 保持行为完全不变
{若边界检查有违规，在此插入边界违规清单}

## 需要读取的文件
- {task_dir}/plan.md（设计摘要，了解设计意图）
})
```

**exec 检查 REFACTOR 结果：**
- 全量测试全部通过
- 边界违规清单逐条已修复
- 未修改 game/tests/ 下文件
合格: 全部条件达成
不合格: 任一条件未达到

