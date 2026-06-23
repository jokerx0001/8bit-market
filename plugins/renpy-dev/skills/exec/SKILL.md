---
name: renpy-dev:exec
description: "Execute a Ren'Py implementation plan with TDD. Use when asked to 'execute the plan', 'start implementation', 'build the feature', or when a conductor spawns you for TDD execution. Also use when resuming an interrupted plan. Coordinates test-agent and coding-agent through RED→GREEN→VERIFY→REFACTOR→VERIFY cycle."
---

# Ren'Py AI 开发 — 执行阶段

exec 是 TDD 循环的**纯编排器**。它不跑测试、不分析失败、不审查代码。它只做一件事：**收 agent 的输出，传给另一个 agent。**

## 核心原则
- **设计文档是唯一的共享真相。** 两个 agent 都读设计文档。
- **exec 不做判断，只做传递。** 测试失败让 coding-agent 自己看输出修，代码问题让 review 查。exec 在中间分析会引入确认偏误——你看的是 agent 报告，不是真实代码。
- **coding-agent 不碰 `game/tests/`。** `renpy.sh test` 的输出是运行时结果，不是测试源码——跑测试不触犯这条规则。但绝不读写测试文件本身——那会破坏 RED/GREEN 的独立性。
- **coding-agent 自己闭环验证。** 实现 → 跑测试 → 看输出 → 修 → 直到全绿。不再 spawn test-agent 做中间验证——那会引入不必要的往返延迟。
- **垂直切片，不是水平切片。** 不允许"写完全部测试再写完全部实现"。每个行为是一条从测试→实现→验证的完整垂直线。对游戏 UI 尤其重要：你必须先看到一个 screen 渲染出来，才知道下一个交互测试应该怎么写。

```
exec 只做:
  RED:      spawn test-agent → 收集 RED report
  GREEN:    spawn coding-agent → 收集 GREEN report（含自验证结果）
  VERIFY:   spawn test-agent → 独立验证门（跑测试，不分析）
  REFACTOR: spawn coding-agent → 收集 REFACTOR report（含自验证结果）
  VERIFY:   spawn test-agent → 独立验证门
  最终:     跑 renpy.sh test 做全局确认

exec 不做:
  ✗ 分析测试失败原因（那是 coding-agent 的事）
  ✗ 审查代码（那是 review 的事）
  ✗ 读取 .work/ 下的中间文件
  ✗ 在 agent 之间插入自己的判断
```

## 工作流

### 1. 定位任务目录和模式
-从 args 解析 `--task-dir` 和 `--mode`：
```bash
# --task-dir 已传 → 使用传入值
# --mode 已传 → 使用传入值（feat | refactor | fix）
# 均未传 → 自动发现最新任务目录：
ls -d .renpy-dev/*/ 2>/dev/null | sort -V | tail -1
```

### 2. 加载设计文档和进度

**只读 `{task_dir}/plan.md`。** 不读 `.work/` 下的任何文件——plan.md 是 exec 读取的唯一设计文档。

读取 `{task_dir}/progress.json`，不存在则创建。

### 3. 解析任务列表

按 `references/plan-format.md` 的规则提取 `[AI-N]` 任务，识别类型（`logic` / `ui`），按依赖拓扑排序。logic 优先于 ui。`[HUMAN]` 任务收集但不执行。

### 4. 确认测试环境

```bash
echo $RENPY_SDK && test -x "$RENPY_SDK" && echo "READY" || echo "NEED_SDK"
ls game/tests/ 2>/dev/null && echo "TESTS_DIR_OK" || echo "TESTS_DIR_MISSING"
grep -rl "teardown:" game/tests/ 2>/dev/null | xargs grep -l "exit" 2>/dev/null && echo "EXIT_OK" || echo "EXIT_MISSING"
```

**硬门：** `RENPY_SDK` 必须可用。`game/tests/` 必须存在。`EXIT_MISSING` 时先修复——在 global suite 确保 `testsuite global: teardown: exit`。**没有 exit = renpy test 进程永不退出 = 工作流卡死。**

### 5. 信息隔离清单

exec 在 agent 之间传递信息时必须遵守以下边界。破坏这些边界 = 破坏 TDD 的独立性。

| 从 | 到 | 可以传 | 禁止传 |
|----|----|--------|--------|
| test-agent | coding-agent | 行为级失败描述、设计文档路径 | 测试源码、测试文件路径 |
| coding-agent | coding-agent (REFACTOR) | 已修改文件列表、设计文档路径 | — |

**为什么不能传测试源码给 coding-agent：** coding-agent 看到测试实现后会针对具体检查点写代码，而不是按设计文档实现行为。行为级描述（"screen X 不存在"）让 coding-agent 去读设计文档找答案，而不是去读测试找答案。

---

### 6. TDD 循环

