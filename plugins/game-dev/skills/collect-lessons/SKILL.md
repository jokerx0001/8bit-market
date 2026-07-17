---
name: game-dev:collect-lessons
description: |
  在游戏开发任务完成后收集和记录开发经验。由 Stop hook 在会话结束时自动触发，
  也支持手动调用。自动检测技术栈，回顾 tdd-iterations.md
  和会话上下文，提取问题和解决方案，区分测试和编码问题，查阅对应技术栈文档
  验证后写入 {dev_dir}/test-lessons.md 和 {dev_dir}/coding-lessons.md，
  同时更新项目 CLAUDE.md。

  <example>
  Context: 会话结束时 Stop hook 检测到 {dev_dir}/ 目录，自动触发
  user: (Stop hook blocked, Claude executes collect-lessons)
  assistant: "使用 collect-lessons skill 收集本次开发经验。"
  <commentary>
  Stop hook 在每次会话结束前检查项目是否有 {dev_dir}/ 目录，有则触发本 skill。
  </commentary>
  </example>

  <example>
  Context: 用户想手动补充经验记录
  user: "/game-dev:collect-lessons"
  assistant: "使用 collect-lessons skill 收集经验。"
  <commentary>
  支持手动调用，无需参数。
  </commentary>
  </example>
---

# Game Dev Collect Lessons — 经验收集

由 Stop hook 在会话结束时自动触发，回顾本次会话中的游戏开发工作，提取并记录经验。

## 触发方式

- **自动**：Stop hook 检测到项目有 `{dev_dir}/` 目录时触发
- **手动**：`/game-dev:collect-lessons`

## 参数

- `tech`（可选）：技术栈标识。exec 调用时传入，Stop hook / 手动调用时为空。

## 工作流

### 1. 确定 tech 和 dev_dir

**a) 传参**：调用时传入了 `tech`，直接使用。

**b) CLAUDE.md 检测**：未传入时，读项目 CLAUDE.md判断技术栈

tech 为小写字母单词,一般为引擎名,示例如下
renpy|godot

确定 tech 后，读取 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md`。从 `## 产物目录` 获取 `dev_dir`，从 `## 文档` 获取验证用文档 URL 和查询方式。

### 2. 快速检查

检查 `{dev_dir}/current-state.json` 是否存在且有 `current_task`。如果不存在或从未有过任务 → 输出 "本次会话无游戏开发活动，跳过经验收集" 后结束。

### 3. 确定任务

从 `{dev_dir}/current-state.json` 读取 `current_task`（如 `feat-1`、`fix-2`、`refactor-3`）。

### 4. 收集上下文

读取产物：
```
{dev_dir}/{current_task}/plan.md                  # 任务概述
{dev_dir}/{current_task}/.work/tdd-iterations.md  # TDD 迭代日志（主要来源）
{dev_dir}/{current_task}/.work/coding/lessons.md  # coding agent 逐轮记录的经验（主要来源）
{dev_dir}/{current_task}/progress.json            # 任务完成状态
```

回顾**当前会话上下文**：
- test-agent 的错误输出和重试
- coding-agent 的反复修改
- VERIFY 阶段的测试失败和修复
- 边界检查阶段的违规和修复

### 5. 提取经验

从上下文和 tdd-iterations.md 中识别反复出现的问题：

- TDD 迭代中多次重试才通过的测试 → 测试写法问题
- coding-agent 反复修改才通过 → 编码规范问题
- VERIFY 阶段意外测试失败 → 框架行为理解偏差
- 边界检查发现的违规 → 规范遗漏

每条经验结构：
- **问题**：具体的错误现象
- **原因**：为什么会出现
- **解决**：最终采用的方案

**如果没有发现值得记录的经验** → 输出 "本次会话无新的 {tech} 经验需要记录"，跳到步骤 8。

### 6. 分类 & 验证

| 分类 | 归入文件 |
|------|---------|
| 测试框架语法、assert 方法、测试配置、测试隔离、测试运行器行为 | `{dev_dir}/test-lessons.md` |
| 源码编写规范、框架 API 使用、资源文件规范、UI 原则 | `{dev_dir}/coding-lessons.md` |
| 工作流/工具链问题（agent 协作、进度恢复等） | 不记录 |

**验证事实**：对涉及框架 API/语法的经验，按 config.md 的 `## 文档` 节指定的方式查阅文档确认。只在文档确认后才写入，无法确认的标注 `[待验证]`。

### 7. 写入文件

**test-lessons.md / coding-lessons.md**：

```markdown
## {current_task}: {从 plan.md 提取的简要任务描述}

### {问题简述}
- **问题**: {具体错误现象}
- **原因**: {根因分析}
- **解决**: {最终采用的方案}
```

- 读取现有文件（不存在则创建）
- 查找 `## {current_task}:` 节 → 已存在则追加，不存在则新建节

**项目 CLAUDE.md**：

- 搜索已有的 `## .*开发经验` 节 → 存在则复用，不存在则新建 `## {tech} 开发经验`
- 每条一行：`- **{问题简述}** → {解决方案}`
- 去重：相同问题不重复添加

### 8. 输出报告

```
## 经验收集完成

**技术栈**: {tech}
**任务**: {current_task}
**测试经验**: {count} 条 → {dev_dir}/test-lessons.md
**编码经验**: {count} 条 → {dev_dir}/coding-lessons.md
**CLAUDE.md 更新**: {count} 条
{如有 [待验证] 条目，逐条列出}
```
