---
name: renpy-dev:exec
description: "Execute a Ren'Py implementation plan with TDD. Use when asked to 'execute the plan', 'start implementation', 'build the feature'. Reads plan documents, spawns subagents for test/code, tracks progress for resume support."
---

# Ren'Py AI 开发 — 执行阶段

读取实现计划，按 TDD 循环逐任务执行，支持断点续跑。

## 核心原则

**TDD 铁律：没有失败测试就不允许写生产代码。**
**子代理铁律：coding agent 只写实现，不改测试。test agent 只写测试，不写实现。**
**任务铁律：不限重试次数，必须完成。连续 5 轮无进展才切换策略。**

---

## 工作流

### 1. 定位任务目录和模式

从 args 解析 `--task-dir` 和 `--mode`：

```
--task-dir 已传   → task_dir = 传入值（如 .renpy-dev/feat-1/）
--mode 已传       → mode = 传入值（feat | refactor | fix）
```

**自动发现（仅当 --task-dir 未传时）：**

```bash
# 如果 --mode 已传，只搜该 kind：
ls -d .renpy-dev/${mode}-*/ 2>/dev/null | sort -V | tail -1

# 如果都没传，搜全部 kind 取最新：
ls -d .renpy-dev/*/ 2>/dev/null | sort -V | tail -1
# 从路径推断 mode：.renpy-dev/fix-1 → mode=fix
```

**优先级：** 显式 `--task-dir` > 显式 `--mode` + 自动发现 > 全自动发现。

确定 `task_dir`（如 `.renpy-dev/fix-1/`）和 `mode`（如 `fix`）。

### 2. 加载 plan.md

**只读取 `{task_dir}/plan.md`**。plan.md 是自包含的——概述、设计摘要、影响范围、任务列表、测试策略全部在此文件中。不读 `.work/` 下的任何中间产物。

### 3. 加载进度追踪

读取 `{task_dir}/progress.json`。如果不存在，创建：

```json
{
  "task_dir": "{task_dir}",
  "mode": "{mode}",
  "started_at": "{ISO timestamp}",
  "last_updated": "{ISO timestamp}",
  "tasks": {}
}
```

### 4. 解析任务列表和测试策略

按 `plan-format.md` 的解析规则提取 `[AI-N]` 任务：

1. 匹配 `- \[AI-(\d+)\]` 提取序号和描述
2. 匹配 `→ \`(.+)\`` 提取目标文件路径
3. 匹配 `(依赖: (.+))` 确定执行顺序
4. 按依赖拓扑排序，无依赖的优先执行
5. `[HUMAN]` 任务收集但不执行

**同时解析测试策略表** — 提取每行（测试文件、覆盖内容），按测试文件路径与 `[AI-N]` 输出路径匹配。RED phase 传测试文件路径和覆盖内容给 test agent，test agent 自行读 `.work/design.md` 获取细节。

对每个任务，检查 `progress.json`：
- `done` → 跳过，输出 `⏭️ [AI-N] 已完成，跳过`
- `pending` 或无记录 → 待执行
- `in_progress` → 上次中断点，从此任务继续

### 5. 确认测试可用性

```bash
# 检查 Ren'Py SDK
echo $RENPY_SDK && test -x "$RENPY_SDK" && echo "READY" || echo "NEED_SDK"
# 检查 game/tests/ 目录
ls game/tests/ 2>/dev/null && echo "TESTS_DIR_OK" || echo "TESTS_DIR_MISSING"
```

**硬门：** `RENPY_SDK` 必须指向可执行的 Ren'Py SDK。`game/tests/` 目录必须存在（不存在则创建）。没有其他条件是测试继续进行的替代方案。

### 6. TDD 循环执行每个任务

对每个待执行的 `[AI-N]` 任务：

#### 7a. 标记开始

更新 `progress.json`：
```json
{..., "tasks": {..., "AI-N": {"status": "in_progress", "started_at": "..."}}}
```

#### 7b. RED — spawn test agent

