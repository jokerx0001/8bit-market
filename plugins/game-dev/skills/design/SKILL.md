---
name: game-dev:design
description: 详细设计。读取 architecture.md ，按技术栈模板编写 design.md。
---

# 详细设计

读取 architecture.md，按技术栈模板编写 design.md。

**格式模板：** `${CLAUDE_PLUGIN_ROOT}/references/{tech}/design.md`

## 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--from {task_dir}` | 是 | 任务目录路径（如 `.godot-dev/feat-3`） |
| `--tech {tech}` | 是 | 技术栈标识（godot / renpy） |

## 工作流

### 1. 读取输入

- `{task_dir}/.work/architecture.md`
- `{task_dir}/.work/domain-design.md`

### 2. 逐项编写

按 architecture 的场景清单逐项编写。新建写完整设计，修改写变更说明，复用跳过。

具体格式、示例和规则见 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/design.md`。

### 3. 输出

写入 `{task_dir}/.work/design.md`
