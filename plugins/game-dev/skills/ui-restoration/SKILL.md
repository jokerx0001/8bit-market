---
name: game-dev:ui-restoration
description: "UI 还原阶段。读取 plan.md 的 UI 还原章节，将 HTML 设计稿翻译为引擎 UI 代码。由 orchestrator 在 exec 完成后调用。"
---

# UI 还原

将 design-ui 产出的 HTML 设计稿逐任务翻译为引擎 UI 代码。独立于 exec 的 TDD 循环——HTML 文件本身就是规格，不做测试驱动。

## 核心原则

- **自己读 plan.md，自己判断有没有 UI 任务。** orchestrator 只传 task_dir 和 tech。
- **一次 spawn 一个 coding agent 处理一个 UI 任务。**
- **coding agent 的 spawn prompt 明确标记为 UI 还原任务。**

---

## 启动

### 1. 解析参数

从 `$ARGUMENTS` 解析 `--task-dir` 和 `--tech`。

### 2. 加载设计文档

读 `{task_dir}/plan.md` 的 `## UI 还原` 章节，提取 `[UI-N]` 任务列表。

```bash
grep '\[UI-\d+\]' {task_dir}/plan.md
```

无匹配 → 输出 "无 UI 还原任务，跳过。" 并结束。

### 3. 确认环境

读 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md`，获取 `project` 名称。

### 4. 回显确认

```
## ui-restoration 初始化确认
- tech: {tech}
- project: {project}
- task_dir: {task_dir}
- UI 任务: {N} 个 ([UI-1] ... [UI-N])
```

---

## Spawn Prompt 模板

每个 `[UI-N]` 任务使用以下模板组装 spawn prompt。`{...}` 为必须填充的变量。

```
Agent({
  subagent_type: "game-dev:coding",
  prompt: `
## 模式
UI 还原

## 项目
{project}

## task_dir
{task_dir}

## UI 任务
html: {task_dir}/{html_path}

## 截图验证
testcase: {screenshot_testcase_name}

## 任务
[UI-N] {任务描述}
  `
})
```

### 变量来源

| 变量 | 来源 |
|------|------|
| `{project}` | 从 config.md 获取 |
| `{task_dir}` | 调用方传入 |
| `{html_path}` | 从 plan.md 的 `## UI 还原` 章节 `[UI-N]` 行提取 `html:` 后的路径 |
| `{screenshot_testcase_name}` | Step A 确认的 testcase 名称（如 `test_ui_backpack_panel`） |
| `{任务描述}` | 从 plan.md 的 `## UI 还原` 章节 `[UI-N]` 行提取 |

coding-agent 检测到 `## 模式: UI 还原` + `## UI 任务` + `html:` 后自动进入 UI 翻译模式，完成后用 `## 截图验证` 中的 testcase 做自验证循环。

---

## 工作流

### 逐个处理 UI 任务

对 plan.md `## UI 还原` 章节中的每个 `[UI-N]` 任务，按顺序执行：

**Step A: 确保 screenshot testcase 存在**

从任务描述推导 testcase 名称（如 `test_ui_backpack_panel`），检查 `{test_dir}/visual/{testcase_name}.gd` 和 `.question` 是否已存在：

- 已存在 → 输出 "testcase {name} 已存在（由 exec 阶段创建），跳过。"，记录 testcase 名称
- 不存在 → spawn `game-dev:test-agent`，传入简洁 prompt 令其按 **Screenshot 测试编写方法** 创建该截图 testcase, 执行一次确认脚本可运行。

**Step B: spawn coding-agent 执行 UI 还原**

组装 spawn prompt（模板见下），将 screenshot testcase 名称传入。coding-agent 在 UI 翻译完成后自循环验证。

**Step C: 等待完成**

收集 coding agent 报告，确认通过后处理下一个 UI 任务。

### 汇总报告

所有 UI 任务完成后：

```
## UI 还原完成

| # | 任务 | HTML | 结果 |
|---|------|------|------|
| UI-1 | 背包面板视觉还原 | layouts/backpack.html | 完成 |
```
