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

**用户描述澄清 — 硬门：绝不自行创建文件。**

**Red Flag：** "grill-interview.md 不存在，我来整理一份" → **STOP。回到本表，按 kind 取对应替代来源。绝不自行创建文件。**

**用户原始输入 + Grill 输出**
- 读取 `{task_dir}/.work/user-prompt.md` — 用户原始输入（原语）。**分析其中是否有直接指示工作内容的技术决策或实现约束。** 有则纳入设计，完成用户明确要求的内容。过滤掉与当前 task 无关的内容。
- 读取 `{task_dir}/.work/grill-interview.md` — grill-with-docs 原始输出。**Grill 的目的是防止 AI 偏差**

**需求文档**
- 读取`{dev_dir}/requirements.md`(如果存在) 项目级需求文档,可以从整体理解这个项目
- 读取`{task_dir}/.work/requirements.md` 该文件是本次feat的需求文档, 是本次任务的主要功能。包含本次 feat 的新增行为清单和边界规则。其中的行为清单直接作为 plan.md 的"行为列表"输入。

**技术栈上下文**
- 读取`${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md`
- 读取`${CLAUDE_PLUGIN_ROOT}/references/{tech}/docs.md`

**项目架构文档**
- 读取`{dev_dir}/architecture.md`（如果存在）。提取当前任务涉及的子系统章节——任务涉及哪些文件/目录就对应该子系统。
- 将这些章节中的领域模型、引擎映射和关键约定作为**架构约束**引入设计。新功能设计应当遵循已有架构决策，不重新发明。
- 文件不存在则跳过，输出提示："项目架构文档尚未创建，跳过架构约束加载。"

**格式契约**
读取 `${CLAUDE_PLUGIN_ROOT}/references/plan-format.md`。所有输出必须遵守此格式规范，exec skill 依赖此格式解析。

**视觉设计稿**
- 读取`{task_dir}/.work/style-decision`。这是视觉的精确风格决策。文件不存在必须明确输出使用的查找命令和结果,确实是空才能证明不存在
- 读取`{task_dir}/.work/layouts`目录下的html格式文件。这些是视觉相关的html设计稿。文件不存在必须明确输出使用的查找命令和结果,文件夹不存在或者文件夹下是空才能证明不存在。

### 4. 提取并分类用户指示（强制门）

步骤 3 已读取 user-prompt.md 和 grill-interview.md。**此步骤不可跳过。** 从这两份文件中提取所有用户直接指示的内容，按后续设计阶段分类，显式输出。

#### 提取规则

- 逐条列出 user-prompt.md 和 grill-interview.md 中用户**明确指示**的内容
- 每条标注来源（user-prompt / grill-interview）
- 分类到以下目标阶段
- **不遗漏、不转化、不总结。** 用户说了什么就记什么

#### 输出格式（强制——必须显式输出以下表格）

```
## 用户指示提取

### 领域设计相关
用户直接指示的领域概念、业务规则、行为约束：
- {指示内容} [来源: user-prompt / grill]
- ...

### 架构设计相关
用户直接指示的技术映射、模块划分、引擎约束、文件组织：
- {指示内容} [来源: user-prompt / grill]
- ...

### 详细设计相关
用户直接指示的数据结构、算法、时序、生命周期：
- {指示内容} [来源: user-prompt / grill]
- ...

### 任务拆分相关
用户直接指示的优先级、依赖关系、实现顺序：
- {指示内容} [来源: user-prompt / grill]
- ...

### 资源相关
用户直接指示的美术风格、资源规格、格式要求：
- {指示内容} [来源: user-prompt / grill]
- ...

### 已过滤（与当前 task 无关）
- {指示内容} → 过滤理由：{一句话}
```

**如果某分类无内容，写"（无）"，不得省略分类。**

#### 路由规则

| 分类 | 传递方式 | 目标 |
|------|---------|------|
| 领域设计相关 | 作为 `--user-directives` 参数传入 domain-modeling skill（可选，无则省略） | 步骤 5 |
| 架构设计相关 | 作为 `--user-directives` 参数传入 architecture skill（可选，无则省略） | 步骤 6 |
| 详细设计相关 | 步骤 8 设计时逐条对照，确认每条已纳入实施方案 | 步骤 8 |
| 任务拆分相关 | 步骤 7 拆分时作为排序和粒度约束 | 步骤 7 |
| 资源相关 | 纳入步骤 8 的资源需求清单 | 步骤 8 |

