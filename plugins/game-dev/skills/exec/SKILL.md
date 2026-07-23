---
name: game-dev:exec
description: "Execute an implementation plan with TDD. Use when asked to 'execute the plan', 'start implementation', 'build the feature', or when a conductor spawns you for TDD implementation. Coordinates game-dev:test-agent and game-dev:coding through RED→GREEN→VERIFY→边界检查→REFACTOR→VERIFY cycle."
---

# Game Dev 执行阶段

exec 是 TDD 循环的**纯编排器**。它不分析失败、不审查代码质量。它只做一件事：**收 agent 的输出，传给另一个 agent。**

## 核心原则

- **设计文档是唯一的共享真相。** 两个 agent 都读设计文档。
- **exec 不做判断，只做传递。** 测试失败让 game-dev:coding 自己看输出修，边界检查由 exec 主会话执行（自动检测违规），代码质量让 REFACTOR 做。
- **垂直切片，不是水平切片。** 不允许"写完全部测试再写完全部实现"。每个行为是一条从测试→实现→验证的完整垂直线。

```
exec 只做:
  RED:       spawn game-dev:test-agent → 收集 RED report
  GREEN:     spawn game-dev:coding → 收集 GREEN report（含自验证结果）
  VERIFY:    spawn game-dev:test-agent → 独立验证门（跑测试，不分析）
  边界检查:  exec 主会话执行 → 违规写入 REFACTOR prompt
  REFACTOR:  spawn game-dev:coding → 收集 REFACTOR report（含边界修复+代码质量）
  最终:      全量测试做全局确认

exec 不做:
  ✗ 分析测试失败原因（那是 game-dev:coding 的事）
  ✗ 审查代码（边界检查由 exec 做，代码质量是 REFACTOR 的事）
  ✗ 读取 .work/ 下的中间文件
  ✗ 在 agent 之间插入自己的判断
```

---

## Red Flags — 停下来，回到 spawn 流程

如果你发现自己在想：

- "--auto 模式下可以简化，直接实现更快"
- "找不到 ${CLAUDE_SKILL_DIR}/references/exec-prompts.md，我自己写 prompt 就行"
- "这个任务简单，不需要 spawn agent，我自己写了再验证"
- "我先写几个文件让 agent 参考"
- "spawn agent 太慢了，我自己跑测试更快"
- "agent 可能会写错，不如我自己写再让它检查"
- "先实现完再让 test-agent 补测试也行"
- "首跑全绿，不需要 VERIFY 了"
- "这个任务只改了一个文件，不需要边界检查"
- "代码很简单不需要 REFACTOR"
- "spawn 返回了我先看看结果再记日志"
- "测试文件已经存在了，我直接 Bash 跑一下看结果就行" → STOP。RED 不是跑已有测试——是 spawn test-agent 创建新测试并确认失败原因正确。已有测试文件不代表 test-agent 不需要 spawn。
- "我先跑个测试看看状态" → STOP。那是 test-agent 的职责。exec 不直接运行测试。
- "直接 Bash 跑测试和 spawn test-agent 效果一样" → STOP。spawn 的目的不是跑测试，是实现 agent 隔离（test-agent 不读实现代码，coding-agent 不读测试代码）。
- "我先用 Bash 验证一下环境/测试能不能跑" → STOP。环境验证在步骤 4 的确认测试环境硬门中完成。后续任何 Bash 测试命令都是越界。
- "批量处理完 8 个 AI 任务再统一做 VERIFY 和边界检查更高效" → STOP。每个 AI 任务是独立的 TDD 循环。不批量处理。

**以上任一条出现 → STOP。回到 6b，从 RED spawn 重新开始。**

## 常见自我合理化

| 借口 | 现实 |
|------|------|
| "--auto 就是全自动，我自己做也是自动" | `--auto` 只跳过人工审查（plan→exec），不跳过 agent 隔离。自己写代码会破坏 RED/GREEN 独立性。 |
| "找不到参考文件，我自己拼 prompt 也一样" | 找不到 ${CLAUDE_SKILL_DIR}/references/exec-prompts.md 说明路径有问题，应报错停止。自己编的 prompt 不会遵守隔离规则。 |
| "自己做比 spawn agent 更快" | 快在一时。没有 agent 隔离 = test-agent 看到实现 = coding-agent 看到测试 = TDD 循环被污染。 |
| "任务很简单，不需要完整流程" | 简单任务也有 RED/GREEN 边界。跳过 spawn = 回到"一个人又写测试又写实现"的非 TDD 模式。 |
| "我先写个草稿让 agent 改" | agent 看到你的草稿会产生锚定效应——它会围绕你的实现修修补补，而不是从设计文档出发。 |

---

## 工作流

### 1. 定位任务目录和模式

