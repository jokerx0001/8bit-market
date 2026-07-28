# Ren'Py 详细设计模板

game-dev:design skill 读本文件，按此模板编写 design.md。

---

## 对每个新建的 screen

```markdown
### {screen_name}（新建）

**设计意图：** 这个 screen 在架构中的角色。

**Widget 树：**

screen_name:
  vbox:
    text "标题" id "title"
    hbox:
      imagebutton idle "icon.png" action ...

**关键属性：**

- widget_id: property = value
- screen: modal = True

**交互流程：**

Mermaid flowchart。用户操作路径——点击按钮 → 跳转 screen / 触发 label / 条件分支。

**持久化数据：**

| 变量 | 类型 | 默认值 | 用途 |
|------|------|--------|------|

**资产声明：**

| # | 资源名称 | 类型 | 尺寸 | 使用场景 |
|---|---------|------|------|---------|
```

## 对每个修改的 screen

```markdown
### {screen_name}（修改）

**为什么改：** 从架构——{这个 screen 的角色变化}。

**改什么：**

- 新增 widget {widget_type}，用途: {说明}
- 修改 {现有 widget/逻辑}: {变更前 → 变更后，理由}
- 删除 {widget/逻辑}: {原因}
```

---

## 内容规则

**必须遵守：**
- 按架构文档列出的 screen 逐行编写
- 新建 screen 写完整 Widget 树
- 修改 screen 必须写"为什么改"和"改什么"

**禁止内容：**
- RPY 代码
- Screen 之间的跳转关系（architecture 已定义）