### 5. 领域设计

**输入：** 步骤 3 的 `{task_dir}/.work/requirements.md` + 步骤 4 提取的**领域设计相关指示**。领域设计的任务是识别每条功能行为背后的领域模式——用引擎无关的语言讲清楚"这个功能本质上是什么"。

**委托给 `game-dev:domain-modeling` skill：**

```
Skill: game-dev:domain-modeling --from {task_dir} --tech {tech} [--user-directives "{步骤4提取的领域设计相关指示}"] [--auto]
```

该 skill 读取 requirements.md，逐行为识别领域模式（状态机 / 资源管理 / 事件队列 / ...），分析核心规则和边界情况，输出 `{task_dir}/.work/domain-design.md`。如传入 `--user-directives`，纳入领域建模考量。

plan 在此步骤加载该 skill 后**等待其完成**，然后检查输出文件存在：

```bash
test -f {task_dir}/.work/domain-design.md && echo "OK"
```

文件存在后继续步骤 6。

### 6. 架构设计

**输入：** 步骤 5 的 `{task_dir}/.work/domain-design.md` + 步骤 4 提取的**架构设计相关指示**。架构设计的任务是把领域模型映射到引擎的 idiomatic 写法——不是从零设计，是**翻译**。

**委托给 `game-dev:architecture` skill 的 `--task` 模式：**

```
Skill: game-dev:architecture --task --from {task_dir} --tech {tech} [--user-directives "{步骤4提取的架构设计相关指示}"] [--auto]
```

该 skill 读取 domain-design.md + requirements，生成 per-task `.work/architecture.md`，包含完整的模块规约（每个领域概念 → 一个模块 → 领域来源、技术映射、对外接口、行为契约、设计理由）。如传入 `--user-directives`，纳入架构映射决策。

plan 在此步骤加载该 skill 后**等待其完成**，然后检查输出文件存在：

```bash
test -f {task_dir}/.work/architecture.md && echo "OK"
```

文件存在后继续步骤 7。

### 7. 任务拆分与排序

**输入：** 步骤 5 的 `{task_dir}/.work/domain-design.md` + 步骤 6 的 `{task_dir}/.work/architecture.md` + 步骤 4 提取的**任务拆分相关指示**。

**拆分原则：按架构模块拆分，不按文件/行为清单拆分。**

步骤 4 中"任务拆分相关"的用户指示作为排序和粒度约束——用户指定了优先级的模块排前面，用户指定了依赖关系的按依赖排序。

architecture.md 的 **"模块规约"章节**（`## 2. 模块规约`）已经划定了模块边界——每个 `### 2.N {模块名}` = 一个 AI 任务候选。行为清单（来自 requirements.md）的作用是确定每个模块的测试覆盖范围，不是用来直接生成任务。

**拆分流程：**

1. 读 `{task_dir}/.work/architecture.md` 的 **"模块规约"章节**和"模块职责一览"表，提取模块列表
2. 对每个模块，从 domain-design.md 确认其领域模式（状态机 / 资源管理 / 事件队列 / ...）
3. 确定模块间依赖关系 → 决定任务排序
4. 行为清单中的每条行为分配到对应模块，作为该模块测试覆盖的范围声明（不是任务本身）
5. 每个模块 = 一个 AI 任务。检查 `{task_dir}/.work/layouts/` 是否有对应 HTML 设计稿 → 有则追加一条 UI 还原任务到 `## UI 还原` 章节：`[UI-N] {模块名}视觉还原 (html: .work/layouts/{name}.html)`
6. **不允许创建"测试"类型的任务——测试在各模块的 TDD 循环中由 test-agent 自然产出**

**硬约束：每个 AI 任务必须对应 architecture.md 中的一个明确模块。无法对应到模块的 → 合入上游模块或删除。任务数量 = 架构模块数量，不应超过模块数。**

**好/坏对照（关键——写任务前先读这个）：**

