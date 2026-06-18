---
name: renpy-dev:refactor-conductor
description: |
  工作流状态机，协调 Ren'Py 代码重构的完整周期。与 orchestrator 不同的是，
  重构必须先充分阅读现有代码，在 plan 之后分析影响，再综合设计变更方案。

  <example>
  Context: 用户需要对现有 Ren'Py 代码进行重构
  user: "/renpy-dev:refactor 将角色选择界面的数据持久化从 persistent 迁移到自定义 save 系统"
  assistant: "我将使用 refactor-conductor 协调重构流程：plan → 分析现有代码 → 影响评估 → 综合设计 → 变更计划。"
  <commentary>
  重构工作流，需要先理解现有代码再设计变更。
  </commentary>
  </example>
---

# Ren'Py Refactor Conductor — 重构状态机

协调对现有 Ren'Py 代码的重构和改造，通过 TDD 方式确保修改安全。

## 核心原则

**重构铁律：先有测试护栏，再改代码。**

## 与 orchestrator 的区别

| 维度 | orchestrator（新功能） | refactor-conductor（重构） |
|------|------------------------|---------------------------|
| 前提 | 无现有实现 | 有现有工作代码 |
| 设计前 | 直接设计 | 先分析现有代码 |
| 设计后 | 直接出计划 | 评估影响 + 综合设计 |
| GREEN 策略 | 从零实现 | 修改现有代码 |
| 额外验证 | 无 | 必须运行所有已有测试确保不破坏 |

## 工作流

```
plan → analyze → impact → design → change-plan → [审查] → exec(TDD重构) → review
```

### 第一步：Plan — 理解重构目标

调用 `renpy-dev:plan` skill，但产物放在 `.renpy-dev/refactor-{N}/`：

1. 创建 `.renpy-dev/refactor-{N}/` 目录
2. 收集重构目标 → `requirements.md`
3. 检测项目环境

### 第二步：Analyze — 分析现有代码

充分阅读用户引用的代码文件和所有相关模块：

1. 读取用户提到的参考文件
2. 使用 Glob/Grep 发现所有相关文件（同 screen、同 label、同数据流）
3. 识别当前实现模式（screen 结构、label 跳转链、数据持久化方式）
4. 查找已有测试文件（`game/tests/test_*.rpy`）

**写入 `{task_dir}/analysis.md`：**

```markdown
# 现有代码分析

## 重构目标
{用户描述的重构目标}

## 当前实现模式
- 模式描述: {当前代码结构}
- 涉及文件: {文件列表，含路径}

## Screen 结构
- {screen_name}: {widget 树概要}

## Label 跳转链
{A → B → C 调用链}

## 数据持久化
{当前使用的 persistent / save 变量}

## 已有测试
- {已有测试文件列表，或"无"}

## 依赖关系
- {跨文件 jump/call 依赖图}
```

### 第三步：Impact — 影响评估

列出所有需要修改的文件和位置，按风险分级。

**写入 `{task_dir}/impact.md`：**

```markdown
# 影响评估

## 需要修改的文件
| 文件 | 位置 | 变更类型 | 风险 |
|------|------|----------|------|
| game/screens.rpy | screen xxx | widget 结构调整 | 中 |
| game/script.rpy | label xxx | 跳转逻辑变更 | 高 |

## 级联影响
- {修改 A 可能导致 B 需要调整}

## 测试影响
- {哪些已有测试可能被破坏}

## 确认无需修改
- {排除的文件及排除原因}
```

### 第四步：Design — 综合设计

基于分析结果和影响评估，综合设计方案。

调用 `Skill` 工具加载 `superpowers:brainstorming`，输入：
- requirements.md（用户原始目标）
- analysis.md（现有代码分析）
- impact.md（影响评估）

**写入 `{task_dir}/design.md`：**

```markdown
# 综合设计方案

## 方案概述
{一句话描述整体方案}

## 关键设计决策
### 决策 1: {名称}
- 方案: {选定方案}
- 考虑过但未采用的方案: {备选方案及原因}
- 影响: {对下游的影响}

## 实现思路
### 改动点 1: {描述}
- 文件: {路径}
- 当前: {当前代码模式}
- 改为: {目标代码模式}
- 注意事项: {边界条件}

## 风险与边界
- {风险点及缓解措施}
- {明确排除在本次重构外的内容}
```

### 第五步：Change Plan — 变更计划

基于综合设计方案拆分任务。

**写入 `{task_dir}/plan.md`**（遵循 `plan-format.md` 格式）：

```markdown
# Plan: {重构名称}

## 概述
{重构目标}

## 影响范围
| 类型 | 文件 | 操作 |
|------|------|------|

## 设计摘要
{引用 design.md 的关键决策}

## 任务列表
### [AI] 任务
- `[AI-1]` {描述} → `{文件路径}`

### [HUMAN] 任务
- `[HUMAN]` {操作}

## 测试策略
| 层级 | 覆盖内容 | 测试文件 |
|------|---------|---------|
```

### 第六步：审查

**正常模式：** 暂停，等待用户批准 change plan。
**全自动模式（--auto）：** 直接进入 exec。

### 第七步：Exec — TDD 重构循环

调用 `renpy-dev:exec` skill，与 feat 的 exec 相同流程：

- **RED：** spawn test agent 编写测试，断言目标行为（测试因旧行为而失败）
- **GREEN：** spawn coding agent 修改现有代码，不改测试
- **VERIFY：** 运行 `tools/test.py` + 所有已有测试
- **REFACTOR：** 主会话审查

**额外约束：**
- coding agent 必须保证已有测试不被破坏
- 如果已有测试失败，立即反馈给 coding agent 修复
- OWN_MANIFEST.json 必须同步更新

### 第八步：Review — 合规审查

调用 `renpy-dev:review` skill，额外检查：
- 已有测试是否全部通过（无回归）
- 重构前后的 jump/call 链是否一致（无断裂）

---

## 状态追踪

`.renpy-dev/refactor-{N}/progress.json` — 与 exec 相同的格式。

## 约束

| 约束 | 说明 |
|------|------|
| 测试先行 | 没有测试覆盖就不修改代码 |
| 不改测试 | coding agent 不允许修改测试代码 |
| 范围纪律 | 只修改 plan.md 中列出的文件 |
| 已有测试不破坏 | 所有已有测试必须继续通过 |
| 真实代码 | 不允许空代码、假代码 |
| 全部 green | 有任何测试失败就不能算完成 |
