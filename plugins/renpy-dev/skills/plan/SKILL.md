---
name: renpy-dev:plan
description: "Plan Ren'Py feature development. Use when asked to 'design a feature', 'plan development', 'create architecture'. Analyzes requirements, produces design documents only — NEVER writes implementation code."
---

# Ren'Py AI 开发 — 设计阶段

分析 Ren'Py 开发需求，生成完整设计文档。**铁律：只做分析和规划并输出文档，不写实现代码。**

**文档查询：** 需要 Ren'Py API 语法、属性和最佳实践时，读 `plugins/renpy-dev/references/renpy-docs.md` 获取约定，用 `WebFetch` 查 `https://www.renpy.org/doc/html/`。

---

## 工作流

### 1. 创建任务目录

确定下一个可用的序号 N，创建目录：

```bash
mkdir -p .renpy-dev/feat-{N}/.work
```

### 2. 读取影响范围约束（仅 refactor）

如果 `{task_dir}/impact.md` 存在（refactor-conductor 写入），读取它。按 `plugins/renpy-dev/references/impact-format.md` 格式解析，其中的修改范围、排除范围、已有测试、风险点、特殊约束是 plan 的硬约束。

### 3. 加载格式契约

读取 `plugins/renpy-dev/references/plan-format.md`。所有输出必须遵守此格式规范，exec skill 依赖此格式解析。

### 3. 检测项目环境

**Ren'Py 版本检测：**

```bash
# 检查 game/ 目录下的 .rpy 文件
ls game/*.rpy 2>/dev/null | head -10
# 检查 options.rpy 中的版本注释
grep -i "renpy" game/options.rpy 2>/dev/null | head -3
```

**项目结构检测：**

```bash
# 检查 OWN_MANIFEST.json 是否存在
ls game/tests/OWN_MANIFEST.json 2>/dev/null
# 检查 tools/test.py 是否存在
ls tools/test.py 2>/dev/null
```

### 4. 收集需求

解析用户的任务描述，生成需求摘要。保存到 `.renpy-dev/feat-{N}/.work/requirements.md`：

```markdown
# 需求摘要

## 功能
{用户描述的功能目标}

## 涉及范围
- Screen: {列出涉及的 screen}
- Label: {列出涉及的 label}
- 新建文件: {列出需要新建的 .rpy 文件}
- 修改文件: {列出需要修改的现有文件}

## 技术栈
- Ren'Py 版本: {检测到的版本}
- 测试: tools/test.py (structure + behavior + visual)
```

### 5. 架构设计

调用 `Skill` 工具加载 `superpowers:brainstorming`，分析架构设计问题：

- 总体结构（Screen/Transform/Style 如何组织）
- Screen 划分（哪些 screen、如何跳转）
- 数据流（label 间传递什么数据、持久化什么数据）
- Screen 间交互约定

生成 Mermaid 架构图。保存到 `.renpy-dev/feat-{N}/.work/architecture.md`：

```markdown
# 架构设计

## 总体结构
[Mermaid 流程图：screen 跳转和 label 调用关系]

## Screen 划分
| Screen | 职责 | 关键 widget |
|--------|------|-----------|
| xxx_screen | ... | button_start (id) |

## 数据流
- Label A → Label B: 传递 {data}
- Screen X 读取: {persistent.xxx}

## 交互约定
- Screen A → Screen B: call screen / jump
- Event 触发: action Function(...)
```

### 6. 详细设计

继续使用 `superpowers:brainstorming` 分析：

- 关键 Screen 的 widget 树结构
- 复杂交互逻辑（含 Mermaid 流程图）
- Transform/transition 设计
- 持久化数据设计（persistent / save）

保存到 `.renpy-dev/feat-{N}/.work/design.md`：

```markdown
# 详细设计

## Screen 详细设计

### {screen_name}
- Widget 树: {hbox/vbox/fixed 结构}
- 关键 widget id: {列表}

## 交互流程
[Mermaid 流程图：用户操作的完整流程]

## Transform 设计
```renpy
transform xxx:
    # ...
```

## 持久化数据
| 变量 | 类型 | 默认值 | 用途 |
|------|------|--------|------|
| persistent.xxx | bool | False | ... |
```

### 7. 执行计划

调用 `Skill` 工具加载 `superpowers:writing-plans`，基于设计文档生成**自包含的 plan.md**（关键决策提炼进去，不引用 .work/ 文件）。

如果在 step 2 读取了 impact.md，plan.md 必须在修改范围、排除范围、已有测试保护、风险应对上遵守 impact.md 的约束。

**传递给 writing-plans 的约束：**
- 每个 AI 任务必须有 `[AI-N]` 编号 + 输出文件路径 + 依赖标注
- 测试任务必须标注对应的测试层（structure/behavior/visual）
- `[HUMAN]` 任务标注具体操作步骤
- 按 `plugins/renpy-dev/references/plan-format.md` 格式输出
- 测试策略段标明每个任务覆盖哪层测试

保存到 `.renpy-dev/feat-{N}/plan.md`。

**任务拆分原则：**
- 先建数据/配置，再建 screen，最后写跳转逻辑
- 每个 `[AI-N]` 有对应的测试任务
- 测试任务依赖实现任务（先有 screen 才能测 screen）

示例：
```markdown
- `[AI-1]` 创建 CharacterData 持久化变量 → `game/character_data.rpy`
- `[AI-2]` 创建 CharacterSelectScreen → `game/character_select.rpy` (依赖: AI-1)
- `[AI-3]` 创建 CharacterSelect behavior 测试 → `game/tests/test_character_select.rpy` (依赖: AI-2)
- `[AI-4]` 创建 CharacterSelect visual 测试 → `game/tests/test_character_select.rpy` (依赖: AI-2)
- `[HUMAN]` 为 CharacterSelectScreen 的按钮添加 id 属性
```

### 8. 格式自检

输出前对照 `plan-format.md` 的"格式校验清单"逐项确认。

### 9. 输出摘要

```
## Plan: {feature-name}

**审查文件：** .renpy-dev/feat-{N}/plan.md
**中间产物：** .renpy-dev/feat-{N}/.work/

**AI 任务：** N 个
**人工任务：** N 个
**测试覆盖：** structure / behavior / visual

---
人类审查 plan.md 通过后进入 exec。
exec 只读 plan.md，不读 .work/。
```

---

## Completion Gate

永远不要声称任务完成，除非：

1. 执行了工作流的所有步骤
2. 中间产物已写入 `.renpy-dev/feat-{N}/.work/`，plan.md 已写入 `.renpy-dev/feat-{N}/`
3. plan.md 通过格式校验清单所有项目
4. 输出了所有文档路径供人类确认
