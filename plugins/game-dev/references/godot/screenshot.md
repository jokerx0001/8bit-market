# Godot 截图方法

非 headless 截图。关键经验两条：

1. **绝不能加 `--headless`** 否则无法截图
2. **切场景后必须多 `await process_frame` + 一次 `await RenderingServer.frame_post_draw`**，等 GPU 真正提交完这一帧。否则 `get_viewport().get_texture()` 拿到的是上一帧或未提交的内容，经常是黑屏。

---

## 已验证的可用示例

以下是一个实际运行通过的截图脚本，包含防黑屏的关键处理：

```gdscript
extends SceneTree

# 非 headless 截图（关键经验就两条）：
#   1) 绝不能加 --headless（否则截到全黑 PNG）。
#   2) 切场景后必须多 await 几帧 + 一次 `await RenderingServer.frame_post_draw`
#      等待 GPU 真正提交完这一帧，否则 get_viewport().get_texture() 拿到的是
#      上一帧或未提交的内容，经常是黑屏。
#
# 用法：
#   godot --path {project} --script test/visual/test_xxx.gd

func _init() -> void:
    await process_frame

    var err := change_scene_to_file("res://scenes/main.tscn")
    if err != OK:
        printerr("SCENE_LOAD_ERROR:%d" % err)
        quit(2)
        return

    # 等场景就绪 + 等 GPU 提交。
    for _i in range(10):
        await process_frame
    await RenderingServer.frame_post_draw

    var img := get_root().get_viewport().get_texture().get_image()
    var png_bytes := img.save_png_to_buffer()
    print(Marshalls.raw_to_base64(png_bytes))
    quit()
```

---

## CLI 命令

```bash
# 执行截图脚本，stdout 输出纯 base64 PNG 字符串
godot --path {project} --script {screenshot_script_path}

# 解码保存为 PNG 文件
godot --path {project} --script {screenshot_script_path} | base64 -d > {output_path}.png
```

Linux 无显示器环境用 `xvfb-run` 包裹：

```bash
xvfb-run godot --path {project} --script {screenshot_script_path} | base64 -d > {output_path}.png
```

---

## 参考模式

以下两种模式是编写截图脚本的**参考起点**。test-agent 根据任务描述自行判断需要哪种模式、是否需要交互、交互的具体逻辑，然后写出定制脚本。

### 模式 A：直接打开场景截图

适用：验证某个关卡/界面的静态视觉。"看看 level_1 长什么样"、"验证主菜单 UI 布局"。

核心逻辑：`change_scene_to_file` → 等帧 + `frame_post_draw` → 截图。

```gdscript
extends SceneTree

func _init() -> void:
    await process_frame

    var err := change_scene_to_file("res://scenes/target.tscn")
    if err != OK:
        printerr("SCENE_LOAD_ERROR:%d" % err)
        quit(2)
        return

    for _i in range(10):
        await process_frame
    await RenderingServer.frame_post_draw

    var img := get_root().get_viewport().get_texture().get_image()
    var png_bytes := img.save_png_to_buffer()
    print(Marshalls.raw_to_base64(png_bytes))
    quit()
```

### 模式 B：交互后截图

适用：需要特定交互后才能看到的界面。"按下 B 键打开背包后截图"、"打开设置面板截图"。

前提：游戏使用 InputMap action（如 `open_backpack`），而非硬编码按键。

核心逻辑：`change_scene_to_file` → 等帧 + `frame_post_draw` → `Input.action_press` → 再等帧 + `frame_post_draw` → 截图。

```gdscript
extends SceneTree

func _init() -> void:
    await process_frame

    var err := change_scene_to_file("res://scenes/main.tscn")
    if err != OK:
        printerr("SCENE_LOAD_ERROR:%d" % err)
        quit(2)
        return

    for _i in range(10):
        await process_frame
    await RenderingServer.frame_post_draw

    # 模拟交互
    Input.action_press("open_backpack")
    for _i in range(5):
        await process_frame
    await RenderingServer.frame_post_draw

    var img := get_root().get_viewport().get_texture().get_image()
    var png_bytes := img.save_png_to_buffer()
    print(Marshalls.raw_to_base64(png_bytes))
    quit()
```

交互步骤不限于单个 action。多个连续操作、条件判断、等待特定节点出现——只要能用 GDScript 表达，都可以写入脚本。关键是**每次交互后都要等帧 + `frame_post_draw`** 确保 UI 已渲染。

