---
name: artifact-manager
description: |
  使用此 skill 管理 .neonbit-vibe-factory 下的所有设计文档。当需要创建新任务、整理文档、查询产物时触发。

  <example>
  Context: 开始新的开发任务，需要创建目录结构
  user: "开始新的用户管理模块开发"
  assistant: "我将使用 artifact-manager skill 创建新的 feat 目录结构。"
  <commentary>
  新任务开始，需要初始化目录和文档。
  </commentary>
  </example>

  <example>
  Context: 需要查询当前有哪些设计产物
  user: "当前 feat-1 的设计文档有哪些？"
  assistant: "使用 artifact-manager skill 列出所有设计产物。"
  <commentary>
  用户需要了解已有产物。
  </commentary>
  </example>
---

# Artifact Manager Skill

你负责管理 `.neonbit-vibe-factory/` 目录下的所有设计文档和中间产物。

## 目录结构规范

```
.neonbit-vibe-factory/
├── current-state.json           # 全局状态（当前 feat、当前阶段）
└── feat-{N}/                    # 第 N 个任务的目录
    ├── requirements.md          # 需求摘要
    ├── architecture.md          # 架构设计（Mermaid 图）
    ├── design.md                # 详细设计文档
    ├── database.sql              # 数据库设计（SQL 建表语句）
    ├── openapi.yaml              # OpenAPI 接口文档
    ├── plan.md                  # 执行计划
    ├── ui-design.md             # UI 设计文档（前端阶段生成）
    └── page-design.md           # 页面设计文档
```

## 核心功能

### 1. 创建新的任务目录（支持三种 kind）

**入参**：
- `kind`: 取值 `feat` / `refactor` / `tdd`
- `task_name`（可选）: 用于日志，不影响目录命名

**执行**:
1. 读取 `.neonbit-vibe-factory/current-state.json`
2. 在 `counters` 对象中查 `kind` 对应计数器；不存在则初始化为 0
3. 计数器 +1，作为新任务编号 N
4. 创建目录：`mkdir -p .neonbit-vibe-factory/{kind}-{N}`
5. 更新 `current-state.json`：写回新计数器，并设置 `current_task = {kind}-{N}`、`current_kind = {kind}`

**约束**：三种 kind 的计数器**互相独立**。`feat-1` 与 `refactor-1` 可同时存在，互不冲突。

**输出**：
```
已创建 {kind}-{N} 目录：
.neonbit-vibe-factory/{kind}-{N}/
```

### 1a. 目录结构按 kind 区分

| kind | 必有产物 | 备注 |
|------|----------|------|
| feat | requirements.md, architecture.md, design.md, database.sql, openapi.yaml, plan.md, ui-design.md（前端阶段） | orchestrator 流程 |
| refactor | analysis.md, impact.md, change-plan.md | refactor-conductor 流程 |
| tdd | task.md（命令入口写入用户输入） | tdd-conductor 流程 |

**所有 kind 都必须包含**：`stack.json` 和 `routing-table.md`（由 stack-detector skill 生成）。

### 2. 保存设计文档

**执行**:
- 根据阶段类型，保存对应文档
- 自动追加到 feat 目录
- 不覆盖已存在的文档（除非明确指定）

**文档命名规范**:

| 阶段 | 文件名 | 格式 |
|------|--------|------|
| 需求收集 | requirements.md | Markdown |
| 架构设计 | architecture.md | Markdown + Mermaid |
| 详细设计 | design.md | Markdown + Mermaid |
| 数据库设计 | database.sql | SQL (可直接执行) |
| 接口设计 | openapi.yaml | OpenAPI 3.0 (YAML) |
| 执行计划 | plan.md | Markdown |
| UI 设计 | ui-design.md | Markdown |
| 页面设计 | page-design.md | Markdown |

**详细格式规范**:
- OpenAPI 接口文档格式规范详见 [references/openapi-spec.md](references/openapi-spec.md)
- SQL 数据库文档格式规范详见 [references/sql-spec.md](references/sql-spec.md)

### 3. 读取设计文档

**执行**:
- 根据需要读取特定文档
- 验证文档存在性
- 返回文档内容摘要

### 4. 状态管理

**current-state.json 结构**:
```json
{
  "current_task": "feat-1",
  "current_kind": "feat",
  "phase": "architecture_designed",
  "phases_completed": ["requirements_collected", "architecture_designed"],
  "counters": {
    "feat": 1,
    "refactor": 0,
    "tdd": 0
  },
  "started_at": "2026-04-28T10:00:00Z",
  "last_updated": "2026-04-28T10:30:00Z"
}
```

> **向后兼容**：旧版 current-state.json 使用 `current_feat` 字段。读取时如发现旧字段而无 `current_task`，按 `current_task = current_feat`、`current_kind = "feat"`、`counters.feat = N` 转换并改写一次。

## 使用方式

### 开始新任务时
```markdown
调用 artifact-manager skill：
- 操作: create_task
- kind: feat | refactor | tdd
- 任务名称: <可选，仅日志用>
```

### 保存设计文档时
```markdown
调用 artifact-manager skill：
- 操作: save_document
- feat: feat-1
- document_type: architecture
- content: (Mermaid 架构图内容)
```

### 查询产物时
```markdown
调用 artifact-manager skill：
- 操作: list_artifacts
- feat: feat-1
```

## 约束

1. **不删除文档** — 所有设计文档必须存档，供后续参考
2. **版本控制** — 如有更新，保留历史版本（加日期后缀）
3. **命名规范** — 严格遵守上述文档命名规范
4. **状态同步** — 每次保存文档后更新 current-state.json