```
❌ 坏: "创建角色选择界面文件，定义 CharacterSelect 类"
     → 问题：描述了文件操作和代码结构，不是功能。无法知道这个界面要做什么。

❌ 坏: "在脚本文件中添加 select_character 入口函数"
     → 问题：同上。入口函数是手段，跳转行为才是目的。

❌ 坏: "编写通用性回归测试,覆盖数据 schema 完整性、单波/多波推进、异常路径"
     → 问题：测试任务。测试在各模块的 TDD 循环中自然产出，不应作为独立 AI 任务。

❌ 坏: "在主场景实例化若干刷新点,绑定不同配置,验证关卡 designer 零代码改动"
     → 问题：这是集成验证——没有对应独立模块。场景装配和验证在依赖模块完成后自然成立。

✅ 好: "实现刷新点的数据描述层：波次序列、延迟时间、敌人类型与数量的可配置定义"
     → 对应架构模块"资源层"，可验证：Inspector 中能编辑嵌套的波次→条目→敌人配置

✅ 好: "实现不可见的刷新点场景：关卡 designer 拖入场景后 Inspector 绑定配置即生效"
     → 对应架构模块"节点层"，可验证：拖入场景 → 选文件 → 运行后该位置出怪

✅ 好: "实现刷新点状态机 + 敌人系统集成：按波次序列延迟→实例化→监听清完→推进下一波"
	     → 对应架构模块"状态机+集成"，可验证：配置的波次按序执行，多刷新点独立并行
```

**描述写作规则：**

| 规则 | 说明 |
|------|------|
| 一个模块一个任务 | architecture.md 中有几个模块 → 几个 AI 任务。不把同一个模块拆成多个任务，也不把多个模块合并 |
| 用行为语言 | 描述"用户/designer 做什么 → 看到什么/发生什么"，不用技术名词（"创建 class"、"定义动画"）开头 |
| 可独立验证 | 读完描述能回答"怎么确认这个任务做完了？"——如果答案需要看另一个任务，就合到一起 |
| 不含文件路径 | 文件名不出现在描述中。同一个文件被多个任务修改是正常的 |
| 不含代码符号 | class 名、方法名、函数名、引擎类型名不出现在描述中——那些是实现方案，不是行为 |
| 不含"测试" | 没有"编写/更新测试"任务——测试在各模块的 TDD 循环中自然产出 |

### 8. 详细设计

**以领域模型为骨架，逐个功能行为展开引擎层实施方案。**

**强制检查：** 进入详细设计前，取出步骤 4 的"详细设计相关"指示列表。展开每个功能行为时逐条对照——确认该指示是否已被当前实施方案覆盖。全部覆盖后方可进入步骤 9。

调用 `superpowers:brainstorming`，但对每个功能行为按以下流程驱动：

对 `{task_dir}/.work/domain-design.md` 的每个功能行为：

1. **确认领域模式** — 这是什么模式？（状态机 / 资源管理 / 事件队列 / 空间查询 / ...）
2. **确认架构映射** — 对照 `{task_dir}/.work/architecture.md`，这个模式映射到了哪个引擎构造？
3. **对照用户详细设计指示** — 步骤 4 中"详细设计相关"项，有无与此行为相关的指示？有则纳入实现方案。
4. **展开实现方案（主体）** — 这个模式在引擎里具体怎么搭：
   - 需要哪些数据结构/变量/配置？
   - 转换/流转逻辑怎么组织？
   - 关键时序和生命周期？
5. **过边界清单** — domain-design.md 中该行为的边界情况清单，逐条确认实现方案覆盖了每一条边界
6. **API/属性/最佳实践不确定时** — 读引擎参考文档查。这是字典，不是驱动

**引擎参考文档的角色：字典，不是主导。** 领域模型驱动结构，架构映射提供框架，引擎文档填充技术细节：

- `${CLAUDE_PLUGIN_ROOT}/references/{tech}/design.md` — 详细设计指引
- `${CLAUDE_PLUGIN_ROOT}/references/{tech}/nodes-{2d,3d}.md`（仅 Godot）— 节点类型速查

7. **显示推导（强制执行，不可跳过）** — 前面的设计文档（requirements/domain/architecture）覆盖了逻辑层和架构层，但没有覆盖显示层。详细设计是第一个面对显示层的阶段——必须从零推导用户最终看到什么。

   从行为目标反推：
   - 这个行为完成后，用户看到什么？（画面/控件/动画/反馈）
   - 视觉元素在屏幕上的位置和布局？
   - 每个视觉元素的用途和尺寸？

   这一步只描述"用户看到什么"，不写用什么节点实现——那是步骤 4 已经覆盖的。

