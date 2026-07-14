# Plan 文件格式规范

此文件定义 plan → exec 的共享契约。plan.md 是 plan 阶段的**唯一输出**、exec 读取的**唯一设计文档**。

---

## 目录结构

```
{dev_dir}/{kind}-{N}/
├── plan.md
├── progress.json
├── impact.md        ← 仅 refactor
└── .work/
    ├── grill-interview.md
    ├── requirements.md
    ├── domain-design.md
    ├── architecture.md
    ├── design.md
    └── debug-analysis.md  ← 仅 fix，根因分析
```

---

## plan.md 模板

```markdown
# Plan: {feature-name}

## 概述
{功能目标 + 项目环境}
{从 requirements.md 提炼}

## 领域模型
{每个功能行为的领域模式——让 exec 和 coding agent 知道"这个功能本质上是什么"}

以 reload 为例：
- **模式**：有限状态机 IDLE → RELOADING → READY
- **核心规则**：满弹不换、空弹自动换、换弹中切武器中断
- **边界**：备弹不足时只装可用数、换弹中不能射击

## 行为列表

{从用户确认的行为清单中提取。每条是一个玩家可见的行为 → 一个 testcase。}

| # | 行为 | 验证方式 |
|---|------|---------|
| 1 | 玩家进入主菜单 → 看到角色选择界面 | screenshot: 默认布局基线 |
| 2 | 玩家点击第2个角色卡片 → 卡片视觉高亮 | screenshot: 高亮状态 |
| 3 | 玩家选中角色后点击"确认" → 跳转到游戏开始 | assert 跳转行为 |
| 4 | 玩家未选中角色点击"确认" → 停留在当前界面 | behavior |

**行为列表的作用：** test-agent 将它作为 testcase 的蓝图——每条行为对应一个 testcase。coding-agent 将它作为实现目标——每条行为是必须支持的功能。

## 设计摘要
{关键设计决策，从 architecture.md + design.md 提炼——自包含，不写"详见 design.md"}

- 界面结构: {界面划分和跳转关系}
- 数据流: {流程间传递的数据、持久化方式}
- 关键交互: {用户操作 → 响应 → 结果}

## 影响范围
{功能影响面，不是文件变更清单}

| 影响面 | 变更描述 |
|--------|---------|
| ... | ... |

> **注意：** 任务列表不按此表拆分——任务按功能模块拆分。一个文件可以被多个任务增量修改。

## 任务列表

### [AI] 任务

**格式：**

```
- [AI-N] (type: {logic|visual|ui}) {描述} (依赖: AI-X, AI-Y)
- [AI-N] (type: visual, spec: .work/visual-specs/{name}.json) {描述} (依赖: AI-X)
- [AI-N] (type: ui, html: .work/layouts/{name}.html) {描述} (依赖: AI-X)
```

> **任务列表不使用代码块（\`\`\`）包裹。** AI 任务列表项是普通 markdown 无序列表。将任务列表包裹在代码块中会偏离格式规范，增加 exec 解析失败的风险。上述代码块仅用于本文档展示格式——实际 plan.md 中的任务列表是裸 markdown 列表。

**`{描述}` 约束：** 每个 AI 任务是一行行为描述，不是多段落文档。用功能行为语言——描述用户/系统可感知的功能，不含文件路径、不含代码符号。禁止 `### [AI-N]` 子章节展开、RED/GREEN 步骤、"输出文件/任务步骤" 指令。

**类型分类规则：**

| 类型 | 含义 | 包含 |
|------|------|------|
| `logic` | 行为/交互/数据逻辑——完成标准来自行为清单 | 状态机转换、数据初始化、持久化读写、流程跳转、计算判定 |
| `visual` | 视觉行为实现——完成标准来自 visual-spec JSON | 元素显示/隐藏、位置布局、大小比例、颜色变化、粒子效果、动画播放——任何玩家可见的新内容或更改 |
| `ui` | 视觉还原——完成标准来自 HTML 设计稿 | 颜色精确值、字体/字号、间距、圆角——对照 HTML 精调视觉属性 |

