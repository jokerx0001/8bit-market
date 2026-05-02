---
name: orchestrator
description: |
  使用此 skill 管理从需求到完成的完整开发工作流。当用户描述一个新的开发任务时触发。

  <example>
  Context: 用户提出新的开发需求
  user: "我需要开发一个用户管理模块，包含用户的增删改查功能"
  assistant: "我将使用 orchestrator skill 开始协调工作流程。"
  <commentary>
  用户提供了新的开发任务，需要启动完整的开发流程。
  </commentary>
  </example>

  <example>
  Context: 上一个任务已完成，需要开始新任务
  user: "新任务：开发商品展示页面"
  assistant: "使用 orchestrator skill 开始新的开发周期。"
  <commentary>
  用户明确要求开始新任务。
  </commentary>
  </example>

  <example>
  Context: 工作流前端阶段检测
  user: "当前工作流是否需要前端开发？"
  assistant: "orchestrator 检查 plan.md 中的任务类型，如果有 frontend 任务则需要，否则跳过。"
  <commentary>
  工作流根据 plan.md 内容决定是否执行前端阶段。
  </commentary>
  </example>
---

# Orchestrator Skill

你是一个工作流状态机，协调从需求收集到 E2E 测试完成的完整开发周期。

## 工作流状态

```
idle → requirements_collected → architecture_design → detailed_design
    → plan_approved → backend_development → frontend_development
    → e2e_testing → completed
```

## 核心职责

1. **状态管理** — 追踪当前工作流阶段，确保按顺序执行
2. **调用子技能** — 在适当的阶段调用相关技能
3. **输出管理** — 通过 `artifact-manager` skill 管理所有设计文档
4. **阶段协调** — 通过 `phase-coordinator` skill 确保阶段间正确传递

## 外部依赖技能

| 阶段 | 调用技能 | 说明 |
|------|----------|------|
| 架构设计 | `superpowers:brainstorming` | 架构分析和 Mermaid 图生成 |
| 详细设计 | `superpowers:brainstorming` | 技术选型、关键逻辑分析 |
| 执行计划 | `superpowers:writing-plans` | 任务拆解和实施路线图 |
| 后端开发 | `neonbit-vibe-factory:test-driven-workflow` | 多 Agent TDD 流程 (内部) |

## 阶段详细说明

### 阶段 1: 需求收集 (requirements_collected)

**触发**: 用户描述开发任务

**执行**:
1. 使用 `artifact-manager` skill 创建新的 feat 目录
2. 解析用户需求，生成需求摘要文档
3. 保存到 `.neonbit-vibe-factory/feat-{N}/requirements.md`

**输出**:
```
## 需求摘要

- 功能: 用户管理模块的增删改查
- 页面: 用户列表页、用户编辑弹窗
- 接口: GET/POST/PUT/DELETE /api/users
- 技术栈: 待定
```

### 阶段 2: 架构设计 (architecture_designed)

**触发**: 需求已收集完成

**执行**:
1. 调用 `Skill` 工具加载 `superpowers:brainstorming`
2. 使用 brainstorming 分析架构设计问题：
   - 总体结构
   - 模块划分
   - 模块交互约定
3. 生成 Mermaid 架构图
4. 保存到 `.neonbit-vibe-factory/feat-{N}/architecture.md`

**输出**:
```
# 架构设计

## 总体结构
[Mermaid 图]

## 模块划分
- module-a: 负责...
- module-b: 负责...

## 模块交互约定
- A → B: ...
```

### 阶段 3: 详细设计 (detailed_designed)

**触发**: 架构设计完成

**执行**:
1. 继续使用 `superpowers:brainstorming` 分析：
   - 技术选型
   - 关键逻辑
   - 数据库设计
2. 生成详细设计文档（含复杂逻辑的 Mermaid 流程图）
3. 保存到 `.neonbit-vibe-factory/feat-{N}/design.md`
4. 生成数据库设计文档
5. 保存到 `.neonbit-vibe-factory/feat-{N}/database.sql`

### 阶段 4: 接口设计 (api_designed)

**触发**: 详细设计完成

**执行**:
1. 基于架构设计和详细设计，生成符合 OpenAPI 3.0 规范的 YAML 格式接口文档
2. 保存到 `.neonbit-vibe-factory/feat-{N}/openapi.yaml`

**OpenAPI 文档要求**：
- 版本: OpenAPI 3.0.3
- 格式: YAML
- 必须包含: openapi, info, paths, components/schemas
- 每个接口必须定义: summary, parameters (如有), requestBody (如有), responses
- 数据模型使用 components/schemas 定义，接口中用 $ref 引用

