---
name: game-dev:exec
description: "Execute an implementation plan with TDD. Use when asked to 'execute the plan', 'start implementation', 'build the feature', or when a conductor spawns you for TDD implementation. Coordinates game-dev:test-agent and game-dev:coding through RED→GREEN→VERIFY→边界检查→REFACTOR→VERIFY cycle."
---

# Game Dev 执行阶段

exec 是 TDD 循环的**纯编排器**。它不分析失败、不审查代码质量。它只做一件事：**收 agent 的输出，传给另一个 agent。**

## 核心原则

- **设计文档是唯一的共享真相。** 两个 agent 都读设计文档。
- **exec 不做判断，只做传递。** 测试失败让 game-dev:coding 自己看输出修，边界检查由 exec 主会话执行（自动检测违规），代码质量让 REFACTOR 做。
- **game-dev:coding 不碰测试目录。** 跑测试不触犯这条规则。但绝不读写测试文件本身——那会破坏 RED/GREEN 的独立性。
- **game-dev:coding 自己闭环验证。** 实现 → 跑测试 → 看输出 → 修 → 直到全绿。
- **垂直切片，不是水平切片。** 不允许"写完全部测试再写完全部实现"。每个行为是一条从测试→实现→验证的完整垂直线。

```
exec 只做:
  RED:       spawn game-dev:test-agent → 收集 RED report
  GREEN:     spawn game-dev:coding → 收集 GREEN report（含自验证结果）
  VERIFY:    spawn game-dev:test-agent → 独立验证门（跑测试，不分析）
  边界检查:  exec 主会话执行 → 违规写入 REFACTOR prompt
  REFACTOR:  spawn game-dev:coding → 收集 REFACTOR report（含边界修复+代码质量）
  VERIFY:    spawn game-dev:test-agent → 独立验证门
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
- "找不到 references/exec-prompts.md，我自己写 prompt 就行"
- "这个任务简单，不需要 spawn agent，我自己写了再验证"
- "我先写几个文件让 agent 参考"
- "spawn agent 太慢了，我自己跑测试更快"
- "agent 可能会写错，不如我自己写再让它检查"
- "先实现完再让 test-agent 补测试也行"

**以上任一条出现 → STOP。回到 6b，从 RED spawn 重新开始。**

## 常见自我合理化

| 借口 | 现实 |
|------|------|
| "--auto 就是全自动，我自己做也是自动" | `--auto` 只跳过人工审查（plan→exec），不跳过 agent 隔离。自己写代码会破坏 RED/GREEN 独立性。 |
| "找不到参考文件，我自己拼 prompt 也一样" | 找不到 references/exec-prompts.md 说明路径有问题，应报错停止。自己编的 prompt 不会遵守隔离规则。 |
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

dev_dir 从 `references/{tech}/config.md` 读取。

### 2. 加载设计文档和进度

**只读 `{task_dir}/plan.md`。** 不读 `.work/` 下的任何文件——plan.md 是 exec 读取的唯一设计文档。

读取 `{task_dir}/progress.json`，不存在则创建。

### 3. 解析任务列表

按 `references/plan-format.md` 的规则提取 `[AI-N]` 任务，识别类型（`logic` / `ui`），按依赖拓扑排序。logic 优先于 ui。`[HUMAN]` 任务收集但不执行。

### 4. 确认测试环境

读取 `references/{tech}/config.md`（一份文件，所有技术栈信息在此）

**硬门：** 测试运行器必须可用。测试目录必须存在。已知坑必须处理。

### 5. 信息隔离清单

| 从 | 到 | 可以传 | 禁止传 |
|----|----|--------|--------|
| game-dev:test-agent | game-dev:coding | 行为级失败描述 + 具体失败 testcase 名称和错误信息、设计文档路径 | 测试源码、测试文件路径 |
| game-dev:coding | game-dev:coding (REFACTOR) | 已修改文件列表、设计文档路径、边界违规清单 | — |

**exec 传递失败信息时必须确保：**
- 具体 testcase 名称，不只是 "N 个失败"
- 该 testcase 的错误信息
- 如果 agent 的报告只有 Summary 数字 → exec 拒绝接受，要求 agent 重新提取

---

### 6. TDD 循环

在开始循环前，一次性读取以下参考文件：
- `references/exec-prompts.md` — agent spawn prompt 模板
- `references/exec-logging.md` — TDD 迭代日志格式
- `references/{tech}/coding.md` — 编码最佳实践
- `references/{tech}/config.md` — 技术栈上下文（测试命令、路径等）

每个任务走完整 RED → GREEN → VERIFY → 边界检查 → REFACTOR → VERIFY 循环。

#### 6a. 标记开始

更新 `progress.json`：状态 → `in_progress`。

按 `references/exec-logging.md` 的"初始化"节初始化 `{task_dir}/.work/tdd-iterations.md`。

创建 coding agent 日志目录：

```bash
mkdir -p {task_dir}/.work/coding
```

#### 6b. RED — spawn game-dev:test-agent

使用 `references/exec-prompts.md` 的 **RED prompt** 模板组装 spawn prompt。

**检查结果**：按 references/exec-prompts.md RED 检查规则验收。
- 不合格 → 指出具体问题，重新 spawn
- 合格 → 进入 GREEN（6c）

**记录日志**：按 exec-logging.md RED 格式追加。

#### 6c. GREEN — spawn game-dev:coding（含自验证）

使用 **GREEN prompt** 模板。从 test-agent 的 RED report 提取行为级失败描述、testsuite 名称和 testcase 名称。

**检查结果**：按 references/exec-prompts.md GREEN 检查规则验收。
- 阻塞（>5 轮）→ 向用户报告
- 通过 → 进入 VERIFY（6d）

**记录日志**：按 exec-logging.md GREEN 格式追加。

#### 6d. VERIFY — spawn game-dev:test-agent（实现后独立验证门）

使用 **VERIFY（实现后）prompt**。

**检查结果**：
- 回退到 GREEN（6c）再修，同一错误反复出现 → exec 向用户报告
- 全部通过 → 进入边界检查（6e）

**记录日志**：按 exec-logging.md VERIFY 格式追加。

#### 6e. 边界检查 — exec 主会话执行

**VERIFY 全部通过后、REFACTOR 之前执行。** 检查 agent 是否越界或留下定时炸弹。

**通用检查（所有技术栈）：**

| 检查项 | 检测方式 |
|--------|---------|
| 测试文件隔离 | coding agent 是否修改了测试文件？ |
| 空代码/假代码 | 是否有 `pass`、`# TODO`、`NotImplemented` 残留？ |

