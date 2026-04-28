---
name: phase-coordinator
description: |
  使用此 skill 协调各阶段之间的输入输出传递。当工作流需要从一个阶段切换到下一个阶段时触发。

  <example>
  Context: 架构设计阶段完成，需要进入详细设计阶段
  user: "架构设计已完成，开始详细设计"
  assistant: "我将使用 phase-coordinator skill 确保详细设计阶段正确接收架构设计的输出。"
  <commentary>
  阶段切换，需要协调输入输出。
  </commentary>
  </example>

  <example>
  Context: 执行计划审查被拒绝，需要返回修改
  user: "执行计划需要修改，请返回架构设计阶段"
  assistant: "使用 phase-coordinator skill 处理阶段回退。"
  <commentary>
  审查失败，需要回退到之前阶段。
  </commentary>
  </example>
---

# Phase Coordinator Skill

你负责协调工作流各阶段之间的输入输出传递，确保每个阶段正确地接收上一阶段的产物。

## 阶段输入输出映射

| 阶段 | 输入 | 输出 | 下一阶段 |
|------|------|------|----------|
| requirements_collected | 用户原始需求 | requirements.md | architecture_designed |
| architecture_designed | requirements.md | architecture.md | detailed_designed |
| detailed_designed | architecture.md | design.md, database.sql | api_designed |
| api_designed | design.md | openapi.yaml | plan_approved |
| plan_approved | openapi.yaml | plan.md (已批准) | backend_development |
| backend_development | plan.md | 实现代码 | frontend_development |
| frontend_development | plan.md, ui-design.md | 前端代码 | e2e_testing |
| e2e_testing | 前端代码, 接口文档 | 测试报告 | completed |

## 核心功能

### 1. 验证阶段前置条件

**执行检查**:
- 上一阶段的输出文档是否存在
- 文档内容是否完整
- 是否满足进入下一阶段的条件

详见 [examples/transition-example.md](examples/transition-example.md)

### 2. 传递产物给下一阶段

**执行**:
1. 读取上一阶段的输出
2. 提取关键信息传递给下一阶段
3. 更新工作流状态

### 3. 处理阶段回退

当审查失败需要回退时，详见 [examples/rollback-example.md](examples/rollback-example.md)

### 4. 阶段状态报告

详见 [examples/status-report-example.md](examples/status-report-example.md)

## 约束

1. **不跳过阶段** — 必须按顺序执行每个阶段
2. **验证完整性** — 进入新阶段前验证上一阶段的输出是否完整
3. **保留上下文** — 回退时保留有用的中间产物
4. **显式传递** — 每个阶段的输入必须显式传递，不能隐式依赖

## 使用方式

### 阶段切换
```markdown
调用 phase-coordinator skill：
- 操作: transition
- from: architecture_designed
- to: detailed_designed
```

### 阶段回退
```markdown
调用 phase-coordinator skill：
- 操作: rollback
- from: plan_approved
- to: architecture_designed
- reason: 执行计划审查未通过
```