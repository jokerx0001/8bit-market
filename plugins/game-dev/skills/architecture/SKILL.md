---
name: game-dev:architecture
description: |
  Maintain project-wide and per-task architecture documents.
  Three modes: --init builds the initial {dev_dir}/architecture.md from source analysis or design docs,
  --task generates per-task {task_dir}/.work/architecture.md from domain-design + requirements,
  --update merges per-task architecture into the project-level document after exec completes.

  <example>
  Context: First time setting up architecture for a project
  user: "/game-dev:architecture --init"
  assistant: "Scanning project structure and design docs to build initial architecture.md..."
  </example>

  <example>
  Context: Plan phase needs per-task architecture
  user: "/game-dev:architecture --task --from .godot-dev/feat-3 --tech godot"
  assistant: "Reading domain-design.md and requirements, generating per-task architecture..."
  </example>

  <example>
  Context: After feat-3 exec completes, merge architecture knowledge
  user: "/game-dev:architecture --update --from .godot-dev/feat-3 --tech godot"
  assistant: "Reading feat-3 architecture and merging into project-level architecture.md..."
  </example>
---

# 项目架构文档维护

维护两类架构文档：

| 文档 | 位置 | 职责 |
|------|------|------|
| 项目级 | `{dev_dir}/architecture.md` | 跨 feat 持久化，记录项目当前架构全貌 |
| 任务级 | `{task_dir}/.work/architecture.md` | per-task，plan 阶段产出，exec 阶段的模块级施工图 |

**格式契约：** `${CLAUDE_SKILL_DIR}/references/architecture-format.md` 定义了统一模板。项目级和任务级结构相同，区别仅模块数量。所有输出必须遵守。

## 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--init` | 三选一 | 初始化项目级 architecture.md |
| `--task` | 三选一 | 生成任务级 .work/architecture.md（plan 步骤 5 调用） |
| `--update` | 三选一 | 将任务级架构合并到项目级（exec 完成后调用） |
| `--from {task_dir}` | task / update 必填 | 任务目录路径（如 `.godot-dev/feat-3`） |
| `--tech {tech}` | 建议 | 技术栈标识（renpy / godot）。未传入时从项目 CLAUDE.md 检测 |
| `--auto` | 可选 | 跳过人工确认。三种模式均生效 |

## 模式判定

由调用者传入 `--init`、`--task` 或 `--update`。
---

## 公共前置步骤：确定 tech 和 dev_dir

三种模式均需此步骤：

1. 如果传入了 `--tech`，直接使用。否则 grep 项目 CLAUDE.md 检测技术栈关键词。
2. 读取 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md`，从 `## 产物目录` 节提取 `dev_dir`。
3. 回显确认 tech 和 dev_dir 值后再继续。

---

## 模式：--init

首次建立项目级架构文档。借鉴 brainstorming skill 的增量确认模式，逐个模块分析、确认、再继续。

### 1. 绿场检测

检查**源码目录是否有实际内容**（不依赖 feat/refactor 目录——调用前 orchestrator 可能已创建当前 feat 目录）：

```bash
# 读取 config.md 的 ## 源码 节获取各子目录路径
ls -d {scripts_path}/*/ 2>/dev/null
ls -d {scenes_path}/*/ 2>/dev/null
ls -d {resources_path}/*/ 2>/dev/null
```

| 条件 | 判定 |
|------|------|
| 源码目录全部为空（无子目录，或有目录但无实际文件） | 绿场 |
| 源码目录仅存在空目录或脚手架模板文件 | 绿场 |
| 源码目录存在实际工程文件（.gd / .rpy / .tscn / .tres 等） | 非绿场（Brownfield） |

### 2. 分支处理

#### 2A. Brownfield：基于源码和历史构建

##### 2A-1. 扫描项目结构

**源码目录扫描：**（绿场检测时已完成，此处可直接复用结果）

**已有设计文档扫描：**

遍历 `{dev_dir}/feat-*/` 和 `{dev_dir}/refactor-*/` 目录。对每个存在的目录：
- 读取 `plan.md` → 提取概述和影响范围
- 读取 `.work/domain-design.md`（如存在）→ 提取领域模型
- 读取 `.work/architecture.md`（如存在）→ 提取引擎映射

按 feat-N 序号排序阅读，从最早的任务开始，逐步积累理解。

##### 2A-2. 识别模块

