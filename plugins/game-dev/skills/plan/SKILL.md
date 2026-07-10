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

### 3. 加载必须文件
**格式契约**
读取 `${CLAUDE_PLUGIN_ROOT}/references/plan-format.md`。所有输出必须遵守此格式规范，exec skill 依赖此格式解析。
读取 `${CLAUDE_PLUGIN_ROOT}/references/visual-spec-format.md`。该文件定义了 visual-spec JSON 的完整结构——plan 在步骤 8 产出 visual-spec 时遵循此格式。

**技术栈上下文**
- 读取`${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md`
- 读取`${CLAUDE_PLUGIN_ROOT}/references/{tech}/docs.md`

**视觉设计稿**
- 读取`{task_dir}/.work/style-decision`。这是视觉的精确风格决策。文件不存在必须明确输出使用的查找命令和结果,确实是空才能证明不存在
- 读取`{task_dir}/.work/layouts`目录下的html格式文件。这些是视觉相关的html设计稿。文件不存在必须明确输出使用的查找命令和结果,文件夹不存在或者文件夹下是空才能证明不存在。

**项目架构文档**
- 读取`{dev_dir}/architecture.md`（如果存在）。提取当前任务涉及的子系统章节——任务涉及哪些文件/目录就对应该子系统。
- 将这些章节中的领域模型、引擎映射和关键约定作为**架构约束**引入设计。新功能设计应当遵循已有架构决策，不重新发明。
- 文件不存在则跳过，输出提示："项目架构文档尚未创建，跳过架构约束加载。"


### 4. 收集需求并确认行为

解析用户的任务描述，生成需求摘要。保存到 `{task_dir}/.work/requirements.md`：

```markdown
# 需求摘要

## 功能
{用户描述的功能目标}

## 涉及范围
- 涉及界面: {列出涉及的界面/场景}
- 涉及流程: {列出涉及的流程/跳转}
- 新增能力: {列出新增的功能能力}
- 影响现有: {列出受影响的现有功能}

## 技术栈
- 技术栈版本: {检测到的版本}
```

**确认行为清单（强制门）：** 在进入任务拆分之前，从需求中提取**玩家可见的行为列表**，向用户确认：

```
## 确认以下行为是否准确

这些是玩家能看到和操作的，每条对应一个 testcase：

1. 玩家进入主菜单 → 看到角色选择界面（截图基线）
2. 玩家点击第 2 个角色卡片 → 卡片视觉高亮
3. 玩家选中角色后点击"确认" → 跳转到游戏开始
4. 玩家未选中角色点击"确认" → 停留在当前界面，无事发生
5. ...

是否有遗漏或不需要的行为？
```

**为什么这样做：** 确认行为比确认设计文档更精确。设计文档描述的是方案（界面结构、组件树），行为描述的是需求（玩家看到什么、做什么、结果是什么）。方案可以有多种，行为只有一种。test-agent 和 coding-agent 都以行为为基准——测试断言行为，实现产出行。

用户确认后，保存行为清单到 `{task_dir}/.work/requirements.md`。

### 5. 领域设计

**在进入引擎落地之前，先做领域建模。** 这一步回答"这个功能在游戏开发中本质上是什么？业界公认的好做法是什么？"——用引擎无关的语言讲清楚，不涉及任何 Screen/Label/Node/GDScript。

**为什么这样做：**
- 领域设计让你先想清楚"做什么"，再决定"怎么写"——顺序不能反
- 引擎 API 不会提醒你漏了边界情况，但领域模型会——状态机少了一个 transition、资源管理少了回滚策略，在领域层就能发现
- 领域模型是评判后续架构设计质量的标尺——没有它，架构设计没有参照基准

**必须阅读文件**
{task_dir}/.work/requirements.md

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
- 边界情况清单
- 如果某个功能的领域模式很明显（如"显示一个按钮"→ 无复杂领域逻辑），简写即可，不需要强行拔高

### 6. 任务拆分与排序

**拆分原则：按功能模块拆分，不按文件/阶段拆分。**

核心规则：**任务描述 = 可验证的功能行为，不含文件路径。** "可验证"意味着读完描述能回答"用户操作后应该看到什么/发生什么？"——如果答案需要看另一个任务才知道，就合到一起。如果你发现自己在写"修改 xxx"或"在 xxx 中创建..."，停下来，用功能语言重写。**如果你发现自己在写 class 名、方法名、函数签名——停下来，你是在描述实现方案，不是描述行为。**

一个 AI 任务 = 一个可独立验证的功能模块。同一文件被多个 AI 任务修改是正常的——每个模块增量修改。

**好/坏对照（关键——写任务前先读这个）：**

