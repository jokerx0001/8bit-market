# Godot 集成测试协议

通过 gopeak MCP 工具控制真实游戏进程。MCP 工具底层通过 MCP Runtime TCP (port 7777) 与游戏通信，skill 直接调用 MCP 工具即可。

## 启动游戏

**必须用直接启动**（非 MCP `run-project`）。`run-project` 使用 dummy renderer，`capture-screenshot` 会失败。

```bash
GODOT=$(which godot 2>/dev/null || echo "/Applications/Godot.app/Contents/MacOS/Godot")
$GODOT --path {project} 2>&1 | tee {task_dir}/.work/integration-console.log &
GODOT_PID=$!
```

停止游戏:
```bash
kill $GODOT_PID
```

## 等待就绪

启动后 MCP Runtime 需要 3-8 秒初始化。用 MCP `runtime-status` 轮询确认:

```
mcp__godot__runtime-status → connected: true
```

或直接试调 `capture-screenshot`，成功则就绪。

## MCP 工具参考

### 截图

```
mcp__godot__capture-screenshot
  参数: width (可选), height (可选)
  返回: PNG 截图 (base64)
```

不传 width/height 使用当前分辨率。skill 写入文件时 base64 解码保存到指定路径。

### 操作游戏

```
mcp__godot__inject-action
  参数: action (string), pressed (bool), strength (0.0-1.0, 可选)
  返回: {type: "input_injected", input_type: "action", ...}
```

action 名称必须与项目 Input Map 中定义的完全一致。常见: `left`, `right`, `up`, `down`, `jump`, `shoot`, `ui_accept`, `pause`。

按住持续移动: `pressed: true` → sleep → `pressed: false`

```
mcp__godot__inject-key
  参数: keycode (key_label string), pressed (bool)
  返回: {type: "input_injected", input_type: "key", ...}
```

常用 key_label: `Enter`, `Escape`, `Space`, `A`~`Z`。

### 运行时检查 (诊断用)

```
mcp__godot__inspect-runtime-tree
  参数: projectPath (string), nodePath (string, 可选), depth (int, 可选)
  返回: 运行时场景树结构
```

```
mcp__godot__call-runtime-method
  参数: projectPath (string), nodePath (string), method (string), args (array, 可选)
  返回: 方法返回值
```

```
mcp__godot__get-runtime-metrics
  参数: projectPath (string), metrics (array, 可选)
  返回: FPS, 内存, 对象数等性能指标
```

## 控制台错误监控

直接启动的 Godot 进程，从 stdout/stderr 捕获。启动时已 `tee` 到 `integration-console.log`。

增量检查:
```bash
START_LINE=$(wc -l < {task_dir}/.work/integration-console.log)
# ... 执行若干操作 ...
tail -n +$START_LINE {task_dir}/.work/integration-console.log | grep -iE '(ERROR|push_error|SCRIPT ERROR|CRITICAL)'
```

**Hard Gate**: 每步操作后必须做增量控制台检查。有 ERROR 则立即进入诊断修复。

## 截图预检

调用 visual-qa 前必须预检:

```bash
# PNG 有效性
file {png} | grep -q 'PNG image data' && echo "PNG_OK" || echo "PNG_INVALID"

# 空白检测
STD=$(identify -format "%[standard-deviation]" {png} 2>/dev/null || echo "0")
IS_BLANK=$(echo "$STD < 0.02" | bc -l 2>/dev/null || echo "0")
```

- PNG_INVALID → 截图失败，标记 FAIL，进入诊断修复
- IS_BLANK=1 → 空白截图，标记 BLANK，进入诊断修复
- 两项都通过 → 调 visual-qa

## 已知坑

1. **MCP `run-project` 用 dummy renderer** — `capture-screenshot` 返回 "Failed to capture viewport image"。必须用直接启动。
2. **角色闪烁** — 截图前额外等待 0.5s 确保渲染稳定。movement 类操作后等待更久 (1-2s)。
3. **inject-action 名称必须匹配** — 检查项目 `project.godot` 的 `[input]` 节确认 action 名称。
4. **macOS 上 Godot 路径** — `/Applications/Godot.app/Contents/MacOS/Godot`
5. **MCP Runtime 启动等待** — 3-8 秒。用 `runtime-status` 或 `capture-screenshot` 轮询确认。