8. **资产声明（强制执行，不可跳过）** — 步骤 7 列出视觉元素后，逐个判定是否需要外部资产：

   **不需要声明资产的情况（纯代码可绘制）：**
   - 纯色块、渐变、圆角矩形 → ColorRect / StyleBoxFlat
   - 系统字体文本 → Label / Theme
   - CSG 基本体 + 纯色材质 → CSGBox3D / CSGSphere3D
   - Tween 动画效果
   - 代码绘制的简单几何（线、圆、网格）

   **需要声明资产的情况（代码无法满足视觉效果）：**
   - 具象图形（图标、头像、插画、精灵）
   - 纹理贴图（不是纯色填充的材质）
   - 背景/场景图
   - 3D 模型超出 CSG 基本体能力范围

   需要资产 → 在实现方案中内联声明，紧跟节点描述之后。格式：

   ```
   **资产: {名称}**
   - 用途: {一句话——显示什么、做什么用}
   - 类型: {精灵/纹理/模型/背景/UI素材/材质}
   - 尺寸: {W×H 或 描述}
   - 视觉要求: {颜色、材质、风格——这是后续资产生成的唯一依据}
   ```

   视觉要求写清楚颜色值、材质描述、尺寸、风格方向。**不写"怎么生成"（mmx/CSG/pillow），不写输出路径，不写格式。** 那些判定是 asset-extract-doc 的职责。

   **示例（设计文档中 InventoryBar 实现方案的样子）：**

   ```
   ### InventoryBar 实现方案

   **前置:**
   从 requirements: 物品栏常驻显示10个槽，键盘1-0/鼠标选择，显示图标和数量
   从 domain-design: InventoryBar 聚合 Slot，Slot 引用 Item，SelectionManager 管理选中
   从 architecture: UI 层用 Control 节点 + 全局 Theme，信号与数据层通信

   **显示推导:**
   物品栏是 HUD 元素，始终可见。需求"屏幕底部居中"→ 锚定底部水平居中。
   10 个槽横向排列，每个槽用户看到：底板 + 物品图 + 数量数字 + 选中高亮。

   **节点:**
   Control(底部居中) → HBoxContainer → InventorySlot × 10
   每槽: PanelContainer(底板) + TextureRect(32×32图标) + Label(数量)

   **数据流:**
   ItemManager.items_changed → _refresh_slots()
   SelectionManager.selection_changed → _update_highlight()

   **资产: Slot Background**
   - 用途: 每个槽位的底板，让槽在任意背景上可辨识
   - 类型: UI素材
   - 尺寸: 64×64 px
   - 视觉要求: 深色半透明（#1a1a2e @ 70%），4px 圆角，无边框

   **资产: Selection Highlight**
   - 用途: 当前选中槽的金色高亮边框
   - 类型: UI素材
   - 视觉要求: 2px 金色描边（#d4a574），4px 圆角，外发光效果

   **资产: Item Icons**
   - 用途: 10种物品在槽中的图标
   - 类型: 精灵
   - 尺寸: 32×32 px
   - 视觉要求: 扁平化风格，粗轮廓。剑(银灰)、盾(深铁)、药水(红/蓝/绿)、钥匙(金)
   ```

   设计文档全部保存到 `{task_dir}/.work/design.md`。

   **plan 不再直接写 resources.md。** resources.md 由 asset-extract-doc skill 从 design.md 的资产声明块提取生成。plan.md 的 `## 资源需求` 节从 design.md 提取所有资产声明的摘要（名称 + 类型 + 用途），供 orchestrator 判断是否触发资产生成阶段。

### 9. 编写 plan.md

**自己编写，不委托外部 skill。** 外部 skill 不知道 `[AI-N]` 任务格式和测试策略表约定，会产生偏离。

基于 `.work/` 下的设计文档（requirements.md / domain-design.md / architecture.md / design.md）编写。

**模板和格式约束：** 以 `${CLAUDE_PLUGIN_ROOT}/references/plan-format.md` 为唯一权威来源。其中的 plan.md 模板定义了完整结构（概述→领域模型→行为列表→设计摘要→影响范围→任务列表→资源需求→测试策略），格式校验清单和禁止内容清单定义了输出门禁。

plan 在此基础之上额外检查：

```bash
# 检查所有 UI 还原任务都有 html: 标注（plan 专属）
grep -n '\[UI-\d+\]' {task_dir}/plan.md | grep -v 'html:'
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