```
❌ 坏: "创建角色选择界面文件，定义 CharacterSelect 类"
     → 问题：描述了文件操作和代码结构，不是功能。无法知道这个界面要做什么。

❌ 坏: "在脚本文件中添加 select_character 入口函数"
     → 问题：同上。入口函数是手段，跳转行为才是目的。

❌ 坏: "QteController 状态对象 + 状态常量定义（class QteController + class QtePhase）"
     → 问题：描述的是代码结构（class 名、方法名），不是玩家可感知的行为。

❌ 坏: "5 个动画效果定义（fly_in / pulse / hit / miss / label_anim）"
     → 问题：描述的是实现手段（动画列表），不是行为结果。

✅ 好: "实现角色卡片列表：头像、名称、状态标签的组件排列和默认布局"
     → 可验证：打开界面后能看到排列整齐的卡片列表

✅ 好: "实现角色选中交互：点击卡片高亮、再次点击取消、选中状态更新"
     → 可验证：点击卡片后卡片高亮，再次点击后取消高亮

✅ 好: "实现确认跳转逻辑：有选中角色 → 跳转游戏开始，无选中 → 停留当前界面"
     → 可验证：选中后确认能跳转，未选中时确认不跳转

✅ 好: "实现商店物品数据层：物品列表定义、价格查询、库存增减接口"
     → 可验证：能查询到物品价格，购买后库存减少

✅ 好: "实现按键命中反馈：玩家按正确键 → 金色粒子爆散 + HIT 文字 + 对应标记变绿"
     → 可验证：按正确键后看到金色粒子、HIT 文字、对应标记变绿

✅ 好: "实现按键失败反馈：玩家按错键 → 红色粒子 + MISS 文字 + 界面关闭"
     → 可验证：按错键后看到红色粒子、MISS 文字、界面关闭

✅ 好: "实现敌人血条显示：血条跟随敌人位置、长度随血量比例变化、颜色按比例渐变(绿→黄→红)、死亡后隐藏"
     → visual 任务，可验证：受击后血条缩短变色，死亡后消失

✅ 好: "实现角色卡片默认布局：头像、名称、状态标签的水平排列和间距"
     → visual 任务，可验证：打开界面看到排列整齐的卡片

❌ 坏: "实现敌人血条显示 + 受击扣血逻辑"
     → 问题：visual 和 logic 混在一起。应拆为 logic（血量数据层）和 visual（血条显示）
```

**描述写作规则：**

| 规则 | 说明 |
|------|------|
| 用行为语言 | 描述"用户做什么 → 看到什么/发生什么"，不用技术名词（"创建 class"、"定义动画"、"创建界面类"）开头 |
| 可独立验证 | 读完描述能回答"怎么确认这个任务做完了？"——如果答案需要看另一个任务，就合到一起 |
| 不含文件路径 | 文件名不出现在描述中。同一个文件被多个任务修改是正常的 |
| 不含代码符号 | class 名、方法名、函数名、动画名不出现在描述中——那些是实现方案，不是行为 |
| 不含"测试" | 没有"编写/更新测试"任务——测试在各模块的 TDD 循环中自然产出 |
| 类型标注 | 每个任务必须标注类型——logic / visual / ui。visual 标注 spec:，ui 标注 html: |

任务列表将在步骤 9 写入 plan.md，届时按以下规则分类和排序：

**分类判定流程（对行为清单逐条判定）：**

```
1. 该行为有玩家不可见的计算/状态/数据部分？
   → 拆为 logic 任务

2. 该行为有玩家可见的新内容或更改？
   → 拆为 visual 任务（必然——任何视觉产出都有 visual 任务）
   → 检查 {task_dir}/.work/layouts/ 是否有对应 HTML 设计稿
      → 有 → 追加 ui 任务（在 visual 基础上做像素级精调）,ui回归任务以设计稿为维度,一个设计稿一个
```

判定辅助——行为描述中的信号词：

| 指向 logic | 指向 visual |
|------------|-------------|
| 计算、判定、存储、传递、转换、校验 | 显示、看到、出现、消失、动画播放 |
| 状态切换、条件判断、数据读写 | 粒子、颜色变化、位置移动、大小变化 |
| 触发、通知、广播 | 跟随、排列、遮挡、层级 |

**分类定义：**

| 类型 | 含义 | 关系 |
|------|------|------|
| `logic` | 行为/交互/数据逻辑——完成标准来自行为清单 | 地基 |
| `visual` | 视觉行为实现——完成标准来自 visual-spec JSON，必须标注 `spec:` | 视觉 | 
| `ui` | 视觉还原——完成标准来自 HTML 设计稿，必须标注 `html:` | 精装 |

`logic` → `visual` → `ui`。同一界面元素可同时有 visual 和 ui 两个任务。`visual` 是必然层——只要有玩家可见的新内容或更改，就有 visual 任务。`ui` 是条件层——只有存在 HTML 设计稿时才追加。

