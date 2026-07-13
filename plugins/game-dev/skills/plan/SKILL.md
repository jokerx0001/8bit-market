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
**用户描述澄清**
- `{task_dir}/.work/grill-interview.md` — 用户原始描述上下文

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
读取 `${CLAUDE_PLUGIN_ROOT}/references/visual-spec-format.md`。该文件定义了 visual-spec JSON 的完整结构——plan 在步骤 7 产出 visual-spec 时遵循此格式。

**视觉设计稿**
- 读取`{task_dir}/.work/style-decision`。这是视觉的精确风格决策。文件不存在必须明确输出使用的查找命令和结果,确实是空才能证明不存在
- 读取`{task_dir}/.work/layouts`目录下的html格式文件。这些是视觉相关的html设计稿。文件不存在必须明确输出使用的查找命令和结果,文件夹不存在或者文件夹下是空才能证明不存在。

### 4. 领域设计

**输入：** 步骤 3 的 `{task_dir}/.work/requirements.md`。领域设计的任务是识别每条功能行为背后的领域模式——用引擎无关的语言讲清楚"这个功能本质上是什么"。

**委托给 `game-dev:domain-modeling` skill：**

```
Skill: game-dev:domain-modeling --from {task_dir} --tech {tech} [--auto]
```

该 skill 读取 requirements.md，逐行为识别领域模式（状态机 / 资源管理 / 事件队列 / ...），分析核心规则和边界情况，输出 `{task_dir}/.work/domain-design.md`。

plan 在此步骤加载该 skill 后**等待其完成**，然后检查输出文件存在：

```bash
test -f {task_dir}/.work/domain-design.md && echo "OK"
```

文件存在后继续步骤 5。

### 5. 架构设计

**输入：** 步骤 4 的 `{task_dir}/.work/domain-design.md`。架构设计的任务是把领域模型映射到引擎的 idiomatic 写法——不是从零设计，是**翻译**。

**委托给 `game-dev:architecture` skill 的 `--task` 模式：**

```
Skill: game-dev:architecture --task --from {task_dir} --tech {tech} [--auto]
```

该 skill 读取 domain-design.md + requirements，生成 per-task `.work/architecture.md`，包含完整的模块规约（每个领域概念 → 一个模块 → 领域来源、技术映射、对外接口、行为契约、设计理由）。

plan 在此步骤加载该 skill 后**等待其完成**，然后检查输出文件存在：

```bash
test -f {task_dir}/.work/architecture.md && echo "OK"
```

文件存在后继续步骤 6。

### 6. 任务拆分与排序

**输入：** 步骤 4 的 `{task_dir}/.work/domain-design.md` + 步骤 5 的 `{task_dir}/.work/architecture.md`。

**拆分原则：按架构模块拆分，不按文件/行为清单拆分。**

architecture.md 的 **"模块规约"章节**（`## 2. 模块规约`）已经划定了模块边界——每个 `### 2.N {模块名}` = 一个 AI 任务候选。行为清单（来自 requirements.md）的作用是确定每个模块的测试覆盖范围，不是用来直接生成任务。

**拆分流程：**

1. 读 `{task_dir}/.work/architecture.md` 的 **"模块规约"章节**和"模块职责一览"表，提取模块列表
2. 对每个模块，从 domain-design.md 确认其领域模式（状态机 / 资源管理 / 事件队列 / ...）
3. 确定模块间依赖关系 → 决定任务排序
4. 行为清单中的每条行为分配到对应模块，作为该模块测试覆盖的范围声明（不是任务本身）
5. 对每个模块判定类型（logic / visual / ui），每个模块 = 一个 AI 任务。**不允许创建"测试"类型的任务——测试在各模块的 TDD 循环中由 test-agent 自然产出**

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
| 类型标注 | 每个任务必须标注类型——logic / visual / ui。visual 标注 spec:，ui 标注 html: |

**分类判定流程（对 architecture.md 的每个模块判定）：**

```
1. 该模块有玩家不可见的计算/状态/数据部分？
   → 标注为 logic 类型

2. 该模块有玩家可见的新内容或更改？
   → 标注为 visual 类型（必然——任何视觉产出都有 visual 任务）
   → 检查 {task_dir}/.work/layouts/ 是否有对应 HTML 设计稿
      → 有 → 追加 ui 任务（在 visual 基础上做像素级精调）,ui 回归任务以设计稿为维度,一个设计稿一个
```

**分类定义：**

| 类型 | 含义 | 关系 |
|------|------|------|
| `logic` | 行为/交互/数据逻辑——完成标准来自行为清单 | 地基 |
| `visual` | 视觉行为实现——完成标准来自 visual-spec JSON，必须标注 `spec:` | 视觉 |
| `ui` | 视觉还原——完成标准来自 HTML 设计稿，必须标注 `html:` | 精装 |

`logic` → `visual` → `ui`。同一界面元素可同时有 visual 和 ui 两个任务。`visual` 是必然层——只要有玩家可见的新内容或更改，就有 visual 任务。`ui` 是条件层——只有存在 HTML 设计稿时才追加。

**排序：** 按架构模块依赖关系排序（`logic` → `visual` → `ui`，同类型按依赖链）。`visual` 任务依赖同界面的最后一个 `logic` 任务（如 logic 存在）。`ui` 任务依赖由 plan 根据实际情况决定。

**visual 任务标记：** 编写 plan.md 时，`visual` 任务必须标注对应的 spec 文件：`(type: visual, spec: .work/visual-specs/{name}.json)`
**UI 任务标记：** 编写 plan.md 时，`ui` 任务必须标注对应的 HTML 文件：`(type: ui, html: .work/layouts/{name}.html)`

### 7. 详细设计

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

### 7b. 加载 UI 视觉标准（如有）

**检查 `{task_dir}/.work/layouts/` 是否存在 HTML 文件。**

如果有：读取 `style-decision.md` + HTML 文件，纳入详细设计的视觉参考。对应 visual 任务之后追加 ui 任务做像素级精调。

如果没有 HTML 但涉及新画面视觉布局 → 正常——visual 任务通过 visual-spec JSON 定义视觉标准，无需 HTML 设计稿。纯逻辑功能且无视觉产出 → 跳过此步。

### 8. 编写 plan.md

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

### 9. 格式自检

输出前对照 `plan-format.md` 的"格式校验清单"逐项确认，然后执行"禁止内容清单"中的所有 grep 命令。全部零命中方可输出。

### 10. 输出摘要

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