test agent 自己读文件获取写测试所需的一切信息。主会话只传任务目标和文件路径。

**主会话根据 mode 组装文档列表，填入 spawn prompt。子代理拿到的全部是已解析的具体路径。**

Mode → 文档列表映射：

| mode | 文档路径（基于 task_dir 拼接） |
|------|------------------------------|
| feat | `{task_dir}/plan.md`（设计摘要段）, `{task_dir}/.work/design.md` |
| refactor | `{task_dir}/plan.md`（设计摘要段）, `{task_dir}/.work/design.md`, `{task_dir}/impact.md` |
| fix | `{task_dir}/plan.md`（根因分析 + 修复方案）, `{task_dir}/.work/debug-analysis.md` |

```
Agent({
  subagent_type: "renpy-dev:test-agent",
  prompt: `
## 任务
为 [AI-N] {任务描述} 编写测试。

## 测试目标
{从 plan.md 测试策略表提取的本行覆盖内容，如 "behavior: 角色选择交互（选中/取消/确认）"}

## 测试文件
{从 plan.md 测试策略表提取的本行测试文件路径}

## 需要读取的文件
{主会话根据 mode 从上述映射表组装，填入已解析的具体路径。例如 mode=feat, task_dir=.renpy-dev/feat-1:}
- {task_dir}/plan.md  — {mode=feat/refactor: 设计摘要段; mode=fix: 根因分析 + 修复方案}
- {task_dir}/.work/design.md  — widget 树、变量定义、交互流程（仅 feat/refactor 模式）
- {task_dir}/impact.md  — 修改范围约束、已有测试保护（仅 refactor 模式）
- {task_dir}/.work/debug-analysis.md  — 详细调试分析（仅 fix 模式）
- plugins/renpy-dev/references/renpy-testing.md  — Ren'Py 原生 testcase/testsuite 完整 API
- game/tests/test_*.rpy（已有测试文件） — 了解命名惯例和代码风格
- game/ 下相关的 .rpy 源文件 — 了解已有 screen 名、widget id、变量名

## 编写要求
1. 使用 Ren'Py 原生 testcase / testsuite 框架，不自定义 helper
2. 从设计文档中提取 screen 名、widget id、变量名写入测试 — 不凭空编造
3. 测试断言目标行为（设计文档中描述的行为），不是当前行为
4. 测试预期失败（因为功能尚未实现/修复尚未应用）
5. 只写 game/tests/ 下的测试文件，不写 game/ 下的业务代码
6. 用 click / advance until screen / assert eval / assert label / screenshot 等原生语句
7. fix 模式：必须包含回归测试，覆盖原 BUG 场景

## 约束
- 不允许 mock、假代码、硬编码预期值来让测试通过
- 只执行逻辑，比对结果
  `
})
```

#### 7c. 评估 RED 结果

检查点：
1. 测试文件已创建/修改？
2. 测试覆盖了 prompt 中"测试目标"列出的功能？
3. 测试中引用的 screen 名、widget id、变量名与 `.work/design.md` 一致（不是凭空编造的）？
4. 没有 mock、假代码、硬编码预期值？
5. 测试语法有效？（`renpy.sh project lint` 或检查 testcase/testsuite 块结构）
6. 使用原生 `testcase` / `testsuite` 框架（非自定义 helper）？

不合格 → 反馈具体问题，重新 spawn test agent（不消耗重试计数）。
合格 → 进入 GREEN。

#### 7d. GREEN — spawn coding agent

**主会话根据 mode 组装文档列表（同 7b 映射表），填入 spawn prompt。**

```
Agent({
  subagent_type: "renpy-dev:coding",
  prompt: `
## 任务
[AI-N] {任务描述}

## 设计上下文
{从 plan.md 的"概述"和"设计摘要"段提取的关于此任务的关键设计决策和约束}

## 需要读取的文件
{主会话根据 mode 从映射表组装，填入已解析的具体路径。与 7b 相同的规则。}

## 需要通过的测试
{7b 中 test agent 写的测试代码}

