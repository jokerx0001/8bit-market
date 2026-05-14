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

按 `references/routing-template.md` 中的模板，结合 stack.json 的 language 字段，渲染出 `task_dir/routing-table.md`。

渲染规则：
1. 读 stack.json 的 backend.language 和 frontend.language
2. 对每个非 null 的语言，从模板中取对应段
3. 将 `${PLUGIN_ROOT}` 替换为 plugin 的绝对路径（运行时解析）
4. 校验每条路径对应的文件是否真实存在于 `references/rules/` 下
5. 不存在的路径跳过，末尾加注释 `<!-- skipped: <path> not found -->`

### 第六步：输出完成报告

```
## Stack Detection 完成

- stack.json: {task_dir}/stack.json ✓
- routing-table.md: {task_dir}/routing-table.md ✓
- backend rules: {N} files
- frontend rules: {M} files
```
