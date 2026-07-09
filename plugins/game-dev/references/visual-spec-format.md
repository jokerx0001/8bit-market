# Visual Spec 格式规范

此文件定义 plan → visual-compare / test-agent 的共享契约。plan 产出 visual-spec JSON，visual-compare 和 test-agent 消费它做视觉验证。

---

## 用途

visual-spec 描述一个界面/场景中**玩家应该看到什么**——元素的位置、大小、颜色、布局关系。用粗粒度自然语言，不做像素级精度。

**产出方：** plan（步骤 8 详细设计阶段）
**消费方：** visual-compare skill、test-agent

---

## 存放位置

```
{task_dir}/.work/visual-specs/{spec-name}.json
```

plan.md 中 visual 任务通过 `spec:` 标注引用：

```
- [AI-N] (type: visual, spec: .work/visual-specs/enemy-health-bar.json) 敌人血条显示：...
```

---

## JSON 结构

```json
{
  "screen": "{界面/场景名称}",
  "description": "{一句话描述这个画面的整体外观}",
  "elements": [
    {
      "id": "{元素标识，snake_case}",
      "type": "{元素类型}",
      "expected": {
        "visible": true,
        "position": "{粗粒度位置描述}",
        "size": "{粗粒度大小描述}",
        "color": "{颜色描述}（可选）",
        "layout": "{子元素排列方式}（仅容器类元素）",
        "relative_to": "{相对位置关系}（可选）"
      }
    }
  ]
}
```

---

## 字段说明

### 顶层

| 字段 | 必须 | 说明 |
|------|------|------|
| `screen` | 是 | 界面/场景名称，用于日志和报告 |
| `description` | 是 | 一句话整体外观描述，建立视觉基线 |
| `elements` | 是 | 需要检查的元素列表 |

### elements[].type

| 类型 | 含义 |
|------|------|
| `text` | 文字标签（标题、名称、数值） |
| `button` | 可交互按钮 |
| `card` | 卡片组件（角色卡、物品卡） |
| `container` | 容器/列表/面板 |
| `bar` | 进度条/血条/能量条 |
| `icon` | 图标/头像 |
| `particle` | 粒子效果 |
| `animation` | 动画片段 |
| `other` | 其他视觉元素 |

### elements[].expected

| 字段 | 必须 | 说明 |
|------|------|------|
| `visible` | 是 | 元素是否可见。`true` / `false` / `conditional`（条件可见，如"选中后可见"） |
| `position` | 是 | 粗粒度位置描述。使用自然语言：上半/下半、左侧/右侧、居中、顶部、底部、屏幕外 |
| `size` | 是 | 粗粒度大小描述。使用相对占比或元素间对比：约占屏幕宽度 1/3、与标题等高、比按钮略宽 |
| `color` | 否 | 仅当颜色有明确要求时填写。粗粒度：白色文字、深色背景、红色警告色、绿色→黄色→红色渐变 |
| `layout` | 否 | 仅容器类元素。描述子元素排列方式：水平排列等间距、纵向堆叠、网格 2 列 |
| `relative_to` | 否 | 相对位置关系：位于 xx 正下方、与 xx 左对齐、在 xx 内部居中 |

---

## 编写原则

- **粗粒度、相对性描述。** 不使用像素坐标或精确百分比。用自然语言表达位置和大小关系。
- **注意元素间关系。** `relative_to` 描述的是硬约束——对齐关系、包含关系、前后关系。
- **不写颜色 hex 值。** 说"红色"不说"#FF0000"——那是 ui 还原的精度范围。
- **条件可见用 `"visible": "conditional"`**，在 description 或 notes 中说明条件。
- **不描述实现方案。** 不写"用 ProgressBar 节点"、"设置 modulate"——只描述玩家看到什么。
- **覆盖所有玩家可见的元素。** 不漏掉标题、按钮、卡片、图标、粒子、动画。

---

## 示例

```json
{
  "screen": "角色选择界面",
  "description": "主菜单点击'开始游戏'后进入。深色渐变背景，中间水平排列 3 张角色卡片，顶部标题，底部确认按钮。",
  "elements": [
    {
      "id": "screen_title",
      "type": "text",
      "expected": {
        "visible": true,
        "position": "屏幕上半部分，水平居中",
        "size": "字号较大，约占屏幕高度 5-8%",
        "color": "白色或浅色文字"
      }
    },
    {
      "id": "character_card_list",
      "type": "container",
      "expected": {
        "visible": true,
        "position": "屏幕中部，水平居中",
        "size": "宽度约占屏幕 80%，高度约占屏幕 50%",
        "layout": "水平排列，等间距",
        "relative_to": "位于 screen_title 正下方"
      }
    },
    {
      "id": "character_card_1",
      "type": "card",
      "expected": {
        "visible": true,
        "position": "卡片列表中最左侧",
        "size": "宽度约为卡片列表总宽的 1/4",
        "relative_to": "与 character_card_2 水平相邻，间距一致"
      }
    },
    {
      "id": "confirm_button",
      "type": "button",
      "expected": {
        "visible": true,
        "position": "屏幕下半部分，水平居中",
        "size": "宽度约占屏幕 30%，高度约占屏幕 8%",
        "color": "与背景色有明显对比，可辨识为可点击按钮",
        "relative_to": "位于 character_card_list 正下方"
      }
    }
  ]
}
```

---

## visual vs ui 的精度边界

| 维度 | visual-spec | HTML 设计稿（ui 任务） |
|------|-------------|----------------------|
| 位置 | 上半部分、左侧、居中 | 精确间距、margin、padding |
| 大小 | 约占屏幕 1/3、比按钮略宽 | 精确宽高 px |
| 颜色 | 红色、深色背景 | #FF0000、rgba(0,0,0,0.8) |
| 字体 | 字号较大 | 14pt、font-weight: 700 |
| 关系 | 位于 xx 下方、与 xx 左对齐 | 精确的 flexbox/grid 约束 |

visual-spec 回答"对的东西在大概对的位置吗？"——ui 还原回答"像素精确吗？"
