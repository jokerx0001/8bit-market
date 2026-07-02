# Godot 文档查询约定

所有 agent（plan、coding、test-agent）使用同一工具和同一文档源查询 Godot 知识。

## 文档地址

```
https://docs.godotengine.org/en/stable/
```

## 查询工具

优先使用 Context7（如果可用），失败则用 `WebFetch`，再失败用 `curl`。

```
WebFetch(url="https://docs.godotengine.org/en/stable/{page}.html", prompt="{查询内容}")
```

## 常用文档页面

| 页面 | URL | 何时查询 |
|------|-----|---------|
| GDScript 基础 | `tutorials/scripting/gdscript/gdscript_basics.html` | 语法、类型、函数 |
| 节点和场景 | `tutorials/scripting/nodes_and_scene_instances.html` | 场景实例化、节点操作 |
| 信号 | `tutorials/scripting/signals.html` | connect、emit、signal 定义 |
| 资源 | `tutorials/scripting/resources.html` | 加载资源、Resource 类型 |
| 导出 | `tutorials/scripting/gdscript/gdscript_exports.html` | @export 变量 |
| 场景文件格式 | `contributing/development/file_formats/tscn.html` | .tscn 文件结构 |
| Control 节点 | `classes/class_control.html` | UI 布局、锚点、边距 |
| Theme | `tutorials/ui/gui_skinning.html` | 主题系统、样式盒 |
| AnimationPlayer | `classes/class_animationplayer.html` | 动画播放 |
| TileMap (2D) | `tutorials/2d/using_tilemaps.html` | TileMap 使用 |
| 物理 (2D) | `tutorials/physics/physics_introduction.html` | 2D 物理 |
| 物理 (3D) | `tutorials/3d/physics_introduction.html` | 3D 物理 |
| 着色器 | `tutorials/shaders/shader_reference/shading_language.html` | .gdshader 语法 |
| ShaderMaterial | `classes/class_shadermaterial.html` | 着色器材质参数 |
| GUT 测试 | `https://gut.readthedocs.io/en/latest/` | GUT API、断言、参数化 |
| 导出 | `tutorials/export/exporting_projects.html` | 项目导出 |
| InputMap | `tutorials/inputs/input_examples.html` | 输入映射 |
| Viewport | `classes/class_viewport.html` | 视口、分辨率 |

## 查询模式

1. **查找 API 语法**：不确定 GDScript 方法签名 → WebFetch 对应页面
2. **查找节点属性**：不确定节点的可用属性 → 查 `classes/class_{nodename}.html`
3. **查找最佳实践**：不确定架构模式 → 查 tutorials 对应章节
4. **查找错误原因**：遇到 Godot 报错 → 用错误信息关键词构造查询

## 示例

```
# 查询 GDScript 信号连接语法
WebFetch(url="https://docs.godotengine.org/en/stable/tutorials/scripting/signals.html", prompt="如何在 GDScript 中连接信号？connect 方法的参数是什么？")

# 查询 .tscn 文件格式
WebFetch(url="https://docs.godotengine.org/en/stable/contributing/development/file_formats/tscn.html", prompt=".tscn 文件中 ext_resource 和 sub_resource 的格式是什么？")
```
