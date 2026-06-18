---
name: renpy-dev:test
description: |
  此 skill 提供 Ren'Py 三层自测体系的方法论和工具使用指南。当需要编写 Ren'Py 测试、
  运行测试、或理解测试基础设施时触发。测试编写 agent 必须遵循此 skill 中的方法论。

  <example>
  Context: 需要为新功能编写测试
  user: "为 CharacterSelectScreen 编写测试"
  assistant: "我将使用 renpy-dev:test skill 中的三层测试方法论来编写测试。"
  <commentary>
  Ren'Py 测试使用三层体系，需要特定的 label 命名和 helper API。
  </commentary>
  </example>
---

# Ren'Py 三层自测体系

三层独立测试，通过单一 `tools/test.py` runner 协调运行。

```
tools/test.py
  ├── structure  →  Lint + AST 检查（不启动引擎，<5s）
  ├── behavior   →  headless SDK 运行 test_b_* labels（~30s）
  ├── visual     →  headless SDK 运行 test_v_* labels，截图 diff（~60s）
  ├── scaffold   →  生成 test_v_<screen> 骨架
  └── --update-baselines  →  重新生成 baselines/
```

## 安装

项目首次使用时，将 `assets/test-infra/` 的内容复制到 Ren'Py 项目根目录：

```
project/
├── tools/
│   └── test.py              # 单入口 runner
└── game/
    └── tests/
        ├── _guard.rpy        # init offset=-100, config.test gate
        ├── _framework.rpy    # helper API + runner labels
        └── OWN_MANIFEST.json  # 声明我们拥有的文件
```

`OWN_MANIFEST.json` 是测试的单一数据源——runner 只扫描此文件中列出的内容。

```json
{
  "screens": ["main_menu", "character_select"],
  "scripts": ["script.rpy", "character_select.rpy"],
  "exclude_dirs": ["libs/", "tl/", "cache/"]
}
```

## Layer 1 — Structure（结构检查）

**目标：** 无需启动引擎即可捕获解析/加载/导入错误和缺失引用。

**检查项（范围为 `OWN_MANIFEST.json`）：**
- `renpy lint`（引擎内置）
- 对于 `OWN_MANIFEST.json` 中的每个 screen：验证定义存在
- 对于每个脚本条目：验证引用的文件存在
- 对于声明的 label：构建 jump/call 图，对不可达 label 发出警告

**速度：** < 5 秒。

## Layer 2 — Behavior（行为测试）

**目标：** 断言交互流程产生正确的 game state。

**机制：** `game/tests/test_*.rpy` 中的 `label test_b_<feature>`。通过 SDK headless（`-W 0 -H 0`）运行，`config.test=True`。

**Helper API：**

| 方法 | 用途 |
|------|------|
| `test_framework.inject_swipe(direction, distance=500)` | 合成滑动输入 |
| `test_framework.inject_click(x, y)` | 合成鼠标点击 |
| `test_framework.inject_key(key_name)` | 合成键盘事件，如 `"K_RETURN"` |
| `test_framework.wait_for_screen(name, timeout=2.0)` | 等待 screen 成为顶层 |
| `test_framework.assert_screen_var(screen, key, expected)` | 断言 screen 变量值 |
| `test_framework.assert_log_contains(marker)` | 断言日志包含子串 |
| `test_framework.log(msg)` | 记录测试日志 |
| `test_framework.read_log()` | 读取全部捕获日志 |

**编写 behavior 测试：**

```rpy
# game/tests/test_swipe.rpy
label test_b_swipe_up:
    jump swipe_demo
    $ renpy.pause(0.1)
    $ test_framework.inject_swipe("up", 500)
    $ test_framework.log("swipe up injected")
    $ renpy.pause(0.3)
    $ test_framework.assert_screen_var("result_screen", "last_direction", "up")
    return
```

**断言规则：**
- 测试断言目标行为，不是当前行为
- RED 阶段测试因功能未实现而失败，GREEN 阶段必须通过
- 只依赖 `test_framework` 的公共 API，不直接访问 Ren'Py 内部