**硬约束：每个 task 只能是单一类型。logic / visual / ui 不允许合并到同一个 task 中。** 验证方式不同（测试 vs visual-compare vs HTML 对比），合并会导致一个 task 内混多种验证标准。

`logic` 处理不可见的计算和状态。`visual` 处理可见的视觉行为（位置、大小、颜色、动画）。`ui` 在 visual 的基础上做像素级精调。

**分类关系：** `logic` → `visual` → `ui`。`visual` 是必然层——只要有玩家可见的新内容或更改就有 visual 任务。`ui` 是条件层——只有存在 HTML 设计稿时才追加 ui 任务。

**排序约束：** `logic` → `visual` → `ui`。

**UI 任务必须标注 `html:` 指向 HTML 标准文件路径**（相对于 task_dir）。
**visual 任务必须标注 `spec:` 指向 visual-spec JSON 文件路径**（相对于 task_dir）。

### [HUMAN] 任务

- `[HUMAN]` {具体操作步骤}

## 资源需求
{从 .work/resources.md 提取摘要，供 orchestrator 判断是否触发资源生成阶段}

| # | 资源名称 | 类型 | 尺寸 | 使用场景 |
|---|---------|------|------|---------|
| 1 | ... | ... | ... | ... |

## 测试策略

测试策略声明**覆盖什么行为**。

**每条覆盖描述只能写高层次的玩家可感知功能，禁止写验证技术手段。**

```
✅ "角色选择交互（选中/取消/确认）; visual: 默认布局基线"
✅ "数据层读写 + 状态机转换 + 按键捕获"
❌ "数据层：default 变量初始化、qte_phase 初始 'waiting'"
❌ "modal True 源码契约、zorder 200 源码契约、4 参数签名契约"
❌ "test_enemy_health.gd | 敌人受击扣血" — 不写文件名
```

| 覆盖 |
|------|
| {交互行为简述}; visual: {视觉状态简述} |
```

---

## plan.md 模板（fix 模式）

fix 模式的 plan.md 结构不同——不需要领域模型、设计摘要、资源需求。根因和修复方案来自 debug-analysis.md。

```markdown
# Plan: Fix {bug-summary}

## 概述
{根因描述 + 项目环境}
{从 debug-analysis.md 提炼}

## 行为列表
{从 debug-analysis.md 提取的预期行为，逐条列出}

| # | 行为 |
|---|------|
| 1 | {行为 1 — 玩家可见/系统可感知} |
| 2 | {行为 2} |

## 修复方案
{从 debug-analysis.md 修复方向展开：改什么逻辑、为什么这样改}

## 影响范围
{功能影响面，不是文件变更清单}

| 影响面 | 变更描述 |
|--------|---------|
| ... | ... |

## 任务列表

### [AI] 任务
- `[AI-N]` (type: logic) {描述} (依赖: ...)
- `[AI-N]` (type: logic) 回归测试 — 锁定现有行为，覆盖 BUG 场景 (依赖: ...)

### [HUMAN] 任务
- `[HUMAN]` ...