基于扫描结果，AI 自行形成模块划分判断。**不是问用户"怎么分"——是 AI 给出判断，让用户确认或纠正。**

**输出格式：**

```
## 项目架构分析

根据源码组织和已有开发历史，识别出以下模块：

1. **{模块 A}** — {一句话职责说明}（源码: {目录路径}，涉及 feat: {列表}）
2. **{模块 B}** — {一句话职责说明}（源码: {目录路径}，涉及 feat: {列表}）
...

以上划分是否准确？
- "OK" → 继续逐个深入分析
- "调整为: ..." → 修正后继续
- "补充: ..." → 追加模块后继续
```

非 auto 模式下必须等待用户确认。auto 模式跳过确认，直接使用当前划分进入下一步。

##### 2A-3. 逐个模块深入分析

一次只处理一个模块，确认后再进入下一个。

**对每个模块：**

**a) 呈现 AI 分析：**

```
### {模块名}

**领域来源：** {domain-design.md 中的模式/概念}

**职责：** {一句话}

**技术映射：**
- {引擎构造} → {领域概念}，理由：{为什么}

**对外接口：**
| 方向 | 接口 | 说明 |
|------|------|------|
| 对外暴露 | {信号/方法} | {调用方、参数、时机} |
| 外部依赖 | {模块/数据源} | {获取什么、何时获取} |

**文件组织：** {脚本/场景/资源的路径和职责}

**关键约定：**
- {约定}: {说明}
```

**b) 请求确认（非 auto 模式必须等待）：**

```
以上是我对 {模块名} 当前实现的理解。请确认：
- "OK" → 记录并继续
- "偏离: ..." → 实现偏离了意图，进入设计讨论
- "意图已变: ..." → 原始设计已更新，进入设计讨论
```

**c) 用户确认 / auto 模式：** 记录为正确 → 进入下一模块。

**d) 用户指出偏离：** 发现代码与意图不一致时，切换到设计讨论模式：

```
### 设计讨论 — {模块}

当前代码行为：
{AI 分析的代码实际行为}

用户期望的行为：
{用户描述}

差距分析：
{AI 分析差距}

建议方案：
- 方案 A: {描述 + 改动范围 + 代价}
- 方案 B: {描述 + 改动范围 + 代价}

推荐方案 {X}，因为 {理由}。请确认采用哪个方向：
```

用户确认方案后，**记录的是用户意图（目标架构），不是当前代码状态。**

##### 2A-4. 写入 architecture.md

所有模块确认完毕后，按 `${CLAUDE_SKILL_DIR}/references/architecture-format.md` 的统一模板写入。

**内容来源优先级：**
1. 用户确认的分析结论
2. 用户确认的目标架构（偏离讨论结果）
3. 已有 feat 的 `.work/architecture.md` 和 `.work/domain-design.md`
4. 源码目录结构推断

**组装规则：**
- 按统一模板五章节结构：总体架构 → 模块规约 → 运行时视图 → 跨模块约定 → 架构决策记录
- 每个模块一个 `### 2.N {模块名}` 节
- 不写任何 feat-N 标注

写入后输出摘要：

```
## Architecture 文档已创建

**文件：** {dev_dir}/architecture.md
**模块：** {N} 个
**覆盖任务：** {feat/refactor 列表}
**偏离记录：** {N} 处（如有）
```

---

#### 2B. Greenfield：从设计文档从零编写

源码目录无内容——这是全新项目。**从设计文档理解要做什么，根据技术栈从零编写架构。**

##### 2B-1. 读取设计文档

必须读取以下文件，理解项目要构建什么：

| 文件 | 用途 | 缺失时 |
|------|------|--------|
| `{task_dir}/.work/grill-interview.md` | 用户意图、游戏类型、技术偏好 | 警告，缺少用户原始上下文 |
| `{dev_dir}/requirements.md` | 项目级需求——全量功能系统 | 警告，无法理解功能全貌 |
| `{task_dir}/.work/requirements.md` | per-task 需求——本次新增行为 | 警告，缺少行为清单 |
| `{task_dir}/.work/domain-design.md` | 领域模型——模式、概念、边界规则 | 警告，缺少领域建模 |
| `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md` | 技术栈项目结构预期 | 必须存在 |
| `${CLAUDE_PLUGIN_ROOT}/references/{tech}/coding.md` | 技术栈编码惯例 | 必须存在 |
| `${CLAUDE_PLUGIN_ROOT}/references/{tech}/patterns.md` | 领域模式 → 引擎构造映射规则（如存在） | 建议存在 |

