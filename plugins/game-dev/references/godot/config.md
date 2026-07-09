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

检测到维度后加载对应的 `${CLAUDE_PLUGIN_ROOT}/references/godot/nodes-{2d,3d}.md`。

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

### 测试命令模板
`{...}` 为必须替换的占位符。

- **test_runner**: `godot` — 测试运行器
- **test_cmd_full**: `godot --headless -s addons/gut/gut_cmdln.gd -gdir=test/ -glog=1 -gexit` — 全量运行
- **test_cmd_suite**: `godot --headless -s addons/gut/gut_cmdln.gd -gdir=test/ -gselect={suite} -glog=1 -gexit` — 指定测试文件（`-gselect` 子串匹配文件名）
- **test_cmd_single**: `godot --headless -s addons/gut/gut_cmdln.gd -gdir=test/ -gselect={suite} -gunit_test_name={case} -glog=1 -gexit` — 单个测试方法

### 输出解析

- **test_failure_grep**: `grep -E '\[Failed\]|\[Fail\]' {log_path}` — 提取失败详情（GUT 输出格式：`[Failed]: test_name` + `[Fail]: assert_eq(...)`）
- 退出码: `0` = 全部通过

### 已知坑

- **-gexit 必须存在** — 没有则 Godot 进程不退出，TDD 循环卡死
- **-gselect 是子串匹配** — `-gselect=test_foo` 会同时匹配 `test_foo.gd` 和 `test_foo_extra.gd`。testsuite 命名必须唯一，避免一个名字是另一个的子串
- **headless 模式下无法访问 DisplayServer** — 涉及窗口操作的测试需要 mock
- **GUT 的 `assert_not_null($NodeName)` 在节点不存在时行为不确定** — 用 `assert_not_null(get_node_or_null("NodeName"))`

## 源码

- **脚本路径**: `**/*.gd`
- **场景路径**: `**/*.tscn`
- **资源路径**: `**/*.tres`
- **测试路径**: `test/**/test_*.gd`
- **不修改**: `addons/`

## 文档

- **本地全量建档**（直接 Read，不要 WebFetch）:
  - 代码风格规范: `${CLAUDE_PLUGIN_ROOT}/references/godot/style-guide.md`
  - 项目组织规范: `${CLAUDE_PLUGIN_ROOT}/references/godot/project-organization.md`
- **在线文档**（API 语法等，用 WebFetch 查询）: `https://docs.godotengine.org/en/stable/`
- **GDScript 参考**: `https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/`
- **常用页面**: 见 `${CLAUDE_PLUGIN_ROOT}/references/godot/docs.md`

## MCP 集成

如果当前会话配置了 GoPeak 等 Godot MCP 服务器，开发时**优先使用 MCP 工具**与 Godot 编辑器/运行时交互。MCP 工具提供比纯 CLI 更丰富、更精确的操作能力（如运行时节点检查、LSP 诊断、截图验证等）。

### MCP 可用性检测

每个 agent 在 spawn 时，系统 prompt 中会列出当前会话所有可用的工具（含 MCP 工具）。不需要调用任何命令来检测——直接看收到的工具列表。

扫描规则：工具名匹配 `mcp__` 前缀且包含 `gopeak` 或 `godot`。匹配到 → 标注 `mcp: active`，后续 Godot 操作优先走 MCP。未匹配到 → 标注 `mcp: unavailable`，全部走 CLI。

MCP 首选模式下，以下场景优先用 MCP 工具而非 CLI 或 Read/Write：

| 场景 | 优选 MCP 工具 | 回退 CLI |
|------|-------------|----------|
| 获取场景节点/属性 | `mcp__*gopeak*__get_*` 或等效运行时检查工具 | `grep`/`Read` 读 `.tscn` 文件 |
| LSP 诊断/补全 | `mcp__*gopeak*__lsp_*` | 无 CLI 回退 — 直接读源码推断 |
| 运行/停止游戏 | `mcp__*gopeak*__run_*` / `mcp__*gopeak*__stop_*` | `godot --headless` CLI |
| 截图验证 UI | `mcp__*gopeak*__screenshot_*` | 无回退 — 人工验证 |
| 调试信息 | `mcp__*gopeak*__debug_*` / `mcp__*gopeak*__dap_*` | `grep` 日志文件 |
| 输入注入 | `mcp__*gopeak*__input_*` | 无回退 — 手动操作 |
| 创建场景/节点 | `mcp__*gopeak*__create_*` | Write `.tscn` 文件 |

### 回退规则

- MCP 工具不可用或调用失败 → 回退到 CLI 命令
- MCP 不可用不是阻塞条件，不因 MCP 问题而暂停流程
- MCP 模式下的自我验证协议不变 — GREEN 三层结构、REFACTOR 自验证协议全部照常执行
