---
name: stack-detector
description: |
  使用此 skill 当需要识别项目的技术栈（编程语言、框架）并生成对应的 rules 路由表时触发。

  <example>
  Context: 命令入口创建了 feat-{N}/、refactor-{N}/ 或 tdd-{N}/ 任务目录后
  user: "已创建 tdd-1/，请检测技术栈"
  assistant: "我将使用 stack-detector skill 检测当前项目的语言/框架并生成 routing-table.md。"
  <commentary>
  在三个命令入口（/start /refactor /tdd）创建任务目录后调用，结果写入对应任务目录。
  </commentary>
  </example>

  <example>
  Context: 检测发现可能的技术栈，需要用户确认
  user: "继续"
  assistant: "stack-detector 在检测后必须输出确认门，等待用户回 OK 才落盘。"
  <commentary>
  强制确认门，避免误判。
  </commentary>
  </example>
---

# Stack Detector Skill

负责识别当前项目的技术栈，并为指定的任务目录生成 `stack.json` + `routing-table.md`。

## 接口

只有一个动作：`detect(task_dir)`。

- **输入参数 task_dir**：相对仓库根的任务目录路径，例如 `.neonbit-vibe-factory/feat-1/`、`.neonbit-vibe-factory/tdd-2/`、`.neonbit-vibe-factory/refactor-3/`。
- **输出**：在 `task_dir/` 中写入两个文件：`stack.json` 和 `routing-table.md`。

**幂等性**：若 `task_dir/stack.json` 已存在且字段完整，直接复用，不重新检测；同时校验 `task_dir/routing-table.md` 存在，缺则重新渲染。

## 工作流程

### 第一步：幂等检查

读 `task_dir/stack.json`：
- 若不存在 → 进入第二步
- 若存在但字段不完整 → 进入第二步
- 若存在且完整 → 跳到第五步（仅校验/补建 routing-table.md）

### 第二步：检测技术栈

按 `references/detection-rules.md` 中定义的优先级检测，命中即止。

输出形如：
```
检测结果（待确认）：
  backend:  java (spring-boot)        ← pom.xml: spring-boot-starter-web 3.2
  frontend: typescript (vue3)         ← package.json: vue ^3.4
```

若全部规则失败：
```
检测结果（待确认）：
  backend:  未识别
  frontend: 未识别
```

### 第三步：强制确认门

向用户输出：
```
## 技术栈确认

检测结果：
  backend:  {lang} ({framework})
  frontend: {lang} ({framework})

请确认或修正（回复 OK 或给出修正）：
```

**必须等待用户回复后才能继续。** 不允许跳过此步。

用户可能回复：
- `OK` / `确认` → 使用检测结果
- `backend 改为 kotlin` → 修正后再次输出确认门
- `没有前端` → frontend 设为 null

### 第四步：落盘 stack.json

写入 `task_dir/stack.json`：
```json
{
  "backend": {
    "language": "java",
    "framework": "spring-boot",
    "evidence": "pom.xml: spring-boot-starter-web 3.2"
  },
  "frontend": {
    "language": "typescript",
    "framework": "vue3",
    "evidence": "package.json: vue ^3.4"
  },
  "detected_at": "2026-05-14T10:00:00Z",
  "confirmed_by_user": true
}
```

若某槽位未识别或用户说"没有"，该槽位设为 `null`。

### 第五步：渲染 routing-table.md

按 `references/routing-template.md` 中定义的目录扫描规则，实际扫描 `references/rules/` 目录并生成 `task_dir/routing-table.md`。

**步骤 5.1：确定 PLUGIN_ROOT**

获取 plugin 目录的绝对路径作为 `{PLUGIN_ROOT}`（即当前 plugin 根目录）。

**步骤 5.2：准备变量**

从 `stack.json` 读取：
- `backend.language` → `{BACKEND_LANG}`（如 `java`、`golang`），null 则跳过 backend 段
- `backend.framework` → `{BACKEND_FW}`（如 `spring-boot`），null 则不过滤框架
- `frontend.language` → `{FRONTEND_LANG}`（如 `typescript`），null 则跳过 frontend 和 web 段

