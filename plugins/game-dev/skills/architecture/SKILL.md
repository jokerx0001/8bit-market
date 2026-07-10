---
name: game-dev:architecture
description: |
  Maintain the project-wide architecture document ({dev_dir}/architecture.md).
  Two modes: --init analyzes the entire project and writes the initial architecture.md,
  --update merges new architectural knowledge after a feat/refactor completes.
  Solves the problem of each feat's architecture being locked in .work/ and invisible to later feats.

  <example>
  Context: First time setting up architecture for a project
  user: "/game-dev:architecture --init"
  assistant: "Scanning project structure, existing feats, and source code to build initial architecture.md..."
  </example>

  <example>
  Context: After feat-3 completes, merge architecture knowledge
  user: "/game-dev:architecture --update --from .godot-dev/feat-3 --tech godot"
  assistant: "Reading feat-3 design documents and merging into architecture.md..."
  </example>
---

# 项目架构文档维护

维护 `{dev_dir}/architecture.md`——跨 feat 的项目级架构文档。解决每个 feat 的架构知识被锁在 `.work/architecture.md` 里、后续 feat 无法获取的问题。

**格式契约：** `${CLAUDE_SKILL_DIR}/references/architecture-format.md` 定义了 architecture.md 的完整格式规范。所有输出必须遵守。

## 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--init` | 二选一 | 初始化模式：扫描项目源码和已有 feat，写出首版 architecture.md |
| `--update` | 二选一 | 更新模式：从已完成的任务合并架构知识 |
| `--from {task_dir}` | update 必填 | 已完成的任务目录路径（如 `.godot-dev/feat-3`） |
| `--tech {tech}` | 建议 | 技术栈标识（renpy / godot）。未传入时从项目 CLAUDE.md 检测 |
| `--auto` | 可选 | update 模式下跳过人工确认，直接写入。init 模式下该标志无效 |

---

## 模式：--init

首次建立项目架构文档。**需要人工参与确认**——借鉴 brainstorming skill 的增量确认模式，逐个子系统分析、确认、再继续。

### 1. 确定 tech 和 dev_dir

与 orchestrator 的阶段 0 相同：

1. 如果传入了 `--tech`，直接使用。否则 grep 项目 CLAUDE.md 检测技术栈关键词。
2. 读取 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md`，从 `## 产物目录` 节提取 `dev_dir`。
3. 回显确认 dev_dir 值后再继续。

### 2. 扫描项目结构

**源码目录扫描：**

```bash
# 读取 config.md 的 ## 源码 节获取各子目录路径
ls -d {scripts_path}/*/ 2>/dev/null
ls -d {scenes_path}/*/ 2>/dev/null
ls -d {resources_path}/*/ 2>/dev/null
```

**已有设计文档扫描：**

遍历 `{dev_dir}/feat-*/` 和 `{dev_dir}/refactor-*/` 目录。对每个存在的目录：
- 读取 `plan.md` → 提取概述和影响范围
- 读取 `.work/domain-design.md`（如存在）→ 提取领域模型
- 读取 `.work/architecture.md`（如存在）→ 提取引擎映射

按 feat-N 序号排序阅读，从最早的任务开始，逐步积累理解。

**结果：** 对项目源码组织和开发历史形成完整认知。

### 3. 识别子系统

基于扫描结果，AI 自行形成子系统划分判断。**不是问用户"怎么分"——是 AI 给出判断，让用户确认或纠正。**

**输出格式：**

```
## 项目架构分析

根据源码组织和已有开发历史，识别出以下子系统：

1. **{子系统 A}** — {一句话职责说明}（源码: {目录路径}，涉及 feat: {列表}）
2. **{子系统 B}** — {一句话职责说明}（源码: {目录路径}，涉及 feat: {列表}）
...

以上划分是否准确？
- "OK" → 继续逐个深入分析
- "调整为: ..." → 修正后继续
- "补充: ..." → 追加子系统后继续
```

**等待用户确认后**进入步骤 4。

### 4. 逐个子系统深入分析

**核心机制：借鉴 brainstorming 的增量确认——一次只处理一个子系统，确认后再进入下一个。**

