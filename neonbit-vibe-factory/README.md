# NeonBit Vibe Factory

开发任务工作流编排器 - 从需求到 E2E 测试的完整开发周期管理。

## 概述

本插件管理完整的开发周期：
1. **需求收集** - 分析用户需求
2. **架构设计** - 系统结构与模块设计（Mermaid 图）
3. **详细设计** - 技术规格、关键逻辑、数据库设计
4. **执行计划** - 任务拆解与实施路线图
5. **后端开发** - 后端编码与代码审查
6. **前端开发** - UI 实现与设计审查
7. **E2E 测试** - 基于 Playwright 的端到端测试

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

## 命令

### `/neonbit-vibe-start`

启动新的开发任务工作流。

```
/neonbit-vibe-start 开发一个用户管理模块，包含增删改查功能
```

## 技能

### orchestrator

管理工作流状态机，协调所有阶段。

### artifact-manager

管理 `.neonbit-vibe-factory/` 下的所有设计文档。

### phase-coordinator

协调阶段间的输入输出传递。

## 代理

### conductor

后端开发的主协调器：
- 读取设计文档
- 将执行计划拆分为任务
- 分配任务给 coding 子代理
- 审查代码合规性

### e2e-test

使用 Playwright 的 E2E 测试代理：
- 通过 SHA256 签名检测变更
- 基于 POM 模式的测试编写
- 与 conductor 的审查循环
- 测试执行与结果报告

## 工作流程

```
用户输入 → 需求收集 → 架构设计 → 详细设计 →
接口文档 → 执行计划（审查）→ 后端开发 →
前端开发 → E2E 测试 → 完成
```

## 依赖

本插件依赖外部技能：
- `superpowers:brainstorming` - 用于架构和设计分析
- `superpowers:writing-plans` - 用于执行计划生成
- `superpowers:test-driven-development` - 用于 TDD 后端开发

## 安装

将插件复制到 Claude Code 插件目录或使用：
```bash
cc --plugin-dir /path/to/neonbit-vibe-factory
```