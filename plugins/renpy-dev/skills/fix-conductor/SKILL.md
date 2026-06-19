---
name: renpy-dev:fix-conductor
description: |
  工作流状态机，协调 Ren'Py BUG 修复的完整周期。
  与 orchestrator/refactor-conductor 的区别：用 systematic-debugging 替代 brainstorming 进行根因分析。

  <example>
  Context: 用户报告了一个 BUG
  user: "/renpy-dev:fix 角色选择界面点击确认后闪退"
  assistant: "systematic-debugging → debug-analysis.md → writing-plans → plan.md → exec --mode fix → review。"
  <commentary>
  BUG 修复用 systematic-debugging 找根因，验证后写 plan，执行 TDD 修复。
  </commentary>
  </example>

  <example>
  Context: 全自动模式
  user: "/renpy-dev:fix 存档加载后数据丢失 --auto"
  assistant: "全自动模式启动。将完成 systematic-debugging → plan → exec → review，不在中间暂停。"
  <commentary>
  --auto 标志表示全自主模式，不等人工审查。
  </commentary>
  </example>
---

# Ren'Py Fix Conductor — BUG 修复状态机

## 工作流

```
systematic-debugging → 验证门 → debug-analysis.md → writing-plans → plan.md → [审查] → exec --mode fix → review
    ↑ 最多 3 轮       ↑ 根因确认     ↑ 根因分析           ↑ 含根因+方案     ↑ 修复计划              ↑ TDD 修复
```

与另外两个 conductor 的区别：

| | orchestrator | refactor-conductor | fix-conductor |
|--|:--:|:--:|:--:|
| 分析手段 | brainstorming | 代码分析 + brainstorming | systematic-debugging |
| 前置产物 | — | impact.md | debug-analysis.md |
| exec 模式 | --mode feat | --mode refactor | --mode fix |

---

## 阶段执行

### 阶段 1：确定任务目录

确定 N 并创建目录：

1. 读取 `.renpy-dev/current-state.json`
   - **文件不存在** → 初始化为 `{"current_task": "", "current_kind": "", "counters": {"feat": 0, "refactor": 0, "fix": 0}}`
   - **旧格式**（有 `current_feat` 无 `counters`）→ 按 `counters = {"feat": N, "refactor": 0, "fix": 0}` 转换
2. 从 `counters.fix` 取值，+1 得到 N
3. 创建目录：`mkdir -p .renpy-dev/fix-{N}/.work`
4. 写回 `current-state.json`：
   ```json
   {
     "current_task": "fix-{N}",
     "current_kind": "fix",
     "phase": "debugging",
     "counters": { "...原有值不变...", "fix": N }
   }
   ```

### 阶段 2：Systematic Debugging — 根因分析

加载 `superpowers:systematic-debugging` skill，分析 BUG：

1. 收集用户报告的 BUG 描述
2. 阅读相关源代码
3. 阅读已有测试文件
4. 如有可能，复现 BUG（运行测试或分析代码逻辑）
5. 形成根因假设
6. 对每个假设：验证能否解释所有症状

### 阶段 3：验证门（Verification Gate）

在写入任何文档前，必须通过验证：

**验证清单：**
1. 根因能否解释用户报告的**所有**症状？
2. 能否**稳定复现**（或从代码逻辑中证明必然发生）？
3. 如果临时修复此根因（哪怕是 hack），BUG 应该消失。能否构造一个最小验证？

**判定：**
```
├── 全部通过 → 进入阶段 4（写入 debug-analysis.md）
├── 不通过（< 3 轮）→ 带着新信息回到阶段 2，重新调试
└── 不通过（≥ 3 轮）→ 暂停，输出已知信息和卡点，请求用户指导
```

### 阶段 4：写入 debug-analysis.md

保存到 `.renpy-dev/fix-{N}/.work/debug-analysis.md`：

```markdown
# 调试分析

## BUG 描述
{用户报告的 BUG，原样引用}

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

### 阶段 5：Writing Plans — 生成修复计划

调用 `Skill` 工具加载 `superpowers:writing-plans`，基于 debug-analysis.md 生成**自包含的 plan.md**。

**传递给 writing-plans 的约束：**
- plan.md 的"概述"段必须包含根因摘要
- plan.md 的"设计摘要"段必须包含修复方案
- 每个 AI 任务有 `[AI-N]` 编号 + 输出文件路径 + 依赖标注
- 必须包含**回归测试**任务（确保 BUG 不再复现）
- 按 `plugins/renpy-dev/references/plan-format.md` 格式输出

保存到 `.renpy-dev/fix-{N}/plan.md`。

### 阶段 6：审查（仅正常模式）

**正常模式：** 暂停，等待用户审查 plan.md。
**全自动模式（--auto）：** 直接进入阶段 7。

### 阶段 7：Exec — TDD 修复

调用 `renpy-dev:exec` skill：

```
Skill({skill: "renpy-dev:exec", args: "--mode fix --task-dir .renpy-dev/fix-{N}"})
```

exec 根据 `--mode fix` 组装文档列表（plan.md + .work/debug-analysis.md）传给子代理。

### 阶段 8：Review

调用 `renpy-dev:review` skill。fix 模式额外检查：
- 根因是否被真正修复（不只是 workaround）
- 回归测试是否覆盖了原 BUG 场景
- 是否有引入新问题的风险

---

## 状态存储

`.renpy-dev/current-state.json`：

```json
{
  "current_task": "fix-1",
  "current_kind": "fix",
  "phase": "exec",
  "mode": "manual",
  "counters": {
    "feat": 1,
    "refactor": 0,
    "fix": 1
  },
  "started_at": "2026-06-19T10:00:00Z",
  "last_updated": "2026-06-19T10:30:00Z"
}
```

> **向后兼容**：旧版 current-state.json 使用 `current_feat` 字段。读取时如发现旧字段而无 `current_task`/`counters`，按 `current_task = current_feat`、`current_kind = "feat"`、`counters = {"feat": N, "refactor": 0, "fix": 0}` 转换并改写。

## 错误处理

- **systematic-debugging 无法确定根因**：最多 3 轮验证门，仍失败则暂停请求用户指导
- **exec 阶段任务失败**：不限重试，连续 5 轮无进展才报告
- **review 阶段违规**：反馈给对应 agent 修复，重新审查
- **用户中断**：progress.json 保存当前状态，下次启动可继续

## 约束

- 根因未通过验证门前，不得写入 plan.md
- plan.md 是 exec 的唯一设计输入
- coding agent 绝不修改测试代码
- 所有已有测试必须继续通过（无回归）
- BUG 修复必须包含回归测试
