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

## 阶段详细说明

### 阶段 1: 需求收集 (requirements_collected)

**触发**: 用户描述开发任务

**执行**:
1. 使用 `artifact-manager` skill 创建新的 feat 目录
2. 解析用户需求，生成需求摘要文档
3. 保存到 `.neonbit-vibe-factory/feat-{N}/requirements.md`
4. **检测技术栈**：调用 `stack-detector` skill 的 `detect` 动作
   - 入参：`task_dir = .neonbit-vibe-factory/feat-{N}/`
   - 等待用户确认门通过
   - 完成后 `feat-{N}/stack.json` 与 `feat-{N}/routing-table.md` 已落盘
5. **填回需求摘要**：将 stack.json 中的 backend/frontend 信息写回 requirements.md 的"技术栈"字段（替换原"待定"占位）

**输出**:
```
## 需求摘要

- 功能: 用户管理模块的增删改查
- 页面: 用户列表页、用户编辑弹窗
- 接口: GET/POST/PUT/DELETE /api/users
- 技术栈: backend={language}({framework}), frontend={language}({framework})
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
1. **加载 Rules**：读取 `.neonbit-vibe-factory/feat-{N}/routing-table.md`，提取全部 rules 文件路径，Read 这些文件。提取 coding rules（编码规范、设计模式、安全约束作为审查标准）和 test rules（排除不测试的文件如"不测试 DTO/Entity/Config/Mapper",作为审查测试代码标准），传递给 writing-plans 作为任务拆分约束
2. 调用 `Skill` 工具加载 `superpowers:writing-plans`
3. 基于以上所有设计文档和测试约束，生成执行计划
4. 保存到 `.neonbit-vibe-factory/feat-{N}/plan.md`
5. **等待用户审查**执行计划
6. 用户批准后进入阶段 6。设计文档与之前讨论冲突时，以设计文档为准。

### 阶段 6: 后端开发 (backend_development)

**触发**: 执行计划已批准

**执行**:
1. **注入 rules 路径**：读取 `.neonbit-vibe-factory/feat-{N}/routing-table.md`，提取 backend 相关的 rules 路径列表。后续 spawn agent 时将这些路径写入 prompt 的"必读编程规范"段。
2. 调用 `Skill` 工具加载 `neonbit-vibe-factory:tdd-conductor` skill
3. 按照 tdd-conductor skill 的指令协调 TDD 流程：
   - 读取设计文档，拆分 TDD 任务
   - spawn test agent 编写失败测试 (RED)
   - spawn coding agent 实现功能 (GREEN)
   - 主会话审查代码 (REFACTOR)
4. 全部任务完成后进入前端阶段

**TDD 多 Agent 流程**:
```
orchestrator → 加载 tdd-conductor skill → spawn test agent (RED)
                                        → spawn coding agent (GREEN)
                                        → 主会话 REFACTOR 审查
                                        → 循环直到完成
```

**约束（必须遵守）**:
- 不允许有空代码或假代码
- 以设计文档（requirements.md、architecture.md、design.md、openapi.yaml、plan.md）为准，与之前讨论冲突时以文档为准

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

**约束（必须遵守）**:
- 以设计文档（ui-design.md、page-design.md、requirements.md）为准

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

**循环参数**:

| 参数 | 值 | 说明 |
|------|-----|------|
| `max_rounds` | 5 | E2E 重跑最大轮数（8b → 8f 外层循环） |
| `coding_max_retries` | 10 | 单轮内 coding 修复+审查+test 验证最大重试次数（8d → 8e → 8e2 内层循环） |
| `health_check_timeout` | 60 | 服务启动健康检查超时秒数 |
| `health_check_interval` | 2 | 健康检查轮询间隔秒数 |

**执行**:

#### 8a. 启动服务

1. 读取 `.neonbit-vibe-factory/feat-{N}/stack.json`，获取后端框架和前端框架信息
2. **端口发现**（Spring Boot 配置继承链：按顺序读取 `application.yml` → `application-{profile}.yml`，后读的覆盖先读的；最终未找到则用默认值）：
   - Spring Boot 后端默认端口: `8080`
   - Vite 前端默认端口: `5173`
   - 约定后端 profile 为 `local`
3. 启动后端（Bash background，记录 PID）：
   - Maven: `mvn spring-boot:run -Dspring-boot.run.profiles=local`
   - Gradle: `./gradlew bootRun --args='--spring.profiles.active=local'`
4. 启动前端（Bash background，记录 PID）：`pnpm run dev`
5. **健康检查**：轮询后端 `/actuator/health` 和前端 `/`，`health_check_interval` 秒间隔，`health_check_timeout` 秒超时。超时则报错退出，先 kill 已启动的进程
6. 构造服务地址：
   - `frontendURL` = `http://localhost:{frontendPort}`
   - `baseURL` = `http://localhost:{backendPort}`