##### 2B-2. 从设计文档提取架构要素

从 domain-design.md 提取：

- **模块列表** — 每个领域模式/概念 → 一个模块候选。模块划分遵循单一职责：一个模块做一件事，边界清晰
- **领域模式** — 各模块的状态机/资源管理/事件队列等模式
- **边界规则** — 各模块的边界情况和预期行为
- **模块间关系** — 数据流方向、依赖关系

从 requirements.md 提取：

- **功能系统归属** — 每个需求行为归属到哪个模块
- **跨模块行为** — 哪些行为需要多模块协作

从 grill-interview.md 提取：

- **游戏类型** — 影响架构惯用模式（如塔防用信号驱动，视觉小说用状态机驱动）
- **技术偏好** — 影响引擎构造选择

##### 2B-3. 从零设计架构

对每个模块，从领域模型映射到引擎构造：

1. **技术映射** — 领域概念 → 该技术栈的 idiomatic 构造（对照 patterns.md + coding.md）
2. **对外接口** — 信号/方法/公共属性，调用方、参数、时机
3. **行为契约** — 状态机/生命周期，关键边界行为（输入为空、依赖缺失、异常路径）
4. **设计理由** — 为什么选方案 A 不是方案 B（如有明显两难选择）

识别关键运行时流程（至少覆盖正常路径 + 一个异常路径）。

识别跨模块约定（错误处理策略、资源生命周期、duck-type 契约等）。

##### 2B-4. 呈现并确认

输出模块划分和架构设计供用户确认（非 auto 模式）：

```
## 项目架构设计（Greenfield）

从设计文档分析，识别出以下模块：

1. **{模块 A}** — {职责}（对应领域概念: {domain-design.md 中的模式}）
2. **{模块 B}** — {职责}（对应领域概念: {domain-design.md 中的模式}）
...

### 模块详情

#### {模块 A}
- 领域来源: {domain-design.md 中的模式/概念}
- 技术映射: {引擎构造} → {领域行为}
- 对外接口: {信号/方法}
- 设计理由: {关键取舍}

#### {模块 B}
...

以上架构设计是否准确？
- "OK" → 写入 architecture.md
- "调整为: ..." → 修正后重新确认
- "补充: ..." → 追加模块后重新确认
```

非 auto 模式下必须等待确认。auto 模式跳过确认直接写入。

##### 2B-5. 写入 architecture.md

按 `${CLAUDE_SKILL_DIR}/references/architecture-format.md` 的统一模板组装写入。

---

## 模式：--task --from {task_dir}

由 **plan 步骤 5** 调用。读取 domain-design.md 和 requirements，生成 per-task `.work/architecture.md`——这是 exec 阶段的模块级施工图。

### 1. 输入文件

确认以下文件存在：

| 文件 | 用途 | 缺失时 |
|------|------|--------|
| `{task_dir}/.work/domain-design.md` | 领域模型——模块划分的来源 | 报错退出 |
| `{task_dir}/.work/requirements.md` | per-task 需求——行为清单 | 警告继续 |
| `{dev_dir}/requirements.md` | 项目级需求——功能系统上下文 | 警告继续 |
| `{task_dir}/.work/grill-interview.md` | 用户原始意图 | 警告继续 |
| `{dev_dir}/architecture.md` | 项目级架构约束（如存在） | 跳过，无架构约束 |
| `${CLAUDE_PLUGIN_ROOT}/references/{tech}/patterns.md` | 领域模式 → 引擎构造映射规则 | 必须存在 |
| `${CLAUDE_PLUGIN_ROOT}/references/{tech}/coding.md` | 技术栈编码惯例 | 必须存在 |

### 2. 提取模块

从 domain-design.md 提取模块列表：

- 每个独立的领域模式/概念 → 一个模块
- 模块边界遵循单一职责原则
- 模块间依赖从数据流方向推导

### 3. 技术映射

对每个模块，将领域概念映射到引擎构造。对照 patterns.md 和 coding.md，确保每个选择都是该引擎推荐的写法。

