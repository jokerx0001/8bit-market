# Ren'Py 自动化测试 — 原生框架完整参考

Ren'Py 内置一等公民的自动化测试框架（`testcase` / `testsuite`），提供输入模拟、条件断言、视觉回归、参数化等完整能力。CLI: `renpy.sh <basedir> test [<testcase>]`。

> **工作流约定：** `screenshot ... max_pixel_difference` 像素对比在本工作流中不使用。视觉正确性由人类对照 HTML 标准文件确认，不由自动化测试验证。`screenshot` 无参形式仅用于调试。

---

## 快速入门

```renpy
# game/tests/test_character_select.rpy

testsuite character_select_suite:
    before testcase:
        run Jump("character_select_demo")

    testcase select_character:
        advance until screen "character_select"
        click id "char_2"
        assert eval (renpy.get_screen("character_select").scope["selected_index"] == 2)
        click "确认"
        assert label start_game

    testcase cancel_selection:
        advance until screen "character_select"
        click id "char_1"
        click "取消"
        assert label main_menu
```

### 惯用模式

| 意图 | 写法 |
|------|------|
| 从已知状态开始 | `run Jump("demo_label")` |
| 等到 screen 出现 | `advance until screen "inventory"` |
| 按文字点按钮 | `click "Start Game"` |
| 按 widget id 点击 | `click id "close_button"` |
| 等 screen 消失 | `click id "close" until not screen "popup"` |
| 断言 screen 变量 | `assert eval (renpy.get_screen("s").scope["key"] == val)` |
| 断言 label 到达 | `assert label chapter_5` |
| 选择菜单选项 | `click "Take the map"` |

---

## 运行测试

```bash
renpy.sh /path/to/project test              # 运行 global suite
renpy.sh /path/to/project test <testcase>   # 运行特定 testcase

# 常用选项
renpy.sh project test --enable_all           # 运行所有测试（忽略 enabled=False）
renpy.sh project test --report-detailed      # 显示每个测试的详细信息
renpy.sh project test --report-detailed --report-skipped  # 包括跳过的测试
renpy.sh project test --overwrite_screenshots  # 重写截图基线
```

**退出码:** `0` = 全部通过 / xfailed，非零 = 有失败或 xpassed。

---

## testcase 语句

```renpy
testcase <name>:
    # 属性（可选）
    description "测试描述"
    enabled True           # False → 跳过
    only False             # True → 只运行此测试
    xfail False            # True → 预期失败
    parameter var = [...]  # 参数化

    # 测试体 — 测试语句序列
    advance until screen "menu"
    click "Start"
    assert label game_start
```

**属性:**

| 属性 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `description` | string | — | 测试报告中的描述 |
| `enabled` | expression | `True` | `False` 则跳过 |
| `only` | expression | `False` | `True` 则只运行此（和其他 `only`）测试 |
| `xfail` | expression | `False` | `True` 则预期失败 |
| `parameter` | var(s) + list | — | 每个值运行一次（详见参数化节） |

---

## testsuite 语句

```renpy
testsuite <name>:
    # 同 testcase 的属性（description, enabled, only, xfail, parameter）

    setup:
        # suite 开始前运行一次
        $ print("suite starting")

    before testsuite:
        # 每个子 suite 前运行

    before testcase:
        # 每个子 testcase 前运行

    after testcase:
        # 每个子 testcase 后运行（失败也运行）

    after testsuite:
        # 每个子 suite 后运行（失败也运行）

    teardown:
        # suite 结束后运行
        exit

    testcase child1:
        ...

    testsuite child_suite:
        ...
```

**钩子执行顺序:** `setup` → `before testsuite` → `before testcase` → [test body] → `after testcase` → ... → `after testsuite` → `teardown`

**嵌套:** 父 suites 的钩子级联到所有后代。`depth 0` 限制仅直接子节点。

默认存在 `global` suite。顶层 suite/testcase 都在其中。

---

## 测试语句完整参考

### 基本命令

| 语句 | 说明 |
|------|------|
| `advance` | 前进一行对话。`advance until <condition>` |
| `exit` | 立即退出游戏（无确认、无自动存档） |
| `pass` | 空操作（占位测试） |
| `pause <seconds>` | 暂停 N 秒。`pause until screen "x"` |
| `run <action>` | 执行 screen 动作。`run Jump("label")` / `run Show("screen")` / `run Return()` |
| `skip [fast]` | 快进。`fast` 直接跳到下一个菜单选择。`skip until screen "x"` |

### 鼠标操作

