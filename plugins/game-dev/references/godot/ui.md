# Godot UI 原则

coding agent 在编写 Control 节点代码和 Theme 资源时必须遵守的规则。

---

## 布局容器原则

### 布局容器不能有视觉属性

`VBoxContainer` / `HBoxContainer` / `GridContainer` 是纯布局工具，不应设置背景色、边框等视觉属性。

```gdscript
# Bad — 布局容器上设置了视觉
var vbox := VBoxContainer.new()
vbox.add_theme_stylebox_override("panel", some_stylebox)

# Good — 用 Panel 或 PanelContainer 包裹
var panel := Panel.new()
var vbox := VBoxContainer.new()
panel.add_child(vbox)
```

### 互斥属性

以下属性对在 Godot Control 上是互斥的，同时设置会导致不可预期的布局行为：

| 属性 A | 属性 B | 说明 |
|--------|--------|------|
| `anchor_left` + `anchor_right` | `size.x` | anchor 相减决定宽度 |
| `anchor_top` + `anchor_bottom` | `size.y` | anchor 相减决定高度 |
| `expand` (Container) | `size_flags_fill` | 功能重叠 |

## Theme 组织

### 一个概念，一个定义

颜色、字体、字号在 Theme 中定义一次，所有 Control 通过 theme 引用。不允许在代码中硬编码颜色值：

```gdscript
# Bad — 硬编码颜色
label.add_theme_color_override("font_color", Color(1, 0.2, 0.2))

# Good — 使用 Theme 中的常量
const ACCENT_COLOR := Color(1, 0.2, 0.2)
label.add_theme_color_override("font_color", ACCENT_COLOR)
```

### Theme 类型变体

Godot 支持按节点类型定义不同样式。利用类型继承链：

```
Button (base)
  → Button.primary (variant)
  → Button.danger (variant)
```

```gdscript
# 定义变体
theme.set_stylebox("normal", "Button.primary", primary_stylebox)
theme.set_stylebox("hover", "Button.primary", primary_hover_stylebox)
```

## 信号连接

### 代码连接优先

信号连接写在 .gd 中，不写入 .tscn。这样 grep 能找到所有连接，重构时不会遗漏：

```gdscript
# Good — 代码连接
func _ready() -> void:
    start_button.pressed.connect(_on_start_pressed)

# Bad — .tscn 中连接（编辑器拖拽）
# [connection signal="pressed" from="StartButton" to="." method="_on_start_pressed"]
```

## 场景结构

### 每个场景自包含

场景应能独立运行。外部依赖通过 `@export` 变量接收，不硬编码路径引用其他场景。

### 节点命名

- 使用 PascalCase 命名节点（Godot 默认风格）
- 关键交互节点命名清晰：`StartButton`、`HealthLabel`、`PlayerSprite`
- 容器节点可简写：`VBox`、`HBox`、`Grid`

## HTML → Godot UI 翻译

当 design-ui 产出 HTML 设计稿后，按以下映射翻译为 Godot UI：

| HTML/CSS | Godot 等价 |
|----------|-----------|
| `<div style="display:flex; flex-direction:column">` | `VBoxContainer` |
| `<div style="display:flex; flex-direction:row">` | `HBoxContainer` |
| `<div style="background:...; padding:...">` | `Panel` + `PanelContainer` |
| `<button>` | `Button` |
| `<button class="primary">` | `Button` with theme type variation |
| `<p>` / `<span>` | `Label` |
| `<img>` | `TextureRect` |
| `<input>` | `LineEdit` |
| `gap: 12px` | `theme_override_constants/separation: 12` (Container) |
| `padding: 8px 16px` | `theme_override_constants/margin_*` |
| `border-radius: 8px` | `StyleBoxFlat.corner_radius_*` |
| `background: #333` | `StyleBoxFlat.bg_color` |
| `color: #fff` | `theme_override_colors/font_color` |
| `font-size: 16px` | `theme_override_font_sizes/font_size` |
| `:hover` | `theme_override_styleboxes/hover` |
| `:active` | `theme_override_styleboxes/pressed` |
| `transition: all 0.3s` | AnimationPlayer / Tween |

## 颜色系统

### 全局颜色常量（Theme 中定义）

```
BASE_BG:     #1a1a2e   — 主背景
PANEL_BG:    #16213e   — 面板背景
ACCENT:      #e94560   — 强调色
TEXT_PRIMARY: #ffffff  — 主文字
TEXT_SECONDARY: #a0a0b0 — 次要文字
BUTTON_BG:   #0f3460   — 按钮背景
BUTTON_HOVER: #1a508b  — 按钮悬停
```

## UI 自查清单

coding agent 在完成 UI 任务后必须检查：

- [ ] 布局容器上无视觉属性（`hseparation` / `vseparation` 除外）
- [ ] 无互斥 anchor 和 size 同时设置
- [ ] 颜色值通过 Theme 或 const 定义，无硬编码
- [ ] 信号连接写在 .gd 中，不写入 .tscn
- [ ] 关键交互节点有有意义的名称（方便 `get_node()` 查找）
- [ ] `StyleBoxFlat` 的 `content_margin_*` 正确设置（Godot 的 padding）
