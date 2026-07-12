---
name: game-dev:design-ui
description: |
  This skill should be used when the user asks to design UI for a game project, produce HTML design mockups, create visual design drafts, or when a conductor detects the task involves visual interface work. Explores existing project UI style, confirms style direction with user, clarifies behavior requirements via brainstorming (with style context to avoid re-asking), then invokes frontend-design to produce HTML mockups. Produces `.work/layouts/*.html` files that become the visual standard for later plan and exec phases. This skill should be invoked BEFORE plan when the task involves new screens or visual redesign of existing screens.
---

# game engine AI 开发 — UI 设计阶段

在 plan 之前执行，产出 HTML 设计稿作为后续所有阶段的视觉真相。**只产出 HTML/CSS 设计稿，不写 game engine 代码。**

---

## 工作流

### 1. 确定任务目录

从 `--task-dir` 参数解析 `task_dir`。如果未传入，从 `{dev_dir}/current-state.json` 读取 `current_task`。如果仍为空，报错退出。

确保 `.work/layouts/` 子目录存在：

```bash
mkdir -p {task_dir}/.work/layouts
```

### 2. 读取需求上下文

从以下文档获取本次 UI 设计的输入：

- `{task_dir}/.work/grill-interview.md` — 用户原始描述（需求侧：功能描述、玩法设想、体验目标；技术侧：引擎选择、技术约束）
- `{dev_dir}/requirements.md` — 项目级全量需求文档（如果存在），了解游戏全貌
- `{task_dir}/.work/requirements.md` — 本次 feat 的行为清单和边界规则

### 3. 探索项目现有 UI 风格

> **前置条件：** conductor 已通过三问分析判断此任务涉及 UI。design-ui 不再重复检测，直接开始风格探索。

扫描项目中的 game engine GUI 配置和已有 screen 定义，提取风格数据：

**扫描范围：**

```bash
# GUI 配置文件
cat {gui_config} 2>/dev/null | head -200

# 已有 screen 定义
grep -rn "screen " {source_dir}/ --include="*.rpy" | head -30

# 样式定义
grep -rn "style " {source_dir}/ --include="*.rpy" | head -30
```

**提取内容：**

| 维度 | 提取内容 | 来源 |
|------|---------|------|
| 配色 | 背景色、文字色、按钮色、高亮/强调色、边框色 | `gui.rpy` 的 `gui.xxx_color` 变量 |
| 字体 | 对话字体、标题字体、UI 标签字体、字号层级 | `gui.rpy` 的 `gui.xxx_font`/`gui.xxx_size` 变量 |
| 布局 | vbox/hbox/fixed/grid 使用习惯、对齐方式、间距规律 | 已有 screen 的 widget 树 |
| 交互 | hover 效果、选中态表达、按钮样式、过渡动画 | 已有 screen 的 button/imagebutton 定义 |
| 插图 | 背景图、立绘、CG 等美术资源的风格倾向 | `image` 定义和实际图片文件 |

**输出风格摘要：**

```markdown
## 项目 UI 风格摘要

### 配色
- 背景: #XXXXXX (来源: gui.background_color)
- 文字: #XXXXXX (来源: gui.text_color)
- 强调: #XXXXXX (来源: gui.accent_color)
- 按钮: #XXXXXX / hover #XXXXXX

### 字体
- 对话: {font_name} {size}px
- 标题: {font_name} {size}px
- UI 标签: {font_name} {size}px

### 布局习惯
- 主菜单: vbox 居中 + 按钮纵向排列
- 对话界面: 文本框底部 + 角色名顶部
- ...

### 交互风格
- hover 效果: {描述}
- 过渡动画: {描述}
- 按钮圆角/边框: {描述}

### 整体风格关键词
{暗黑+金色点缀 / 明亮扁平 / 日系轻小说 / ...}
```

### 4. 风格确认门

将风格摘要呈现给用户，提出选择：

```
## 风格确认

当前项目的 UI 风格如上。请选择方向：

1. **沿用现有风格** — 保持配色/字体/布局习惯，只设计新画面
2. **全新风格** — 换掉整体视觉方向
3. **在现有基础上调整** — 沿用为基础，但要改的部分请描述

请选择 1/2/3。
```

