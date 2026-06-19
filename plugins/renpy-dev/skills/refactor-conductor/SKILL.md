---
name: renpy-dev:refactor-conductor
description: |
  工作流状态机，协调 Ren'Py 代码重构的完整周期。与 orchestrator 唯一区别：
  先分析影响范围并写入 impact.md，再调用 plan（plan 读取 impact.md 约束设计范围）。

  <example>
  Context: 用户需要对现有 Ren'Py 代码进行重构
  user: "/renpy-dev:refactor 将角色选择界面的数据持久化从 persistent 迁移到自定义 save 系统"
  assistant: "分析影响范围 → 写入 impact.md → 调用 plan（带约束设计）→ exec。"
  <commentary>
  重构多一步：先分析影响范围，生成 impact.md 约束 plan 的设计范围。
  </commentary>
  </example>
---

# Ren'Py Refactor Conductor — 重构状态机

## 工作流

```
分析影响范围 → 写入 impact.md → plan(读impact约束) → [审查] → exec → review
↑___唯一增量___↑            ↑_________正常流程_________↑
```

---

### 第一步：Analyze & Impact — 分析影响范围

确定序号 N，创建目录：

```bash
mkdir -p .renpy-dev/refactor-{N}
```

充分阅读现有代码：

1. 读取受影响的 `.rpy` 文件
2. 使用 Glob/Grep 发现关联文件（共享 screen、共用 label、数据依赖）
3. 识别当前实现模式
4. 查找已有测试文件（`game/tests/test_*.rpy`）
5. 检查测试基础设施状态（`tools/test.py` + `game/tests/OWN_MANIFEST.json`）
6. 评估级联影响和风险

### 第二步：写入 impact.md

按 `plugins/renpy-dev/references/impact-format.md` 格式写入 `{task_dir}/impact.md`。关键信息：
- 修改范围（硬约束，plan 不得超出）
- 排除范围（plan 不得触碰）
- 已有测试（plan 必须在测试策略中保护）
- **测试基础设施状态**（如缺失，plan 必须添加 `[AI-0]` bootstrap 任务）
- 风险点（plan 必须在设计摘要中应对）
- 特殊约束（用户指定的限制）

### 第三步：调用 plan

调用 `renpy-dev:plan` skill。plan 会：
1. 读取 `impact.md` 获取约束
2. 在约束范围内用 `superpowers:brainstorming` 分析+设计
3. 用 `superpowers:writing-plans` 生成自包含的 `plan.md`

### 第四步：审查

**正常模式：** 暂停，等待用户批准 plan.md。
**全自动模式（--auto）：** 直接进入 exec。

### 第五步：Exec — TDD 重构循环

调用 `renpy-dev:exec` skill。**重构额外约束：**
- coding agent 必须保证所有已有测试继续通过
- 已有测试被破坏 → 立即反馈修复，最高优先级

### 第六步：Review

调用 `renpy-dev:review` skill。重构额外检查：
- 已有测试是否全部通过（无回归）
- 重构前后 jump/call 链是否一致

---

## 对比

| | orchestrator | refactor-conductor |
|--|:--:|:--:|
| 分析影响范围 | — | ✅ 写 impact.md |
| plan (brainstorming + writing-plans) | ✅ | ✅ 读 impact.md 约束 |
| 审查 plan.md | ✅ | ✅ |
| exec | ✅ | ✅ + 已有测试保护 |
| review | ✅ | ✅ + 回归检查 |

## 约束

| 约束 | 说明 |
|------|------|
| 测试先行 | 没有测试覆盖就不修改代码 |
| 不改测试 | coding agent 不允许修改测试代码 |
| 范围纪律 | 只修改 plan.md 中列出的文件 |
| 已有测试不破坏 | 所有已有测试必须继续通过 |
| 真实代码 | 不允许空代码、假代码 |