映射内容：
- **技术映射** — 引擎构造 1 → 实现领域行为 A，理由：为什么选这个而非替代方案
- **对外接口** — 信号/方法/公共属性、调用方、参数含义、调用时机
- **外部依赖** — 依赖的模块/数据源、获取什么数据、何时获取
- **行为契约** — 状态机/生命周期，关键边界行为（输入为空、依赖缺失、异常路径）
- **设计理由** — 关键取舍（如有两难选择）

### 4. 运行时视图

用序列图展示至少一个关键跨模块流程（正常路径 + 一个关键异常路径）。

### 5. 跨模块约定

识别跨模块的通用约定：错误处理策略、资源生命周期、duck-type 契约等。说明本次设计与现有项目架构的契合点。

### 6. 架构决策记录

用表格记录关键决策：选择方案、替代方案、理由。

### 7. 输出

按 `${CLAUDE_SKILL_DIR}/references/architecture-format.md` 的统一模板写入 `{task_dir}/.work/architecture.md`。

```bash
mkdir -p {task_dir}/.work
```

**非 auto 模式：** 输出架构摘要，等待用户确认后写入。
**auto 模式：** 跳过确认，直接写入。

输出摘要：

```
## Per-task Architecture 已生成

**文件：** {task_dir}/.work/architecture.md
**模块数：** {N} 个
**运行时流程：** {N} 个
**架构决策：** {N} 条

模块列表：
- {模块 A} → {技术映射摘要}
- {模块 B} → {技术映射摘要}
...
```

---

## 模式：--update --from {task_dir}

在 feat 或 refactor 的 exec 完成后调用，将 per-task 架构知识合并到项目级 architecture.md。

### 1. 定位输入文件

| 文件 | 用途 | 缺失时 |
|------|------|--------|
| `{dev_dir}/architecture.md` | 当前项目架构文档 | **降级为 --init 模式**，先建立初版 |
| `{task_dir}/.work/domain-design.md` | 本次任务的领域模型 | 警告并跳过，无法合并 |
| `{task_dir}/.work/architecture.md` | 本次任务的任务级架构 | 警告并跳过，无法合并 |
| `{task_dir}/plan.md` | 参考——设计摘要和概述 | 降级处理，仅从 domain-design + architecture 合并 |

全部关键文件存在才继续。任一缺失 → 输出具体警告。

### 2. 分类变更

| 类型 | 判断标准 | 合并操作 |
|------|---------|---------|
| **新模块** | 涉及全新概念，不在现有 architecture.md 的模块规约中 | 更新模块职责一览表 + 在模块规约末尾追加 `### 2.N {模块名}` 节 |
| **架构变更** | 现有模块的核心架构改变（技术映射/对外接口/行为契约/设计理由） | 定位该 `### 2.N {模块名}` 节，替换变更部分，保留未变更部分 |
| **功能扩展** | 现有模块内新增功能，核心架构不变 | 定位该 `### 2.N {模块名}` 节，更新/丰富规约内容 |
| **无变更** | 纯 bug fix、纯界面调整、纯重命名等 | 输出"本次任务无架构变更"，直接完成 |

如果分类不确定 → 非 auto 模式下输出判断和理由，请求用户确认。

### 3. 智能合并

**不是 append，是 merge。**

```
读取 architecture.md → 按 ### 2.N {模块名} 解析模块规约
  │
  ├── 新模块 → 更新模块职责一览表
  │          → 在模块规约末尾追加 ### 2.N {模块名} 节
  │
  ├── 架构变更 → 定位匹配的 ### 2.N {模块名} 节
  │            → 对比新旧内容，替换变更部分，保留未变更部分
  │            → 保留用户在前次确认中手动编辑的内容
  │
  └── 功能扩展 → 定位匹配的 ### 2.N {模块名} 节
                → 更新/丰富模块规约内容
```

**禁止行为：**
- 直接在文件末尾盲追加（除非是新模块）
- 写 feat-N 标注
- 对同一模块的内容写到文件两个不同位置
- 覆盖用户手动编辑的已有内容

### 4. 写入

按 `${CLAUDE_SKILL_DIR}/references/architecture-format.md` 规范写回。

**`--auto` 模式：** 跳过确认，直接写入。
**非 `--auto` 模式：** 输出变更摘要，等待用户确认后写入。

```
## Architecture 更新完成

**文件：** {dev_dir}/architecture.md
**来源任务：** {task_dir}

**变更摘要：**
- 新模块: {N}（{清单}）
- 架构变更: {N}（{清单}）
- 功能扩展: {N}（{清单}）
- 无变更: {N}

**详细变更：**
{对每个有变更的模块，简述变更了什么}
```

