# NeonBit Vibe Factory

开发任务工作流编排器 - 从需求到 E2E 测试的完整开发周期管理。

## 概述

本插件管理完整的开发周期：
1. **需求收集** - 分析用户需求
2. **架构设计** - 系统结构与模块设计（Mermaid 图）
3. **详细设计** - 技术规格、关键逻辑、数据库设计
4. **执行计划** - 任务拆解与实施路线图
5. **后端开发** - 基于多 Agent TDD 的后端编码
6. **前端开发** - UI 实现与设计审查
7. **E2E 测试** - 基于 Playwright 的端到端测试

## TDD 多 Agent 架构

```
┌─────────────────────────────────────────────────────────┐
│                    orchestrator                          │
│                  (工作流状态机)                           │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              tdd-conductor skill                         │
│          (主会话中协调 TDD 流程)                          │
└───────────────────────────┬─────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   test agent    │ │  coding agent   │ │   REFACTOR      │
│                 │ │                 │ │                 │
│ RED: 写失败测试  │ │ GREEN: 实现功能  │ │ 主会话审查      │
│                 │ │                 │ │                 │
│ 单元测试        │ │ 最小化实现       │ │ 代码质量检查    │
│ 集成测试        │ │ 不改测试         │ │ 设计文档验证    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 组件职责

| 组件 | 类型 | 职责 | 阶段 |
|------|------|------|------|
| tdd-conductor | skill | 在主会话中协调 TDD 流程，spawn agent，审查代码 | 全局 |
| test agent | agent | 编写失败测试 (单元测试/集成测试) | RED |
| coding agent | agent | 实现功能让测试通过 | GREEN / 前端开发 |

### 技能 (Skills)

| Skill | 说明 |
|-------|------|
| orchestrator | 工作流状态机，协调所有阶段 |
| tdd-conductor | 在主会话中协调多 Agent TDD 流程 |
| artifact-manager | 管理 `.neonbit-vibe-factory/` 下的所有设计文档 |
| phase-coordinator | 协调阶段间的输入输出传递 |

## 命令

### `/neonbit-vibe-start`

启动新的开发任务工作流。

```
/neonbit-vibe-start 开发一个用户管理模块，包含增删改查功能
```

### `/neonbit-vibe-tdd`

直接启动 TDD 开发流程（跳过设计阶段）。

```
/neonbit-vibe-tdd rag-plug-file service层
```

## TDD 流程

### RED → GREEN → REFACTOR 循环

```
1. tdd-conductor 拆分任务，spawn test agent (RED)
2. test agent 编写失败测试，返回主会话
3. 主会话评估 RED 结果，spawn coding agent (GREEN)
4. coding agent 实现功能，返回主会话
5. 主会话审查代码 (REFACTOR)
6. 循环直到所有任务完成
```

### 测试类型判断

| 类型 | 场景 | 工具 |
|------|------|------|
| 单元测试 | Service 层业务逻辑、Domain 对象 | Mockito |
| 集成测试 | Controller 层 HTTP 接口 | @SpringBootTest + MockMvc |

## 目录结构

所有产物存储在 `.neonbit-vibe-factory/`：

```
.neonbit-vibe-factory/
├── current-state.json           # 全局状态追踪
└── feat-{N}/                    # 第 N 个任务的 workspace
    ├── requirements.md          # 需求摘要
    ├── architecture.md          # 架构设计（Mermaid）
    ├── design.md                # 详细设计
    ├── database.sql              # 数据库设计
    ├── openapi.yaml              # 接口文档
    ├── plan.md                  # 执行计划
    ├── ui-design.md             # UI 设计文档
    └── page-design.md           # 页面设计文档
```

## 工作流程

```
用户输入 → 需求收集 → 架构设计 → 详细设计 →
接口文档 → 执行计划（审查）→ 后端开发 (TDD) →
前端开发 → E2E 测试 → 完成
```

## 依赖

本插件依赖外部技能：
- `superpowers:brainstorming` - 用于架构和设计分析
- `superpowers:writing-plans` - 用于执行计划生成
- `/frontend-design:frontend-design` - 用于设计前端页面 
