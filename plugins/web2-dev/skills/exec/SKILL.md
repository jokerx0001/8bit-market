---
name: web2-dev:exec
description: |
  实现阶段编排 skill。被 orchestrator 在审查通过后调用。
  只读 plan.md（任务清单），spawn coding agent 完成 TDD + 集成测试 + E2E，
  spawn ops agent 完成基础设施和服务部署。

  <example>
  Context: orchestrator 审查通过，进入实现阶段
  user: "exec 启动 — 按 plan.md 任务清单循环实现。"
  assistant: "spawn ops → 任务1 TDD+review → 任务2 TDD+review → 集成测试 → 部署 → E2E。"
  </example>
---

# Exec — 实现阶段编排

## The Iron Law

```
EXEC WRITES ZERO CODE. EXEC RUNS ZERO TESTS.

Exec spawns: coding agent for TDD/测试/修复, ops agent for 部署.
Exec's job: build the right prompt, spawn the right agent, check the results, log everything.
Exec NEVER: writes implementation code, runs tests itself, fixes bugs itself.

Violating the letter of this rule is violating the spirit of this rule.
```

## 数据来源

**只读 plan.md 产物，不依赖 plan 阶段上下文：**
- `{task_dir}/plan.md` — 任务清单
- `{task_dir}/.work/design.md` — 详细设计（按模块，coding agent 按模块名查找）
- `{task_dir}/.work/architecture.md` — 架构设计
- `{task_dir}/.work/requirements.md` — 行为清单
- 项目 CLAUDE.md — 服务器、账户、部署方式

---

## 执行流程总览

```
阶段 1: spawn ops agent → 基础设施部署（infra-ops）

阶段 2: 按任务串行循环（每个 plan.md 任务）
  ├── spawn coding agent (TDD via mattpocock-skills:tdd)
  ├── 主agent code-review (设计一致性 + 测试覆盖)
  └── 不合格? spawn coding agent 一次性修复全部 → re-review

阶段 3: spawn coding agent → 后端集成测试(本地 + 自修复)

阶段 4: spawn ops agent → 部署后端(service-ops)

阶段 5: spawn coding agent → 后端集成测试(部署后 + 自修复)

阶段 6: spawn coding agent → 前端开发(逻辑 TDD + UI 编码)

阶段 7: spawn coding agent → 前端 E2E(自修复)

阶段 8: 主agent code-review (前端)

阶段 9: spawn ops agent → 部署前端(service-ops)

阶段 10: spawn coding agent → 前端 E2E(部署后 + 自修复)
```

---

## 初始化

**Step 0a — 解析 task_dir 为绝对路径：**

所有后续 Bash/Grep/Read 操作使用绝对路径，不依赖 CWD。

**Step 0b — 读取 plan.md 获取任务列表：**
```bash
grep -E '^\|' {task_dir}/plan.md | grep -v '模块|-----'
```

提取模块名列表。任务按行号顺序串行执行。

**Step 0c — 回显初始化确认（硬门）：**
```
## exec 初始化确认
task_dir: {绝对路径}
模式: {new|feat|refactor}
任务数: {N}
任务列表: {模块名1}, {模块名2}, ...
```



## 阶段 1：基础设施部署

读取 plan.md 任务列表 + design.md，确定需要的组件。

```
Agent({
  subagent_type: "ops",
  description: "Deploy infrastructure",
  prompt: "
## 操作类型
infra-ops

## task_dir
{task_dir}

## 任务
部署以下组件：
{从 design.md 中分析出的组件清单，如 PostgreSQL、Redis 等}

## 要求
- 使用 Ansible playbook（从 CLAUDE.md 中获取 Ansible 项目路径）
- 部署后测试可用性
- 超管操作只输出命令，由人工执行
- 读 ${CLAUDE_PLUGIN_ROOT}/references/ops/security.md 遵守安全规范
  "
})
```

ops agent 返回后验证部署结果。

---

## 阶段 2：按任务串行循环

读取 `{task_dir}/plan.md` 中的任务列表。**按顺序逐个处理，不跳过不并行。**

对每个任务（模块）：

### Step 2a — Spawn coding agent (TDD)