---

## 核心约束

- `--init` 时，架构文档是全量的——覆盖项目所有模块，不仅限于当前已实现的功能
- `--init` 绿场时，从设计文档（grill-interview + requirements + domain-design）理解要做什么，从零编写架构。不从 feat 目录推导，不凭空猜测
- `--task` 时，每个模块必须来自 domain-design.md 的领域概念——**一个领域概念 → 一个模块规约**。模块数量 = 领域概念数量
- `--task` 的产出必须有**模块规约**章节——每个模块讲清楚"领域来源 → 技术映射 → 对外接口 → 行为契约 → 设计理由"
- `--update` 时，合并操作必须定位到正确章节，**严禁末尾盲追加**。相同模块的内容必须聚合
- **非 auto 模式下，设计中有疑点必追问，严禁凭猜测决定。** 包括但不限于：模块划分不确定、变更类型分类模糊、领域映射存在多种解释、用户意图与设计文档不一致。auto 模式跳过追问，基于已有信息继续
- 领域模型部分用引擎无关语言，引擎映射部分必须具体到文件路径和构造名称
- 不写 feat-N、refactor-N 等任务编号标注。项目级架构文档始终反映当前状态，不是变更日志

---

## 红牌

以下想法出现时 → **STOP，回到流程：**

- "这个项目很简单，扫一眼就能写出架构" → 仍然需要逐个模块确认。简单项目也有出乎意料的偏离。
- "update 时 architecture.md 不存在，我直接跳过" → 不应该跳过。应该降级为 --init，先建立初版架构。
- "这个变更太小了，直接追加到文件末尾就行" → 不。相同模块的内容必须聚合。盲追加是架构文档腐化的开始。
- "用户说 OK 我就全写了" → 不。确认一个模块才能进入下一个。
- "绿场项目没有源码可分析，我跳过扫描直接退出" → 不。绿场项目读设计文档从零编写架构，参照 --init 的 2B 分支。
- "task 模式下 domain-design 模块很多，我合并几个" → 不。一个领域概念一个模块规约。合并会导致职责模糊、exec 无法分配任务。
- "task 模式下不需要模块规约，有个架构图就够了" → 不。模块规约是 exec 阶段拆分 AI 任务的唯一依据。缺少它，plan 步骤 6 无法正确拆分。

---

## Completion Gate

永远不要声称任务完成，除非：

**--init 模式（Brownfield）：**
- [ ] 项目源码和已有 feat 已扫描
- [ ] 模块划分已获用户确认（非 auto 模式）
- [ ] 每个模块完成了增量分析确认（领域模型 + 引擎映射 + 约定）
- [ ] 用户指出的偏离已切换设计讨论并记录目标架构
- [ ] 非 auto 模式下疑点均已追问并确认
- [ ] architecture.md 已按统一模板写入
- [ ] 输出文档路径和模块摘要

**--init 模式（Greenfield）：**
- [ ] grill-interview.md、requirements.md、domain-design.md 已读取
- [ ] 模块列表从 domain-design.md 提取，无凭空捏造
- [ ] 每个模块完成了技术映射（领域概念 → 引擎构造 + 理由）
- [ ] 关键流程和跨模块约定已识别
- [ ] 模块划分已获用户确认（非 auto 模式）
- [ ] architecture.md 已按统一模板写入
- [ ] 输出文档路径和模块摘要

**--task 模式：**
- [ ] domain-design.md、requirements.md 已读取
- [ ] 模块列表从 domain-design.md 提取，每个领域概念对应一个模块规约
- [ ] architecture.md 已按统一模板写入（含模块规约章节）
- [ ] 每个模块包含：领域来源、技术映射、对外接口、行为契约、设计理由
- [ ] 运行时视图至少覆盖一个正常路径 + 一个异常路径
- [ ] 非 auto 模式下已获用户确认后写入
- [ ] 输出模块摘要

**--update 模式：**
- [ ] 输入文件全部确认存在
- [ ] 变更类型已分类（新模块 / 架构变更 / 功能扩展 / 无变更）
- [ ] 非 auto 模式下分类不确定时已追问用户
- [ ] 合并已按模块智能完成（不是盲 append）
- [ ] 无 feat-N 标注残留
- [ ] 非 auto 模式下已获用户确认后写入
- [ ] 输出变更摘要
