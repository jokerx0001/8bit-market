# Exec Spawn Prompt Templates

exec 在 TDD 循环每个 phase 使用以下模板组装 agent spawn prompt。`{...}` 为 exec 必须填充的变量。

## 变量来源

| 变量 | 来源 |
|------|------|
| `{project}` | 项目名称（传给 agent 用于填充 config.md 中的占位符） |
| `{task_dir}` | 任务目录路径 |
| `{dev_dir}` | 产物目录路径（从 config.md 的 `## 产物目录` 节获取） |
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
- {task_dir}/.work/design.md  — widget 树、变量定义、交互流程（仅 feat/refactor 模式）
- {task_dir}/impact.md  — 修改范围约束（仅 refactor 模式）
  `
})
```

**exec 检查 RED 结果：**
- behavior 验证方式：测试文件已创建、所有 testcase 失败且原因正确、无 mock/假代码
- screenshot 验证方式：截图脚本 + `.question` 文件已创建、截图脚本可执行（退出码 0，PNG 非空）
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
- game/ 下相关的源文件 — 了解已有代码模式
- {dev_dir}/architecture.md — 项目架构文档（如存在）
  `
})
```
- coding-agent 自验证报告显示目标 testsuite 全部通过
- 有 screenshot 验证方式的行为：visual-qa PASS
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

## 测试文件
{test-agent RED 阶段创建的测试文件路径}
  `
})
```

**exec 检查 VERIFY 结果：**
- 合格: 全量测试全部通过，有 screenshot 验证方式的行为额外通过 visual-qa
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