**步骤 5.3：框架过滤函数**

对 `code/` 和 `test/` 下的每个 `.md` 文件判断是否应包含：

```
function framework_match(filename, framework):
    if filename 不含 "-{name}.md" 后缀 → 包含（无框架标记，总是包含）
    if framework == null → 跳过（纯语言不需要框架特有文件）
    else:
        提取文件名中最后一个 "-{name}.md" 的 {name}
        if {name} == framework（小写比较）→ 包含
        else → 跳过
```

根目录（非 code/ 非 test/）的 `.md` 文件不做框架过滤，总是包含。

**步骤 5.4：扫描并生成路由表**

依次扫描以下目录层级，对每个文件校验存在性后写入路由表：

**Common 段**（总是执行）：
- `ls {PLUGIN_ROOT}/references/rules/common/code/*.md` → Applies to: coding
- `ls {PLUGIN_ROOT}/references/rules/common/test/*.md` → Applies to: test
- `ls {PLUGIN_ROOT}/references/rules/common/*.md`（根目录直接子文件）→ Applies to: coding, test

**Backend 段**（仅当 BACKEND_LANG 非 null）：
- `ls {PLUGIN_ROOT}/references/rules/{BACKEND_LANG}/code/*.md` → 应用框架过滤(BACKEND_FW) → Applies to: coding
- `ls {PLUGIN_ROOT}/references/rules/{BACKEND_LANG}/test/*.md` → 应用框架过滤(BACKEND_FW) → Applies to: test
- `ls {PLUGIN_ROOT}/references/rules/{BACKEND_LANG}/*.md`（根目录直接子文件）→ Applies to: coding, test

**Frontend 段**（仅当 FRONTEND_LANG 非 null）：
- `ls {PLUGIN_ROOT}/references/rules/{FRONTEND_LANG}/code/*.md` → Applies to: coding
- `ls {PLUGIN_ROOT}/references/rules/{FRONTEND_LANG}/test/*.md` → Applies to: test
- `ls {PLUGIN_ROOT}/references/rules/{FRONTEND_LANG}/*.md`（根目录直接子文件）→ Applies to: coding, test

**Web 段**（仅当 FRONTEND_LANG 非 null）：
- `ls {PLUGIN_ROOT}/references/rules/web/code/*.md` → Applies to: coding, e2e
- `ls {PLUGIN_ROOT}/references/rules/web/test/*.md` → Applies to: test, e2e
- `ls {PLUGIN_ROOT}/references/rules/web/*.md`（根目录直接子文件）→ Applies to: coding, test, e2e

**步骤 5.5：输出格式**

生成的 `routing-table.md` 按角色分组为 Markdown 表格：

```markdown
# Rules Routing Table

> 本文件由 stack-detector 自动生成。
> conductor 派发 agent 时读取本文件，按角色注入对应路径列表。

- Generated: {ISO timestamp}
- Stack: backend={BACKEND_LANG}/{BACKEND_FW}, frontend={FRONTEND_LANG}

## Coding Rules
| # | File | Applies to |
|---|------|-----------|
| 1 | {PLUGIN_ROOT}/references/rules/common/code/coding-style.md | coding |
| ...

## Test Rules
| # | File | Applies to |
|---|------|-----------|
| 1 | {PLUGIN_ROOT}/references/rules/common/test/testing.md | test |
| ...

## Shared Rules (code & test)
| # | File | Applies to |
|---|------|-----------|
| 1 | {PLUGIN_ROOT}/references/rules/common/hooks.md | coding, test |
| ...
```

文件路径使用绝对路径。不存在的目录或空目录对应段输出 `(empty)`。不存在的文件跳过。

### 第六步：输出完成报告

```
## Stack Detection 完成

- stack.json: {task_dir}/stack.json ✓
- routing-table.md: {task_dir}/routing-table.md ✓
- backend rules: {N} files
- frontend rules: {M} files
```
