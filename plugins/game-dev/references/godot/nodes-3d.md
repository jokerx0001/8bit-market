# Godot 3D 核心节点速查

编码时最常用的 3D 节点。完整节点列表查官方文档：`https://docs.godotengine.org/en/stable/classes/`

---

## 常用节点

### 渲染

| 节点 | 用途 | 关键属性 |
|------|------|---------|
| `MeshInstance3D` | 显示 3D 网格 | `mesh` (BoxMesh, SphereMesh 等) |
| `Sprite3D` | 3D 空间中的 2D 精灵 | `texture`, `billboard` |
| `CSGBox3D` / `CSGSphere3D` / `CSGCylinder3D` | CSG 几何体 | `size`, `radius`, `material` |
| `WorldEnvironment` | 全局环境设置 | `environment` (天空、雾、后处理) |
| `GPUParticles3D` / `CPUParticles3D` | 3D 粒子 | `mesh`, `amount`, `lifetime` |

### 光照

| 节点 | 用途 |
|------|------|
| `DirectionalLight3D` | 方向光（太阳） |
| `OmniLight3D` | 点光源 |
| `SpotLight3D` | 聚光灯 |

### 物理

| 节点 | 用途 | 关键属性 |
|------|------|---------|
| `CharacterBody3D` | 角色移动 | `velocity`, `move_and_slide()` |
| `RigidBody3D` | 物理模拟 | `mass`, `apply_force()` |
| `StaticBody3D` | 静态碰撞 | 地形、建筑 |
| `Area3D` | 检测区域 | `body_entered`, `area_entered` signals |
| `CollisionShape3D` | 碰撞形状 | `shape` (BoxShape3D, SphereShape3D 等) |

### 摄像机

| 节点 | 用途 |
|------|------|
| `Camera3D` | 3D 摄像机 |
| `Marker3D` | 3D 位置标记 |

### 其他

| 节点 | 用途 |
|------|------|
| `AnimationPlayer` | 动画播放器 |
| `AudioStreamPlayer3D` | 3D 空间音频 |
| `NavigationRegion3D` | 导航网格区域 |
| `Path3D` | 3D 路径 |
| `Timer` | 定时器 |

## 3D 坐标系统

- **Y-up**: Y 轴向上（与 Blender 不同，Blender 是 Z-up）
- **单位**: 米（1 unit = 1 meter）
- **rotation**: 欧拉角（度）

## 3D 导入

3D 模型文件 (.glb, .fbx, .blend) 放入项目后，Godot 自动生成 `.import` 文件。导入后可访问：
- 网格: `load("res://models/character.glb")` 或通过场景树访问子节点
- 动画: 通过 AnimationPlayer 节点引用
- 材质: 可在导入设置中提取或在代码中覆盖

## 更多

不在此列表中的节点 → 查 Godot 文档 `classes/` 或问用户。
