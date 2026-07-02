# Ren'Py 详细设计指引

plan skill 的 step 7 读本文件，执行 Ren'Py 项目的详细设计。

---

## 设计内容

使用 `superpowers:brainstorming` 分析：

### Widget 树结构
- 每个 Screen 的 widget 层级（vbox/hbox/fixed/grid）
- 关键交互 widget 的 `id` 属性

### 交互流程

用 Mermaid 流程图描述用户操作路径：
- Screen A → 点击按钮 → Screen B
- 条件分支（如：有选中角色 → 跳转；无选中 → 停留）

### Transform/Transition 设计

- 入场/退场动画
- hover 效果
- 过渡效果

### 持久化数据

| 变量 | 类型 | 默认值 | 用途 |
|------|------|--------|------|
| persistent.xxx | bool | False | ... |

### 资源需求

从 widget 树提取外部资源引用。Ren'Py 项目通常由美术预先提供，此处列出需求供 design-resources 阶段（或人工）处理：

| # | 资源名称 | 类型 | 尺寸 | 使用场景 |
|---|---------|------|------|---------|
| 1 | char_alice_happy | 立绘 | — | Alice 角色对话时显示 |
| 2 | bg_school | 背景 | 1920x1080 | 学校场景背景 |

---

保存到 `{task_dir}/.work/design.md`。
