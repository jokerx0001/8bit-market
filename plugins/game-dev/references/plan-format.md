# Plan 文件格式规范

此文件定义 plan → exec 的共享契约：plan.md 是 exec 读取的**唯一设计文档**。

---

## 目录结构

```
{dev_dir}/{kind}-{N}/
├── plan.md          ← 自包含，exec 唯一读取，人类唯一审查
├── progress.json    ← exec 任务追踪，断点续跑
├── impact.md        ← 仅 refactor，修改范围约束（根目录，不在 .work/ 里）
└── .work/           ← 中间产物，可追溯但不审查
    ├── requirements.md
    ├── architecture.md
    ├── design.md
    └── debug-analysis.md  ← 仅 fix，根因分析
```

---

## plan.md 必须自包含

exec 不读 `.work/` 下的任何文件。plan.md 必须包含 exec 需要的**全部信息**：

```markdown
# Plan: {feature-name}

## 概述
{功能目标 + 项目环境 + 测试基础设施状态}
{这部分吸收 requirements.md 的核心}

## 设计摘要
{关键设计决策，从 architecture.md + design.md 提炼}
{不能写"详见 design.md"——必须把关键决策写在这里}

- Screen 结构: {screen 划分和跳转关系}
- 数据流: {label 间传递的数据、持久化方式}
- 关键交互: {用户操作 → 响应 → 结果}

## 行为列表

{从用户确认的行为清单中提取。每条是一个玩家可见的行为 → 一个 testcase。用自然语言描述，不写代码。}

示例：

| # | 行为 | 验证方式 |
|---|------|---------|
| 1 | 玩家进入主菜单 → 看到 character_select screen | screenshot: 默认布局基线 |
| 2 | 玩家点击第2个角色卡片 → 卡片视觉高亮 | screenshot: 高亮状态 |
| 3 | 玩家选中角色后点击"确认" → 跳转到 start_game | assert label + behavior |
| 4 | 玩家未选中角色点击"确认" → 停留在当前 screen | behavior |

**行为列表的作用：** test-agent 将它作为 testcase 的蓝图——每条行为对应一个 testcase。coding-agent 将它作为实现目标——每条行为是必须支持的功能。

## 影响范围
{所有涉及的文件，新建/修改}
| 类型 | 文件 | 操作 |
|------|------|------|
| screen | game/screens.rpy | 新增 xxx_screen |
| script | game/script.rpy | 修改 — 新增 label |
| 新建 | game/xxx.rpy | 创建 |

> **注意：** 此表供 exec 了解涉及的文件范围。**任务列表不按此表拆分**——任务按功能模块拆分（见 SKILL.md step 7c），一个文件可以被多个任务增量修改。

## 任务列表

### [AI] 任务

**格式：**

```
- [AI-N] (type: {logic|ui}) {描述} (依赖: AI-X, AI-Y)
- [AI-N] (type: ui, html: .work/layouts/{screen}.html) {描述} (依赖: AI-X)
```

**`{描述}` 约束：** 每个 AI 任务是一行行为描述，不是多段落文档。用功能行为语言——描述用户/系统可感知的功能，不含文件路径（源码文件名）。禁止 `### [AI-N]` 子章节展开、RED/GREEN 步骤、"输出文件/任务步骤" 指令。详见 SKILL.md step 7 的好/坏对照。

**类型分类规则：**

| 类型 | 定义 | 示例 |
|------|------|------|
| `logic` | 数据/流程/基础 screen 骨架/widget 树/交互逻辑 | 创建 screen 基本结构（widget 排列不含精调样式）、label 跳转、变量初始化、持久化读写 |
| `ui` | 匹配 HTML 设计稿的视觉还原：颜色/背景/字体大小/间距/状态样式/自定义 style | 对照 HTML 标准文件精调 screen 的 visual 属性 |

`logic` 可以写基础 screen 和 widget 树 — 不含精细视觉调整。`ui` 任务依赖对应的 logic 任务，在 logic 提供的骨架上做视觉还原。

**UI 任务必须标注 `html:` 指向 HTML 标准文件路径**（相对于 task_dir）。

**排序约束：** 所有 `logic` 任务排在 `ui` 任务前面。`ui` 任务依赖同 screen 的最后一个 logic 任务。

### [HUMAN] 任务

- `[HUMAN]` {具体操作步骤}

## 测试策略

测试策略声明**覆盖什么行为**。

**每条覆盖描述只能写高层次的玩家可感知功能，禁止写验证技术手段。

```
✅ "角色选择交互（选中/取消/确认）; visual: 默认布局基线"
❌ "数据层：default 变量初始化、qte_phase 初始 'waiting'"
❌ "modal True 源码契约、zorder 200 源码契约、4 参数签名契约"
```

