---
name: renpy-dev:plan
description: "Plan Ren'Py feature development. Use when asked to 'design a feature', 'plan development', 'create architecture'. Analyzes requirements, produces design documents only — NEVER writes implementation code."
---

# Ren'Py AI 开发 — 设计阶段

分析 Ren'Py 开发需求，生成完整设计文档。**铁律：只做分析和规划并输出文档，不写实现代码。**

**文档查询：** 需要 Ren'Py API 语法、属性和最佳实践时，读 `plugins/renpy-dev/references/renpy-docs.md` 获取约定，用 `WebFetch` 查 `https://www.renpy.org/doc/html/`。

---

## 工作流

### 1. 确定任务目录

`task_dir` 由调用者（conductor）传入。如果未传入，从 `.renpy-dev/current-state.json` 读取 `current_task`。

`kind` 从 `task_dir` 路径推断：`.renpy-dev/feat-1` → `kind=feat`。

确保 `.work/` 子目录存在：

```bash
mkdir -p {task_dir}/.work
```

### 2. 读取影响范围约束（仅 refactor）

如果 `{task_dir}/impact.md` 存在（refactor-conductor 写入），读取它。按 `plugins/renpy-dev/references/impact-format.md` 格式解析，其中的修改范围、排除范围、已有测试、风险点、特殊约束是 plan 的硬约束。

### 3. 加载格式契约

读取 `plugins/renpy-dev/references/plan-format.md`。所有输出必须遵守此格式规范，exec skill 依赖此格式解析。

### 4. 检测项目环境

**Ren'Py 版本检测：**

```bash
# 检查 game/ 目录下的 .rpy 文件
ls game/*.rpy 2>/dev/null | head -10
# 检查 options.rpy 中的版本注释
grep -i "renpy" game/options.rpy 2>/dev/null | head -3
```

**测试基础设施检测与决策：**

```bash
# 检查 OWN_MANIFEST.json 是否存在
ls game/tests/OWN_MANIFEST.json 2>/dev/null && echo "MANIFEST_OK" || echo "MANIFEST_MISSING"
# 检查 tools/test.py 是否存在
ls tools/test.py 2>/dev/null && echo "TEST_RUNNER_OK" || echo "TEST_RUNNER_MISSING"
```

**检测后的强制分支：**

| 检测结果 | 强制行为 |
|---------|---------|
| 测试基础设施完整（MANIFEST_OK + TEST_RUNNER_OK） | 所有验证使用 `python tools/test.py`（structure/behavior/visual） |
| 测试基础设施缺失 | **必须**在任务列表最前面添加 `[AI-0]` bootstrap 任务：从 `plugins/renpy-dev/assets/test-infra/` 复制到项目根目录，编辑 `OWN_MANIFEST.json`，运行 `python tools/test.py scaffold` |

**铁律：绝不使用"人工启动目视"作为验证手段。** Ren'Py 项目支持全自动化三层测试（structure/behavior/visual），所有 feature 都可以自动化验证。如果测试基础设施缺失，第一个 AI 任务就是安装它。

### 5. 收集需求

解析用户的任务描述，生成需求摘要。保存到 `{task_dir}/.work/requirements.md`：

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

## 测试基础设施
- 状态: {已就绪 / 需安装 — 见 [AI-0] bootstrap 任务}
```

### 6. 架构设计

调用 `Skill` 工具加载 `superpowers:brainstorming`，分析架构设计问题：

- 总体结构（Screen/Transform/Style 如何组织）
- Screen 划分（哪些 screen、如何跳转）
- 数据流（label 间传递什么数据、持久化什么数据）
- Screen 间交互约定

生成 Mermaid 架构图。保存到 `{task_dir}/.work/architecture.md`：

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

### 7. 详细设计

继续使用 `superpowers:brainstorming` 分析：

- 关键 Screen 的 widget 树结构
- 复杂交互逻辑（含 Mermaid 流程图）
- Transform/transition 设计
- 持久化数据设计（persistent / save）

保存到 `{task_dir}/.work/design.md`：

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

### 8. 执行计划

调用 `Skill` 工具加载 `superpowers:writing-plans`，基于设计文档生成**自包含的 plan.md**（关键决策提炼进去，不引用 .work/ 文件）。

如果在 step 2 读取了 impact.md，plan.md 必须在修改范围、排除范围、已有测试保护、风险应对上遵守 impact.md 的约束。

**传递给 writing-plans 的约束：**
- 每个 AI 任务必须有 `[AI-N]` 编号 + 输出文件路径 + 依赖标注
- 测试任务必须标注对应的测试层（structure/behavior/visual）
- `[HUMAN]` 任务标注具体操作步骤
- 按 `plugins/renpy-dev/references/plan-format.md` 格式输出
- **测试策略只声明测什么文件、覆盖什么功能**：不需要写 screen 名、变量名、断言规格。test agent 自己读 `.work/design.md` 获取这些细节

保存到 `{task_dir}/plan.md`。

**任务拆分原则：**
- 先建数据/配置，再建 screen，最后写跳转逻辑
- 每个 `[AI-N]` 有对应的测试任务
- 测试任务依赖实现任务（先有 screen 才能测 screen）

示例：
```markdown
- `[AI-0]` 安装测试基础设施（如缺失） → 从 plugins/renpy-dev/assets/test-infra/ 复制，编辑 OWN_MANIFEST.json
- `[AI-1]` 创建 CharacterData 持久化变量 → `game/character_data.rpy`
- `[AI-2]` 创建 CharacterSelectScreen → `game/character_select.rpy` (依赖: AI-1)
- `[AI-3]` 创建 CharacterSelect behavior 测试 → `game/tests/test_character_select.rpy` (依赖: AI-2)
- `[AI-4]` 创建 CharacterSelect visual 测试 → `game/tests/test_character_select.rpy` (依赖: AI-2)
- `[HUMAN]` 为 CharacterSelectScreen 的按钮添加 id 属性（coding agent 应在实现时自动添加 id，此为最终确认）
```

**验证手段始终为 `python tools/test.py`（structure + behavior + visual），绝不使用"人工启动目视"。**

### 9. 格式自检

输出前对照 `plan-format.md` 的"格式校验清单"逐项确认。

### 10. 输出摘要

```
## Plan: {feature-name}

**审查文件：** {task_dir}/plan.md
**中间产物：** {task_dir}/.work/

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
2. 中间产物已写入 `{task_dir}/.work/`，plan.md 已写入 `{task_dir}/`
3. plan.md 通过格式校验清单所有项目
4. 输出了所有文档路径供人类确认