从 args 解析 `--task-dir` 和 `--mode`。均未传 → 自动发现最新任务目录：

```bash
ls -d {dev_dir}/*/ 2>/dev/null | sort -V | tail -1
```

dev_dir 从 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md` 读取。

**硬门 — 锁定项目根，绝对化 task_dir：** 后续所有 Bash 命令不依赖 CWD。获取 task_dir 后立即执行：

```bash
PROJECT_ROOT=$(pwd)
case "{task_dir}" in
  /*) task_dir="{task_dir}" ;;
  *) task_dir="$PROJECT_ROOT/{task_dir}" ;;
esac
```

之后所有 `{task_dir}` 引用均为绝对路径，`mkdir`、`cat >>` 等操作不受 CWD 偏移影响。传给 agent 的 `## task_dir` 也使用绝对化后的值。

### 2. 加载设计文档和进度

**只读 `{task_dir}/plan.md`。** 不读 `.work/` 下的任何文件——plan.md 是 exec 读取的唯一设计文档。

读取 `{task_dir}/progress.json`，不存在则创建。

### 3. 解析任务列表

按 `${CLAUDE_PLUGIN_ROOT}/references/plan-format.md` 的规则提取 `[AI-N]` 任务，按依赖拓扑排序。`[HUMAN]` 任务收集但不执行。

**解析行为列表 — 提取 screenshot 验证需求（硬门）：**

从 plan.md 的 `## 行为列表` 表格中提取每条行为的验证方式：

```bash
grep 'screenshot' {task_dir}/plan.md
```

有 screenshot 行为 → 记录 screenshot 验证需求列表（行为 # + 问题描述），在 RED spawn prompt 中传入。无匹配 → 标注 "无 screenshot 验证需求"。

### 4. 确认测试环境

读取 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md`（一份文件，所有技术栈信息在此）

**硬门：** 测试运行器必须可用。测试目录必须存在。已知坑必须处理。

### 5. 信息隔离清单

| 从 | 到 | 可以传 | 禁止传 |
|----|----|--------|--------|
| game-dev:test-agent | game-dev:coding | 行为级失败描述 + 具体失败 testcase 名称和错误信息、设计文档路径 | 测试源码、测试文件路径 |
| game-dev:coding | game-dev:coding (REFACTOR) | 已修改文件列表、设计文档路径、边界违规清单 | — |

### Spawn prompt 信息边界

exec 只传任务上下文。agent 自己读自己的定义文件和参考文件。

| exec 传入（任务上下文） | agent 自己读（静态参考 + 流程规则） |
|---|---|
| `project` — 用于填充 config.md 占位符 | `${CLAUDE_PLUGIN_ROOT}/references/{tech}/testing.md` |
| `task_dir` — 任务目录路径 | `${CLAUDE_PLUGIN_ROOT}/references/{tech}/coding.md` |
| 任务描述 `[AI-N]` | `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md` |
| 行为/失败描述、testsuite、testcase 名 | `${CLAUDE_PLUGIN_ROOT}/references/{tech}/style-guide.md`（如有） |
| 测试文件路径 | `${CLAUDE_PLUGIN_ROOT}/references/{tech}/project-organization.md`（如有） |

| 已修改文件列表（REFACTOR） | `{task_dir}/plan.md`、`.work/design.md` 等任务文件 |
| 边界违规清单（REFACTOR） | `game/` 下源文件 |

**exec 传递失败信息时必须确保：**
- 具体 testcase 名称，不只是 "N 个失败"
- 该 testcase 的错误信息
- 如果 agent 的报告只有 Summary 数字 → exec 拒绝接受，要求 agent 重新提取

---

### 6. TDD 循环

在开始循环前，一次性读取以下参考文件：
- `${CLAUDE_SKILL_DIR}/references/exec-prompts.md` — agent spawn prompt 模板
- `${CLAUDE_SKILL_DIR}/references/exec-logging.md` — TDD 迭代日志格式（exec 主会话记录用）
- `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md` — 提取 project 名称、测试环境信息、已知坑
- `${CLAUDE_PLUGIN_ROOT}/references/{tech}/coding.md` — 提取边界检查规则

测试命令（test_cmd_full 等）由 agent 在 spawn 初始化时自行从 config.md 读取并用 project 参数填充。exec 不再提取和填充这些变量。

**回显确认（硬门）：** 读取完成后必须回显：

```
## exec 初始化确认
- exec-prompts.md: RED/GREEN/VERIFY/REFACTOR 模板已加载
- exec-logging.md: 日志格式已加载
- {tech}/config.md: test_cmd_full={cmd}, project={project}
- {tech}/coding.md: 边界检查规则 {N} 条
```

**日志铁律：spawn 返回后第一件事是追加日志。不等检查结果。先记日志，再检查。**

**阶段转换门（Phase Transition Gate）— 每个 phase 不可跳过：**

每个 phase (RED/GREEN/VERIFY/边界检查/REFACTOR) 完成后必须输出显式判定：

```
## Phase {N} 判定: {phase_name}
- Verdict: ✅ 通过 → 进入 {next_phase} / ❌ 未通过 → {action}
```

**只有输出 ✅ 判定后才能进入下一 phase。** 未输出判定直接进入下一 phase = 违规。Completion Gate 要求所有 5 个 phase 的判定记录存在于 tdd-iterations.md 中。

每个任务走完整 RED → GREEN → VERIFY → 边界检查 → REFACTOR 循环。

**硬门：每个阶段不可跳过。GREEN 首跑全绿不是跳过 VERIFY 的理由。简单任务不是跳过边界检查的理由。**

#### 6a. 标记开始

更新 `progress.json`：状态 → `in_progress`。

按 `${CLAUDE_SKILL_DIR}/references/exec-logging.md` 的"初始化"节初始化 `{task_dir}/.work/tdd-iterations.md`（**这是 `.work/` 下的一个文件，不是目录**）。

创建 coding agent 日志目录

```bash
mkdir -p {task_dir}/.work/coding
```

#### 6b. RED — spawn game-dev:test-agent

使用 `${CLAUDE_SKILL_DIR}/references/exec-prompts.md` 的 **RED prompt** 模板组装 spawn prompt。

**记录日志**：spawn 返回后立即按 exec-logging.md RED 格式追加日志。先记日志，再检查。

**检查结果**（逐项打勾，缺一不可）：

- [ ] 测试文件已创建（路径：___）
- [ ] RED report 中所有 testcase 都失败了且原因正确（非语法错误、非标识符错误——语法错误和错误的标识符不算 RED）
- [ ] 没有 mock、假代码

- 全部打勾 → 进入 GREEN（6c）
- 任一未打勾 → 指出具体问题，重新 spawn（不限重试，但同问题 >3 轮报告用户）

#### 6c. GREEN — spawn game-dev:coding（含自验证）

使用 **GREEN prompt** 模板。从 test-agent 的 RED report 提取 testsuite 名称和 testcase 名称。

**记录日志**：spawn 返回后立即按 exec-logging.md GREEN 格式追加日志。先记日志，再检查。

**检查结果**（逐项打勾，缺一不可）：

**所有任务：**
- [ ] coding-agent 自验证报告显示目标 testsuite 全部通过
- [ ] 有 screenshot 验证方式的行为：visual-qa PASS
- [ ] 未修改 test/ 下文件（检查 coding agent 的已修改文件列表）
- [ ] 无 pass / TODO / NotImplemented 残留（grep 已修改的源文件）
- [ ] `.work/coding/` 目录包含本轮测试运行日志（至少一个 `<testsuite>_run<N>.log` 文件——coding agent 自我验证必须落盘原始输出）

- 全部打勾 → 进入 VERIFY（6d）
- 任一未打勾 → 指出具体问题，重新 spawn

**test 文件自身有 bug 时（非 coding agent 实现问题）：** exec 主会话不直接修改 test/ 文件。① 在 tdd-iterations.md 记录 bug 详情；② 重新 spawn test-agent 传入 bug 描述修复测试；③ 修复后重新进入 RED → GREEN。exec 是编排器，不修改任何源文件或测试文件。

**硬门：GREEN 全绿不是跳过 VERIFY 的理由。** VERIFY 验证的是"独立测试环境下的全量测试"，不是 coding agent 自己跑的测试。无论 GREEN 结果如何，必须执行 VERIFY。

#### 6d. VERIFY — spawn game-dev:test-agent（实现后独立验证门）

使用 **VERIFY prompt**。

**记录日志**：spawn 返回后立即按 exec-logging.md VERIFY 格式追加日志。先记日志，再检查。

**检查结果**：

- [ ] 全量测试全部通过（`test_cmd_full` 退出码 0）
- [ ] 有 screenshot 验证方式的行为：额外通过 visual-qa PASS
- [ ] 如有失败，报告包含具体 testcase 名称和错误行（禁止只有 Summary 数字）

- 全部通过 → 进入边界检查（6e）
- 有失败 → 回退到 GREEN（6c）再修。同一错误反复出现（>2 轮）→ exec 向用户报告，不自动循环

#### 6e. 边界检查 — exec 主会话执行（独立质量门）

**对每个任务强制执行。不是 REFACTOR 的子步骤——即使跳过 REFACTOR，边界检查也必须执行。**

检查 agent 是否越界或留下定时炸弹。

**通用检查（所有技术栈）：**

| 检查项 | 检测方式 |
|--------|---------|
| 测试文件隔离 | coding agent 是否修改了测试文件？`git diff --name-only` 检查是否包含 test/ 路径 |
| 空代码/假代码 | `grep -rn 'pass\|# TODO\|NotImplemented' {修改的源文件}` 零命中？（@abstract 方法的 `pass` stub 除外） |

**技术栈专属检查（从 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/coding.md` 提取规则）：**

以 Godot 为例：
- 资源引用完整性 — .tscn 中 `ExtResource("id")` 引用的资源是否已声明？
- 节点路径有效性 — .gd 中 `$NodeName` 或 `get_node("...")` 的路径在对应 .tscn 中是否存在？
- 信号连接有效性 — `.connect("signal_name", method)` 的目标方法是否已定义？
- 文件路径有效性 — ext_resource 的 `path` 是否指向存在的文件？

**记录日志**：追加到 tdd-iterations.md，格式：

```
### Iter {iter_N} — BOUNDARY-CHECK (exec) — {timestamp}
- 测试文件隔离: ✅ / ❌ {详情}
- 空代码/假代码: ✅ / ❌ {详情}
- 技术栈专属: ✅ / ❌ {详情}
- Verdict: ✅ clean → 进入 REFACTOR 判定 / ❌ {N} 项违规 → 必须 REFACTOR
```

**检查结果处理：**

```
├── 零违规 → 进入 REFACTOR 判定（6f）
└── 有违规 → 必须进入 REFACTOR（6f），将违规清单写入 REFACTOR prompt
```

违规清单格式：
```
## 边界违规（REFACTOR 阶段必须修复）

| # | 文件:行 | 违规类型 | 描述 |
|---|---------|---------|------|
| 1 | scenes/ui.tscn:15 | 资源引用缺失 | ext_resource "3_abc" 未声明 |
| 2 | scripts/player.gd:42 | 空代码 | `pass` 残留 |
```

#### 6f. REFACTOR — spawn game-dev:coding

**REFACTOR 触发规则（逐条判定）：**

| 条件 | 判定 |
|------|------|
| 边界检查有违规 | **必须 REFACTOR** |
| GREEN 阶段修改了 >1 个文件 | **必须 REFACTOR**（需要检查跨文件一致性） |
| GREEN 阶段有 >1 轮自我验证 | **必须 REFACTOR**（代码有迭代痕迹，需清理） |
| 以上均不满足 | REFACTOR 可选，标记为"跳过 REFACTOR：{原因}" |

**跳过 REFACTOR 时：** 追加日志 `### Iter {iter_N} — REFACTOR (skip) — 原因：{条件} — {timestamp}`，直接进入 6h（标记完成）。

使用 **REFACTOR prompt** + 边界违规清单（如有）。

**检查结果**：按 ${CLAUDE_SKILL_DIR}/references/exec-prompts.md REFACTOR 检查规则验收。
- 阻塞（>5 轮）→ 报告用户，建议撤销重构保持 GREEN 状态
- 全部通过 → 标记 done（6h）

**记录日志**：按 exec-logging.md REFACTOR 格式追加。

#### 6h. 标记完成

更新 `progress.json`，输出摘要。

---

### 7. 提醒人工任务

所有 AI 任务完成后汇总 `[HUMAN]` 任务。

### 8. 最终验证

从 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md` 读取 test_cmd_full 并执行。验证全部通过。

### 9. 收集开发经验

调用 `game-dev:collect-lessons` skill，传入 tech：

```
Skill("game-dev:collect-lessons", "tech={tech}")
```

### 10. 编写教学文档

**仅 feat 和 refactor 任务执行此步骤。**

**硬门：** 步骤 9 (collect-lessons) 和步骤 10 (write-tutorial) 必须全部完成才能声明 Completion Gate 通过。步骤 9 完成后立即进入步骤 10，不得在步骤 9 之后、步骤 10 之前输出完成报告。

调用 `game-dev:write-tutorial` skill：

```
Skill("game-dev:write-tutorial")
```

将本次开发工作编写为教学文档，追加到项目 `TUTORIAL.md`。同时检查最佳实践合规性，发现不合理违规时记录到 `TODO-BEST-PRACTICES.md`。

---

## 断点续跑

在新 session 中调用 exec 时：
1. 读 `progress.json`
2. 跳过 `done` 的任务
3. `in_progress` 的任务从 RED 重新开始（不信任中间状态）

---

## Completion Gate

永远不要声称任务完成，除非：
1. 所有 `[AI-N]` 标记 `done`（progress.json 中 status=done）
2. 全量测试全部通过
3. 边界违规全部修复
4. 所有 screenshot 验证行为已创建截图 testcase 且通过 visual-qa
5. 每个 AI 任务的 5 个 phase 判定记录存在于 tdd-iterations.md
6. `game-dev:collect-lessons` 已完成
7. `game-dev:write-tutorial` 已完成
8. 输出完成报告