| 语句 | 说明 |
|------|------|
| `click <selector>` | 点击。`click "Start"` / `click id "btn"` / `click pos (0.5, 0.5)` |
| `click <selector> button 2` | 右键点击。button 1=左 2=右 3=中 |
| `click <selector> until not screen "x"` | 重复点击直到 screen 消失 |
| `move <selector>` | 移动虚拟鼠标到元素上 |
| `drag <from> to <to>` | 拖拽。`drag id "item" to id "slot"` |
| `scroll [amount] <selector>` | 滚轮。正数=向下。`scroll amount 10 id "viewport"` |

**Selector 类型:**
- `"text"` — 文本匹配（按钮文字、alt text），大小写不敏感，最短匹配优先
- `"text" raw` — 翻译前/插值前的原始文本匹配
- `id "widget_id"` — 按 widget id
- `pos (x, y)` — 坐标，小数=比例（0-1），整数=像素
- `expression <expr>` — 表达式求值

### 键盘操作

```renpy
keysym "K_RETURN"           # 发送按键事件
keysym "K_BACKSPACE" repeat 10  # 重复 10 次
keysym "skip"               # 支持 config.keymap 条目
type "Hello, World!"        # 输入字符串
```

### 条件/断言

```renpy
# assert — 条件检查
assert screen "main_menu"                    # screen 是否显示
assert id "close_button"                     # widget 是否存在
assert id "close_button" timeout 5.0         # 等待最多 5 秒
assert eval (player.hp == 100)               # 任意 Python 表达式
assert eval (renpy.get_screen("shop").scope["coins"] >= 50)
assert label chapter_5                       # label 是否被到达（一次性检查）
assert "Start Game"                          # 文本是否存在

# if/elif/else — 条件分支
if screen "main_menu":
    click "Start"
elif screen "game_over":
    run Return()
else:
    skip until screen "main_menu"

# 重复执行
click "+" repeat 3                           # 点击 3 次
advance repeat 10                             # 前进 10 行对话

# until — 重复直到条件满足
advance until screen "choice"
click "Close" until not screen "popup"
skip until label chapter_5 timeout 20.0
```

### eval 常用断言模板

```renpy
# 获取 screen 变量
assert eval (renpy.get_screen("shop").scope["selected_item"] == "potion")

# 检查 screen 是否存在
assert eval (renpy.get_screen("inventory") is not None)

# 调用自定义函数
assert eval (check_game_state("chapter_2"))

# 复合条件
assert eval (persistent.unlocked_characters >= 3 and screen "gallery")
```

### 截图/视觉回归

```renpy
screenshot "screens/main_menu.png"               # 仅截图，不做对比
screenshot "screens/inventory" max_pixel_difference 0.01  # 像素对比（本工作流不使用）
screenshot "button.png" crop (10, 10, 100, 50)   # 裁剪区域
```

- 仅 `.png`。文件已存在时对比差异，超过 `max_pixel_difference`（整数=像素数，小数=比例）则失败
- `--overwrite_screenshots` 重写基线
- **本工作流约定：** 不使用 `max_pixel_difference`。`screenshot` 无参形式仅用于调试确认 screen 可渲染。视觉验证由人工对照 HTML 标准完成。

### 参数化测试

```renpy
# 单参数 — 每个值运行一次
testcase click_all_buttons:
    parameter button_name = ["Load", "Save", "Options"]
    click expression button_name

# 多参数组合
testcase combinations:
    parameter a = [1, 2]
    parameter b = [3, 4]
    # 运行 4 次: (1,3), (1,4), (2,3), (2,4)

# 分组参数
testcase addition:
    parameter (x, y, z) = [(1, 2, 3), (2, 3, 5), (3, 5, 8)]
    assert eval (x + y == z)
```

---

## 配置变量

`_test` 命名空间，在测试体中用 `$` 设置：

| 变量 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `_test.timeout` | float | `10.0` | 条件等待超时 |
| `_test.transition_timeout` | float | `5.0` | 转场等待超时 |
| `_test.maximum_framerate` | bool | `True` | 解锁帧率上限 |
| `_test.screenshot_directory` | string | `tests/screenshots` | 截图存储目录 |

---

## 注意事项

1. **`label` 条件是一次性的** — 检查自上次测试语句后是否到达，断言一次后重置
2. **不要用 `click` 推进对话** — 用 `advance` 或 `skip`
3. **参数传递是引用传递** — 在测体内修改可变参数会影响其他测试运行
4. **`eval` 不能单独使用** — 必须在 `assert`、`if`、`until` 等条件语句内部
5. **测试语句不能写在 testcase/testsuite 块外**
6. **testcase 没有 `return` 等价物**

---

## 更多细节

本文档覆盖常用场景。完整细节见官方文档：https://www.renpy.org/doc/html/testcases.html
