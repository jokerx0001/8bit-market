# Ren'Py 架构映射指引

plan 步骤 7（架构设计）时读取本文件。本文件回答：**领域模型中的模式，在 Ren'Py 中用什么构造来表达？**

所有规则均来自 [Ren'Py 官方文档](https://www.renpy.org/doc/html/)，每条标注来源页面。

---

## 一、核心设计哲学

Ren'Py 的架构分为三层，各司其职：

| 层 | 用什么 | 性质 | 规则 |
|----|--------|------|------|
| UI | Screen Language | 声明式 | 无副作用——screen 代码在预测时也会执行，不能修改外部状态 |
| 交互 | Actions | 声明式 | 描述"点击后做什么"，在交互时评估，预测时不执行 |
| 逻辑 | Python / Label | 命令式 | 游戏状态变更、条件分支、函数调用放在这里 |

> 来源：[Screens](https://www.renpy.org/doc/html/screens.html)、[Screen Actions](https://www.renpy.org/doc/html/screen_actions.html)、[Python](https://www.renpy.org/doc/html/python.html)

---

## 二、构造选型速查

> 综合自：[Python](https://www.renpy.org/doc/html/python.html)、[Persistent](https://www.renpy.org/doc/html/persistent.html)、[Screens](https://www.renpy.org/doc/html/screens.html)

### 游戏状态（可变、参与存档）→ `default`

```renpy
default hp = 100
default inventory = []
```

**所有会在游戏中改变的变量都必须用 `default`**。否则读档时变量缺失（状态泄露）。

### 常量/配置（不可变）→ `define`

```renpy
define e = Character("Eileen")
define config.default_text_speed = 40
```

`define` 在 init 阶段执行，不参与保存/加载/回滚。

### 跨周目状态（画廊、成就、设置）→ `persistent`

```renpy
default persistent.gallery_unlocked = False
$ persistent.ending_a_seen = True
```

persistent 不绑定存档槽，游戏重启后仍存在。

### UI 模板/组件 → `screen` + `use` + `transclude`

`transclude` 是 Ren'Py 的插槽系统——容器 screen 控制布局，调用方填充内容：

```renpy
screen panel_frame():
    frame:
        transclude  # 调用方的内容注入这里

screen character_sheet():
    use panel_frame():
        vbox:
            text "HP: [hp]"
```

> 来源：[Screens - use](https://www.renpy.org/doc/html/screens.html#use)

### 同一概念槽的多屏切换 → `tag`

```renpy
screen preferences():   # tag menu
    ...
screen save():          # tag menu — show 时自动替换 preferences
    ...
```

同一个 tag 的 screen 自动互斥替换，支持 ATL 过渡动画。

### 模态交互（需要返回值）→ `call screen` + `Return()`

```renpy
call screen character_select
# _return 包含用户选择的结果
```

> 来源：[Screen Actions](https://www.renpy.org/doc/html/screen_actions.html#call)

### 模块/命名空间划分 → 命名 Store

```renpy
init python in economy:
    gold = 100

default combat.hp = 100
```

每个命名 Store 对应一个 Python 模块。

### 不需要回滚的启动数据 → 常量 Store

```renpy
init python in my_constants:
    _constant = True
    ITEM_DB = {"sword": {"damage": 10}}
```

常量 Store 免除保存/加载/回滚的开销。

---

## 三、Screen 组织原则

> 来源：[Screens](https://www.renpy.org/doc/html/screens.html)

### 声明式，无副作用

Screen 代码在预测时也会执行——**不能在 screen 的 Python 块中修改全局状态**。逻辑通过 Action 触发，不在 screen 构建时执行。

### 变量作用域链

```
局部变量（SetLocalVariable） → Screen 变量（SetScreenVariable） → Store 变量（SetVariable）
```

- Screen 参数：不可变输入（预测时会重置）
- `default` 语句：screen 首次显示时初始化一次
- 优先用 `SetScreenVariable`（性能更好，允许更多缓存）

### UI 可见性动画 → `showif`（不用 `if`）

`showif` 给子元素发送 `appear`/`show`/`hide` 事件，支持 ATL 动画。`if` 直接增删子元素，无过渡。

### 跨平台适配 → `variant`

```renpy
screen my_screen():
    variant "touch"
    ...
```

不用在 screen 内写条件判断，Ren'Py 自动选择匹配的 variant。

---

## 四、交互模式

> 来源：[Screen Actions](https://www.renpy.org/doc/html/screen_actions.html)

### 组合多个操作

```renpy
textbutton "Start":
    action [SetVariable("lives", 3), SetVariable("score", 0), Jump("game_start")]
```

列表中的 action 按顺序执行。敏感条件：所有 action 都敏感；选中条件：任一 action 选中。

### 条件 action → `If()`

```renpy
action If(has_save, FileLoad(1), NullAction())
```

`If(condition, true_action, false_action)` — `NullAction()` 用于不可用的默认态。

### 破坏性操作确认 → `Confirm()`

```renpy
textbutton "Delete":
    action Confirm("Delete this save?", FileDelete(name))
```

### 自定义逻辑 → `Function()`

```renpy
action Function(my_custom_func, arg1, kwarg=value)
```

非 None 返回值会结束当前交互。

### 变量作用域——用对 action 类型

| 要改的变量 | 用 |
|-----------|-----|
| 全局 store 变量 | `SetVariable("name", value)` |
| 当前 screen 的变量 | `SetScreenVariable("name", value)` |
| use'd screen 的局部变量 | `SetLocalVariable("name", value)` |
| Python 对象字段 | `SetField(object, "field", value)` |
| 字典键 | `SetDict(dict, "key", value)` |

---

## 五、领域模式 → Ren'Py 构造映射

以下映射综合了上述全部官方原则。

### 状态机 → Python 状态变量 + Screen Actions

领域模型中的状态用 `default` 变量存储，状态转换通过 screen action 触发，UI 根据状态变量条件渲染。

```
领域: IDLE → RELOADING → READY
Ren'Py:
  default reload_state = "idle"
  screen ...:
    if reload_state == "idle":
        textbutton "Reload" action SetVariable("reload_state", "reloading")
```

原则依据：逻辑在 Python 后端，UI 在 Screen 前端，交互通过 Action 桥接。

### 数据流 → Store 变量 + Action

实体间共享数据通过 Store 变量（`default`），数据变更通过 Action（`SetVariable` 等），UI 响应通过 screen 中的变量引用。

原则依据：Screen 无副作用 + Store 参与存档回滚。

### 跨周目持久化 → persistent

画廊解锁、成就、玩家偏好等跨周目数据用 `persistent`。当前游戏进度（HP、位置）用 `default` + save/load。

原则依据：persistent 不绑定存档槽。

### UI 组件复用 → use + transclude

重复的 UI 布局（面板、对话框壳、卡片框架）做成带 `transclude` 的 screen，调用方 `use` 并注入内容。

原则依据：声明式组合，类似组件模式。

### 模态选择 → call screen + Return()

玩家必须做出选择才能继续时，用 `call screen` 而不是 `show screen`。选择结果通过 `_return` 获取。

原则依据：call screen 会暂停 label 执行直到交互返回。

### 时序控制 → Timer screen statement 或 Python 层的 renpy.pause()

Screen 中用 `timer` 语句；Label 中用 `pause` 语句或 `renpy.pause()`。

```
screen countdown():
    timer 3.0 action Return("timeout")
```

### 边界校验 → Action 组合中

领域模型中的边界规则（"满弹不换弹"）通过条件 action 表达：

```renpy
textbutton "Reload":
    action If(ammo < max_ammo and reserve > 0,
              [SetVariable("ammo", ...), SetVariable("reload_state", "reloading")],
              NullAction())
    sensitive (ammo < max_ammo and reserve > 0)
```

原则依据：逻辑不写在 screen 构建代码中，通过 Action 的敏感/条件机制处理。

### 游戏实体 → default 变量 + screen 模板

领域模型中的"玩家"、"物品"等实体用 `default` 变量存储，screen 模板渲染。Ren'Py 不需要 Godot 那种"每个实体一个场景"——Ren'Py 是数据驱动 UI，实体就是数据。

---

## 六、参考页面索引

需要更深入理解某个主题时，访问对应页面：

| 主题 | URL |
|------|-----|
| Screens | `screens.html` |
| Screen Actions | `screen_actions.html` |
| Screen Special | `screen_special.html` |
| Python Statements | `python.html` |
| Persistent Data | `persistent.html` |
| Save/Load | `save_load_rollback.html` |
| Labels & Control Flow | `label.html` |
| Style Properties | `style_properties.html` |
| Transforms (ATL) | `transforms.html` |
| Transitions | `transitions.html` |
| Displayables | `displayables.html` |
| GUI Customization | `gui.html` |
| Audio | `audio.html` |
| Input | `input.html` |
| Config Variables | `config.html` |
| Custom Displayables | `udd.html` |

基础 URL：`https://www.renpy.org/doc/html/`