## 实现文件
{plan.md 中标注的输出文件路径}

## 约束
1. 只修改使测试通过所需的最少代码
2. 不修改任何测试代码（game/tests/ 下的文件）（绝对禁止）
3. 不修改 game/libs/、game/tl/ 等第三方代码
4. 不写空代码或假代码（pass、TODO、NotImplementedError）
5. 新增 screen 时必须给关键交互 widget 添加 id 属性
6. 确保代码语法正确（renpy 可加载）
7. 不得修改 plan.md 中未列出的文件
8. 实现必须基于设计文档中的设计，不得自行偏离
9. refactor 模式：所有已有测试必须继续通过；fix 模式：回归测试必须通过
  `
})
```

#### 7e. VERIFY — 运行测试

使用 `renpy.sh` 运行对应 testcase。

**验证原则（不可妥协）：**

任务完成的判定必须基于**真实的运行时输出** — 从 `renpy.sh project test` 的 stdout/stderr 获取的**实际文本**。绝不能凭代码逻辑推测"应该通过"。

1. 运行 `$RENPY_SDK <project> test <testcase_name> --report-detailed`
2. 读取 stdout/stderr 获取测试结果
3. 对比期待值和实际值：

```
验证 [AI-N]:
  测试: select_character
  结果: ✅ Passed
  测试: cancel_selection
  结果: ✅ Passed
  结论: ✅ 全部通过
```

**失败处理：**

1. 从 `renpy.sh test --report-detailed` 输出中读取失败详情
2. 对比 expected vs actual，定位具体差异
3. 分析根因（不是猜测，基于失败事实推导）
4. 携带**实际输出 + 根因分析**重新 spawn coding agent
5. 重复直到验证通过

**如果连续 5 轮同一个错误没有进展：**
- 重新审视测试本身是否合理
- 检查依赖的前置任务是否有隐含 bug
- 简化实现方案再逐步扩展
- 向用户报告当前卡点和已尝试的方案，请求指导

#### 7f. REFACTOR — 主会话审查

调用 `renpy-dev:review` skill 审查代码变更：

1. coding agent 的实现是否符合 plan.md 的设计摘要？
2. 是否修改了测试代码？（零容忍）
3. 是否有超出 plan.md 影响范围的改动？
4. 新增 screen 的关键 widget 是否有 `id`？
5. 跨文件 `jump/call` 目标是否存在？

合格 → 标记任务完成。
不合格 → 反馈具体问题，重新 spawn coding agent。

#### 7g. 标记完成

更新 `progress.json`：
```json
{..., "tasks": {..., "AI-N": {"status": "done", "completed_at": "..."}}}
```

输出：
```
✅ [AI-N] {任务描述}
   测试: {通过的测试数量/总数}
   文件: {创建/修改的文件列表}
```

### 7. 提醒人工任务

所有 AI 任务完成后，汇总 `[HUMAN]` 任务：

```
## 待人工完成

- [ ] {HUMAN 任务 1}
- [ ] {HUMAN 任务 2}

完成人工任务后，运行 /renpy-dev:review 进行最终审查。
```

### 8. 最终验证

1. 运行 `$RENPY_SDK <project> test --report-detailed` 检查全部测试
2. 输出完成摘要

---

## 断点续跑

当 exec 在新 session 中被调用时：

1. 读取 `progress.json`
2. 跳过 `done` 的任务
3. 找到第一个非 `done` 任务，从那里继续
4. `in_progress` 的任务被视为中断，重新执行（不信任中间状态）

---

## Completion Gate

永远不要声称任务完成，除非：

1. 所有 `[AI-N]` 任务在 `progress.json` 中标记为 `done`
2. `$RENPY_SDK <project> test` 全部测试通过
3. 输出下面的完成报告：

```
## 执行完成

**任务：** {done_count}/{total_count} 完成
**测试：** ✅ 全部通过
**创建/修改文件：**
  - {file1}
  - {file2}

**待人工完成：**
- [ ] {HUMAN 任务列表}
```
