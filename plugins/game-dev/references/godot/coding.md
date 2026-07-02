# Godot GDScript + .tscn 编码规范

coding agent 在编写 Godot 代码时必须遵守这些约定。

---

## GDScript 规范

### 命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件名 | snake_case | `player_controller.gd` |
| 类名 | PascalCase | `class_name PlayerController` |
| 函数名 | snake_case | `func take_damage(amount):` |
| 变量名 | snake_case | `var max_health: int` |
| 常量 | UPPER_SNAKE_CASE | `const MAX_SPEED := 500` |
| 信号 | snake_case (过去式) | `signal health_changed(new_health)` |
| 私有成员 | `_` 前缀 | `var _internal_state` |

### 类型注解（必须）

```gdscript
# Good
var speed: float = 100.0
func take_damage(amount: int) -> void:
var player: Player = $Player as Player

# Bad — 无类型注解
var speed = 100
func take_damage(amount):
```

### 信号

```gdscript
# 定义信号（在 class 顶层）
signal health_changed(new_health: int)
signal died()

# 连接信号（推荐代码连接，不用编辑器连接以保持可追溯性）
button.pressed.connect(_on_button_pressed)

# 方法命名对应信号
func _on_button_pressed() -> void:
    pass
```

### 节点引用

```gdscript
# 使用 @onready 延迟初始化（推荐）
@onready var start_button: Button = $VBoxContainer/StartButton
@onready var health_label: Label = $HUD/HealthLabel

# 避免在 _ready 中手动赋值（除非是动态创建的节点）
```

### 资源加载

```gdscript
# 预加载（编译时常量）
const BULLET_SCENE := preload("res://scenes/bullet.tscn")
const PLAYER_TEXTURE := preload("res://assets/player.png")

# 运行时加载
var data := load("res://data/levels.json")
```

### 禁止

- `pass` 语句（空方法/空分支）
- `# TODO` 注释
- `print()` 调试语句（release 代码中保留除 `assert` 外的日志）
- 硬编码路径字符串（用 `const` 或 `@export`）

---

## .tscn 场景文件规范

### 文件结构

```
[gd_scene load_steps=2 format=3 uid="..."]

[ext_resource type="Script" path="res://scripts/player.gd" id="1_abc"]
[ext_resource type="Texture2D" path="res://assets/player.png" id="2_def"]

[node name="Player" type="CharacterBody2D"]
script = ExtResource("1_abc")

[node name="Sprite2D" type="Sprite2D" parent="."]
texture = ExtResource("2_def")
position = Vector2(0, 0)

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("CircleShape2D_ghi")
```

### 关键规则

1. **ext_resource 路径必须指向存在的文件** — 引用 `res://assets/missing.png` 会导致运行时紫色占位块
2. **每个节点的 `parent` 字段正确** — 错误的 parent 引用会导致节点层级断裂
3. **`load_steps` 必须与实际资源数一致** — ext_resource + sub_resource 总数
4. **script 引用使用 `ExtResource("id")`** — 已声明过的 ext_resource 通过 id 引用
5. **节点必须有 `name` 和 `type`** — 缺 type 会导致加载失败

### 创建场景文件时

- 从 plan 的节点树设计出发，逐层创建
- 先用简单的节点结构（name + type + parent），再补充属性
- 资源引用先声明 `ext_resource`，再用 `ExtResource("id")` 引用
- 信号连接优先在 .gd 中通过代码连接，不写入 .tscn

---

## .tres 资源文件规范

```tres
[gd_resource type="ShaderMaterial" load_steps=2 format=3 uid="..."]

[ext_resource type="Shader" path="res://shaders/glow.gdshader" id="1_xyz"]

[resource]
shader = ExtResource("1_xyz")
shader_parameter/glow_color = Color(1, 1, 1, 1)
shader_parameter/glow_intensity = 0.8
```

### 常用资源类型

| 类型 | 用途 |
|------|------|
| `ShaderMaterial` | 着色器材质 |
| `StandardMaterial3D` | 3D PBR 材质 |
| `Theme` | UI 主题 |
| `StyleBoxFlat` | UI 平面样式盒 |
| `StyleBoxTexture` | UI 纹理样式盒 |
| `CircleShape2D` / `RectangleShape2D` | 2D 碰撞形状 |
| `InputEventKey` | 输入事件 |
| `GDScript` | 脚本资源 |
| `AnimationLibrary` | 动画库 |

---

## 项目结构约定

```
project/
├── project.godot            # 项目配置
├── scenes/                  # .tscn 场景文件
│   ├── levels/
│   ├── ui/
│   └── characters/
├── scripts/                 # .gd 脚本文件
│   ├── autoload/            # Autoload 单例
│   ├── components/          # 可复用组件
│   └── systems/             # 系统逻辑
├── assets/                  # 美术资源
│   ├── sprites/             # 2D 精灵
│   ├── textures/            # 3D 纹理
│   ├── models/              # 3D 模型 (.glb, .fbx)
│   ├── audio/               # 音频
│   └── shaders/             # 着色器 (.gdshader)
├── resources/               # .tres 资源文件
│   ├── materials/
│   ├── themes/
│   └── animations/
├── test/                    # GUT 测试
│   ├── unit/
│   └── integration/
└── addons/                  # 第三方插件（不修改）
```

## 禁止硬编码路径

```gdscript
# Bad
var scene := load("res://scenes/level_1.tscn")

# Good — 用 const 预加载
const LEVEL_SCENE := preload("res://scenes/level_1.tscn")

# 或用 @export 暴露给编辑器
@export var level_scene: PackedScene
```
