# Godot 2D 核心节点速查

编码时最常用的 2D 节点。完整节点列表查官方文档：`https://docs.godotengine.org/en/stable/classes/`

---

## 节点层级约定

```
Node2D               ← 2D 空间中的基础节点（位置、旋转、缩放）
├── CanvasItem        ← 所有 2D 可绘制对象的基类
│   ├── Node2D        ← 见上
│   └── Control       ← UI 控件基类
├── PhysicsBody2D     ← 2D 物理体
│   ├── CharacterBody2D  ← 角色控制器
│   ├── RigidBody2D      ← 刚体
│   ├── StaticBody2D     ← 静态碰撞体
│   └── Area2D           ← 检测区域
└── CollisionObject2D
    ├── Area2D
    └── PhysicsBody2D
```

## 常用节点

### 渲染

| 节点 | 用途 | 关键属性 |
|------|------|---------|
| `Sprite2D` | 显示 2D 纹理 | `texture`, `region_enabled`, `region_rect` |
| `AnimatedSprite2D` | 精灵帧动画 | `sprite_frames`, `animation`, `frame` |
| `TileMap` / `TileMapLayer` | 瓦片地图 | `tile_set`, layer 数据 |
| `CanvasLayer` | 独立渲染层 | `layer`, `follow_viewport_enabled` |
| `Parallax2D` | 视差滚动 | `scroll_scale` |
| `Particles2D` / `CPUParticles2D` | 2D 粒子 | `texture`, `amount`, `lifetime` |
| `Line2D` | 画线 | `points`, `width`, `default_color` |

### 物理

| 节点 | 用途 | 关键属性 |
|------|------|---------|
| `CharacterBody2D` | 角色移动 | `velocity`, `move_and_slide()` |
| `RigidBody2D` | 物理模拟 | `mass`, `gravity_scale`, `apply_force()` |
| `StaticBody2D` | 静态碰撞 | 不可移动的地形/墙壁 |
| `Area2D` | 检测区域 | `monitoring`, `monitorable`, signals: `body_entered` |
| `CollisionShape2D` | 碰撞形状 | `shape` (CircleShape2D, RectangleShape2D 等) |
| `RayCast2D` | 射线检测 | `target_position`, `is_colliding()` |

### UI (Control)

| 节点 | 用途 |
|------|------|
| `Control` | 所有 UI 的基类 |
| `Label` | 文本显示 |
| `Button` | 按钮 |
| `LineEdit` | 单行文本输入 |
| `TextEdit` | 多行文本编辑 |
| `Panel` | 背景面板 |
| `PanelContainer` | 带样式的容器 |
| `VBoxContainer` | 垂直布局 |
| `HBoxContainer` | 水平布局 |
| `GridContainer` | 网格布局 |
| `MarginContainer` | 边距容器 |
| `ScrollContainer` | 滚动视图 |
| `TextureRect` | 显示纹理 |
| `ProgressBar` | 进度条 |
| `HSlider` / `VSlider` | 滑块 |
| `CheckBox` | 复选框 |
| `OptionButton` | 下拉选择 |
| `PopupMenu` | 弹出菜单 |

### 其他

| 节点 | 用途 |
|------|------|
| `Camera2D` | 2D 摄像机 |
| `AudioStreamPlayer2D` | 2D 空间音频 |
| `AnimationPlayer` | 动画播放器 |
| `Timer` | 定时器 |
| `Marker2D` | 位置标记 |

## 2D 坐标系统

- **原点**: 左上角 (0, 0)
- **X 轴**: 向右为正
- **Y 轴**: 向下为正
- **单位**: 像素（默认缩放下）

## 更多

不在此列表中的节点 → 查 Godot 文档 `classes/` 或问用户。