## 测试策略
| 覆盖 |
|------|
| {交互行为简述} |
```

fix 模式任务类型由 plan-fix 根据根因决定。回归测试囊括在第一个任务中：先锁定行为，再修复根因。

---

## exec 解析规则

exec **只读两个文件**：
1. `{task_dir}/plan.md` — 自包含的设计文档
2. `{task_dir}/progress.json` — 任务追踪

解析 plan.md：
1. **提取 AI 任务**：匹配 `- \[AI-(\d+)\]` 提取序号和描述
2. **提取任务类型**：匹配 `\(type: (logic|visual|ui)\)` 确定任务类型
3. **提取 spec 引用**（visual 任务）：匹配 `spec: (.+?)[) ]` 提取 visual-spec JSON 文件路径
4. **提取 HTML 引用**（ui 任务）：匹配 `html: (.+?)[) ]` 提取 HTML 标准文件路径
5. **提取依赖**：匹配 `(依赖: (.+))` 确定执行顺序
6. **按依赖拓扑排序**：`logic` → `visual` → `ui`，同类型按依赖排序
7. **[HUMAN] 任务不执行**：最终汇总提醒用户
8. **解析测试策略表**：提取每条覆盖内容（行为描述）

---

## 格式校验清单

plan 输出前自检：
- [ ] 概述自包含（含功能目标 + 项目环境）
- [ ] 领域模型覆盖每个功能行为
- [ ] 行为列表覆盖每个玩家可见行为
- [ ] 设计摘要自包含（不引用外部文件如"详见 design.md"）
- [ ] 影响范围描述功能影响面（不写文件路径）
- [ ] 每个 AI 任务有唯一编号 `[AI-N]`
- [ ] 每个 AI 任务标注了类型：`(type: logic)` 或 `(type: visual, spec: ...)` 或 `(type: ui, html: ...)`
- [ ] **每个 AI 任务只有一种 type，不同 type 的任务未合并**
- [ ] visual 任务有 `spec:` 指向 visual-spec JSON 文件
- [ ] UI 任务有 `html:` 指向 HTML 标准文件
- [ ] logic → visual → ui 排序正确
- [ ] 依赖关系引用的编号存在
- [ ] 无循环依赖
- [ ] HUMAN 任务标注了具体操作步骤
- [ ] 资源需求表完整（如有新增资源）
- [ ] 测试策略段只有"覆盖"一列，每条只用行为语言（玩家可感知的功能），不含"源码契约"/"签名契约"/"变量初始化"/"正则匹配"等静态分析术语，不含测试文件名
- [ ] 中间产物已写入 `.work/` 子目录
- [ ] 禁止内容零命中（见下节）
- [ ] **任务列表不含文件路径**（`grep -nP '\[AI-\d+\].*\.(rpy|gd|tscn|tres)\b' plan.md` 零命中）
- [ ] **不含 agent 微指令**（RED/GREEN 步骤、`### [AI-N]` 子章节、"输出文件/任务步骤"）——plan 说 WHAT，agent 决定 HOW
- [ ] **不含代码级 API 调用**（引擎特定 API、`scope[`、`assert len(` 等）——实现细节属于 agent 自主决策
- [ ] **任务描述不含 PascalCase 标识符**（`grep -nP '\[AI-\d+\].*\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b' plan.md` 零命中）——class 名信号
- [ ] **任务描述不含 snake_case 标识符**（`grep -nP '\[AI-\d+\].*\b[a-z]+_[a-z]+(?:_[a-z]+)*\b' plan.md` 零命中）——方法名/变量名信号
- [ ] **Godot 项目：不含 Godot API**（`grep -nPi 'func\s+\w+\s*\(|\.connect\(|queue_free|_ready\b' plan.md` 零命中）
- [ ] **语义复查**：逐条读每个 AI 任务描述，问：① 描述了用户做什么→看到什么吗？② 不看其他任务能判断完成吗？③ 含代码术语吗？——任一条不满足则改写

---

## 禁止内容清单

以下是 plan.md 中**绝对不能出现**的短语和模式。plan 和 plan-fix 输出前，必须用以下 grep 扫描 plan.md，**全部零命中**才可输出。

### 禁止短语

- "lint 代替测试" / "lint 验证"
- "人工启动目视" / "人工验证" / "手动测试"
- "测试基础设施缺失不阻塞" / "测试暂缓" / "跳过测试"
- "源码契约" / "签名契约" / "源码中查找" — 测试策略不能指挥 test agent 用静态分析代替运行时验证
- "变量初始化" / "正则匹配" — 同上，这是测试实现细节
- 任何将 `{test_runner} project test` 之外的验证手段作为替代方案的描述

