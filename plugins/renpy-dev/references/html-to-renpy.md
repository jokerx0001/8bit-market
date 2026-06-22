# HTML → Ren'Py Screen Language 翻译指南

coding-agent UI 翻译模式必读。将 HTML/CSS 概念映射到 Ren'Py Screen Language。

---

## 核心差异

| HTML/CSS | Ren'Py |
|----------|--------|
| block 元素默认 100% 宽度 | displayable 默认收缩到内容尺寸 |
| `margin` 推离外部 | `margin` 同语义（透明空间） |
| `padding` 推离内部 | `padding` 同语义（`window`/`frame`/`button`） |
| `border` | 无原生 border。用 `Frame()` 图片或 `background` |
| `border-radius` | **不支持**。用九宫格 `Frame()` 图片方案 |
| `box-shadow` | 不支持。预切背景图替代 |
| CSS 动画 `@keyframes` | ATL `transform` 语句 |

---

## 布局结构映射

### Flexbox → Box 容器

```css
/* HTML: 垂直排列 */
.container {
    display: flex;
    flex-direction: column;
    gap: 10px;
}
```

```renpy
# Ren'Py:
vbox:
    spacing 10
    # children
```

```css
/* HTML: 水平排列 */
.row {
    display: flex;
    flex-direction: row;
    gap: 12px;
}
```

```renpy
# Ren'Py:
hbox:
    spacing 12
    # children
```

### 网格 → Grid

```css
.grid { display: grid; grid-template-columns: repeat(3, 1fr); }
```

```renpy
grid 3 2:  # 3列 2行
    # children (必须恰好 cols×rows 个)
```

### 绝对定位 → Fixed

```css
.absolute-container { position: relative; }
.child { position: absolute; left: 100px; top: 50px; }
```

```renpy
fixed:
    textbutton "X" xpos 100 ypos 50
```

### 带背景面板 → Frame

CSS:
```css
.panel {
    background: #2a2a2a;
    padding: 16px;
    border-radius: 8px;
}
```

Ren'Py:
```renpy
frame:
    background "#2a2a2a"
    xpadding 16
    ypadding 16
    # border-radius 不支持，需 Frame() 图片替代
    has vbox
    # children
```

**关键**：`frame` 只接受 1 个子元素。多个子元素时用 `has vbox`/`has hbox` 显式声明容器。

---

## 元素映射

### div

| CSS 特征 | Ren'Py |
|----------|--------|
| 纯布局（无 background） | `vbox` / `hbox` / `fixed` |
| 有 `background` + 有子元素 | `frame`（单子）/ `frame` + `has vbox` |
| `display:flex` + `background` | `frame` + `has vbox`/`has hbox` |

### button → textbutton / imagebutton

```html
<button class="primary">确认</button>
```

```renpy
textbutton "确认":
    style "primary_btn"  # 含 background, color, padding 等
    action Return(True)
```

`textbutton` 以下属性关键：
- `action` — 点击行为（必须）
- `hovered` / `unhovered` — hover 回调
- `selected` — 选中态表达式
- `sensitive` — 可交互条件

### 文本 → text

```html
<p class="title">角色选择</p>
```

```renpy
text "角色选择":
    style "title_text"
```

### 图片 → add

```html
<img src="character.png" width="200" height="300">
```

```renpy
add "character.png" xsize 200 ysize 300
# 或
add "character.png" size (200, 300)
```

### 输入框 → input

```html
<input type="text" placeholder="输入名字">
```

```renpy
input:
    value VariableInputValue("player_name")
    default "输入名字"
```

---

## 样式映射

### 颜色

```css
color: #ff6b6b;
background-color: #333333;
```

```renpy
color "#ff6b6b"
background "#333333"
```

### 字体大小

```css
font-size: 24px;
```

```renpy
size 24
```

### 宽度/高度

```css
width: 200px;
height: 50px;
width: 100%;
```

```renpy
xsize 200          # 固定像素
ysize 50
xfill True          # 撑满 (≈ width: 100%)
```

### 间距

```css
margin: 20px;              /* 外边距 */
padding: 12px 16px;        /* 内边距 */
gap: 10px;                 /* flex 子元素间距 */
```

```renpy
xmargin 20 ymargin 20        # margin
xpadding 16 ypadding 12      # padding (注意顺序)
spacing 10                    # vbox/hbox 子元素间距
```

### 对齐

```css
text-align: center;
justify-content: center;
align-items: center;
```

```renpy
text_align 0.5           # 文本居中 (≈ text-align)
xalign 0.5 yalign 0.5    # 自身居中 (≈ align-self)
```

**注意**：`box_align` 控制 box 内容对齐（≈ justify-content/align-items），但设置后 `xfill`/`yfill` 失效。

---

## 状态映射

```css
/* CSS */
.button { background: #333; }
.button:hover { background: #555; }
.button:active { background: #111; }
.button:disabled { opacity: 0.5; }
```

```renpy
# Ren'Py — 状态前缀属性
textbutton "确认":
    background "#333"          # idle (正常态)
    hover_background "#555"    # hover
    selected_background "#111" # 选中/按下
    insensitive_background "#333"  # disabled
    insensitive_color "#888"
```

Ren'Py 支持的状态前缀：`idle_`, `hover_`, `selected_`, `insensitive_`, `selected_idle_`, `selected_hover_`, `selected_insensitive_`

---

## CSS 过渡/动画 → ATL Transform

```css
.button { transition: all 0.3s ease; }
.button:hover { transform: scale(1.1); }
```

```renpy
transform button_hover:
    ease 0.3 zoom 1.1

textbutton "确认" at button_hover:
    hovered SetVariable("btn_hover", True)
    unhovered SetVariable("btn_hover", False)
```

复杂的入场/退场动画用 ATL `transform` + `on show`/`on hide` 事件。

---

## 不支持的特性及替代方案

| 不支持 | 替代方案 |
|--------|---------|
| `border-radius` | `Frame("rounded_bg.png", 12, 12, ...)` 九宫格图片 |
| `box-shadow` | 预切带阴影的背景图 |
| `gradient` (CSS) | Ren'Py `LinearGradient()` 或预切渐变图 |
| `opacity` (CSS transition) | ATL `alpha` 动画 |
| `grid-template-areas` | Ren'Py `grid` 只支持等大单元格。复杂布局用 `fixed` + 手动 `xpos`/`ypos` |
| `overflow: scroll` | `viewport` 组件 |
| `position: sticky` | 不支持。用独立 screen + `zorder` 模拟 |
| `@media` 响应式 | `variant` 语句区分设备 |

---

## 不确定时

用 `WebFetch` 查 Ren'Py 官方文档：
```
https://www.renpy.org/doc/html/screens.html
https://www.renpy.org/doc/html/style_properties.html
https://www.renpy.org/doc/html/transforms.html
https://www.renpy.org/doc/html/screen_actions.html
```

参照 `plugins/renpy-dev/references/renpy-docs.md` 的页面索引和查询模式。