对每个子系统，依次执行以下子步骤：

#### 4a — 呈现 AI 分析

基于扫描结果，对当前子系统输出三要素分析：

```
## 子系统: {Name}

### 领域模型分析
- 模式: {状态机/数据驱动/观察者/资源管理/事件队列/空间查询/...}
- 核心概念: {列出并说明}
- 边界规则: {表格列出}

### 引擎映射分析
- 文件组织: {脚本/场景/资源的路径和职责}
- 核心构造: {引擎构造 → 领域概念的映射关系}
- 对外接口: {信号/group/方法签名}

### 关键约定
- {约定 1}: {说明}
- {约定 2}: {说明}
```

#### 4b — 请求确认

```
以上是我对 {子系统名} 当前实现的理解。请确认：
- "OK" → 这就是我的意图，记录并继续
- "偏离: ..." → 实现偏离了意图，进入讨论
- "意图已变: ..." → 原始设计已更新，进入讨论
```

#### 4c — 用户确认（"OK"）

记录当前分析为正确 → 直接进入下一子系统（回到步骤 4 开头）。

#### 4d — 用户指出偏离

发现代码与意图不一致时，切换到设计讨论模式：

```
### 设计讨论 — {子系统}

当前代码行为：
{AI 分析的代码实际行为}

用户期望的行为：
{用户描述}

差距分析：
{AI 分析差距}

建议方案：
- 方案 A: {描述 + 改动范围 + 代价}
- 方案 B: {描述 + 改动范围 + 代价}
- 方案 C: {描述 + 改动范围 + 代价}（如适用）

推荐方案 {X}，因为 {理由}。请确认采用哪个方向：
```

用户确认方案后，**记录的是用户意图（目标架构），不是当前代码状态。** 继续下一子系统。

### 5. 写入 architecture.md

所有子系统确认完毕后，按 `${CLAUDE_SKILL_DIR}/references/architecture-format.md` 的模板组装并写入 `{dev_dir}/architecture.md`。

```bash
mkdir -p $(dirname {dev_dir}/architecture.md)
```

**内容来源优先级：**
1. 用户在步骤 4c 中确认的分析结论
2. 用户在步骤 4d 中确认的目标架构
3. 已有 feat 的 `.work/architecture.md` 和 `.work/domain-design.md`
4. 源码目录结构推断

**组装规则：**
- 先写 `## Overall Architecture`（子系统地图 + 数据流）
- 每个子系统一个 `## Subsystem: {Name}` 节
- 子系统内部按"领域模型 → 引擎映射 → 关键约定"顺序
- 子系统内的子特性用 `#### Feature: {Name}` 子节
- 不写任何 feat-N 标注

写入后输出：

```
## Architecture 文档已创建

**文件：** {dev_dir}/architecture.md
**子系统：** {N} 个
**覆盖任务：** {feat/refactor 列表}
**偏离记录：** {N} 处（如有）
```

---

## 模式：--update --from {task_dir}

在 feat 或 refactor 完成后调用，将任务的架构知识合并到项目级 architecture.md。

**核心原则：智能合并，不是盲追加。** 相同子系统的内容聚合在一起，不分散在文件不同位置。

### 1. 定位输入文件

确认以下文件存在：

| 文件 | 用途 | 缺失时 |
|------|------|--------|
| `{dev_dir}/architecture.md` | 当前项目架构文档 | **降级为 --init 模式**，先建立初版架构 |
| `{task_dir}/.work/domain-design.md` | 本次任务的领域模型 | 警告并跳过，无法合并 |
| `{task_dir}/.work/architecture.md` | 本次任务的引擎映射 | 警告并跳过，无法合并 |
| `{task_dir}/plan.md` | 参考——设计摘要和概述 | 降级处理，仅从 domain-design + architecture 合并 |

全部关键文件存在才继续。任一缺失 → 输出具体警告，说明跳过了什么。

### 2. 分类变更

基于 `.work/domain-design.md` 和 `.work/architecture.md` 的内容，判断变更类型：

