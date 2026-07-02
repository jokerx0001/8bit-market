# Godot 技术栈配置

game-dev orchestrator 通过读项目 CLAUDE.md 检测技术栈。当 CLAUDE.md 中出现 "Godot" / "godot" 时加载本文件。

---

## 维度检测

Godot 项目需要进一步检测 2D/3D 维度：

```bash
# 读 project.godot 的 renderer 字段
grep -i "rendering/renderer" project.godot 2>/dev/null
```

| Renderer 值 | 维度 |
|------------|------|
| `gl_compatibility` | 2D |
| `forward_plus` | 2D 或 3D（需进一步检查是否有 3D 场景文件） |
| `mobile` | 2D 或 3D（同上） |
| 无法自动判断 | 检查是否有关键词：`MeshInstance3D`、`CSG`、`NavigationRegion3D` → 3D |

检测到维度后加载对应的 `references/godot/nodes-{2d,3d}.md`。

## 产物目录

- **根目录**: `.godot-dev/`
- **任务目录格式**: `.godot-dev/{kind}-{N}/`
- **计数器**: `feat`, `refactor`, `fix`

## 测试 (GUT)

### 环境检测

```bash
# 检查 Godot CLI 可用
which godot 2>/dev/null && echo "GODOT_OK" || echo "GODOT_MISSING"

# 检查 GUT 插件
ls addons/gut/ 2>/dev/null && echo "GUT_OK" || echo "GUT_MISSING"

# 检查测试目录
ls test/ 2>/dev/null && echo "TESTS_OK" || echo "TESTS_MISSING"
```

### 测试命令

```bash
# 全量运行
godot --headless -s addons/gut/gut_cmdln.gd -gdir=test/ -gexit

# 指定测试文件
godot --headless -s addons/gut/gut_cmdln.gd -gselect=test_unit.gd -gexit

# 指定单个测试
godot --headless -s addons/gut/gut_cmdln.gd -gselect=test_unit.gd:test_method -gexit
```

### 输出解析

- 搜索 `Failed:` 和 `Pending:` 行
- 搜索 `[FAILED]` 标记获取具体失败测试
- 退出码: `0` = 全部通过

### 已知坑

- **-gexit 必须存在** — 没有则 Godot 进程不退出，TDD 循环卡死
- **headless 模式下无法访问 DisplayServer** — 涉及窗口操作的测试需要 mock
- **GUT 的 `assert_not_null($NodeName)` 在节点不存在时行为不确定** — 用 `assert_not_null(get_node_or_null("NodeName"))`

## 源码

- **脚本路径**: `**/*.gd`
- **场景路径**: `**/*.tscn`
- **资源路径**: `**/*.tres`
- **测试路径**: `test/**/test_*.gd`
- **不修改**: `addons/`

## 文档

- **官方文档**: `https://docs.godotengine.org/en/stable/`
- **GDScript 参考**: `https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/`
- **查询方式**: `WebFetch` + `curl` fallback
- **常用页面**: 见 `references/godot/docs.md`
