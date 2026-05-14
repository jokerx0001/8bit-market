# NeonBit Vibe Factory

**Development Workflow Orchestrator — From Requirements to E2E Testing**

一个掌控开发全流程的 Claude Code 插件，将传统需要数周的开发周期压缩为自动化工作流。

[![Version](https://img.shields.io/badge/version-0.666.0-blue.svg)](.claude-plugin/plugin.json)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)

---

## ✨ 为什么选择 Vibe Factory？

### 🏗️ 从零到生产级代码，只需一个命令

```bash
/neonbit-vibe-start 开发一个电商订单系统，包含下单、退货、库存管理
```

传统流程需要：需求评审 → 技术方案设计 → 接口定义 → 代码实现 → 测试 → 集成 → 上线

Vibe Factory 流程：描述需求 → AI 自动完成全流程 → 可执行的 E2E 测试

### 🤖 真正的多 Agent TDD

不是口号，而是架构：

```
主会话 (tdd-conductor 协调)
    ├── test agent  ──→ RED (编写失败测试)
    ├── coding agent ──→ GREEN (实现功能)
    └── 主会话  ──→ REFACTOR (审查代码)
```

每个功能都经历：**测试先行 → 最小实现 → 代码审查**，确保交付质量。

### 📊 文档驱动开发

设计文档是唯一的事实来源，告别"口口相传"：

- `requirements.md` — 需求定义
- `architecture.md` — 架构设计 (Mermaid 图)
- `design.md` — 详细设计
- `openapi.yaml` — 接口规范 (OpenAPI 3.0.3)
- `plan.md` — 执行计划（需用户批准）

### 🎯 智能阶段跳过

根据实际需要自动跳过不必要的阶段：

- 无前端任务？自动跳过前端开发阶段
- 无页面设计？自动跳过 E2E 测试阶段
- 不浪费任何时间

---

## 🚀 快速开始

### 安装

克隆本仓库，将 `plugins/neonbit-vibe-factory` 目录放入 Claude Code 插件目录：

```bash
git clone https://github.com/neonbit/8bit-market.git
```

### 启动完整工作流

```bash
/neonbit-vibe-start 开发一个用户管理模块，包含增删改查功能
```

### 直接进入 TDD 开发

当已有设计文档或需要快速补充测试时：

```bash
/neonbit-vibe-tdd UserService service层
```

---

## 🏛️ 架构

### 核心组件

```
┌─────────────────────────────────────────────────────────────┐
│                    orchestrator                              │
│                  (工作流状态机)                                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              tdd-conductor skill                              │
│          (主会话中协调 TDD 流程)                               │
└───────────────────────────┬─────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   test agent    │ │  coding agent   │ │   REFACTOR     │
│                 │ │                 │ │                 │
│ RED: 写失败测试  │ │ GREEN: 实现功能  │ │ 主会话审查      │
│                 │ │                 │ │                 │
│ 单元测试        │ │ 最小化实现       │ │ 代码质量检查    │
│ 集成测试        │ │ 不改测试         │ │ 设计文档验证    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 工作流状态机

```
idle → requirements → architecture → detailed_design → api_design
    → plan_approved → backend_development → frontend_development
    → e2e_testing → completed
```

---

## 🔄 TDD 循环详解

### RED → GREEN → REFACTOR

| 阶段 | Agent | 职责 | 约束 |
|------|-------|------|------|
| RED | test agent | 编写失败测试 | 只写测试，不写实现 |
| GREEN | coding agent | 实现功能让测试通过 | 不修改测试代码 |
| REFACTOR | 主会话 | 审查代码质量 | 不允许假代码/空代码 |

### 测试类型

| 场景 | 测试类型 | 工具 |
|------|----------|------|
| Service 层业务逻辑 | 单元测试 | Mockito |
| Controller 层 HTTP 接口 | 集成测试 | @SpringBootTest + MockMvc |
| Domain 对象验证规则 | 单元测试 | Mockito |

---

## 📁 产物结构

所有设计文档存储在 `.neonbit-vibe-factory/<kind>-{N}/`，其中 `<kind>` 为 `feat`/`refactor`/`tdd`。每种 kind 的计数器独立。

```
.neonbit-vibe-factory/
├── current-state.json           # 全局状态追踪
├── feat-{N}/                    # 新功能任务
│   ├── requirements.md          # 需求摘要
│   ├── architecture.md          # 架构设计（Mermaid 图）
│   ├── design.md                # 详细设计
│   ├── database.sql              # 数据库设计
│   ├── openapi.yaml              # 接口文档 (OpenAPI 3.0.3)
│   ├── plan.md                  # 执行计划
│   ├── stack.json               # 技术栈检测结果
│   ├── routing-table.md         # Rules 路由表
│   ├── ui-design.md             # UI 设计文档
│   └── page-design.md           # 页面设计文档
├── refactor-{N}/                # 重构任务
│   ├── task.md                  # 重构目标描述
│   ├── analysis.md              # 现有代码分析
│   ├── impact.md                # 影响评估
│   ├── change-plan.md           # 变更计划
│   ├── stack.json               # 技术栈检测结果
│   └── routing-table.md         # Rules 路由表
└── tdd-{N}/                     # TDD 任务
    ├── task.md                  # 任务描述
    ├── stack.json               # 技术栈检测结果
    └── routing-table.md         # Rules 路由表
```

---

## 📐 Rules 注入机制

本 plugin 内 vendor 了一份语言无关 + 12 个语言特化的编程规范（位于 `references/rules/`）。

工作流：

1. 命令入口（`/neonbit-vibe-start` / `/neonbit-vibe-refactor` / `/neonbit-vibe-tdd`）创建任务目录后，调用 `stack-detector` skill 检测项目语言/框架
2. 检测结果在主会话中以"确认门"形式呈现，由用户确认或修正
3. 确认后写入 `<task_dir>/stack.json` 与 `<task_dir>/routing-table.md`
4. conductor 派发 sub-agent 时读 routing-table.md，按 (语言, 角色) 把对应 rule 的绝对路径注入 prompt
5. agent 在第零步强制 Read 全部必读 rule，再开始任务

### 任务目录类型

| 命令 | 目录 | 主要产物 |
|------|------|----------|
| `/neonbit-vibe-start` | `.neonbit-vibe-factory/feat-{N}/` | requirements/architecture/design/openapi/plan + stack.json + routing-table.md |
| `/neonbit-vibe-refactor` | `.neonbit-vibe-factory/refactor-{N}/` | task/analysis/impact/change-plan + stack.json + routing-table.md |
| `/neonbit-vibe-tdd` | `.neonbit-vibe-factory/tdd-{N}/` | task + stack.json + routing-table.md |

### 修改 rules

`references/rules/` 已与上游脱钩，可自由演化。修改后无需重新检测；下次派发 agent 时即生效。

---

## ⚙️ 依赖

本插件依赖以下 Claude Code 技能：

| 技能 | 用途 |
|------|------|
| `superpowers:brainstorming` | 架构分析和设计规划 |
| `superpowers:writing-plans` | 执行计划生成 |
| `frontend-design` | 前端页面设计 |

---

## 📖 详细文档

- [CLAUDE.md](CLAUDE.md) — 开发者指南
- [Orchestrator Skill](skills/orchestrator/SKILL.md) — 工作流状态机
- [TDD Conductor Skill](skills/tdd-conductor/SKILL.md) — TDD 协调器
- [Artifact Manager Skill](skills/artifact-manager/SKILL.md) — 文档管理
- [Phase Coordinator Skill](skills/phase-coordinator/SKILL.md) — 阶段协调

---

## 📄 License

Apache License 2.0

---

<div align="center">

**Built with ❤️ by [neonbit](mailto:neon-bit-wh@outlook.com)**

*让开发工作流自动化成为可能*

</div> 
