# NeonBit Vibe Factory

**Claude Code Plugin for End-to-End Development Workflow Automation**

从需求到 E2E 测试的完整开发周期管理 — 一个插件掌控全流程。

[![Version](https://img.shields.io/badge/version-0.666.0-blue.svg)](plugins/neonbit-vibe-factory/.claude-plugin/plugin.json)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)

---

## ✨ 核心特性

### 🏗️ 全流程自动化
覆盖开发全生命周期：需求 → 架构 → 详细设计 → 接口文档 → 执行计划 → 后端开发 → 前端开发 → E2E 测试

### 🤖 多 Agent TDD 架构
```
主会话 (tdd-conductor 协调)
    ├── test agent  ──→ RED (编写失败测试)
    ├── coding agent ──→ GREEN (实现功能)
    └── 主会话  ──→ REFACTOR (审查代码)
```

### 📊 设计文档驱动
所有决策都以文档形式存储，遵循设计文档而非过程讨论，确保开发过程可追溯、可审查。

### 🎯 智能工作流状态机
`orchestrator` skill 管理完整状态转换，自动检测阶段条件，按需执行或跳过阶段。

---

## 🚀 快速开始

### 安装

将 `plugins/neonbit-vibe-factory` 目录克隆到你的 Claude Code 插件目录：

```bash
git clone https://github.com/neonbit/8bit-market.git
# 或直接复制 plugins/neonbit-vibe-factory 目录
```

### 启动开发任务

```bash
/neonbit-vibe-start 开发一个用户管理模块，包含增删改查功能
```

### 直接进入 TDD 开发

```bash
/neonbit-vibe-tdd UserService service层
```

---

## 🏛️ 架构

### 组件一览

| 组件 | 类型 | 职责 |
|------|------|------|
| `orchestrator` | Skill | 工作流状态机，协调所有开发阶段 |
| `tdd-conductor` | Skill | 在主会话中协调 RED→GREEN→REFACTOR 循环 |
| `artifact-manager` | Skill | 管理所有设计文档的存储与访问 |
| `phase-coordinator` | Skill | 协调阶段间的输入输出传递 |
| `test` | Agent | 编写高质量的失败测试 (RED) |
| `coding` | Agent | 实现功能让测试通过 (GREEN) |
| `e2e-test` | Agent | 生成 Playwright E2E 测试 |

### 工作流状态

```
idle → requirements_collected → architecture_design → detailed_design
    → api_designed → plan_approved → backend_development → frontend_development
    → e2e_testing → completed
```

---

## 🔄 TDD 流程详解

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

| 场景 | 测试类型 | 工具 |
|------|----------|------|
| Service 层业务逻辑 | 单元测试 | Mockito |
| Controller 层接口 | 集成测试 | @SpringBootTest + MockMvc |
| Domain 对象验证 | 单元测试 | Mockito |

---

## 📁 产物结构

设计文档统一存储在 `.neonbit-vibe-factory/` 目录下：

```
.neonbit-vibe-factory/
├── current-state.json           # 全局状态追踪
└── feat-{N}/                    # 第 N 个任务的 workspace
    ├── requirements.md          # 需求摘要
    ├── architecture.md          # 架构设计（Mermaid 图）
    ├── design.md                # 详细设计
    ├── database.sql              # 数据库设计
    ├── openapi.yaml              # 接口文档 (OpenAPI 3.0.3)
    ├── plan.md                  # 执行计划
    ├── ui-design.md             # UI 设计文档
    └── page-design.md           # 页面设计文档
```

---

## 🎨 命令

| 命令 | 说明 |
|------|------|
| `/neonbit-vibe-start <任务>` | 启动完整开发工作流（需求→架构→设计→TDD→E2E） |
| `/neonbit-vibe-tdd <范围> <层>` | 直接启动 TDD 开发流程（跳过设计阶段） |

---

## ⚙️ 外部依赖

本插件依赖以下 Claude Code 技能：

- `superpowers:brainstorming` — 架构分析和设计规划
- `superpowers:writing-plans` — 执行计划生成
- `frontend-design` — 前端页面设计与实现

---

## 📖 文档

- [完整插件文档](plugins/neonbit-vibe-factory/README.md)
- [CLAUDE.md](plugins/neonbit-vibe-factory/CLAUDE.md) — 开发者指南
- [Orchestrator Skill](plugins/neonbit-vibe-factory/skills/orchestrator/SKILL.md)
- [TDD Conductor Skill](plugins/neonbit-vibe-factory/skills/tdd-conductor/SKILL.md)

---

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ by [neonbit](mailto:neon-bit-wh@outlook.com)**

*让开发工作流自动化成为可能*

</div>