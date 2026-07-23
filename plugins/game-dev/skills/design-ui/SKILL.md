---
name: game-dev:design-ui
description: |
  This skill should be used when the user asks to design UI for a game project, produce HTML design mockups, create visual design drafts, or when a conductor detects the task involves visual interface work. Explores existing project UI style, confirms style direction with user, clarifies behavior requirements via brainstorming (with style context to avoid re-asking), then invokes frontend-design to produce HTML mockups. Produces `.work/layouts/*.html` files that become the visual standard for later plan and exec phases. This skill should be invoked BEFORE plan when the task involves new screens or visual redesign of existing screens.
---

# Game Dev AI — UI 设计阶段

在 plan 之前执行，产出 HTML 设计稿作为后续所有阶段的视觉真相。**只产出 HTML/CSS 设计稿，不写 game engine 代码。**

---

## 工作流

### 0. 加载技术栈配置

从 `--tech` 参数获取技术栈标识。如果未传入，从 `{dev_dir}/current-state.json` 读取 `tech` 字段。如果仍为空，报错退出。

```bash
# 示例：tech = renpy | godot
```

加载以下技术栈参考文件：

- `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md` — 源码路径、文件扩展名、项目结构
- `${CLAUDE_PLUGIN_ROOT}/references/{tech}/ui.md` — UI 原则 + 风格探索命令

从 config.md 提取：

| 字段 | 来源 | 用途 |
|------|------|------|
| `script_ext` | 脚本路径（如 `*.rpy` / `*.gd`） | 搜索 screen/page 定义 |
| `source_dir` | 源码目录（如 `game/` / 项目根） | 限定搜索范围 |
| `scene_ext` | 场景文件扩展名（如 `*.tscn`，Ren'Py 此项为空） | 搜索场景 UI |
| `theme_ext` | 主题/资源文件扩展名（如 `*.tres`，Ren'Py 此项为空） | 搜索主题配置 |

### 1. 确定任务目录

从 `--task-dir` 参数解析 `task_dir`。如果未传入，从 `{dev_dir}/current-state.json` 读取 `current_task`。如果仍为空，报错退出。

确保 `.work/layouts/` 子目录存在：

```bash
mkdir -p {task_dir}/.work/layouts
```

### 2. 读取需求上下文

从以下文档获取本次 UI 设计的输入：

- `{task_dir}/.work/user-prompt.md` — 用户原始输入（原语），检查用户是否直接指示了 UI 风格、配色、布局等视觉偏好
- `{task_dir}/.work/grill-interview.md` — grilling 采访记录, 对用户原始输入的偏差确认，防止理解错误
- `{dev_dir}/requirements.md` — 项目级全量需求文档（如果存在），了解游戏全貌
- `{task_dir}/.work/requirements.md` — 本次 feat 的行为清单和边界规则

### 3. 探索项目现有 UI 风格

按以下优先级寻找风格参考。找到即停止，不继续后续优先级。

**优先级 1 — 历史 design-ui 产出的 layout.html：**

搜索 `{dev_dir}/` 下所有 `feat-*/` 和 `refactor-*/` 目录，找到 `.work/layouts/*.html` 文件。取最新（按目录编号降序）的 HTML 文件作为风格参考。

```bash
find {dev_dir}/feat-* {dev_dir}/refactor-* -path "*/.work/layouts/*.html" 2>/dev/null | sort -r | head -5
```

**优先级 2 — concept-art 产出的 reference.png：**

如果无历史 layout.html，检查 `{task_dir}/reference.png`（orchestrator 阶段 4a 已生成）。用 mmx vision 提取风格信息：

```bash
mmx vision describe --image {task_dir}/reference.png \
  --prompt "Describe the UI style in this screenshot: color palette, typography feel, layout patterns, button styling, and overall visual aesthetic. Describe in 3-5 sentences."
```

**优先级 3 — 用户描述或指定文件：**

如果以上皆不存在，检查 `{task_dir}/.work/user-prompt.md`（用户原语）和 `{task_dir}/.work/grill-interview.md` 中是否有风格相关的描述或指定的参考文件路径。如果有指定文件，用 mmx vision 读取其风格。

**优先级 4 — 自行决定：**

如果以上全部不存在，根据游戏类型和 genre convention 自行确定一个合适的 UI 风格方向。

---

**从找到的风格参考中提取以下维度，输出风格摘要：**

```markdown
## 项目 UI 风格摘要

**来源：** {layout.html 路径 / reference.png / 用户描述 / 自行决定}

### 配色
- 背景: #XXXXXX
- 文字: #XXXXXX
- 强调: #XXXXXX
- 按钮: #XXXXXX / hover #XXXXXX

### 字体
- 对话: {font_name} {size}px
- 标题: {font_name} {size}px
- UI 标签: {font_name} {size}px

### 布局习惯
- {从参考中提取的布局模式}
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

**在生成 HTML 前，读取 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/ui.md` 的 UI 原则节**，确保 HTML 设计稿中的视觉表达与该引擎的能力边界对齐（如：某引擎不支持 `border-radius` 则 HTML 中避免使用圆角设计；某引擎按钮自带 padding 则 HTML 按钮遵循相同规则）。

**传入 frontend-design 的上下文：**

```
## 设计约束

### 技术栈
{tech}

### 引擎 UI 约束
{从 {tech}/ui.md 提取的关键约束——如不支持 border-radius、默认尺寸行为、容器规则等}

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
- 遵循引擎 UI 约束，不设计引擎无法实现的效果
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
   - **"OK"** → 用户确认，退出循环，进入步骤 8
   - **调整诉求** → 将诉求传回 frontend-design，重新生成对应 HTML，回到步骤 1

### 8. 输出摘要

```
## Design UI 完成

**技术栈：** {tech}
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