**在开始循环前，一次性读取以下参考文件。后续 phase 用简称指代：**
- `references/exec-prompts.md` — 简称 **{phase} prompt**（如 "RED prompt"、"GREEN prompt"）
- `references/exec-logging.md` — 简称 **{phase} log**（如 "RED log"、"GREEN log"）

每个任务走完整 RED → GREEN → VERIFY → REFACTOR → VERIFY 循环。

**垂直切片原则：** test-agent 使用 tracer bullet 模式——先写测试证明 screen 可到达，跑通后再增量加交互测试。coding-agent 响应每个可验证的行为失败。

```
WRONG (水平切片):
  RED:   一次写 5 个 testcase
  GREEN: 一次实现整个 screen

RIGHT (垂直切片):
  RED:   写 tracer bullet (screen 可到达)
  → GREEN → VERIFY → 路径通了
  RED:   加交互 testcase (点击高亮)
  → GREEN → VERIFY → 高亮对了
  RED:   加交互 testcase (确认跳转)
  → GREEN → VERIFY → 跳转对了
  ...直到该 screen 全部行为覆盖
```

#### 6a. 标记开始

更新 `progress.json`：状态 → `in_progress`。初始化 TDD 迭代日志。

#### 6b. RED — spawn test-agent

使用 **RED prompt**组装 spawn prompt。

**检查结果：**
- 测试文件已创建？所有 testcase 都失败且原因正确？没有 mock/假代码？
- 不合格 → 指出具体问题，重新 spawn（exec 不替 agent 修）
- 合格 → 进入 GREEN

**记录日志**：按 **RED log** 追加。记录全部 test case 的预期失败原因。

#### 6c. GREEN — spawn coding-agent（含自验证）

使用 **GREEN prompt**组装 spawn prompt。从 test-agent 的 RED report 提取行为级失败描述——不传测试源码或测试文件路径。

```
结果检查:
├── ✅ 全部通过 → 进入 VERIFY（6d）
├── ❌ 有失败（≤5 轮）→ coding-agent 已自行重试修复
└── 🚫 阻塞（>5 轮）→ 向用户报告，附 coding-agent 的失败输出
```

**记录日志**：按 **GREEN log** 追加。通过时简洁；失败/阻塞时必须补充 Key output + Analysis。

#### 6d. VERIFY — spawn test-agent（独立验证门）

使用 **VERIFY（实现后）prompt**。test-agent 是写测试的人，视角独立，没有确认偏误。

```
结果检查:
├── ✅ 全部通过 → 进入 REFACTOR（6e）
└── ❌ 有失败 → 将运行输出传给 coding-agent，回到 6c 再修
    （同一错误反复出现则 exec 向用户报告）
```

**记录日志**：按 **VERIFY log** 追加。

#### 6e. REFACTOR — spawn coding-agent（含自验证）

**只有 VERIFY 全部通过后才执行。** 使用 **REFACTOR prompt**。

```
结果检查:
├── ✅ 全部通过 → 进入 VERIFY（6f）
├── ❌ 有失败（≤5 轮）→ coding-agent 已自行修复
└── 🚫 阻塞（>5 轮）→ 报告用户，建议撤销重构保持 GREEN 状态
```

**记录日志**：按 **REFACTOR log** 追加。

#### 6f. VERIFY — spawn test-agent（重构后独立验证门）

使用 **VERIFY（重构后）prompt**。

```
结果检查:
├── ✅ 全部通过 → 标记 done（6g）
└── ❌ 有失败 → 运行输出传给 coding-agent，回到 6e 再修（最多 2 轮回退）
    2 轮回退仍失败 → 报告用户，建议撤销重构
```

**记录日志**：按 **VERIFY log** 追加。

#### 6g. 标记完成

更新 `progress.json`：
```json
{..., "tasks": {..., "AI-N": {"status": "done", "completed_at": "..."}}}
```

输出摘要：
```
✅ [AI-N] {任务描述}
   RED:      test-agent → N testcases, 失败原因正确
   GREEN:    coding-agent → M files, tests pass
   VERIFY:   test-agent → all pass
   REFACTOR: coding-agent → K improvements, tests pass
   VERIFY:   test-agent → all pass
```

---

### 7. 提醒人工任务

所有 AI 任务完成后汇总 `[HUMAN]` 任务：

```
## 待人工完成
- [ ] {HUMAN 任务 1}
- [ ] {HUMAN 任务 2}
```

### 8. 最终验证

直接跑 `renpy.sh <project> test` 做全局确认。

---

## 断点续跑

在新 session 中调用 exec 时：
1. 读 `progress.json`
2. 跳过 `done` 的任务
3. `in_progress` 的任务从 RED 重新开始（不信任中间状态）

---

## Completion Gate

不要声称任务完成，除非：
1. 所有 `[AI-N]` 标记 `done`
2. `renpy.sh <project> test` 全局通过
3. 输出完成报告