**技术栈专属检查（从 `references/{tech}/coding.md` 提取规则）：**

以 Godot 为例：
- 资源引用完整性 — .tscn 中 `ExtResource("id")` 引用的资源是否已声明？
- 节点路径有效性 — .gd 中 `$NodeName` 或 `get_node("...")` 的路径在对应 .tscn 中是否存在？
- 信号连接有效性 — `.connect("signal_name", method)` 的目标方法是否已定义？
- 文件路径有效性 — ext_resource 的 `path` 是否指向存在的文件？

**检查结果处理：**

```
├── 零违规 → 直接进入 REFACTOR（6f）
└── 有违规 → 将违规清单写入 REFACTOR prompt 的 "## 边界违规" 节，进入 6f
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

使用 **REFACTOR prompt** + 边界违规清单（如有）。

**检查结果**：按 references/exec-prompts.md REFACTOR 检查规则验收。
- 阻塞（>5 轮）→ 报告用户，建议撤销重构保持 GREEN 状态
- 全部通过 → 进入 VERIFY（6g）

**记录日志**：按 exec-logging.md REFACTOR 格式追加。

#### 6g. VERIFY — spawn game-dev:test-agent（重构后独立验证门）

使用 **VERIFY（重构后）prompt**。

**检查结果**：
- 回退到 REFACTOR（6f）再修，最多 2 轮回退；仍失败 → 报告用户
- 全部通过 → 标记 done（6h）

#### 6h. 标记完成

更新 `progress.json`，输出摘要。

---

### 7. 提醒人工任务

所有 AI 任务完成后汇总 `[HUMAN]` 任务。

### 8. 最终验证

从 `references/{tech}/config.md` 读取 test_cmd_full 并执行。验证全部通过。

### 9. 收集开发经验

调用 `game-dev:collect-lessons` skill：

```
Skill("game-dev:collect-lessons")
```

### 10. 编写教学文档

**仅 feat 和 refactor 任务执行此步骤。fix 任务跳过。**

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
1. 所有 `[AI-N]` 标记 `done`
2. 全量测试全部通过
3. 边界违规全部修复
4. `game-dev:collect-lessons` 已完成
5. `game-dev:write-tutorial` 已完成（feat/refactor），fix 跳过
6. 输出完成报告