**验证手段始终且唯一为 `{test_runner} project test`。**

### 自检 grep 命令

**扫描禁止短语：**

```bash
grep -iE '(lint.*(代替|验证|替代)|人工.*(启动|验证|目视)|手动.*(测试|验证)|(测试.*)?缺失.*不阻塞|测试.*暂缓|跳过.*测试)' {task_dir}/plan.md
```

**扫描测试策略中的静态分析语言：**

```bash
grep -iE '(源码契约|签名契约|源码中查找|正则匹配|default\s+\w+\s*=\s*|变量初始化)' {task_dir}/plan.md
```

**扫描 agent 微指令**（plan 的职责是说清 WHAT，HOW 是 exec 和 agent 的领域）：

```bash
grep -nPi '(^\s*\d+\.\s*\*\*RED\*\*|^\s*\d+\.\s*\*\*GREEN\*\*|RED 验证|GREEN 验证|^###\s+\[AI-\d+\]|^\*\*输出文件\*\*|^\*\*任务步骤\*\*)' {task_dir}/plan.md
```

**扫描代码级表达式**（引擎 API 调用是实现细节——agent 自己决定 API）：

```bash
grep -nPi '(scope\[|assert\s+len\(|assert\s+scope)' {task_dir}/plan.md
```

**扫描 Godot 代码级 API**（Godot 项目额外检查）：

```bash
grep -nPi '(func\s+\w+\s*\(|\.connect\(|queue_free|_ready\b|_process\b|_physics_process\b|@export|preload\(|load\()' {task_dir}/plan.md
```

**扫描任务描述中的文件路径**（文件级拆分的信号）：

```bash
grep -nP '\[AI-\d+\].*\.(rpy|gd|tscn|tres)\b' {task_dir}/plan.md
```

**扫描任务描述中的 PascalCase 标识符**（class 名信号）：

```bash
grep -nP '\[AI-\d+\].*\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b' {task_dir}/plan.md
```

**扫描任务描述中的引擎类型名**（Godot: Node3D/MeshInstance3D 等；Ren'Py: Screen/Label 等）：

```bash
grep -nPi '\[AI-\d+\].*\b(Node3D|Node2D|MeshInstance3D|CharacterBody3D|CharacterBody2D|CollisionShape3D|CollisionShape2D|Area3D|Area2D|RigidBody3D|RigidBody2D|StaticBody3D|StaticBody2D|AnimationPlayer|Sprite3D|Sprite2D|Camera3D|Camera2D|Timer|NavigationRegion3D|NavigationRegion2D|CSG|Screen|Label|Imagebutton|Textbutton|Frame|Vbox|Hbox|Grid|Fixed|Viewport)\b' {task_dir}/plan.md
```

**扫描任务描述中的 snake_case 标识符**（方法名/变量名信号）：

```bash
grep -nP '\[AI-\d+\].*\b[a-z]+_[a-z]+(?:_[a-z]+)*\b' {task_dir}/plan.md
```

**扫描测试类任务**（"编写测试"/"回归测试" 等——测试应在各模块 TDD 循环中自然产出，不应作为独立 AI 任务）：

```bash
grep -nPi '\[AI-\d+\].*\b(编写.*测试|回归测试|单元测试|集成测试|测试覆盖|测试.*schema|测试.*完整性)\b' {task_dir}/plan.md
```

### plan 专属（feat/refactor，plan-fix 不需要）

扫描 visual 任务 spec 引用完整性：

```bash
grep -n '(type: visual' {task_dir}/plan.md | grep -v 'spec:'
```

扫描 UI 任务 HTML 引用完整性：

```bash
grep -n '(type: ui' {task_dir}/plan.md | grep -v 'html:'
```
