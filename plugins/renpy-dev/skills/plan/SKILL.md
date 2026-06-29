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

### 2. 读取模式约束

根据 `kind` 读取对应的约束文件。三个 mode 互斥——只有一个约束文件会存在：

| kind | 约束文件 | 来源 | 提取内容 |
|------|---------|------|---------|
| feat | （无） | — | 无预约束，走完整 brainstorming 流程 |
| refactor | `{task_dir}/impact.md` | refactor-conductor | 修改范围、排除范围、已有测试保护、风险点 |

**refactor 约束：** 按 `plugins/renpy-dev/references/impact-format.md` 格式解析 impact.md，其中的修改范围、排除范围、已有测试、风险点、特殊约束是 plan 的硬约束。

### 3. 加载格式契约 + 检测项目环境

读取 `plugins/renpy-dev/references/plan-format.md`。所有输出必须遵守此格式规范，exec skill 依赖此格式解析。

同时检测项目环境：

**Ren'Py 版本检测：**

**Ren'Py 版本检测：**

```bash
# 检查 game/ 目录下的 .rpy 文件
ls game/*.rpy 2>/dev/null | head -10
# 检查 options.rpy 中的版本注释
grep -i "renpy" game/options.rpy 2>/dev/null | head -3
```

**测试基础设施检测：**

```bash
# 检查 RENPY_SDK 环境变量
echo $RENPY_SDK && test -x "$RENPY_SDK" && echo "SDK_OK" || echo "SDK_MISSING"
# 检查 game/tests/ 目录
ls game/tests/ 2>/dev/null && echo "TESTS_OK" || echo "TESTS_MISSING"
```

**检测后的强制行为：**

| 检测结果 | 强制行为 |
|---------|---------|
| SDK_OK + TESTS_OK + EXIT_OK | 测试文件写入 `game/tests/`，验证使用 `renpy.sh project test` |
| SDK_MISSING | **阻断** — `RENPY_SDK` 环境变量必须指向可执行的 Ren'Py SDK |
| TESTS_MISSING | **必须**在任务列表最前面添加 `[AI-0]` bootstrap 任务：创建 `game/tests/` 目录和 `__init__.py`，写入 `testsuite global: teardown: exit` |
| EXIT_MISSING | **必须**在任务列表最前面添加 `[AI-0.1]` 修复任务：在 `game/tests/` 中确保 `testsuite global: teardown: exit` 存在。缺失则写入 |

**EXIT_OK 检测方式：**
```bash
grep -rl "teardown:" game/tests/ 2>/dev/null | xargs grep -l "exit" 2>/dev/null && echo "EXIT_OK" || echo "EXIT_MISSING"
```

**为什么这很重要：** Ren'Py 测试跑完后不会自动退出进程。没有 `teardown: exit` 会导致 `renpy test` 进程永久挂起、bash 后台任务永远不返回、整个 TDD 循环卡死。

### 4. 收集需求并确认行为

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
- 测试: renpy.sh project test

## 测试基础设施
- 状态: {已就绪 / 需安装 — 见 [AI-0] bootstrap 任务}
```

**确认行为清单（强制门）：** 在进入任务拆分之前，从需求中提取**玩家可见的行为列表**，向用户确认：

```
## 确认以下行为是否准确

这些是玩家能看到和操作的，每条对应一个 testcase：

1. 玩家进入主菜单 → 看到 character_select screen（截图基线）
2. 玩家点击第 2 个角色卡片 → 卡片视觉高亮
3. 玩家选中角色后点击"确认" → 跳转到 start_game
4. 玩家未选中角色点击"确认" → 停留在当前 screen，无事发生
5. ...

是否有遗漏或不需要的行为？
```

**为什么这样做：** 确认行为比确认设计文档更精确。设计文档描述的是方案（screen 结构、widget 树），行为描述的是需求（玩家看到什么、做什么、结果是什么）。方案可以有多种，行为只有一种。test-agent 和 coding-agent 都以行为为基准——测试断言行为，实现产出行。

用户确认后，保存行为清单到 `{task_dir}/.work/requirements.md`。

### 5. 任务拆分与排序

**拆分原则：按功能模块拆分，不按文件/阶段拆分。**

核心规则：**任务描述 = 可验证的功能行为，不含文件路径。** "可验证"意味着读完描述能回答"用户操作后应该看到什么/发生什么？"——如果答案需要看另一个任务才知道，就合到一起。如果你发现自己在写"修改 xxx.rpy"或"在 xxx.rpy 中创建..."，停下来，用功能语言重写。**如果你发现自己在写 class 名、方法名、函数签名——停下来，你是在描述实现方案，不是描述行为。**

一个 AI 任务 = 一个可独立验证的功能模块。同一文件被多个 AI 任务修改是正常的——每个模块增量修改。

**好/坏对照（关键——写任务前先读这个）：**

```
❌ 坏: "创建 game/character_select.rpy，定义 character_select screen"
     → 问题：描述了文件操作，不是功能。无法知道这个 screen 要做什么。