**用户选择后的处理：**

| 选择 | 操作 |
|------|------|
| 沿用 | 锁定当前风格数据，写入风格决策 |
| 全新 | 不传现有风格，brainstorming 帮用户确定新方向 |
| 调整 | 锁定当前风格数据 + 用户指定的调整诉求，写入风格决策 |

**写入风格决策文件** `{task_dir}/.work/style-decision.md`**：**

```markdown
# 风格决策

**决策：** {沿用 / 全新 / 调整}
**锁定时间：** {timestamp}

## 风格数据（brainstorming 和 frontend-design 的共同输入）

{沿用/调整: 完整的风格摘要数据}
{全新: "用户决定换新风格，请帮助确定风格方向。"}
{调整的额外诉求: "在现有基础上需要调整：{用户描述}"}
```

### 5. 需求澄清 — brainstorming

调用 `superpowers:brainstorming` skill 澄清 UI 行为需求。

**传入 brainstorming 的上下文：**

```
## 风格决策（已锁定，勿重复询问）

{style-decision.md 的完整内容}

---
请基于以上风格决策，澄清以下问题：

- 有哪些画面需要设计？（只问画面和行为，不问风格）
- 每个画面包含哪些交互状态？（默认态、hover、选中、禁用、过渡等）
- 每个交互状态的玩家行为是什么？

风格（配色/字体/布局方向）已锁定，不再讨论修改。
```

**关键约束：** 如果风格决策是"沿用"或"调整"，必须在 prompt 中明确："风格数据已锁定，只问画面、行为和交互状态。不要问配色、字体、暗亮等风格问题。"如果风格决策是"全新"，允许 brainstorming 帮用户确定新风格方向。

brainstorming 完成后保存输出：

- 画面清单 + 每个画面的交互状态 → `{task_dir}/.work/requirements.md`（行为部分）
- 如果是全新风格，风格方向 → 追加到 `{task_dir}/.work/style-decision.md`

### 6. 产出 HTML 设计稿 — frontend-design

为每个涉及视觉设计的逻辑屏幕调用 `frontend-design` skill 生成 HTML。

**传入 frontend-design 的上下文：**

```
## 设计约束

### 风格数据
{style-decision.md 中的风格数据}

### 画面规格
{从 brainstorming 确认的画面清单和交互状态}

---
请为以下画面生成 HTML 设计稿：
- {画面1名称}: {交互状态列表}
- {画面2名称}: {交互状态列表}

要求：
- 每个画面一个独立 HTML 文件，内联 CSS，浏览器可直接打开
- 包含该画面的所有交互状态（默认态、hover、选中、禁用、过渡动画）
- 使用 CSS 伪类和过渡表达动态效果
- 严格遵循上述风格数据中的配色、字体、布局习惯
- 颜色、字体、间距、背景等视觉属性精确设置
```

每个画面输出到 `{task_dir}/.work/layouts/{screen_name}.html`。

### 7. 设计稿确认门

确认门是循环，直到用户满意才退出：

1. 输出 HTML 文件后，呈现确认提示：
   ```
   ## UI 设计稿确认

   以下 HTML 文件定义了各画面的视觉标准，请用浏览器打开查看：

   {逐个列出 HTML 文件路径和说明}

   确认后回复"OK"继续。如需调整，请描述具体改动。
   ```

2. 等待用户响应：
   - **"OK"** → 用户确认，退出循环，进入步骤 7
   - **调整诉求** → 将诉求传回 frontend-design，重新生成对应 HTML，回到步骤 1

### 8. 输出摘要

```
## Design UI 完成

**风格决策：** {沿用 / 全新 / 调整}
**设计稿：**
{逐个列出 HTML 文件}

**下一步：** conductor 调用 plan 进行技术拆分
```

---

## Completion Gate

永远不要声称任务完成，除非：

1. 风格决策已写入 `{task_dir}/.work/style-decision.md`
2. 所有 HTML 设计稿已写入 `{task_dir}/.work/layouts/`
3. 用户已确认设计稿（回复 "OK" 或等效确认）
4. 输出摘要已呈现
