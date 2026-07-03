---
name: game-dev:write-tutorial
description: |
  Write teaching-oriented tutorial documentation for game development work.
  Triggered automatically as the final step of exec phase (after collect-lessons)
  for feat and refactor tasks. Also available as standalone /game-dev:write-tutorial
  command. Use when user asks to 'write tutorial', 'document this feature',
  'create teaching docs', 'add to tutorial', or wants to explain the project
  architecture and best practices to learners.

  <example>
  Context: exec phase completed all TDD cycles, collect-lessons finished
  user: (exec invokes write-tutorial as final step)
  assistant: "使用 write-tutorial skill 编写教学文档。"
  <commentary>
  exec 将 write-tutorial 作为最后一步自动调用。
  </commentary>
  </example>

  <example>
  Context: 用户想单独补充某次工作的教学文档
  user: "/game-dev:write-tutorial feat-1"
  assistant: "使用 write-tutorial skill 为 feat-1 编写教学文档。"
  <commentary>
  支持手动指定任务目录，不指定则自动发现最新。
  </commentary>
  </example>
---

# Write Tutorial — 教学文档编写

将每次开发工作转化为教学文档。核心原则：**写教程不是写变更日志**——你要解释"为什么"，而不是罗列"做了什么"。

## 教学者心态

教程的目标是让读者**学会这个技术**，而不是知道"这个项目改了哪些文件"。

### 两层最佳实践

写教程时，每个技术点涉及两个层次的最佳实践，两层都要讲：

**第一层：领域通用做法（domain-level）**
引擎无关的、业界公认的优雅实现方式。比如：
- reload 系统怎么设计？（ammo 管理、reload 状态机、时序控制、中断处理）
- 对话系统怎么设计？（节点树、条件分支、变量绑定）
- 存档系统怎么设计？（序列化策略、版本兼容、增量写入）

这些是"干货"——官方文档不会教你怎么实现 reload，但好的实现有公认的模式。教程的价值就在于把这些模式讲清楚。

**第二层：引擎落地方式（engine-level）**
用具体引擎的推荐方式来表达领域设计。比如 Godot：
- 用 `enum` 做状态机，用 `signal` 通知状态变化
- 用 `Timer` 节点处理 reload 延迟，用 `@onready` 获取节点引用
- 用 `@export` 暴露可配置参数给编辑器

这两层不是并列的——**领域设计决定"做什么"，引擎落地决定"怎么写"**。教程要把两个层次都讲清楚：先讲领域通用做法（读者学到可迁移的知识），再讲怎么用这个引擎的 idiomatic 方式落地。

### 写作原则

- 先讲"为什么需要这个"，再讲"怎么实现"
- 架构用文字说清楚——数据怎么流、模块怎么通信
- 代码片段要解释——关键行的"为什么"比"这行干什么"重要
- 假设读者有基础但不熟悉本项目的设计思路

---

## 工作流

### 1. 定位任务目录

从 args 解析 `--task-dir`。未传 → 自动发现最新：

```bash
ls -d {dev_dir}/*/ 2>/dev/null | sort -V | tail -1
```

dev_dir 从 `references/{tech}/config.md` 读取（`.godot-dev/` 或 `.renpy-dev/`）。

**只看 feat 和 refactor 任务，跳过 fix 任务。**

### 2. 收集上下文

读取：
- `{task_dir}/plan.md` — 了解设计意图
- `{task_dir}/.work/tdd-iterations.md` — 了解实现过程中的坑
- `{task_dir}/progress.json` — 确认完成状态

### 3. 查阅最佳实践

根据技术栈查阅官方文档，**不可凭记忆**——每次都要确认最新文档：

**Godot**:
- 本地全量建档（直接 Read）：`references/godot/style-guide.md`, `references/godot/project-organization.md`
- 在线文档（WebFetch）：`https://docs.godotengine.org/en/stable/tutorials/best_practices/`
- 场景组织：`https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html`
- GDScript 风格：`https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html`

**Ren'Py**:
- Screen 文档：`https://www.renpy.org/doc/html/screens.html`
- Screen Actions：`https://www.renpy.org/doc/html/screen_actions.html`
- 根据 plan.md 涉及的内容查询对应页面（参照 `references/renpy/docs.md`）

### 4. 判断首次写入 vs 追加

检查项目根目录的 `TUTORIAL.md`：

```
项目根目录/TUTORIAL.md 存在？ → 跳到步骤 6（追加章节）
不存在？               → 执行步骤 5（写开篇）
```