| 类型 | 判断标准 | 合并操作 |
|------|---------|---------|
| **新子系统** | 涉及全新目录/全新概念，不在现有 architecture.md 中 | 创建 `## Subsystem: {Name}` 新节 |
| **架构变更** | 现有子系统的核心架构改变（状态机结构/数据流/对外接口/职责划分） | 更新该子系统的 `## Subsystem` 节 |
| **功能扩展** | 现有子系统内新增文件/功能，核心架构不变 | 在子系统下追加 `#### Feature: {Name}` 子节 |
| **无变更** | 纯 bug fix、纯界面调整、纯重命名等 | 输出"本次任务无架构变更"，直接完成 |

**辅助判定方法：**
- 从 `plan.md` 的 `## 影响范围` 看涉及的文件和子系统
- 新目录/新概念出现 → 新子系统
- 改核心逻辑/数据流/接口 → 架构变更
- 子系统内加功能/界面/扩展 → 功能扩展

如果分类不确定 → 输出判断和理由，请求用户确认。

### 3. 智能合并

这是核心步骤——**不是 append，是 merge。**

**合并策略：**

```
读取 architecture.md → 按 ## Subsystem: {Name} 解析为节
  │
  ├── 新子系统 → 更新 Overall Architecture 的子系统地图
  │             → 追加新的 ## Subsystem: {Name} 节（放在文件末尾）
  │
  ├── 架构变更 → 定位匹配的 ## Subsystem: {Name} 节
  │             → 对比新旧内容
  │             → 替换变更的部分（领域模型/引擎映射/约定）
  │             → 保留未变更的部分
  │             → 保留用户在前次确认中手动编辑的内容
  │
  └── 功能扩展 → 定位匹配的 ## Subsystem: {Name} 节
                → 在节末尾追加 #### Feature: {Name} 子节
                → 子节内容：领域增量 + 引擎增量 + 新增约定
```

**禁止行为：**
- 直接在文件末尾盲追加（除非是新子系统）
- 写 feat-N 标注
- 对同一子系统的内容写到文件两个不同位置
- 覆盖用户手动编辑的已有内容

### 4. 写入

合并完成后按 `${CLAUDE_SKILL_DIR}/references/architecture-format.md` 规范写回 `{dev_dir}/architecture.md`。

**`--auto` 模式：** 跳过人工确认，直接写入。
**非 `--auto` 模式：** 输出变更摘要，等待用户确认后写入。

**输出摘要：**

```
## Architecture 更新完成

**文件：** {dev_dir}/architecture.md
**来源任务：** {task_dir}

**变更摘要：**
- 新子系统: {N}（{清单}）
- 架构变更: {N}（{清单}）
- 功能扩展: {N}（{清单}）
- 无变更: {N}
```

---

## 红牌

以下想法出现时 → **STOP，回到流程：**

- "这个项目很简单，扫一眼就能写出架构" → 仍然需要逐个子系统确认。简单项目也有出乎意料的偏离。
- "update 时 architecture.md 不存在，我直接跳过" → 不应该跳过。应该降级为 --init，先建立初版架构。
- "这个变更太小了，直接追加到文件末尾就行" → 不。相同子系统的内容必须聚合。盲追加是架构文档腐化的开始。
- "用户说 OK 我就全写了" → 不。确认一个子系统才能进入下一个。全部一次呈现用户会漏看。

---

## Completion Gate

永远不要声称任务完成，除非：

**--init 模式：**
- [ ] 项目源码和已有 feat 已扫描
- [ ] 子系统划分已获用户确认
- [ ] 每个子系统完成了增量分析确认（领域模型 + 引擎映射 + 约定）
- [ ] 用户指出的偏离已切换设计讨论并记录目标架构
- [ ] architecture.md 已按 format 规范写入
- [ ] 输出文档路径和子系统摘要

**--update 模式：**
- [ ] 输入文件全部确认存在（architecture.md、domain-design.md、architecture.md）
- [ ] 变更类型已分类（新子系统 / 架构变更 / 功能扩展 / 无变更）
- [ ] 合并已按子系统智能完成（不是盲 append）
- [ ] 无 feat-N 标注残留
- [ ] 更新后的 architecture.md 已写回
- [ ] 输出变更摘要
