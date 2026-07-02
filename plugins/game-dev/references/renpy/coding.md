# Ren'Py Coding Reference

最佳实践和已知陷阱。每一条都是从真实调试中发现的——官方文档不会明确告诉你这些。

---

## Init 优先级

Ren'Py 按优先级从低到高执行 init 块。默认优先级 0。`< 0` 用于库/主题，`>= 0` 用于普通游戏代码。同优先级按 Unicode 文件名排序，文件内自上而下。

### 最佳实践

参考 FMV_Template 项目中的成熟模式：

```
优先级 -2  →  GUI 基础常量（gui.rpy: init offset = -2 → init python:）
               字体、颜色、尺寸等被 style 和 screen 引用的基础值

优先级 -1  →  样式定义（style 语句，用 init -1: 包裹）
               样式引用 gui 常量（-2 已就绪），需要在 screen 加载前存在

优先级  0  →  游戏逻辑常量、辅助函数（init python:，默认）
               不依赖 -1/-2 的东西可以留在这里
```

### 两种控制方式

```renpy
# 方式 1: 文件级偏移（影响该文件所有后续 init 块）
init offset = -2

# 方式 2: 块级显式指定
init -1:
    style my_button is button:
        ...
```

**规则：** 如果文件中只有部分代码需要提前优先级，用 `init N:` 块级指定。如果整个文件（如 gui.rpy）都需要某个优先级，用 `init offset = N`。

---

## Screen Language

### `$` Python 语句不能在 widget 列表中使用

```renpy
# WRONG — $ 不能出现在 vbox/hbox 的子 widget 序列中
screen encyclopedia():
    vbox:
        for entry in entries:
            $ unlocked = encyclopedia_is_unlocked(entry.id)  # SYNTAX ERROR
            textbutton entry.name action ...

# RIGHT — 用内联表达式或 screen default 预计算
screen encyclopedia():
    default unlocked_set = encyclopedia_get_unlocked_set()
    vbox:
        for entry in entries:
            textbutton entry.name:
                sensitive (entry.id in unlocked_set)
                action ...
```

**原因：** Screen language 的 `for` 循环在 widget 容器（vbox/hbox）中期望子 widget，不是 Python 语句。`$` 是 Python 语句，不是 widget。widget 属性内的内联表达式可以正常工作。

### textbutton 本身就是 button，不要嵌套 frame

```renpy
# WRONG
frame:
    background "#333"
    textbutton "Click me" action ...

# RIGHT
textbutton "Click me":
    background "#333"
    action ...
```

**原因：** `textbutton` 就是 `button`，已有 `background`、`padding`、`margin` 等属性。多余嵌套会打乱布局和 hover 行为。

### 容器选择

| 容器 | 用途 |
|------|------|
| `vbox` / `hbox` | 纯布局——不加 visual 属性 |
| `frame` | 需要背景的面板——单子节点，多用 `has vbox`/`has hbox` 包装多个子节点 |
| `fixed` | 绝对定位（子节点用 xpos/ypos） |

```renpy
# WRONG — 用纯布局容器加 visual 属性
vbox:
    background "#333"

# RIGHT — 用 frame 加背景
frame:
    background "#333"
    has vbox spacing 10
```

### 互斥属性对

以下不能共存。写了两者，一个会静默覆盖另一个：

| 用这个 | 不要用这个 |
|--------|-----------|
| `xalign 0.5` | `xpos` |
| `yalign 0.5` | `ypos` |
| `xsize 200` | `xfill True` |
| `ysize 100` | `yfill True` |

跨层（named style + inline）同时定义也会触发此问题。

### Style 自动继承用下划线前缀

```renpy
style my_button:        # 自动继承 style button
style my_button_small:  # 自动继承 style my_button
```

下划线前的部分被识别为父 style 名。不需要自动继承时用显式 `is` 或改用连字符命名。

---

## 数据与状态

### default vs define

```renpy
default selected_index = 0   # 随存档保存，值可变
define MAX_SLOTS = 10        # 常量，不随存档保存
```

不要用 `$ variable = value` 在模块级别初始化需要存档持久化的状态。

### Screen scope 是隔离的

Screen 内用 `$` 赋值的变量是 screen 局部变量。screen 隐藏后即消失，除非通过 `Return()` 显式传出。

---

## 性能

### O(1) 查询不需要预计算

复杂度比一次重复调用更高时，直接内联调用更好：

```renpy
# FINE — encyclopedia_is_unlocked() 是 set 查找，O(1)
textbutton entry.name:
    sensitive encyclopedia_is_unlocked(entry.id)
```

不需要因为"调用了两次"就预计算缓存——缓存本身的复杂度更高。

---

## 硬约束（绝对不能违反）

1. 不在 widget 列表（vbox/hbox 子节点 for 循环）中使用 `$`
2. 不给纯布局容器（vbox/hbox）加 visual 属性
3. 不同时使用互斥属性对
4. 不给 textbutton 套 frame 做背景
5. 同一个属性不在 named style 和 inline 两层同时定义