**排序：** `logic` → `visual` → `ui`。`visual` 任务依赖同界面的最后一个 `logic` 任务（如 logic 存在）。`ui` 任务依赖由 plan 根据实际情况决定——visual 可能已存在，ui 直接在已有视觉上做还原。

**visual 任务标记：** 编写 plan.md 时，`visual` 任务必须标注对应的 spec 文件：`(type: visual, spec: .work/visual-specs/{name}.json)`
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
[Mermaid 流程图：界面跳转和流程调用关系]

## 界面/场景划分
| 界面 | 职责 | 关键组件 |
|--------|------|-----------|
| xxx_界面 | ... | button_start (id) |

## 数据流
- 流程节点 A → 流程节点 B: 传递 {data}
- 界面 X 读取: {数据来源}

## 交互约定
- 界面 A → 界面 B: 跳转方式
- 事件触发: {处理方式}
```

### 8. 详细设计

**以领域模型为骨架，逐个功能行为展开引擎层实施方案。**

调用 `superpowers:brainstorming`，但对每个功能行为按以下流程驱动：

对 `{task_dir}/.work/domain-design.md` 的每个功能行为：

1. **确认领域模式** — 这是什么模式？（状态机 / 资源管理 / 事件队列 / 空间查询 / ...）
2. **确认架构映射** — 对照 `{task_dir}/.work/architecture.md`，这个模式映射到了哪个引擎构造？
3. **展开实现方案（主体）** — 这个模式在引擎里具体怎么搭：
   - 需要哪些数据结构/变量/配置？
   - 转换/流转逻辑怎么组织？
   - 关键时序和生命周期？
4. **过边界清单** — domain-design.md 中该行为的边界情况清单，逐条确认实现方案覆盖了每一条边界
5. **API/属性/最佳实践不确定时** — 读引擎参考文档查。这是字典，不是驱动

**引擎参考文档的角色：字典，不是主导。** 领域模型驱动结构，架构映射提供框架，引擎文档填充技术细节：

- `${CLAUDE_PLUGIN_ROOT}/references/{tech}/design.md` — 详细设计指引
- `${CLAUDE_PLUGIN_ROOT}/references/{tech}/nodes-{2d,3d}.md`（仅 Godot）— 节点类型速查

**资源需求：展开过程中自然识别需要新生成的资源。** 记入 `{task_dir}/.work/resources.md`：

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

**visual-spec 产出：** 对每个 visual 任务，生成对应的 visual-spec JSON 文件。格式遵循 `${CLAUDE_PLUGIN_ROOT}/references/visual-spec-format.md`。

```bash
mkdir -p {task_dir}/.work/visual-specs
```

对每个 visual 任务涉及的界面/场景，生成一个 spec JSON：

```
{task_dir}/.work/visual-specs/{name}.json
```

spec 描述该 visual 任务中**玩家应该看到什么**——元素的位置、大小、颜色、布局关系。用粗粒度自然语言，不做像素精度。像素精度是 ui 任务的职责。

每个 visual 任务对应一个 spec JSON。如果一个界面有多个 visual 任务，分别生成各自的 spec（每个任务关注不同的视觉行为）。

保存到 `{task_dir}/.work/design.md`。

### 8b. 加载 UI 视觉标准（如有）

**检查 `{task_dir}/.work/layouts/` 是否存在 HTML 文件。**

如果有：读取 `style-decision.md` + HTML 文件，纳入详细设计的视觉参考。对应 visual 任务之后追加 ui 任务做像素级精调。

如果没有 HTML 但涉及新画面视觉布局 → 正常——visual 任务通过 visual-spec JSON 定义视觉标准，无需 HTML 设计稿。纯逻辑功能且无视觉产出 → 跳过此步。

### 9. 编写 plan.md

**自己编写，不委托外部 skill。** 外部 skill 不知道 `[AI-N]` 任务格式和测试策略表约定，会产生偏离。

基于 `.work/` 下的设计文档（requirements.md / domain-design.md / architecture.md / design.md）编写。

**模板和格式约束：** 以 `${CLAUDE_PLUGIN_ROOT}/references/plan-format.md` 为唯一权威来源。其中的 plan.md 模板定义了完整结构（概述→领域模型→行为列表→设计摘要→影响范围→任务列表→资源需求→测试策略），格式校验清单和禁止内容清单定义了输出门禁。

plan 在此基础之上额外检查：

```bash
# 检查所有 visual 任务都有 spec: 标注（plan 专属，plan-fix 不需要）
grep -n '(type: visual' {task_dir}/plan.md | grep -v 'spec:'

# 检查所有 UI 任务都有 html: 标注（plan 专属，plan-fix 不需要）
grep -n '(type: ui' {task_dir}/plan.md | grep -v 'html:'
```

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
