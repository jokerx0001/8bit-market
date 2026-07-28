# Godot 详细设计模板

---

## 对每个新建的 scene

```markdown
### {scene_name}.tscn（新建）

**节点树：**

RootNode (NodeType)
├── Child1 (NodeType)              # 用途
│   └── Grandchild (NodeType)      # 用途
└── Child2 (NodeType)              # 用途
    └── (挂载点，子 scene 结构见本节第 N 章)

**关键属性：**

- 节点路径: property = value（非默认值）

**内部信号连接：**

NodeA.signal → NodeB.method()

**显示推导：**

用户在这个 scene 中看到什么——画面描述、位置、布局。

**GDScript 主要内容：**

- 主要方法的逻辑（做什么，不写代码）
- 关键状态变量和生命周期

**资产: {名称}**
- 用途: {一句话}
- 类型: {精灵/纹理/UI素材/材质}
- 尺寸: {W×H}
- 视觉要求: {颜色、材质、风格}
```

---

## 对每个修改的 scene

```markdown
### {scene_name}.tscn（修改）
- 新增/删除挂载scene，创建方式: {编译期嵌套 / 运行时 instantiate}，挂载点: {节点路径}
- 自身节点变化
- GDScript 逻辑变更: {哪些方法/逻辑需要改，改什么}

```

---

## 内容规则

**必须遵守：**
- 新建 scene 的节点树完整展开到底