### 5. 写开篇章节

开篇是整份教程的根基——读者从这里建立对项目的认知。必须严谨，每个结论都要有最佳实践出处。

结构：

```markdown
# {项目名} 开发教程

## 一、项目架构总览

### 1.1 整体设计

{项目的目录结构 + 模块划分 + 数据流。要具体，不要泛泛而谈。}

示例（Godot 项目）：
- `scenes/` 存放场景文件，按功能分 `levels/`、`ui/`、`characters/`
- `scripts/` 存放 GDScript，`autoload/` 下是全局单例，`components/` 下是可复用组件
- `modules/` 存放垂直切片的独立特性，每个模块有自己的场景、脚本、测试
- `assets/` 按类型分 `sprites/`、`audio/`、`shaders/`
- 模块间通过 autoload 单例或信号通信，禁止直接 preload 其他模块的脚本

### 1.2 为什么这样设计

{每个架构决策对应一个"为什么"。必须引用官方最佳实践。}

**原则：Godot 官方推荐"先考虑场景拆分，再考虑继承"。**
— 来源：[Scene Organization](https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html)

本项目实践：
{具体说明本项目是如何做场景拆分的，哪些地方用了组合代替继承}

**原则：避免 Godot 中的常见架构错误。**
— 来源：[Godot Best Practices](https://docs.godotengine.org/en/stable/tutorials/best_practices/)

本项目实践：
{逐一对照最佳实践清单，说明本项目的处理方式}

### 1.3 技术栈选择

{为什么选这个引擎/框架。不是列举功能，是说明它适合这个项目的什么地方。}

### 1.4 最佳实践对照表

| 官方最佳实践 | 要求 | 本项目实现 | 调整说明 |
|-------------|------|-----------|---------|
| {实践名称} | {官方要求} | {本项目做法} | {无调整 / 调整原因：xxx} |
```

**开篇要求**：
- 架构说明必须引用官方最佳实践，标注来源 URL
- 有调整的地方必须说明"为什么调整"和"解决了什么问题"
- 不能只说"我们用了 MVC"——要说清楚"为什么 MVC 适合这个项目，具体到哪个目录对应 M、哪个对应 V、哪个对应 C"
- 如果官方最佳实践有 checklist，逐项对照

### 6. 追加章节

在 `TUTORIAL.md` 末尾追加。每个章节代表一次 feat/refactor 工作。

```markdown
---

## {N}. {Task 标题}（{task-id，如 feat-1}）

### 目标

{用一句话说清楚这次开发要解决的问题。为什么需要解决它——不解决会怎样。}

### 设计方案

{不是罗列代码，是解释思路。}
- 为什么选这个方案而不是其他方案？
- 领域层的通用做法是什么？（如 reload 的状态机设计、对话系统的节点树结构）
- 引擎层用什么 idiomatic 方式落地？（如 Godot 的 signal + Timer + enum）
- 如果有 trade-off，取舍的理由是什么？

### 关键实现

{按技术主题组织，每个主题是一个完整的教学单元。不按文件或修改列表组织。}

#### {技术主题，如 "Reload 状态机"}

**领域通用做法：**

{先讲这个技术问题在游戏开发中一般怎么解决。业界公认的模式是什么。}

以 reload 为例：
- reload 的核心是状态机：`IDLE → RELOADING → READY`，以及是否需要支持中断（`RELOADING → IDLE`）
- ammo 管理：弹夹容量 vs 备弹数量，边界情况（满弹时不 reload、空弹时射击自动触发 reload）
- 时序控制：reload_time 是核心参数，Timer 驱动状态切换是常见做法

**引擎落地方式：**

{在上面领域设计的基础上，用引擎的 idiomatic 写法来表达。}

```gdscript
# 状态定义 — 用 enum 是 GDScript 惯用方式
enum ReloadState { IDLE, RELOADING, READY }

# 信号 — Godot 推荐用信号通知状态变化，解耦 UI 和逻辑
signal reload_started()
signal reload_finished()

# @export — 把可调参数暴露给编辑器
@export var reload_time: float = 1.5
@export var magazine_size: int = 30

# Timer 节点 — Godot 推荐用节点而非手动 delta 计时
@onready var reload_timer: Timer = $ReloadTimer
```

{逐段解释：为什么用 enum 而不是 string 常量？为什么用 signal 而不是直接调 UI 方法？为什么用 @export 而不是硬编码？每个选择都要有对应的引擎最佳实践出处。}

**为什么这样做是好的：**

{总结这个实现好在哪里——具体说，不笼统。比如：状态机让 reload 逻辑可独立测试、signal 让 UI 不依赖武器内部状态、@export 让数值调整不用改代码。}
```

