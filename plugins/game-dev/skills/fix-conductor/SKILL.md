---
name: game-dev:fix-conductor
description: |
  工作流状态机，协调游戏项目 BUG 修复的完整周期。
  行为澄清 → test agent 写 BUG 复现测试 → debug-root-cause 定位根因 → plan-fix → exec。

  <example>
  Context: 用户报告了一个 BUG
  user: "/game-dev:fix 角色选择界面点击确认后闪退"
  assistant: "行为澄清 → BUG 复现测试 → 根因分析 → plan → exec。"
  <commentary>
  先澄清正确行为，再用测试复现 BUG，然后逆向追踪找根因。
  </commentary>
  </example>

  <example>
  Context: 全自动模式
  user: "/game-dev:fix 存档加载后数据丢失 --auto"
  assistant: "全自动模式启动。将完成 行为澄清 → BUG 复现测试 → 根因分析 → plan → exec，不在中间暂停。"
  <commentary>
  --auto 标志表示全自主模式，不等人工审查。
  </commentary>
  </example>
---

# Game Dev Fix Conductor — BUG 修复状态机

## 工作流

```
[检测技术栈] → 行为澄清 → test agent 写 BUG 复现测试 → debug-root-cause → debug-analysis.md → plan-fix → [审查] → exec --mode fix → completed
    ↑ 预期行为      ↑ 确认 BUG 存在 + 可复现          ↑ 逆向追踪定位根因  ↑ 根因+预期行为   ↑ 含根因+方案
```

与另外两个 conductor 的区别：

| | orchestrator | refactor-conductor | fix-conductor |
|--|:--:|:--:|:--:|
| 分析手段 | brainstorming | 代码分析 + brainstorming | 逆向追踪 |
| 前置产物 | — | impact.md | BUG 复现测试 + debug-analysis.md |
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

**Step 0d — 写入 config + 创建 .work：**

```bash
mkdir -p {task_dir}/.work
```

将 Step 0b 提取的字段写入 `references/{tech}/config.md`（格式同 orchestrator 阶段 0）。所有后续阶段只读此文件。

### 阶段 1：行为澄清（Behavior Clarification）

在动手之前，先搞清楚**正确的行为应该是什么**。没有行为基准，根因分析无法判断什么算"错"。

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

5. **硬门：** 未确认预期行为前，不得进入阶段 2
6. 用户自己也无法确定预期行为 → 暂停，建议先搞清楚功能需求再继续

### 阶段 2：Test Agent 写 BUG 复现测试

用 test agent 编写一个专门复现 BUG 的测试文件。这个测试当前必然 FAIL（BUG 存在），它是后续根因分析的**可运行输入**。这个测试必须是依据预期行为来写，要体现出预期行为失败

```
Agent({
  subagent_type: "game-dev:test-agent",
  description: "Write BUG reproduction test",
  prompt: "
    为以下 BUG 编写复现测试：

    BUG 描述：{用户报告的 BUG}

    预期行为：
    1. {行为 1}
    2. {行为 2}
    3. ...

    要求：
    - 测试文件写入 {test_dir}/
    - 测试必须复现 BUG——当前应 FAIL
    - 测试通过的标准是：实际行为 = 预期行为
    - 只写测试，不修改源代码
  "
})
```

**硬门：** 测试必须 FAIL。如果 PASS → 检查测试是否真正覆盖了 BUG 场景，修正后重试。

### 阶段 3：根因分析

调用 `game-dev:debug-root-cause` skill，由它执行逆向追踪、假设验证、产出 debug-analysis.md：

```
Skill({skill: "game-dev:debug-root-cause"})
```

**传入内容：**

```
## 根因分析任务

BUG 描述：{用户报告的 BUG}

预期行为：
1. {行为 1}
2. {行为 2}
3. ...

BUG 复现测试：{test_dir}/{test_file}
task_dir：{task_dir}

环境：
- tech：{tech}
- test_runner：{从 config.md 读取}
- sdk_env_var：{从 config.md 读取}
```

**不干预 debug-root-cause 的执行。** 它有自己的流程（跑测试 → 逆向追踪 → 假设验证 → 写入 debug-analysis.md）。只提供环境和输入。

**产出：** `{task_dir}/.work/debug-analysis.md`

**debug-root-cause 无法确定根因时：** 它会输出已知信息和不确定性标注。conductor 暂停，将信息呈现给用户，请求指导。

### 阶段 4：调用 plan-fix

```
Skill({skill: "game-dev:plan-fix", args: "--task-dir {task_dir}"})
```

plan-fix 读取 debug-analysis.md（根因 + 预期行为），产出 plan.md。

### 阶段 5：审查（仅正常模式）

**正常模式：** 暂停，等待用户审查 plan.md。
**全自动模式（--auto）：** 直接进入阶段 6。

### 阶段 6：Exec — TDD 修复

调用 `game-dev:exec` skill：

```
Skill({skill: "game-dev:exec", args: "--mode fix --task-dir {task_dir}"})
```

exec 根据 `--mode fix` 组装文档列表（plan.md + .work/debug-analysis.md）传给子代理。

exec 完成后，主会话验证：
- 根因是否被真正修复（不只是 workaround）
- BUG 复现测试现在 PASS
- 已有测试全部通过（无回归）

---

## 状态存储

状态由 `game-dev:artifact-manager` 统一管理，详见 `skills/artifact-manager/SKILL.md`。conductor 不直接操作 `current-state.json`。

## 错误处理

- **BUG 复现测试 PASS（BUG 未复现）**：检查测试覆盖是否准确，修正后重试。确认无误后可能是用户环境问题，报告用户。
- **debug-root-cause 无法确定根因**：输出已知信息和卡点，暂停请求用户指导
- **用户无法确定预期行为**：暂停，建议用户先搞清楚功能需求再继续。给出基于代码推断的 2-3 个合理选项供参考
- **exec 阶段任务失败**：不限重试，连续 5 轮无进展才报告
- **用户中断**：progress.json 保存当前状态，下次启动可继续

## 约束

- 预期行为未经用户确认前，不得进入阶段 2
- BUG 复现测试未 FAIL 前，不得进入阶段 3
- debug-analysis.md 未产出前，不得调用 plan-fix
- plan.md 是 exec 的唯一设计输入
- coding agent 绝不修改测试代码
- 所有已有测试必须继续通过（无回归）
- BUG 复现测试必须在修复后 PASS
