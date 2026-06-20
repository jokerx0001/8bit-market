---
name: renpy-dev:exec
description: "Execute a Ren'Py implementation plan with TDD. Use when asked to 'execute the plan', 'start implementation', 'build the feature'. Coordinates test-agent and coding-agent through RED→GREEN→VERIFY→REFACTOR→VERIFY cycle. Never runs tests or analyzes failures directly."
---

# Ren'Py AI 开发 — 执行阶段

exec 是 TDD 循环的**纯编排器**。它不跑测试、不分析失败、不审查代码。它只做一件事：**收 A 的输出，传给 B。**

## 核心原则

- **test-agent 是唯一跑测试的实体。** exec 不碰 `renpy.sh test`。
- **coding-agent 永远不能接触测试源码。** exec 在 spawn coding-agent 时绝不传递测试代码、测试文件路径、测试运行命令。
- **设计文档是唯一的共享真相。** 两个 agent 都读设计文档。
- **反馈循环闭合在 test-agent 内部。** 写测试的人验证测试。

```
exec 只做:
  spawn → 收集结果 → 传给下一个 agent → spawn → 收集 → 传给下一个 → ...

exec 不做:
  ✗ 跑 renpy.sh test
  ✗ 分析测试失败原因
  ✗ 审查代码
  ✗ 读取 .work/ 下的中间文件
  ✗ 在 agent 之间插入自己的判断
```

---

## 工作流

### 1. 定位任务目录和模式

从 args 解析 `--task-dir` 和 `--mode`：

```
--task-dir 已传   → task_dir = 传入值
--mode 已传       → mode = 传入值（feat | refactor | fix）
```

**自动发现（仅当 --task-dir 未传时）：**

```bash
ls -d .renpy-dev/${mode}-*/ 2>/dev/null | sort -V | tail -1
# 如果都没传，搜全部 kind 取最新：
ls -d .renpy-dev/*/ 2>/dev/null | sort -V | tail -1
```

### 2. 加载 plan.md

**只读取 `{task_dir}/plan.md`。** 不读 `.work/` 下的任何文件。plan.md 是 exec 读取的唯一设计文档。

### 3. 加载进度追踪

读取 `{task_dir}/progress.json`。如果不存在则创建。

### 4. 解析任务列表

按 `plan-format.md` 的解析规则提取 `[AI-N]` 任务，按依赖拓扑排序。`[HUMAN]` 任务收集但不执行。

### 5. 确认测试环境

```bash
echo $RENPY_SDK && test -x "$RENPY_SDK" && echo "READY" || echo "NEED_SDK"
ls game/tests/ 2>/dev/null && echo "TESTS_DIR_OK" || echo "TESTS_DIR_MISSING"
```

**硬门：** `RENPY_SDK` 必须可用。`game/tests/` 必须存在（不存在则创建）。

---

### 6. TDD 循环 — 对每个 [AI-N] 任务

每个任务走完整 RED → GREEN → VERIFY → REFACTOR → VERIFY 循环。

#### 6a. 标记开始

更新 `progress.json`：状态 = `in_progress`。

---

#### 6b. RED — spawn test-agent

**exec 做的事：** 组装 spawn prompt，传给 test-agent，收集结果。

```
Agent({
  subagent_type: "renpy-dev:test-agent",
  prompt: `
## 模式
RED

## 任务
为 [AI-N] {任务描述} 编写测试。

## 要验证的行为
{从 plan.md 测试策略表提取的覆盖内容}

## 测试文件
{从 plan.md 测试策略表提取的测试文件路径}

## 需要读取的文件
- {task_dir}/plan.md  — 设计摘要、影响范围
- {task_dir}/.work/design.md  — widget 树、变量定义、交互流程（仅 feat/refactor 模式）
- {task_dir}/impact.md  — 修改范围约束（仅 refactor 模式）
- {task_dir}/.work/debug-analysis.md  — 根因分析（仅 fix 模式）
- plugins/renpy-dev/references/renpy-testing.md  — Ren'Py testcase/testsuite 完整 API
- game/ 下相关的 .rpy 源文件 — 了解已有 screen 名、widget id、变量名

## 约束
- 写完测试后必须自己跑测试确认失败原因正确
- 语法错误/标识符错误必须自己修复后重跑（最多 3 轮）
- 只写 game/tests/，不写 game/ 业务代码
  `
})
```

**exec 检查 RED 结果：**
- 测试文件已创建？
- RED report 中所有 testcase 都失败了且原因正确？
- 没有 mock、假代码？

不合格 → 指出具体问题，重新 spawn test-agent。
合格 → 进入 GREEN。

---

#### 6c. GREEN — spawn coding-agent

**exec 做的事：** 从 test-agent 的 RED report 中提取失败描述（行为语言），组装 spawn prompt。**绝不传递测试源码、测试文件路径、测试运行命令。**

```
Agent({
  subagent_type: "renpy-dev:coding",
  prompt: `
## 模式
GREEN

## 任务
[AI-N] {任务描述}

## 当前状态 — 以下行为尚未实现
{从 test-agent RED report 中提取的失败描述，用行为语言}

