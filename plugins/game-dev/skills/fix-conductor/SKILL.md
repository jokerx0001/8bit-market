---
name: game-dev:fix-conductor
description: |
  工作流状态机，协调 Ren'Py BUG 修复的完整周期。
  在 systematic-debugging 前强制进行行为澄清，确保 debugging 有正确的行为基准。

  <example>
  Context: 用户报告了一个 BUG
  user: "/game-dev:fix 角色选择界面点击确认后闪退"
  assistant: "行为澄清 → systematic-debugging → debug-analysis.md → plan.md → exec --mode fix。"
  <commentary>
  先澄清正确行为，再以正确行为为基准进行 systematic-debugging 找根因。
  </commentary>
  </example>

  <example>
  Context: 全自动模式
  user: "/game-dev:fix 存档加载后数据丢失 --auto"
  assistant: "全自动模式启动。将完成 行为澄清 → systematic-debugging → plan → exec，不在中间暂停。"
  <commentary>
  --auto 标志表示全自主模式，不等人工审查。
  </commentary>
  </example>
---

# Game Dev Fix Conductor — BUG 修复状态机

## 工作流

```
[检测技术栈] → 行为澄清 → systematic-debugging → 验证门 → debug-analysis.md → plan-fix skill → [审查] → exec --mode fix → completed
                  ↑ 预期行为     ↑ 以预期行为为基准     ↑ 根因确认     ↑ 根因+预期行为    ↑ 含根因+方案
```

与另外两个 conductor 的区别：

| | orchestrator | refactor-conductor | fix-conductor |
|--|:--:|:--:|:--:|
| 分析手段 | brainstorming | 代码分析 + brainstorming | systematic-debugging |
| 前置产物 | — | impact.md | debug-analysis.md |
| exec 模式 | --mode feat | --mode refactor | --mode fix |

---

### 阶段 0：检测技术栈 + 创建上下文

**Step 0a — 读 CLAUDE.md 确定 tech**（同 orchestrator 阶段 0）。

**Step 0b — 读 `references/{tech}/config.md`**，提取上下文字段值。

**Step 0c — 创建任务目录：**

```
Skill({skill: "game-dev:artifact-manager", args: "--task-dir {dev_dir}/fix-{N} --kind fix --dev-dir {dev_dir}"})
```

返回 `task_dir`。

**Step 0d — 写入 references/{tech}/config.md：**

```bash
mkdir -p {task_dir}/.work
```

将 Step 0b 提取的字段写入 `references/{tech}/config.md`（格式同 orchestrator 阶段 0）。所有后续阶段只读此文件。

### 阶段 1：行为澄清（Behavior Clarification）

在 debugging 之前，先搞清楚**正确的行为应该是什么**。没有行为基准，debugging 无法判断什么算"错"、什么算"对"。

**执行步骤：**

1. 解析用户的 BUG 描述，检查是否已包含预期行为
2. 向用户询问预期行为：

```
## 行为澄清

在开始调试之前，需要先确认：**这个功能的正确行为应该是什么？**

{根据 BUG 描述提出 2-4 个具体问题，例如：}
- 正常情况下，这个 screen 应该显示什么内容？
- 用户执行这个操作后，应该发生什么？
- 这个变量的有效值/有效范围是什么？
- 如果这是个边界情况，正确的降级/兜底行为是什么？
```

3. 用户无法确定时，基于代码分析给出 2-3 个合理选项供选择
4. 将用户确认的预期行为整理为清单，回显确认：

```
## 预期行为确认

请确认以下正确行为描述是否准确：

1. {行为 1 — 用户可见/系统可感知的}
2. {行为 2}
3. ...

确认后回复"OK"继续。
```

5. **硬门：** 未确认预期行为前，不得进入阶段 3（systematic-debugging）
6. 用户自己也无法确定预期行为 → 暂停，建议先搞清楚功能需求再继续

### 阶段 3：Systematic Debugging — 根因分析

加载 `superpowers:systematic-debugging` skill，**将阶段 2 确认的预期行为列表作为输入约束传入**：