```
Agent({
  subagent_type: "coding",
  description: "Implement {模块名}",
  prompt: "
## 模式
TDD

## project
{project 名称}

## task_dir
{task_dir}

## 模块
{模块名}

## 目标
从 {task_dir}/.work/design.md 中读取 {模块名} 的详细设计（DB + API + 交互）。
从 {task_dir}/.work/requirements.md 中读取对应的行为清单。

调用 Skill(\"mattpocock-skills:tdd\") 完成 RED→GREEN 循环：
1. 从行为清单确认 seam（公共接口边界）
2. 逐个 seam: RED(写失败测试) → verify RED → GREEN(最小实现) → verify GREEN
3. 全部通过后返回报告

## 规则
- 只测试有逻辑的方法——跳过纯 CRUD/透传/配置方法
- 遵守 ${CLAUDE_PLUGIN_ROOT}/references/rules/{lang}/ 中的编码规范
- 不写空壳/假代码
  "
})
```

### Step 2b — Code Review

主 agent 执行 code-review：
```
Skill({skill: "web2-dev:code-review", args: "--task-dir {task_dir} --module {模块名}"})
```

产出不合格项清单。**有不合格项 → spawn coding agent 一次性修复全部：**

```
Agent({
  subagent_type: "coding",
  description: "Fix code review findings for {模块名}",
  prompt: "
## 模式
code-review-fix

## task_dir
{task_dir}

## 模块
{模块名}

## 不合格项（必须全部修复）
{逐条列出 code-review 报告中的每一项，含位置+问题+原因}

## 要求
逐条修复，修复后跑测试验证。全部通过后返回。
  "
})
```

修复后主 agent 再次 code-review。循环直到零不合格项。**最多 3 轮。**

### Step 2c — 记录进度

将任务完成状态写入 `{task_dir}/progress.json`：
```json
{
  "current_stage": "task_loop",
  "current_task": {任务序号},
  "completed_tasks": [
    {"module": "{模块名}", "status": "completed", "review_passed": true}
  ]
}
```

「阶段 3-10 的 spawn prompt 模板结构与阶段 1/2 一致，均使用 `Agent({subagent_type, description, prompt: "## 模式\\n..."})` 格式，省略重复。」

### 阶段 3：后端集成测试（本地）

```
Agent({
  subagent_type: "coding",
  description: "Backend integration test (local)",
  prompt: "
## 模式
integration-test

## project
{project 名称}

## task_dir
{task_dir}

## 任务
按 CLAUDE.md 中的方式在本地启动后端服务。
对 design.md 中每个模块的 API 接口运行集成测试（成功 + 失败场景）。
对 design.md 中声明的集成验证/全链路要求（如"跑通 爬取→MQ→消费→入库→精炼 全链路"）执行端到端验证——不限于单接口，最后一环是页面数据源查询接口返回该批次数据。

调用 Skill(\"web2-dev:backend-integration-test\") 完成测试 + 自修复循环。
  "
})
```

### 阶段 4：部署后端

```
Agent({
  subagent_type: "ops",
  description: "Deploy backend to dev server",
  prompt: "
## 操作类型
service-ops

## task_dir
{task_dir}

## 任务
按 CLAUDE.md 中的部署方式将后端服务部署到开发服务器。
{feat/refactor/fix 模式}：创建分支 {mode}-{任务名}（与任务名对应，如任务目录 feat-1 → 分支 feat-1），
commit + push 到远程触发部署；push 后检查部署状态，失败则寻找原因解决问题。
{new 模式}：按 CLAUDE.md 部署方式执行，不创建特性分支。
部署完成后执行健康检查。
  "
})
```

### 阶段 5：后端集成测试（部署后）

```
Agent({
  subagent_type: "coding",
  description: "Backend integration test (deployed)",
  prompt: "
## 模式
integration-test

## task_dir
{task_dir}

## 任务
对部署后的后端服务运行 API 测试（地址从 CLAUDE.md 获取）。
对 design.md 中声明的集成验证/全链路要求执行端到端验证（例如含页面数据源查询接口返回该批次数据）。
调用 Skill(\"web2-dev:backend-integration-test\") 完成测试 + 自修复。
  "
})
```

### 阶段 6：前端开发