## Layer 3 — Visual（视觉回归）

**目标：** 检测我们拥有的 widget 的非预期视觉变化。

**机制：** `game/tests/test_*.rpy` 中的 `label test_v_<feature>`。全屏截图 → 裁剪至 widget 边界框 → 与 baseline PNG difff。

**Helper API：**

| 方法 | 用途 |
|------|------|
| `test_framework.assert_visual(screen, widget_id, baseline_name, threshold=0.02)` | 完整 pipeline |

**Pipeline：**
1. 跳转到目标 screen，`renpy.pause(stable_seconds)`（默认 0.3s，让动画稳定）
2. `renpy.screenshot()` → 全屏 RGBA 缓冲
3. `renpy.get_widget(screen, widget_id).get_placement()` → 裁剪区域
4. PIL 像素 diff（每通道最大 abs delta > 8/255，超过 `threshold` 比例的像素 → 失败）
5. Diff > threshold → 失败；实际图片保存到 `game/tests/artifacts/`

**前置要求：** 被测 widget 必须在 `screens.rpy` 中设置 `id`。如果 widget 没有 `id`，则无法进行视觉测试，`OWN_MANIFEST.json` 不应包含它。

**编写 visual 测试：**

```rpy
label test_v_main_menu:
    jump main_menu
    $ renpy.pause(0.3)
    $ test_framework.assert_visual("main_menu", "start_button", "main_menu_start")
    return
```

**Baseline 管理（显式，非自动）：**
- 无 baseline 文件的首次运行：将当前截图保存为 baseline，**通过**
- 后续运行：与已存在的 baseline diff
- 失败：实际图片保存到 `artifacts/`，**不修改** baseline
- 更新 baseline：人类运行 `python tools/test.py --update-baselines`，**单独 commit**，commit message 以 `chore: baseline update` 开头

## 规则

1. **修改源码后始终运行 `python tools/test.py`**，stage 之前
2. **永远不使用 `--update-baselines` 掩盖失败**，除非向人类展示 artifact 图片并获得明确批准
3. **永远不将 baseline 更新与导致变更的源码修改放在同一个 commit 中**。至少两个 commit：`feat: ...` 然后 `chore: baseline update`
4. **新增 screen/effect 时必须**：(a) 在 `screens.rpy` 中给关键 widget 设置 `id`，(b) 将 screen 添加到 `OWN_MANIFEST.json`，(c) 编写 `test_v_<name>` label，(d) 运行测试生成 baseline
5. **永远不修改 `game/libs/`、`game/tl/`** 或 Ren'Py 库代码以添加测试

## Scaffold 生成

首次设置测试时，生成骨架 labels：

```bash
python tools/test.py scaffold              # OWN_MANIFEST 中的全部 screen
python tools/test.py scaffold --screen X   # 单个 screen
```

骨架包含 `TODO: widget_id` 占位符。在 `screens.rpy` 中为 widget 添加 `id` 后，填入实际的 widget id。

## Bootstrap 序列

一次性设置，按顺序执行：

1. 复制 `assets/test-infra/` 到项目根目录
2. 编辑 `OWM_MANIFEST.json` 列出我们拥有的 screen 和 script
3. `python tools/test.py scaffold` — 生成骨架
4. 对于每个新创建的 screen，在 `screens.rpy` 中为关键 widget 添加 `id`，填入 widget id
5. `python tools/test.py visual` 首次运行 — 创建所有 `baselines/*.png`，通过
6. `git add game/tests/ tools/ && git commit -m "chore: add UI effect self-test infrastructure"`

## 运行测试

```bash
python tools/test.py                        # 全部三层
python tools/test.py structure              # 仅 structure
python tools/test.py behavior               # 仅 behavior
python tools/test.py visual                 # 仅 visual
python tools/test.py --filter <name>        # 按名称过滤
```

**退出码：** `0`=全部通过，`1`=测试失败，`2`=环境错误（SDK 未找到、manifest 缺失）

**SDK 路径：** 通过 `RENPY_SDK` 环境变量设置。
