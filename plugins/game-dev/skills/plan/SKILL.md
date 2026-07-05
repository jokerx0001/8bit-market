---
name: game-dev:plan
description: "Plan game feature development. Use when asked to 'design a feature', 'plan development', 'create architecture'. Analyzes requirements, produces design documents only — NEVER writes implementation code."
---

# Game Dev AI 开发 — 设计阶段

分析游戏开发需求，生成完整设计文档。**铁律：只做分析和规划并输出文档，不写实现代码。**

**文档查询：** 需要技术栈 API 语法、属性和最佳实践时，读 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/docs.md` 获取约定，用 `WebFetch` 查 config.md 中的 docs_url。

---

## 工作流

### 1. 确定任务目录

`task_dir` 由调用者（conductor）传入。如果未传入，从 `{dev_dir}/current-state.json` 读取 `current_task`。

`kind` 从 `task_dir` 路径推断：`{dev_dir}/feat-1` → `kind=feat`。

确保 `.work/` 子目录存在：

```bash
mkdir -p {task_dir}/.work
```

### 2. 读取模式约束

**feat** — 无预约束，跳过。

**refactor** — 读取 `{task_dir}/impact.md`，提取修改范围、排除范围、已有测试、风险点、特殊约束。这些是后续设计的硬约束。

**fix** — 读取 `{task_dir}/.work/debug-analysis.md`，提取根因、预期行为。计划必须围绕根因修复设计，不得偏离。

### 3. 加载格式契约 + 技术栈上下文

读取 `${CLAUDE_PLUGIN_ROOT}/references/plan-format.md`。所有输出必须遵守此格式规范，exec skill 依赖此格式解析。

**读取技术栈上下文（一份文件，所有信息在此）：**

```
${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md
```

**检测测试基础设施：**

从 ${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md 提取 `test_runner`、`sdk_env_var`、`test_dir` 字段，执行对应的环境检测命令：

```bash
# 示例（具体命令从 ${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md 拼接）
echo ${SDK_ENV_VAR} && test -x "${SDK_ENV_VAR}" && echo "SDK_OK" || echo "SDK_MISSING"
ls {test_dir}/ 2>/dev/null && echo "TESTS_OK" || echo "TESTS_MISSING"
```

**检测后的强制行为：**

| 检测结果 | 强制行为 |
|---------|---------|
| SDK_OK + TESTS_OK | 测试文件写入 `{test_dir}/` |
| SDK_MISSING | **阻断** — 环境变量必须指向可执行的 SDK |
| TESTS_MISSING | **必须**在任务列表最前面添加 `[AI-0]` bootstrap 任务 |

**已知坑：** 从 ${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md 的 `known_pitfall` 字段读取。如 Ren'Py 的 `teardown: exit`、GUT 的 `-gexit`。这些硬门必须在 bootstrap 任务中处理。

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
- 技术栈版本: {检测到的版本}
- 测试: {test_runner} project test

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

### 5. 领域设计

**在进入引擎落地之前，先做领域建模。** 这一步回答"这个功能在游戏开发中本质上是什么？业界公认的好做法是什么？"——用引擎无关的语言讲清楚，不涉及任何 Screen/Label/Node/GDScript。

**为什么这样做：**
- 领域设计让你先想清楚"做什么"，再决定"怎么写"——顺序不能反
- 引擎 API 不会提醒你漏了边界情况，但领域模型会——状态机少了一个 transition、资源管理少了回滚策略，在领域层就能发现
- 领域模型是评判后续架构设计质量的标尺——没有它，架构设计没有参照基准

**对每个功能行为，分析三层：**

```
功能行为: "玩家按 R 键换弹，换弹期间不能射击"

领域分析:
  ├── 这是什么模式？ → 状态机（IDLE → RELOADING → READY）
  ├── 业界通用做法？ → 有限状态机 + Timer 驱动 + 事件通知
  └── 有哪些边界？   → 满弹时不换弹、换弹中切武器中断、空弹射击自动触发换弹
```

**输出 `{task_dir}/.work/domain-design.md`：**

```markdown
# 领域设计

## 领域模型识别

{对每个功能行为，识别背后的领域模式}

### {功能行为 1}

**这是什么模式：** {状态机 / 资源管理 / 事件队列 / 空间查询 / 命令模式 / ...}

**业界通用做法：**

{这个模式在游戏开发中一般怎么实现。讲清楚核心概念、状态/阶段、关键规则。}

以 reload 为例：
- 核心是有限状态机：IDLE → RELOADING → READY 三个状态
- 状态转换由事件驱动：玩家按 R 键、Timer 到期、切武器
- ammo 管理：`magazine_ammo` 和 `reserve_ammo` 两个变量，边界规则明确（满弹不换、空弹自动换、备弹不够只装部分）
- 中断策略：换弹中切武器 → 状态回 IDLE，不补充弹药

**边界情况清单：**

{这个模式常见的边界情况和处理方式。领域模型的价值就在这里——提前发现边界。}

| # | 边界情况 | 预期行为 |
|---|---------|---------|
| 1 | 满弹时按 R | 忽略，不进入 RELOADING |
| 2 | 备弹为 0 时按 R | 忽略，不进入 RELOADING |
| 3 | 换弹中再次按 R | 忽略（或：触发快速换弹，视设计而定） |
| 4 | 换弹中切武器 | 取消换弹，状态回 IDLE |
| 5 | 空弹时按射击键 | 自动触发换弹 |
| 6 | 备弹不足填满弹夹 | 只装可用数量（如弹夹 30 但备弹仅剩 5 → 装 5 发） |
```

**要求：**
- 每个功能行为都要做领域分析，不能跳过
- 领域描述中不出现引擎概念（不写 "Screen"、"Label"、"Node"、"Signal"、"@export"）
- 边界情况清单是重点——这是领域模型的核心价值
- 如果某个功能的领域模式很明显（如"显示一个按钮"→ 无复杂领域逻辑），简写即可，不需要强行拔高

### 6. 任务拆分与排序

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

任务列表将在步骤 9 写入 plan.md，届时按以下规则分类和排序：

**分类定义：**

| 类型 | 含义 |
|------|------|
| `logic` | 行为/交互/数据逻辑——完成标准来自行为清单，不依赖 HTML 设计稿 |
| `ui` | 视觉还原——完成标准来自 HTML 设计稿，必须标注 `html:` |

**排序：** 所有 `logic` 任务排在 `ui` 任务前面。`ui` 任务依赖同 screen 的最后一个 `logic` 任务。

**UI 任务标记：** 编写 plan.md 时，`ui` 任务必须标注对应的 HTML 文件：`(type: ui, html: .work/layouts/{name}.html)`

### 7. 架构设计

**输入：** 步骤 5 的 `{task_dir}/.work/domain-design.md`。架构设计的任务是把领域模型映射到引擎的 idiomatic 写法——不是从零设计，是**翻译**。

**读取引擎映射指引：** `${CLAUDE_PLUGIN_ROOT}/references/{tech}/patterns.md` 包含了该引擎的领域模式 → 引擎构造映射规则。映射时对照其中的规则，确保每个选择都是该引擎推荐的写法，不是"能跑就行"。

调用 `Skill` 工具加载 `superpowers:brainstorming`，基于领域模型做引擎层映射：

- 领域模型中的状态机 → 引擎中用什么表达？
- 领域模型中的数据流 → 引擎中用什么承载？
- 领域模型中的边界规则 → 引擎中在哪里校验？
- 总体结构：文件/模块如何组织以表达领域模型

**映射时对照 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/coding.md` 中的规则**，确保每个映射都是该引擎推荐的写法，不是"能跑就行"。

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

### 8. 详细设计

继续使用 `superpowers:brainstorming`。

**读 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/design.md`** 获取该引擎的详细设计指引。
**读 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/nodes-{2d,3d}.md`**（仅 Godot）获取节点类型速查。
**读 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/design-resources-{2d,3d}.md`**（如有）获取各资源类型的输出目录。

**从设计中提取所有需要新生成的美术资源引用，写入 `{task_dir}/.work/resources.md`：**

```markdown
# 资源需求清单

## 风格方向
{从 design-ui 的 style-decision.md 或 plan 架构设计中提取的整体美术风格描述}

## 资源列表

### {资源名称}
- **用途**: {使用场景}
- **类型**: {精灵/背景/UI素材/纹理/材质/模型}
- **尺寸**: {W}x{H}
- **格式**: {PNG/GLB/tres}
- **风格要求**: {具体视觉要求}
- **输出目录**: {从 ${CLAUDE_PLUGIN_ROOT}/references/{tech}/design-resources-{2d,3d}.md 获取}
```

同时将资源需求摘要写入 plan.md 的 `## 资源需求` 节，供 orchestrator 判断是否触发 design-resources。

保存到 `{task_dir}/.work/design.md`。

### 8b. 加载 UI 视觉标准（如有）

**检查 `{task_dir}/.work/layouts/` 是否存在 HTML 文件。**

如果有：读取 `style-decision.md` + HTML 文件，纳入详细设计的视觉参考。

如果没有但涉及新画面视觉布局 → 异常。纯逻辑功能 → 跳过。

### 9. 编写 plan.md

**自己编写，不委托外部 skill。** 外部 skill 不知道 `[AI-N]` 任务格式和测试策略表约定，会产生偏离。

基于 `.work/` 下的设计文档（requirements.md / domain-design.md / architecture.md / design.md）编写。

**结构：**

```markdown
# Plan: {feature-name}

## 概述
{从 requirements.md 提炼：功能目标、项目环境、{sdk_env_var} 状态、{test_dir}/ 状态}

## 领域模型
{从 domain-design.md 提炼每个功能行为的领域模式——让 exec 和 coding agent 知道"这个功能本质上是什么"。}

以 reload 为例：
- **模式**：有限状态机 IDLE → RELOADING → READY
- **核心规则**：满弹不换、空弹自动换、换弹中切武器中断
- **边界**：备弹不足时只装可用数、换弹中不能射击

## 设计摘要
{从 architecture.md + design.md 提炼：领域模型如何映射到引擎构造}
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

## 资源需求
{从 .work/resources.md 提取摘要，供 orchestrator 判断是否触发资源生成阶段}

| # | 资源名称 | 类型 | 尺寸 | 使用场景 |
|---|---------|------|------|---------|
| 1 | ... | ... | ... | ... |

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

**验证手段始终且唯一为 `{test_runner} project test`。** 若 {test_dir}/ 目录缺失，`[AI-0]` bootstrap 任务是强制的，不是可选的。

### 10. 格式自检

输出前对照 `plan-format.md` 的"格式校验清单"逐项确认，然后执行"禁止内容清单"中的所有 grep 命令。全部零命中方可输出。

### 11. 输出摘要

```
## Plan: {feature-name}

**审查文件：** {task_dir}/plan.md
**中间产物：** {task_dir}/.work/

**AI 任务：** N 个
**人工任务：** N 个
**测试覆盖：** `{test_runner} project test`

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