示例格式（不要传测试代码）:
- Screen "character_select" 不存在 — 需要创建
- 点击角色卡片后 selected_index 变量没有更新 — 需要实现选中逻辑
- 点击"确认"按钮后没有跳转到 start_game — 需要实现确认跳转

## 实现文件
{plan.md 中标注的输出文件路径}

## 需要读取的文件
- {task_dir}/plan.md  — 设计摘要、影响范围
- {task_dir}/.work/design.md  — widget 树、变量定义、交互流程（仅 feat/refactor 模式）
- {task_dir}/impact.md  — 修改范围约束（仅 refactor 模式）
- game/ 下相关的 .rpy 源文件 — 了解已有代码模式

## 约束
- 按设计文档实现行为，不是按测试要求实现
- 新增 screen 时必须给关键交互 widget 添加 id 属性
- 不修改 game/tests/、game/libs/、game/tl/
- 不写空代码或假代码
  `
})
```

**关键：coding-agent 的 prompt 中不出现测试源码。** 只出现行为描述。

---

#### 6d. VERIFY — spawn test-agent (GREEN mode)

```
Agent({
  subagent_type: "renpy-dev:test-agent",
  prompt: `
## 模式
GREEN

## 任务
验证测试是否通过。

## 测试文件
{test-agent RED 阶段创建的测试文件路径}

## 设计文档
- {task_dir}/plan.md
- {task_dir}/.work/design.md（仅 feat/refactor 模式）

## 要求
- 运行测试
- 如果全部通过 → 报告成功
- 如果有失败 → 分析每个失败，产出行为级描述（不是代码行号）
- 如果是截图对比失败 → 使用 mmx vision describe 对比 baseline 和 actual
  `
})
```

**exec 检查 VERIFY 结果：**

```
├── ✅ 全部通过 → 进入 REFACTOR（6e）
├── ❌ 有失败 → 提取失败分析，传给 coding-agent 重新 GREEN（回到 6c）
│   └── 累计轮数 = 编码轮的次数（不限），但同一错误重复出现则标记
└── 连续 5 轮同一错误无进展 → 向用户报告，请求指导
```

---

#### 6e. REFACTOR — spawn coding-agent (REFACTOR mode)

**只有所有测试通过后才执行。**

```
Agent({
  subagent_type: "renpy-dev:coding",
  prompt: `
## 模式
REFACTOR

## 已完成的任务
[AI-N] {任务描述} — 所有测试通过 ✅

## 要重构的文件
{从 coding-agent GREEN 阶段收集的已修改文件列表}

## 重构目标
- 消除重复代码/样式
- 改善命名（变量、函数、label）
- 提取可复用的公共逻辑
- 保持行为完全不变

## 需要读取的文件
- {task_dir}/plan.md（设计摘要，了解设计意图）

## 约束
- 不改任何 game/tests/ 下的文件
- 不改行为 — 所有已有测试必须继续通过
- 不添加新功能、新配置项
- 不改范围外的文件
  `
})
```

---

#### 6f. VERIFY (post-REFACTOR)

再次 spawn test-agent (GREEN mode) 验证全部测试仍通过。

```
├── ✅ 全部通过 → 任务完成，标记 done
├── ❌ 有失败 → 回到 6e（REFACTOR），最多 2 轮
│   └── 2 轮仍失败 → 报告用户，建议撤销重构保持 GREEN 状态
```

---

#### 6g. 标记完成

更新 `progress.json`：
```json
{..., "tasks": {..., "AI-N": {"status": "done", "completed_at": "..."}}}
```

输出：
```
✅ [AI-N] {任务描述}
   RED:     test-agent → N testcases, 失败原因正确
   GREEN:   coding-agent → M files modified
   VERIFY:  test-agent → all pass
   REFACTOR: coding-agent → K improvements
   VERIFY:  test-agent → all pass
```

---

### 7. 提醒人工任务

所有 AI 任务完成后，汇总 `[HUMAN]` 任务：

```
## 待人工完成
- [ ] {HUMAN 任务 1}
- [ ] {HUMAN 任务 2}
```

---

### 8. 最终验证

spawn test-agent (GREEN mode) 跑全部测试确认全局通过。

---

## 信息隔离清单（exec 必须遵守）

| 从 | 到 | 可以传 | 禁止传 |
|----|----|--------|--------|
| test-agent | coding-agent | 行为级失败描述、设计文档路径 | 测试源码、测试文件路径、运行命令 |
| coding-agent | test-agent | 实现文件路径 | 实现源码 |
| test-agent | coding-agent (REFACTOR) | 重构文件列表、设计文档路径 | 测试源码、测试文件路径 |

---

## 断点续跑

在新 session 中调用 exec 时：
1. 读取 `progress.json`
2. 跳过 `done` 的任务
3. `in_progress` 的任务重新执行（不信任中间状态，从 RED 重新开始）

---

## Completion Gate

永远不要声称任务完成，除非：
1. 所有 `[AI-N]` 任务标记为 `done`
2. test-agent (GREEN) 确认全部测试通过
3. 输出完成报告