```
Skill({skill: "superpowers:systematic-debugging"})
```

在调用时明确告知 systematic-debugging：

```
## 调试任务

BUG 描述：{用户报告的 BUG}

## 预期行为（正确行为基准）
{阶段 2 用户确认的预期行为列表}
1. {行为 1}
2. {行为 2}
3. ...

请以以上预期行为为基准进行调试。当前实际行为偏离了预期行为，找出根因。
```

**调试步骤：**
1. 阅读相关源代码
2. 阅读已有测试文件
3. 如有可能，复现 BUG（运行测试或分析代码逻辑）
4. 对比实际行为与预期行为，定位偏差点
5. 形成根因假设
6. 对每个假设：验证能否解释所有症状

### 阶段 4：验证门（Verification Gate）

在写入任何文档前，必须通过验证：

**验证清单：**
1. 根因能否解释用户报告的**所有**症状？
2. 根因能否解释**实际行为与预期行为的偏差**？
3. 能否**稳定复现**（或从代码逻辑中证明必然发生）？
4. 如果临时修复此根因（哪怕是 hack），BUG 应该消失。能否构造一个最小验证？

**判定：**
```
├── 全部通过 → 进入阶段 5（写入 debug-analysis.md）
├── 不通过（< 3 轮）→ 带着新信息回到阶段 3，重新调试
└── 不通过（≥ 3 轮）→ 暂停，输出已知信息和卡点，请求用户指导
```

### 阶段 5：写入 debug-analysis.md

保存到 `{dev_dir}/fix-{N}/.work/debug-analysis.md`：

```markdown
# 调试分析

## BUG 描述
{用户报告的 BUG，原样引用}

## 预期行为
{阶段 2 确认的正确行为，逐条列出}
1. {行为 1 — 用行为语言描述，不含技术术语}
2. {行为 2}
3. ...

## 根因
{经 systematic-debugging 确认的根因，精确到具体代码位置}

## 证据链
1. {证据 1：如何复现}
2. {证据 2：为什么这就是根因}
3. {证据 3：排除的替代假设}

## 影响范围
| 文件 | 问题 |
|------|------|
| game/xxx.rpy | {具体问题描述} |

## 修复方向
{修复方案的概要描述，一两句话}
```

### 阶段 6：调用 plan-fix skill

```
Skill({skill: "game-dev:plan-fix", args: "--task-dir {dev_dir}/fix-{N}"})
```

### 阶段 7：审查（仅正常模式）

**正常模式：** 暂停，等待用户审查 plan.md。
**全自动模式（--auto）：** 直接进入阶段 8。

### 阶段 8：Exec — TDD 修复

调用 `game-dev:exec` skill：

```
Skill({skill: "game-dev:exec", args: "--mode fix --task-dir {dev_dir}/fix-{N}"})
```

exec 根据 `--mode fix` 组装文档列表（plan.md + .work/debug-analysis.md）传给子代理。

exec 完成后，主会话验证：
- 根因是否被真正修复（不只是 workaround）
- 回归测试是否覆盖了原 BUG 场景 + 所有预期行为
- 已有测试全部通过（无回归）

---

## 状态存储

状态由 `game-dev:artifact-manager` 统一管理，详见 `skills/artifact-manager/SKILL.md`。conductor 不直接操作 `current-state.json`。

## 错误处理

- **systematic-debugging 无法确定根因**：最多 3 轮验证门，仍失败则暂停请求用户指导
- **用户无法确定预期行为**：暂停，建议用户先搞清楚功能需求再继续。给出基于代码推断的 2-3 个合理选项供参考
- **exec 阶段任务失败**：不限重试，连续 5 轮无进展才报告
- **用户中断**：progress.json 保存当前状态，下次启动可继续

## 约束

- 根因未通过验证门前，不得写入 plan.md
- 预期行为未经用户确认前，不得写入 debug-analysis.md 和 plan.md
- plan.md 是 exec 的唯一设计输入
- coding agent 绝不修改测试代码
- 所有已有测试必须继续通过（无回归）
- BUG 修复必须包含回归测试，回归测试覆盖所有预期行为