```markdown
## 测试策略
| 覆盖 |
|------|
| {交互行为简述}; visual: {视觉状态简述} |
```

**示例：**

```markdown
## 测试策略
| 覆盖 |
|------|
| 角色选择交互（选中/取消/确认）; visual: 默认布局基线、选中高亮状态 |
| 确认跳转逻辑（选中→跳转、未选中→停留） |
```

---

## exec 解析规则

exec **只读两个文件**：
1. `{task_dir}/plan.md` — 自包含的设计文档
2. `{task_dir}/progress.json` — 任务追踪

解析 plan.md：
1. **提取 AI 任务**：匹配 `- \[AI-(\d+)\]` 提取序号和描述
2. **提取任务类型**：匹配 `\(type: (logic|ui)\)` 确定任务类型
3. **提取 HTML 引用**（ui 任务）：匹配 `html: (.+?)[) ]` 提取 HTML 标准文件路径
4. **提取依赖**：匹配 `(依赖: (.+))` 确定执行顺序
5. **按依赖拓扑排序**：`logic` 任务优先于 `ui` 任务，同类型按依赖排序
6. **[HUMAN] 任务不执行**：最终汇总提醒用户
7. **解析测试策略表**：提取每条覆盖内容（行为描述）

spawn coding-agent 时，若任务类型为 `ui`，在 prompt 中添加 `## UI 任务\nhtml: {task_dir}/{html_path}`。coding-agent 内置 UI 翻译模式，检测到此标记后自动激活。
spawn test-agent 时，对于 `ui` 任务，明确要求只测行为（advance/click/assert），不做 `screenshot ... max_pixel_difference` 像素对比。

---

## 格式校验清单

plan 输出前自检：
- [ ] 设计摘要自包含（不引用外部文件如"详见 design.md"）
- [ ] 每个 AI 任务有唯一编号 `[AI-N]`
- [ ] 每个 AI 任务标注了类型：`(type: logic)` 或 `(type: ui, html: ...)`
- [ ] UI 任务有 `html:` 指向 HTML 标准文件
- [ ] logic 任务排在 ui 任务前面
- [ ] 依赖关系引用的编号存在
- [ ] 无循环依赖
- [ ] HUMAN 任务标注了具体操作步骤
- [ ] 影响范围表列出了所有涉及的文件
- [ ] 测试策略段只有"覆盖"一列，每条只用行为语言（玩家可感知的功能），不含"源码契约"/"签名契约"/"变量初始化"/"正则匹配"等静态分析术语，不含测试文件名
- [ ] 中间产物已写入 `.work/` 子目录
- [ ] 禁止内容零命中（不含"lint 代替测试"、"人工验证"等）——验证手段唯一：`{test_runner} project test`
- [ ] **任务列表不含文件路径**（`grep -nP '\[AI-\d+\].*\.(rpy|gd|tscn|tres)\b' plan.md` 零命中）
- [ ] **不含 agent 微指令**（RED/GREEN 步骤、`### [AI-N]` 子章节、"输出文件/任务步骤"）——plan 说 WHAT，agent 决定 HOW
- [ ] **不含代码级 API 调用**（引擎特定 API、`scope[`、`assert len(` 等）——实现细节属于 agent 自主决策

---

## 禁止内容清单

以下是 plan.md 中**绝对不能出现**的短语和模式。plan 和 plan-fix 输出前，必须用以下 grep 扫描 plan.md，**全部零命中**才可输出。

### 禁止短语

- "lint 代替测试" / "lint 验证" / "Ren'Py Lint"
- "人工启动目视" / "人工验证" / "手动测试"
- "测试基础设施缺失不阻塞" / "测试暂缓" / "跳过测试"
- "源码契约" / "签名契约" / "源码中查找" — 测试策略不能指挥 test agent 用静态分析代替运行时验证
- "default xxx = yyy" / "变量初始化" / "正则匹配" — 同上，这是测试实现细节
- 任何将 `{test_runner} project test` 之外的验证手段作为替代方案的描述

**验证手段始终且唯一为 `{test_runner} project test`。**

### 自检 grep 命令

**扫描禁止短语：**

```bash
grep -iE '(lint.*(代替|验证|替代)|人工.*(启动|验证|目视)|手动.*(测试|验证)|(测试.*)?缺失.*不阻塞|测试.*暂缓|跳过.*测试|Ren.Py Lint)' {task_dir}/plan.md
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

**扫描任务描述中的文件路径**（文件级拆分的信号）：

```bash
grep -nP '\[AI-\d+\].*\.(rpy|gd|tscn|tres)\b' {task_dir}/plan.md
```

### plan 专属（feat/refactor）

仅 plan（非 plan-fix）额外扫描 UI 任务 HTML 引用完整性：

```bash
grep -n '(type: ui' {task_dir}/plan.md | grep -v 'html:'
```
