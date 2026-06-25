---
name: renpy-dev:collect-lessons
description: |
  在 Ren'Py 开发任务完成后收集和记录开发经验。由 Stop hook 在会话结束时自动触发，
  也支持手动调用。回顾 tdd-iterations.md 和会话上下文，提取问题和解决方案，
  区分测试和编码问题，查阅 Ren'Py 文档验证后写入 .renpy-dev/test-lessons.md
  和 .renpy-dev/coding-lessons.md，同时更新项目 CLAUDE.md。

  <example>
  Context: 会话结束时 Stop hook 检测到 .renpy-dev/ 目录，自动触发
  user: (Stop hook blocked, Claude executes collect-lessons)
  assistant: "使用 collect-lessons skill 收集本次开发经验。"
  <commentary>
  Stop hook 在每次会话结束前检查项目是否有 .renpy-dev/ 目录，有则触发本 skill。
  </commentary>
  </example>

  <example>
  Context: 用户想手动补充经验记录
  user: "/renpy-dev:collect-lessons"
  assistant: "使用 collect-lessons skill 收集经验。"
  <commentary>
  支持手动调用，无需参数。
  </commentary>
  </example>
---

# Ren'Py Collect Lessons — 经验收集

由 Stop hook 在会话结束时自动触发，回顾本次会话中的 Ren'Py 开发工作，提取并记录经验。

## 触发方式

- **自动**：Stop hook 检测到项目有 `.renpy-dev/` 目录时触发
- **手动**：`/renpy-dev:collect-lessons`

## 工作流

### 1. 快速检查

检查 `.renpy-dev/current-state.json` 是否存在且有 `current_task`。如果不存在或从未有过任务 → 输出 "本次会话无 Ren'Py 开发活动，跳过经验收集" 后结束。

### 2. 确定任务

从 `.renpy-dev/current-state.json` 读取 `current_task`（如 `feat-1`、`fix-2`、`refactor-3`）。

### 3. 收集上下文

读取产物：
```
.renpy-dev/{current_task}/plan.md                  # 任务概述
.renpy-dev/{current_task}/.work/tdd-iterations.md  # TDD 迭代日志（主要来源）
.renpy-dev/{current_task}/progress.json            # 任务完成状态
```

回顾**当前会话上下文**：
- test-agent 的错误输出和重试
- coding-agent 的反复修改
- VERIFY 阶段的测试失败和修复
- review 阶段的违规和修复

### 4. 提取经验

从上下文和 tdd-iterations.md 中识别：

- TDD 迭代中多次重试才通过的测试 → 测试写法问题
- coding-agent 反复修改才符合 review → 编码规范问题
- VERIFY 阶段意外测试失败 → 框架行为理解偏差
- review 发现的违规（widget id 缺失、jump/call 目标不存在等）→ 规范遗漏

每条经验结构：
- **问题**：具体的错误现象
- **原因**：为什么会出现
- **解决**：最终采用的方案

**如果没有发现值得记录的经验** → 输出 "本次会话无新的 Ren'Py 经验需要记录"，跳到步骤 7。

### 5. 分类 & 验证

| 分类 | 归入文件 |
|------|---------|
| testcase/testsuite 语法、assert、click id、测试框架行为、测试配置、测试隔离 | `.renpy-dev/test-lessons.md` |
| Ren'Py screen/widget/样式/label/jump/call、框架行为（存档/回滚/persistent）、UI 原则 | `.renpy-dev/coding-lessons.md` |
| 工作流/工具链问题（agent 协作、进度恢复等） | 不记录 |

**验证事实**：对涉及 Ren'Py API/语法的经验，使用 `WebFetch` 查询 `https://www.renpy.org/doc/html/{page}.html` 确认（页面选择参照 `references/renpy-docs.md`）。只在文档确认后才写入，无法确认的标注 `[待验证]`。

### 6. 写入文件

按 `references/lessons-format.md` 格式写入：

**test-lessons.md / coding-lessons.md**：
- 读取现有文件（不存在则创建）
- 查找 `## {current_task}:` 节 → 已存在则追加，不存在则新建节

**项目 CLAUDE.md**：
- 查找 `## Ren'Py 开发经验` 节 → 不存在则追加
- 每条一行：`- **{问题简述}** → {解决方案}`
- 去重：相同问题不重复添加

### 7. 输出报告

```
## 经验收集完成

**任务**: {current_task}
**测试经验**: {count} 条 → .renpy-dev/test-lessons.md
**编码经验**: {count} 条 → .renpy-dev/coding-lessons.md
**CLAUDE.md 更新**: {count} 条
{如有 [待验证] 条目列出}
```
