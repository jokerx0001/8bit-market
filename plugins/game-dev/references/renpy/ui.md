# Ren'Py UI 编码原则

coding-agent 在 UI 翻译模式下必须遵守此文件。违反任何一条 → REFACTOR 阶段必须修正。

---

## 1. 样式层级唯一性

同一视觉属性只在一个层级定义。层级从低到高：

```
default → named style → inline property
```

**规则：**

- 跨 screen 共用的视觉属性 → 提取为 `style xxx:` 命名样式
- 单个 screen 内多次出现的属性 → screen 文件顶部定义命名样式
- 仅出现一次且无复用价值的属性 → 可以用 inline
- **禁止**：named style 定义了 `color`，inline 又写 `color` 覆盖 → 删掉 inline

**命名样式自动继承（Ren'Py 下划线规则）：**

```renpy
style my_button:      # 自动继承 style button → 继承 window 属性
    color "#f00"      # 只写差异部分
```

`my_button` 包含下划线 → 父级是 `button`。不需要 `is button` 声明。

**反例：**

```renpy
# BAD: 多层定义
style card_button:
    background "#333"
    color "#fff"

textbutton "选择":
    style "card_button"
    background "#444"      # ← 冗余，层冲突
    color "#eee"           # ← 冗余，层冲突
```

---

## 2. 互斥属性检查清单

以下属性组不能同时出现。来自 Ren'Py 官方文档 `style_properties.html`：

| 组 | 冲突属性 | 解释 |
|----|---------|------|
| **x位置** | `xalign` ↔ `xpos` + `xanchor` | `xalign` 同时设 xpos 和 xanchor |
| **y位置** | `yalign` ↔ `ypos` + `yanchor` | 同上 |
| **中心定位** | `xcenter` ↔ `xalign` / `xpos` | `xcenter` 设 xpos=值, xanchor=0.5 |
| **尺寸锁定** | `xsize` ↔ `xminimum` + `xmaximum` | `xsize` = 同时设两者为相同值 |
| **弹性vs固定** | `xfill` ↔ `xsize` | `xfill=True` 需要弹性空间，`xsize` 锁死尺寸 |
| **全属性覆盖** | `area` ↔ 任何位置/尺寸属性 | `area` 一次性设 xpos, ypos, xanchor, yanchor, x/y min/max, xfill, yfill |
| **内边距简写** | `xpadding` ↔ `left_padding` / `right_padding` | `xpadding` 覆盖左右 |
| **外边距简写** | `xmargin` ↔ `left_margin` / `right_margin` | 同上模式 |
| **间距覆盖** | `spacing` ↔ `first_spacing` | `first_spacing` 覆盖第一个间距 |
| **网格间距** | `spacing` ↔ `xspacing` / `yspacing` | `xspacing`/`yspacing` 优先 |
| **fixed收缩** | `fit_first` ↔ `xfit` / `yfit` | 不同参考点，语义冲突 |

**自检方法**：写完 screen 后 grep 每个属性名，出现超过一次就需要审查。

---

## 3. 容器零样式

若容器仅用于布局（排列子元素），不加 visual 属性：

```renpy
# GOOD: 纯布局 vbox
vbox:
    spacing 10
    textbutton "A"
    textbutton "B"

# BAD: 不必要的样式
vbox:
    spacing 10
    background "#fff"     # ← 不必要，vbox 默认透明
    xpadding 20            # ← 需要 padding 应该用 frame 包
    textbutton "A"
    textbutton "B"
```

**需要背景/边距 → 用 `frame`（自带 background/padding 语义），不是给 vbox 加样式。**

---

## 4. textbutton/imagebutton 自带 window 属性

`textbutton` 继承 `button` → `button` 继承 `window`，所以 textbutton 已有：

- `background`, `foreground`
- `left_padding`, `right_padding`, `top_padding`, `bottom_padding`
- `left_margin`, `right_margin`, `top_margin`, `bottom_margin`
- `hover_background`, `insensitive_background`, `selected_background` 等状态变体

**禁止**给 textbutton 外面包一个 frame 来加背景 — 这是双重背景。

```renpy
# BAD: 嵌套冗余
frame:
    background "#333"
    textbutton "确认"     # textbutton 自己就能设 background

# GOOD: 直接样式
textbutton "确认":
    style "confirm_btn"   # style 里设 background "#333"
```

---

## 5. 一概念一定义

同一个视觉概念（颜色、字体、间距模式）在多个位置出现时，提取为命名样式或变量：

```renpy
# BAD: 颜色散落
textbutton "A" color "#ff6b6b"
textbutton "B" color "#ff6b6b"
text "提示" color "#ff6b6b"

# GOOD: 统一定义
define accent_color = "#ff6b6b"
# 或在 style 中
style accent_text:
    color "#ff6b6b"
```

---

## 6. Ren'Py UI 特殊约束

### Frame 单子元素

`frame` 只能有一个子元素。多个子元素会被自动包在 `fixed` 里，产生意外布局。用 `has vbox` 或 `has hbox` 显式控制：

```renpy
# GOOD
frame:
    has vbox
    text "标题"
    textbutton "按钮"

# BAD
frame:
    text "标题"        # ← 自动包入 fixed，布局不可控
    textbutton "按钮"
```

### 默认尺寸

不同于 HTML 的 block 元素默认撑满宽度，Ren'Py displayable 默认收缩到内容尺寸。需要用 `xfill True` 或 `xsize` 显式控制。

### 不支持 border-radius

Ren'Py 不支持 CSS `border-radius`。圆角方案：
- 用 `Frame("rounded_panel.png", ...)` 九宫格图片
- 用预切好的圆角背景图
- 简单直角设计

---

## 7. 输出自检

GREEN report 末尾必须包含「样式定义清单」：

```
### 样式定义清单

| 样式名 | 定义属性 | 用途 |
|--------|---------|------|
| card_button | background "#333", color "#fff" | 角色选择卡片 |
| confirm_btn | background "#4a4", xpadding 20 | 确认按钮 |
| (无命名样式) | — | 仅 inline，无复用 |

**自检结果：**
- [ ] 无互斥属性同时出现
- [ ] 无重复样式定义
- [ ] 无容器被不必要样式污染
- [ ] 无 textbutton 外嵌套 frame
```

清单为空也必须输出（证明检查过）。