```
Agent({
  subagent_type: "coding",
  description: "Frontend development",
  prompt: "
## 模式
frontend

## project
{project 名称}

## task_dir
{task_dir}

## 任务
开发前端。

1. 逻辑层（hooks、stores、utils）：
   调用 Skill(\"mattpocock-skills:tdd\") 完成 TDD 循环

2. UI 层（组件、页面）：
   参照 {task_dir}/.work/layouts/ 中的 HTML 设计稿编码

## 规则
- 接口调用地址从 CLAUDE.md 获取开发服务器地址
- 遵守 ${CLAUDE_PLUGIN_ROOT}/references/rules/web/ 中的前端编码规范
  "
})
```

### 阶段 7：前端 E2E

```
Agent({
  subagent_type: "coding",
  description: "Frontend E2E test (local)",
  prompt: "
## 模式
e2e-test

## task_dir
{task_dir}

## 任务
启动前端开发服务器，运行 Playwright E2E 测试。
调用 Skill(\"web2-dev:frontend-e2e-test\") 完成 E2E + 自修复循环。
  "
})
```

### 阶段 8：Code Review（前端）

```
Skill({skill: "web2-dev:code-review", args: "--task-dir {task_dir} --target frontend"})
```

### 阶段 9：部署前端

```
Agent({
  subagent_type: "ops",
  description: "Deploy frontend",
  prompt: "
## 操作类型
service-ops

## task_dir
{task_dir}

## 任务
按 CLAUDE.md 中的部署方式部署前端静态资源。
  "
})
```

### 阶段 10：前端 E2E（部署后）

```
Agent({
  subagent_type: "coding",
  description: "Frontend E2E test (deployed)",
  prompt: "
## 模式
e2e-test

## task_dir
{task_dir}

## 任务
对部署后的前端运行 Playwright E2E 测试（地址从 CLAUDE.md 获取）。
调用 Skill(\"web2-dev:frontend-e2e-test\") 完成测试 + 自修复。
  "
})
```

---

## 断点续跑

`{task_dir}/progress.json` 记录每个阶段的完成状态：

```json
{
  "current_stage": "task_loop",
  "current_task": 2,
  "completed_tasks": [
    {"module": "user-service", "status": "completed", "review_passed": true}
  ],
  "stages_completed": ["infra_deploy"]
}
```

exec 启动时读取 progress.json，从上次中断处继续。**in_progress 任务从 TDD 重新开始（不信任中间状态）。**

## 错误处理

| 场景 | 处理 |
|------|------|
| coding agent TDD 失败 | 不限重试，连续 3 轮同一问题 → 报告用户 |
| code-review 3 轮仍不合格 | 报告阻塞，列出所有不合格项 |
| 集成测试自修复 5 轮仍失败 | 报告阻塞，列出失败详情 |
| 已有测试被破坏（refactor） | 立即反馈 coding agent 修复，最高优先级 |
| 后端部署后健康检查失败 | 执行回滚命令 |
| 用户中断 | 保存 progress.json，下次启动可继续 |

---

## Red Flags — STOP

- "任务简单不需要 spawn agent，我自己写更快" → STOP。exec 不写代码——这是 Iron Law
- "测试失败了我直接修一下就好" → STOP。exec 不修代码——重新 spawn coding agent
- "`--auto` 模式下可以简化流程" → STOP。--auto 只跳过人工审查，不跳过流程
- "批量完成所有任务的 TDD 再统一 review" → STOP。每个任务独立循环
- "code-review 没有不合格项的可能性很大，先跳过进入下个任务" → STOP。code-review 不可跳过
- "ops agent 部署好像失败了，我直接 ssh 上去修" → STOP。重新 spawn ops agent
- "前端没几个页面不需要 E2E" → STOP。E2E 不可跳过
- "这个模块太简单了不需要 review" → STOP。code-review 对每个模块必做
- "集成测试有几项失败但看起来不影响核心功能" → STOP。所有测试必须通过
- "已经 3 轮了差不多的，我自己补一下" → STOP。阻塞就报告，不自己补

**以上任一条 → STOP。回到对应阶段的 spawn。**

## 约束

- plan.md 是 exec 唯一的任务来源
- exec 只 spawn agent 进行工作，主会话负责编排和 review
- coding agent 不修改已有测试文件（除非是新增集成测试/E2E 脚本）
- 所有测试通过才算任务完成
- 每个模块的 code-review 不可跳过