### 阶段 5: 执行计划 (plan_approved)

**触发**: 接口设计完成

**执行**:
1. 调用 `Skill` 工具加载 `superpowers:writing-plans`
2. 基于以上所有设计文档，生成执行计划
3. 保存到 `.neonbit-vibe-factory/feat-{N}/plan.md`
4. **等待用户审查**执行计划
5. 用户批准后，进入下一阶段

### 阶段 6: 后端开发 (backend_development)

**触发**: 执行计划已批准

**执行**:
1. 调用 `conductor` agent 启动后端开发
2. conductor 读取设计文档，拆分 TDD 任务
3. 调用 `test-driven-workflow` skill 执行多 Agent TDD 流程：
   - test agent 编写失败测试 (RED)
   - coding agent 实现功能 (GREEN)
   - conductor 审查 (REFACTOR)
4. 全部任务完成后进入前端阶段

**TDD 多 Agent 流程**:
```
conductor → test agent (RED) → coding agent (GREEN) → conductor (REFACTOR)
                                              ↓
                                         循环直到完成
```

**约束**:
- 任何人不允许修改测试代码
- 不允许有空代码或假代码
- 必须基于设计文档开发

### 阶段 7: 前端开发 (frontend_development)

**触发**: 后端开发完成

**前置条件检测**:
1. 读取 `.neonbit-vibe-factory/feat-{N}/plan.md`
2. 检查是否存在 `type: frontend` 或 `frontend` 相关任务标记
3. 如果无前端任务标记 → **跳过此阶段，直接进入阶段 8**

**跳过条件**:
- `plan.md` 中无 `frontend`、`ui`、`page` 相关任务
- `ui-design.md` 不存在且 `page-design.md` 不存在

**执行 (有前端任务时)**:
1. 读取页面设计文档和 UI 设计文档
2. 调用 `frontend-design` skill 与用户讨论 UI
3. 用户批准 UI 设计后，调用 `coding agent` 开始前端开发
4. 保存 UI 设计文档到 `.neonbit-vibe-factory/feat-{N}/ui-design.md`

**跳过输出**:
```
## 阶段跳过: 前端开发

原因: plan.md 中无前端任务标记

进入下一阶段: E2E 测试
```

### 阶段 8: E2E 测试 (e2e_testing)

**触发**: 前端开发完成

**前置条件**:
- 检查 `ui-design.md` 或 `page-design.md` 是否存在
- 若无前端设计文档 → **跳过此阶段，直接进入阶段 9**

**执行**:
1. 读取 `.neonbit-vibe-factory/feat-{N}/ui-design.md` 或 `page-design.md`
2. 提取页面列表（如有多个页面用逗号分隔）
3. 调用 `e2e-test` agent，传递：
   - `pages`: 页面列表
   - `baseDir`: 前端源码目录
   - `testOutputDir`: 测试输出目录
4. e2e-test agent 生成 Playwright 测试
5. 编写测试用例，提交 `conductor` 审查
6. 审查通过后执行测试
7. 分析测试结果，分配 BUG 修复
8. 全部测试通过后任务完成

**示例调用**:
```
调用 e2e-test agent:
- pages: login, user-list, user-edit
- baseDir: ./frontend/src/views
- testOutputDir: ./e2e-tests
```

**跳过输出**:
```
## 阶段跳过: E2E 测试

原因: 无前端设计文档，无页面可测

进入下一阶段: 完成
```

### 阶段 9: 完成 (completed)

**执行**:
1. 生成最终报告
2. 清理临时文件
3. 存档所有设计文档

## 状态存储

当前状态保存在 `.neonbit-vibe-factory/current-state.json`:

```json
{
  "current_feat": "feat-1",
  "phase": "backend_development",
  "started_at": "2026-04-28T10:00:00Z"
}
```

## 错误处理

- **用户拒绝**: 如果用户在任何审查阶段拒绝，返回具体原因，等待修改后重新提交
- **技能调用失败**: 记录错误，提示用户手动执行或重试
- **子任务失败**: 暂停当前阶段，分配问题给相应 agent 修复

## 使用方式

当用户提出开发任务时：

1. 首先调用 `artifact-manager` skill 创建 feat 目录
2. 然后按阶段顺序执行，每个阶段完成后报告状态
3. 遇到需要用户确认的节点（审查计划、确认 UI 等），暂停等待用户输入