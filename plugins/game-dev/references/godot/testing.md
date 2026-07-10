# GUT 自动化测试 — 完整参考

GUT (Godot Unit Testing) 是 Godot 的标准测试框架。支持单元测试、集成测试、参数化测试。

> **关键：`-gexit` 是强制要求。** 没有 `-gexit`，`godot --headless` 跑完测试后进程不退出 → bash 后台任务永久挂起 → TDD 循环卡死。这是硬门，不是可选项。

---

## 快速入门

```gdscript
# test/unit/test_player.gd
extends GutTest

func test_player_health_starts_at_100():
    var player = Player.new()
    assert_eq(player.health, 100)

func test_player_take_damage():
    var player = Player.new()
    player.take_damage(30)
    assert_eq(player.health, 70)

func test_player_cannot_go_below_zero():
    var player = Player.new()
    player.take_damage(200)
    assert_eq(player.health, 0)
```

---

## 运行测试

```bash
# 全量运行
godot --headless -s addons/gut/gut_cmdln.gd -gdir=test/ -gexit

# 指定目录
godot --headless -s addons/gut/gut_cmdln.gd -gdir=test/unit -gexit

# 指定文件
godot --headless -s addons/gut/gut_cmdln.gd -gselect=test_unit.gd -gexit

# 指定单个测试方法
godot --headless -s addons/gut/gut_cmdln.gd -gselect=test_unit.gd:test_player_health -gexit

# 详细输出
godot --headless -s addons/gut/gut_cmdln.gd -gdir=test/ -gexit -glog=3
```

### 命名规则

- 测试文件必须以 `test_` 开头，扩展名 `.gd`
- 测试类继承 `GutTest`
- 测试方法以 `test_` 开头
- 文件放在 `test/` 目录（可分子目录如 `test/unit/`、`test/integration/`）

---

## 断言方法

| 断言 | 说明 |
|------|------|
| `assert_eq(actual, expected)` | 相等 |
| `assert_ne(actual, expected)` | 不相等 |
| `assert_true(value)` | 为 true |
| `assert_false(value)` | 为 false |
| `assert_null(value)` | 为 null |
| `assert_not_null(value)` | 不为 null |
| `assert_gt(a, b)` | a > b |
| `assert_lt(a, b)` | a < b |
| `assert_between(value, low, high)` | low <= value <= high |
| `assert_has(arr, element)` | 数组包含元素 |
| `assert_does_not_have(arr, element)` | 数组不包含元素 |
| `assert_file_exists(path)` | 文件存在 |
| `assert_file_does_not_exist(path)` | 文件不存在 |
| `assert_called(thing, method)` | 方法被调用（doubles） |
| `assert_not_called(thing, method)` | 方法未被调用 |
| `assert_signal_emitted(obj, signal_name)` | 信号已发出 |
| `assert_signal_not_emitted(obj, signal_name)` | 信号未发出 |
| `assert_signal_emit_count(obj, signal_name, count)` | 信号发出次数 |

---

## 场景测试（集成测试）

```gdscript
# test/integration/test_ui.gd
extends GutTest

var _scene: Node

func before_each():
    _scene = load("res://scenes/main_menu.tscn").instantiate()
    add_child_autofree(_scene)

func test_start_button_exists():
    var btn = _scene.get_node("StartButton")
    assert_not_null(btn)

func test_start_button_emits_pressed():
    var btn = _scene.get_node("StartButton")
    watch_signals(btn)
    btn.emit_signal("pressed")
    assert_signal_emitted(btn, "pressed")
```

---

## 生命周期钩子

```gdscript
func before_all():     # 所有测试前运行一次
    pass

func before_each():    # 每个测试前运行
    pass

func after_each():     # 每个测试后运行
    pass

func after_all():      # 所有测试后运行一次
    pass
```

---

## 参数化测试

```gdscript
func test_addition(params = use_parameters([
    [1, 2, 3],
    [2, 3, 5],
    [0, 0, 0],
])):
    assert_eq(params[0] + params[1], params[2])
```

---

## 已知限制

1. **headless 模式下 DisplayServer 不可用** — 涉及 `DisplayServer`、窗口大小、屏幕信息等调用会崩溃。需要 mock 或跳过。
2. **`$NodeName` 简写依赖于场景树** — 在 `new()` 创建的对象上不生效，需要用 `get_node_or_null()` 或 `get_node()`。
3. **`await` 在 GUT 测试中的行为不可靠** — 尽量避免，用信号断言代替。
4. **资源路径在测试中不同** — 测试运行时 `res://` 指向项目根目录，确认资源路径正确。
5. **GUT 在自动发现测试文件时可能遗漏** — 确保文件名以 `test_` 开头且在 `test/` 下。

---

## 测试编写原则

### 集成测试优先（Public Interface）

**测试玩家看到和操作的，不测试内部实现细节。**

| Good (public interface) | Bad (implementation detail) |
|--------------------------|----------------------------|
| 实例化场景 → 检查节点存在 → 模拟点击 → 验证信号 | 检查内部变量 `_selected_index` 的值 |
| 调用 `player.take_damage(10)` → 断言 `player.health == 90` | 检查 `player._damage_multiplier` 的值 |
| 加载 .tscn → 检查节点树结构 | 检查 .gd 文件中私有方法的返回值 |

### 垂直切片

不要一次性写所有测试再实现。先写一个 tracer bullet（场景能否加载？节点能否找到？），通过后再逐步加交互测试。

---

## Headless 模式下的输入模拟

在 `--headless` 模式下无法使用键盘/鼠标，需要代码模拟玩家输入。

### 定时触发

```gdscript
var timer := Timer.new()
timer.wait_time = 1.0
timer.one_shot = true
timer.timeout.connect(func(): Input.action_press("jump"))
root.add_child(timer)
timer.start()
```

### 持续移动：闭环控制（不要开环输入）

开环输入（定时 press → 定时 release）在长时间运行时，每帧误差会累积，导致角色漂移、卡边、轨迹螺旋偏离。

使用闭环控制——每帧根据实际位置计算目标方向：

```gdscript
var _targets: Array[Vector3] = []
var _current_target_idx: int = 0

func _process(delta: float) -> bool:
    if _current_target_idx >= _targets.size():
        # 所有目标到达
        return false
    
    var target := _targets[_current_target_idx]
    var to_target := target - player.global_position
    var dist := to_target.length()
    
    if dist < 0.5:
        # 到达当前目标 → 下一个
        _current_target_idx += 1
    else:
        # 根据实际位置计算输入方向（不是固定时间）
        var direction := to_target.normalized()
        Input.action_press("move_forward")
        # 调整朝向...
    
    return false
```

开环和闭环的区别：开环说"按住 W 2 秒再松手"，闭环说"朝 X 目标前进直到到达"。后者不受帧率、物理 tick 偏差和误差累积的影响。

---


## 更多细节

完整文档: https://gut.readthedocs.io/en/latest/