❌ 坏: "修改 game/script.rpy，添加 select_character label"
     → 问题：同上。label 是手段，跳转行为才是目的。

❌ 坏: "在 game/screens.rpy 中新增 shop_screen"
     → 问题：文件路径+screen名，没有功能语义。

❌ 坏: "QteController 状态对象 + 状态常量定义（class QteController + class QtePhase）"
     → 问题：描述的是代码结构（class 名、方法名），不是玩家可感知的行为。

❌ 坏: "5 个 ATL transforms 定义（qte_fly_in / qte_pulse / qte_hit / qte_miss / qte_label_anim）"
     → 问题：描述的是实现手段（transform 列表），不是行为结果。

✅ 好: "实现角色卡片列表：头像、名称、状态标签的 widget 排列和默认布局"
     → 可验证：打开 screen 后能看到排列整齐的卡片列表

✅ 好: "实现角色选中交互：点击卡片高亮、再次点击取消、选中状态更新"
     → 可验证：点击卡片后卡片高亮，再次点击后取消高亮

✅ 好: "实现确认跳转逻辑：有选中角色 → 跳转 start_game，无选中 → 停留当前 screen"
     → 可验证：选中后确认能跳转，未选中时确认不跳转

✅ 好: "实现商店物品数据层：物品列表定义、价格查询、库存增减接口"
     → 可验证：能查询到物品价格，购买后库存减少

✅ 好: "实现按键命中反馈：玩家按正确键 → 金色粒子爆散 + HIT 文字 + legend dot 变绿"
     → 可验证：按正确键后看到金色粒子、HIT 文字、对应 dot 变绿

✅ 好: "实现按键失败反馈：玩家按错键 → 红色粒子 + MISS 文字 + Return(False)"
     → 可验证：按错键后看到红色粒子、MISS 文字、screen 关闭返回 False
```

**描述写作规则：**

| 规则 | 说明 |
|------|------|
| 用行为语言 | 描述"用户做什么 → 看到什么/发生什么"，不用技术名词（"创建 class"、"定义 transform"、"创建 screen"）开头 |
| 可独立验证 | 读完描述能回答"怎么确认这个任务做完了？"——如果答案需要看另一个任务，就合到一起 |
| 不含文件路径 | `.rpy` 文件名不出现在描述中。同一个 rpy 文件被 3 个任务改是正常的 |
| 不含代码符号 | class 名、方法名、函数名、transform 名不出现在描述中——那些是实现方案，不是行为 |
| 不含"测试" | 没有"编写/更新测试"任务——测试在各模块的 TDD 循环中自然产出 |

任务列表将在步骤 8 写入 plan.md，届时按以下规则分类和排序：

**分类定义：**

| 类型 | 含义 |
|------|------|
| `logic` | 行为/交互/数据逻辑——完成标准来自行为清单，不依赖 HTML 设计稿 |
| `ui` | 视觉还原——完成标准来自 HTML 设计稿，必须标注 `html:` |

**排序：** 所有 `logic` 任务排在 `ui` 任务前面。`ui` 任务依赖同 screen 的最后一个 `logic` 任务。

**UI 任务标记：** 编写 plan.md 时，`ui` 任务必须标注对应的 HTML 文件：`(type: ui, html: .work/layouts/{name}.html)`

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

### 6b. UI 设计稿（按需）

分析用户需求，判断是否涉及 UI 视觉设计：

- 是否产生了新画面/新 widget？
- 用户明确要求出 HTML 设计稿？

以上任一为真 → 调用 design-ui：

```
Skill({skill: "renpy-dev:design-ui", args: "--task-dir {task_dir}"})
```

design-ui 产出 HTML 设计稿到 `.work/layouts/`，确认后继续步骤 7。

不涉及 UI → 跳过，直接进入步骤 7。

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

### 7b. 产出 UI 标准文件（UI 功能必须）

**触发条件：** 需求涉及用户可见的视觉界面（新 screen 或 screen 视觉重设计）。纯逻辑功能（如 save/load、数据迁移、后端通信）跳过。

**粒度：** 一个逻辑屏幕一个 HTML 文件。例如 "角色选择画面" → 一个 HTML，"剧情对话画面" → 一个 HTML。

**HTML 内容要求：**

- 包含该逻辑屏幕的**所有交互状态**（默认态、hover、选中、禁用、过渡动画等）
- 使用 CSS 伪类（`:hover`、`:active`、`:disabled`）和过渡（`transition`）表达动态效果
- 单文件自包含（内联 CSS，浏览器可直接打开）
- 颜色、字体、间距、背景等视觉属性精确设置
- 与设计文档中的 widget 树一致

**步骤：**

**1. 生成 HTML**

为每个涉及视觉设计的逻辑屏幕生成 HTML，保存到 `{task_dir}/.work/layouts/`：

```
{task_dir}/.work/layouts/
├── character_select.html
├── dialogue.html
└── shop.html
```

**2. 用户确认**

```
## UI 标准确认