#### 8b. spawn e2e-test agent（FULL-RUN 模式）

**注入 rules**：从 `<task_dir>/routing-table.md` 中提取 `Applies to` 含 `e2e` 的 rules 路径列表，追加到 prompt 的"必读编程规范"段。

```
Agent({
  subagent_type: "neonbit-vibe-factory:e2e-test:e2e-test",
  prompt: `
## 任务描述
对以下页面执行 E2E 测试

## 页面列表
{从 ui-design.md 或 page-design.md 提取的页面列表}

## 服务地址
- frontendURL: {frontendURL}
- baseURL: {baseURL}

## 源码目录
{前端页面源码根目录}

## 测试输出目录
./e2e-tests

## 模式
FULL-RUN

FULL-RUN 模式说明：
- 跳过审查循环（第四步、第五步），不需要等待 APPROVED
- 变更检测后，对变更页面生成/更新测试文件
- 直接进入第六步执行测试
- 测试完成后输出结构化失败报告

开始执行 E2E 测试。
  `
})
```

#### 8c. 主会话分析测试结果

```
├── 全部通过 → 跳到 8g（停服完成）
├── 测试代码问题（选择器定位错误、等待超时配置不当等）：
│   → 反馈具体问题给 e2e-test agent，重新 spawn（本轮不消耗 coding_max_retries）
│   → 最多 2 次测试修复尝试，仍失败则降级为业务代码问题处理
└── 业务代码问题（接口返回错误、页面逻辑缺陷、数据问题等）→ 进入 8d
```

#### 8d. spawn coding agent 修复业务代码

**注入 rules**：从 `<task_dir>/routing-table.md` 中提取 `Applies to` 含 `coding` 的 rules 路径列表，追加到 prompt 的"必读编程规范"段。

```
Agent({
  subagent_type: "neonbit-vibe-factory:coding:coding",
  prompt: `
## 任务描述
修复 E2E 测试发现的 BUG

## 失败测试信息
{从 e2e-test agent 返回的结构化失败报告中提取：测试名称、错误类型、错误信息、截图路径、疑似根因模块、相关接口}

## E2E 测试文件位置
{e2e 测试文件路径}

## 实现约束
1. 分析失败原因，修复业务代码
2. 不修改任何测试代码（含 E2E 测试和单元/集成测试）
3. 修复范围限于失败测试对应的功能模块
4. 不写假代码 (NotImplementedException / TODO)

开始执行 BUG 修复。
  `
})
```

#### 8e. 主会话审查代码变更

**审查清单**：
1. 修复是否针对失败原因？
2. 是否有超范围修改？（含修改测试代码、改动无关文件、改动计划外模块）
3. 是否有空代码/假代码？
4. 是否符合 coding rules？

```
├── 合格 → 进入 8e2
└── 不合格 → 反馈具体问题给 coding agent，重新 spawn（8d），不消耗 coding_max_retries
```

#### 8e2. spawn test agent 验证

```
Agent({
  subagent_type: "neonbit-vibe-factory:test:test",
  prompt: `
## 任务描述
运行受影响模块的全部测试，验证 BUG 修复没有破坏已有功能

## 模式
GREEN

## 受影响模块
{根据 coding agent 修改的文件推断}

## 验证要求
1. 运行受影响模块的全部单元测试和集成测试
2. 如果有测试失败，报告失败的测试和原因
3. 确认所有已有测试仍然通过

开始执行测试验证。
  `
})
```

**评估**：
```
├── 全部通过 → 进入 8f
└── 有失败 → 失败信息反馈给 coding agent，回到 8d（消耗 1 次 coding_max_retries）
```

#### 8f. 判断

```
本轮 E2E 修复完成，round++

├── 全部 E2E 通过 → 跳到 8g
├── round < max_rounds → 回到 8b 重跑 E2E（不重启服务）
├── coding_max_retries 耗尽 → 标记需人工介入，进入 8g
└── round >= max_rounds → 标记需人工介入，进入 8g
```

#### 8g. 停服清理

1. 输出最终报告（通过数/失败数/轮数/是否人工介入）
2. kill 后端进程（从 PID 文件读取）
3. kill 前端进程（从 PID 文件读取）
4. 清理 PID 文件 `/tmp/neonbit-e2e-backend.pid`、`/tmp/neonbit-e2e-frontend.pid`

**约束（必须遵守）**:
- 以设计文档（ui-design.md、openapi.yaml、requirements.md）为准
- 无论测试结果如何，8g 清理步骤必须执行
- 服务启动失败时，先 kill 已启动的进程再报错

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
