# Godot 详细设计指引

plan skill 的 step 7 读本文件，执行 Godot 项目的详细设计。

---

## 设计内容

使用 `superpowers:brainstorming` 分析，从 `references/godot/nodes-{2d,3d}.md` 查节点类型。

### 场景节点树设计

对每个需要新建的场景，设计节点树结构：

```markdown
### {scene_name}.tscn
- 节点类型: {Node2D / Control / Node3D}
- 用途: {简要说明}

节点树:
{root_node} ({type})
├── {child_1} ({type})           # 用途
│   └── {grandchild} ({type})    # 用途
├── {child_2} ({type})           # 用途
└── {child_3} ({type})           # 用途

关键属性:
- {node_path}: {property} = {value}
- {node_path}: {signal} → {handler}

引用的外部资源:
- ext_resource: {type}, path="res://{path}"
```

### 信号连接设计

用 Mermaid 流程图描述场景间和场景内信号流：
- 场景 A 的信号 → 场景 B 的处理方法
- 节点内信号链

### 数据模型

- Autoload 单例：全局状态管理
- 场景内数据：节点属性、脚本变量
- 资源文件：.tres 配置文件

### 资源需求清单

从节点树提取所有外部资源引用（精灵、纹理、材质、模型、音频等）：

| # | 资源名称 | 类型 | 尺寸 | 使用场景 | 节点引用 |
|---|---------|------|------|---------|---------|
| 1 | player_sprite | Texture2D | 64x64 | Player 角色的 Sprite2D | Player/Sprite2D.texture |

AI 可生成的类型：.tres 材质、.gdshader 着色器、简单几何体 .tscn。
AI 不可生成的类型：.glb/.fbx 模型、复杂纹理贴图、骨骼动画 → 标记 `[HUMAN]`。

---

保存到 `{task_dir}/.work/design.md`。