**追加要求**：
- 按技术主题组织，不按文件或修改列表组织
- 每个技术主题先讲领域通用做法，再讲引擎落地方式
- 代码片段只保留关键行，省略无关细节
- 每个代码选择都要解释"为什么这样写"——对应哪个最佳实践
- 禁止罗列变更（"修改了 A，新增了 B，删除了 C"）
- 技术主题的数量由实际内容决定——有几个值得讲的技术点就写几个

### 7. 最佳实践合规检查

对照步骤 3 查阅的最佳实践，逐一检查本次修改的文件：

```
遍历本次修改的每个源文件：
  ├── 符合最佳实践 → 跳过
  ├── 不符合但有合理理由 → 在教程中说明这个理由
  └── 不符合且无合理理由 → 记录到 TODO-BEST-PRACTICES.md
```

**合理理由的判断标准：**
- 项目特殊性导致最佳实践不适用（如性能约束、引擎限制、与其他系统的兼容性要求）
- 有明确的 trade-off 分析，选择了另一条路
- 不是个人偏好、不是"忘了"、不是"懒得改"

**不合理理由的典型表现：**
- 命名不符合规范（如 `camelCase` 而非 `snake_case`）
- 缺少类型注解（Godot GDScript 要求静态类型）
- 硬编码路径而非用 `const`/`@export`
- 信号在编辑器中连接而非代码中连接（Godot 项目）
- 模块间直接 preload 其他模块的脚本

### 8. 写入 TODO-BEST-PRACTICES.md

**仅当步骤 7 发现了不合理违规时才写入。没有任何违规 → 不创建、不修改此文件。**

格式：

```markdown
## {task-id}: {任务标题}

发现日期：{当前日期}

| # | 文件:行 | 违规内容 | 最佳实践要求 | 修复建议 |
|---|---------|---------|-------------|---------|
| 1 | scripts/player.gd:42 | 变量名 `playerSpeed` 应改为 `player_speed` | GDScript 风格指南：变量使用 snake_case | 重命名为 `player_speed`，一并更新所有引用 |
| 2 | scenes/ui.tscn:15 | 信号 `pressed` 在 .tscn 中连接，应移到 .gd 代码中 | coding.md：信号连接推荐代码连接以保持可追溯性 | 去掉 .tscn 中的连接，在 .gd 中用 `button.pressed.connect()` |
```

**注意事项**：
- 每条违规必须引用最佳实践的出处（URL 或文件路径）
- 修复建议要具体，可以直接执行
- 同类型违规合并为一条（如"3 个变量命名不规范"记一条，列出具体位置）

### 9. 报告

完成后输出：

```
## 教程编写完成

**任务**: {task-id}
**TUTORIAL.md**: {新增开篇 / 追加第 N 章}
**TODO-BEST-PRACTICES.md**: {无新违规 / 新增 N 条违规}
```

---

## 技术栈适配

### Godot

官方最佳实践首页是 `https://docs.godotengine.org/en/stable/tutorials/best_practices/`，使用 WebFetch 获取。关键子页面已在步骤 3 列出。本地全量建档文件直接 Read。

### Ren'Py

Ren'Py 没有独立的 "best practices" 页面，最佳实践散落在各功能文档中。根据 plan.md 涉及的 Ren'Py 特性，查阅对应的文档页面。重点：

- Screen 组织原则 → `screens.html`
- Screen Action 选择 → `screen_actions.html`
- 持久化策略（persistent vs save）→ `persistent.html` + `save_load_rollback.html`
- GUI 定制规范 → `gui.html`

---

## 禁止

- 泛泛而谈（"项目采用 MVC 模式"——为什么？哪个目录是 M？）
- 没有出处支撑的断言（"这是最好的做法"——谁说的？）
- 复制粘贴代码不加解释
- 变更日志式流水账（"修改了 A，新增了 B，删除了 C"）
- 凭记忆写最佳实践——每次都要查文档确认
- fix 任务不算教学内容（只处理 feat 和 refactor）

## 与其他 skill 的关系

- **exec** → 完成 TDD 循环 + collect-lessons 后，自动调用本 skill 作为最后一步
- **collect-lessons** → 记录的是给 AI 用的经验（测试/编码规范），本 skill 写的是给人看的学习材料
- 本 skill 不替代 collect-lessons，两者互补
