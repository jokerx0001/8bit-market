# Ren'Py 截图方法

visual/ui 任务的验证依赖截图 + visual-compare。test-agent 在测试代码中执行截图，coding agent 确保实现的画面满足截图条件。此文件是双方的共享契约。

---

## 截图 API

在 testcase 中使用 `screenshot` 语句：

```renpy
screenshot "path/to/file.png"                         # 仅截图，不做对比
screenshot "screens/inventory" max_pixel_difference 0.01  # 像素对比（基线需存在）
screenshot "button.png" crop (10, 10, 100, 50)        # 裁剪区域
```

- 默认路径相对于 `_test.screenshot_directory`（默认 `tests/screenshots`）
- 需要自定义路径时，在 testcase 中用 `$ _test.screenshot_directory = "..."` 调整，或直接在 `screenshot` 参数中写目标路径

---

## 截图路径约定

所有 visual/ui 任务的截图统一存放到：

```
{task_dir}/.work/screenshots/{testcase_name}.png
```

test-agent 负责创建目标目录并在截图中使用此路径。

---

## testcase 模板（给 test-agent）

```renpy
testcase {name}:
    advance until screen "{target_screen}"
    # 触发视觉状态（根据 spec/HTML 描述）
    $ trigger_visual_state()
    pause 0.5
    screenshot "{task_dir}/.work/screenshots/{name}.png"
```

流程：导航到目标 screen → 触发视觉状态 → pause 等渲染完成 → 截图保存到约定路径。

---

## 实现约束（给 coding-agent）

test-agent 截图依赖以下条件，coding agent 实现时必须保证：

1. **画面完全渲染** — screen 已显示（`show screen` 或 `call screen`），不能处于转场中途。转场期间截图结果不可靠
2. **widget 有 id** — 所有可交互 widget 必须有 `id` 属性（参见 `references/renpy/coding.md` 硬约束第 6 条）
3. **不依赖编辑器工具** — 截图通过 Ren'Py 内建 `screenshot` 语句完成，不能依赖 MCP 或其他仅在编辑器环境可用的工具
4. **状态稳定** — test-agent 截图前会 `pause 0.5`，coding agent 确保动画/过渡在 0.5s 内达到稳定状态（或不存在需要更长等待的动画）

---

## 已知限制

- `screenshot` 语句只能在 testcase 内使用，不能在 testsuite 钩子（setup/teardown）中使用
- 被遮挡或 offscreen 的 screen 截图结果不可靠。test-agent 只对当前显示的 screen 截图
- `max_pixel_difference` 对比需要基线截图已存在（通过 `--overwrite_screenshots` 生成），visual-compare 流程不使用此模式