以下 HTML 文件定义了各画面的视觉标准，请用浏览器打开查看：

- character_select.html — 角色选择画面（含默认态、hover、选中态）
- dialogue.html — 剧情对话画面

这些文件将成为 coding-agent 的视觉真相 — 后续 Ren'Py 代码的布局/颜色/字体/间距以此为准。

确认后回复"OK"继续。如需调整，请描述具体改动。
```

**3. 确认后保存**

用户确认后，HTML 文件即为最终视觉标准，后续不可随意修改。

### 8. 编写 plan.md

**自己编写，不委托外部 skill。** 外部 skill 不知道 Ren'Py 测试铁律、`[AI-N]` 任务格式和测试策略表约定，会产生偏离。

基于 `.work/` 下的设计文档（requirements.md / architecture.md / design.md）编写。

**结构：**

```markdown
# Plan: {feature-name}

## 概述
{从 requirements.md + architecture.md 提炼：功能目标、项目环境、RENPY_SDK 状态、game/tests/ 状态}

## 设计摘要
{从 architecture.md + design.md 提炼关键决策 — screen 结构、数据流、关键交互}
{自包含，不写"详见 design.md"}

## 影响范围
| 类型 | 文件 | 操作 |
|------|------|------|
| ... | ... | ... |

## 任务列表

### [AI] 任务
- `[AI-N]` (type: logic) 描述 (依赖: ...)
- `[AI-N]` (type: ui, html: .work/layouts/xxx.html) 描述 (依赖: ...)

### [HUMAN] 任务
- `[HUMAN]` ...

## 测试策略
| 测试文件 | 覆盖 |
|---------|------|
| ... | behavior: ... |
```

**硬约束：**

- 如果在 step 2 读取了 impact.md，修改范围、排除范围、已有测试保护、风险应对必须遵守其约束
- 每个 `[AI-N]` 有唯一编号 + 类型标注 + 依赖标注
- `ui` 任务必须有 `html:` 标注对应的 HTML 标准文件
- 所有 `logic` 任务排在 `ui` 任务前面
- 测试在各功能模块的 TDD 循环中自然产出，不作为独立 AI 任务
- 先建数据/配置，再建 screen，最后写跳转逻辑

**测试策略"覆盖"列约束：**

"覆盖"列**只能**写高层次的玩家可感知功能简述，**不能**写验证技术手段。test agent 自己读 `.work/design.md` 获取细节来设计具体测试。

```
✅ 正确: "角色选择交互（选中/取消/确认）; visual: 默认布局基线"
✅ 正确: "数据层读写 + 状态机转换 + 按键捕获 + Return 值"
❌ 错误: "数据层：default 变量初始化、qte_phase 初始 'waiting'"
❌ 错误: "modal True 源码契约、zorder 200 源码契约、4 参数签名契约"
❌ 错误: "源码中查找 screen qte_screen(keys, hit_window, x, y): 声明"
```

规则：如果"覆盖"列里出现了"源码"、"正则"、"查找"、"契约"、"default"、"声明"、"变量初始化"，那就是在指挥 test agent 怎么测——这是越界。test agent 有完整的测试哲学（`agents/test-agent.md`），不需要 plan 告诉它用什么技术手段。

**禁止写入 plan.md 的内容：** 见 `plan-format.md` 的"禁止内容清单"节——禁止短语列表 + 全部 grep 自检命令。plan 在此基础之上额外检查：

```bash
# 检查所有 UI 任务都有 html: 标注（plan 专属，plan-fix 不需要）
grep -n '(type: ui' {task_dir}/plan.md | grep -v 'html:'
```

**验证手段始终且唯一为 `renpy.sh project test`。** 若 game/tests/ 目录缺失，`[AI-0]` bootstrap 任务是强制的，不是可选的。

### 9. 格式自检

输出前对照 `plan-format.md` 的"格式校验清单"逐项确认，然后执行"禁止内容清单"中的所有 grep 命令。全部零命中方可输出。

### 10. 输出摘要

```
## Plan: {feature-name}

**审查文件：** {task_dir}/plan.md
**中间产物：** {task_dir}/.work/

**AI 任务：** N 个
**人工任务：** N 个
**测试覆盖：** `renpy.sh project test`

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
