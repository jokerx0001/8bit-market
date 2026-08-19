---
name: web2-dev:artifact-manager
description: |
  产物目录管理 skill。管理任务目录创建和全局状态。
  三个 conductor 通过本 skill 统一创建任务目录，消除样板代码重复。
  dev_dir 由 conductor 显式传入，不自己读 config。

  <example>
  Context: orchestrator 阶段 1 — 需要创建任务目录
  assistant: "使用 artifact-manager 创建 feat-3 任务目录。"
  </example>
---

# Artifact Manager

管理产物目录的创建和状态维护。**current-state.json 的唯一写入者。**

## 调用格式

```
Skill({skill: "web2-dev:artifact-manager", args: "--kind {new|feat|refactor|fix} --dev-dir {dev_dir}"})
```

dev_dir 由 conductor 在检测技术栈后显式传入，不自己读 config。

## 执行

### Step 1: 读状态

```bash
cat {dev_dir}/current-state.json 2>/dev/null || echo '{"current_task":"","current_kind":"","counters":{"new":0,"feat":0,"refactor":0,"fix":0}}'
```

### Step 2: 递增计数器

`counters.{kind}` +1 → `{N}`。

### Step 3: 创建目录

```bash
mkdir -p {dev_dir}/{kind}-{N}/.work
```

### Step 4: 写回状态

```json
{
  "current_task": "{kind}-{N}",
  "current_kind": "{kind}",
  "counters": {
    "new": {原有值},
    "feat": {原有值},
    "refactor": {原有值},
    "fix": {N}
  }
}
```

### Step 5: 返回

```
task_dir = {dev_dir}/{kind}-{N}
```

## 目录结构

```
{dev_dir}/{kind}-{N}/
├── plan.md                    # 任务清单（简洁，exec 唯一依赖）
├── progress.json              # exec 进度（支持断点续跑）
└── .work/                     # 中间产物
    ├── user-prompt.md         # 用户原始输入
    ├── grill-interview.md     # grilling 采访记录
    ├── requirements.md        # 本次需求/行为清单
    ├── architecture.md        # 架构设计（含领域模型）
    ├── design.md              # 详细设计（按模块）
    ├── layouts/               # frontend-design 产出的 UI 设计稿
    ├── integration/           # 后端集成测试脚本
    ├── e2e/                   # 前端 E2E 测试脚本
    ├── fix-attempts.md        # 集成/E2E 失败经验（按用例分节）
    └── debug-analysis-*.md    # 集成/E2E 失败用例根因分析
```

## 约束

- 不直接操作 `current-state.json`——除了读/写计数器和当前任务
- 不猜测 dev_dir——从 conductor 传入
- kind 不在 {new, feat, refactor, fix} 中 → 报错
- `current-state.json` 不存在 → 用默认值初始化
