---
name: game-dev:visual-compare
description: |
  This skill should be used when a coding agent or test agent needs to visually verify UI implementation.
  Compares a game screenshot against a visual-spec JSON file using coarse-grained semantic comparison
  (position, size, visibility, layout relationships — NOT pixel-precise).
  Triggered when the task involves visual/UI verification of a rendered screen.
---

# Visual Compare — 截图 vs 视觉规格对比

对比游戏截图与视觉规格 JSON，粗粒度判断 UI 是否达标。

**视觉规格格式定义：** `${CLAUDE_PLUGIN_ROOT}/references/visual-spec-format.md`。该文件定义了 spec JSON 的完整结构、字段说明和编写原则——读取它作为 spec 格式的权威来源。

## 输入

调用方传入两个路径：

- `screenshot`: 截图文件路径（PNG/JPG）
- `spec`: 视觉规格 JSON 文件路径（设计阶段产出）

## 工作流

### 1. 加载视觉规格

读取 spec JSON 文件。确认包含 `screen` 和 `elements` 字段。

### 2. 读取并分析截图

读取截图文件，对 spec 中每个 element 逐项观察实际渲染状态。

**分析原则：**

- **粗粒度、相对性描述。** 不使用像素坐标或精确百分比。使用自然语言表达位置关系（上半/下半、左侧/右侧、居中、偏左等）和大小关系（约占屏幕宽度 1/3、与标题等高、比按钮略宽等）。
- **注意元素间关系。** spec 中有 `relative_to` 字段时，检查该关系是否成立（如"与 xx 左对齐"、"在 xx 正下方"）。
- **注意缺失和溢出。** 元素完全不可见、部分被截断、超出容器边界都是重要问题。
- **不猜测。** 如果某个元素在截图中无法辨认（太小、被遮挡、颜色与背景融为一体），如实报告 `"visible": false` 并说明原因。
- **不关心像素级细节。** 间距差几个像素、圆角大小、字体粗细等不在此检查范围内。

### 3. 输出观察结果

将观察结果输出为 JSON。格式与 spec 同构（结构定义见 `${CLAUDE_PLUGIN_ROOT}/references/visual-spec-format.md`），每个 element 包含 `observed` 字段：

```json
{
  "screen": "{从 spec 复制}",
  "elements": [
    {
      "id": "title_text",
      "observed": {
        "visible": true,
        "position": "屏幕上三分之一处，水平居中",
        "size": "约占屏幕高度 6%",
        "color": "白色文字，深色背景上可辨",
        "notes": "与 spec 描述的'屏幕上半部分'吻合"
      }
    }
  ]
}
```

**observed 字段说明：**

| 字段 | 必须 | 说明 |
|------|------|------|
| `visible` | 是 | 元素是否在截图中可见。`false` 时其他字段可省略 |
| `position` | 是 | 粗粒度位置描述。使用上下左右中、对齐关系等自然语言 |
| `size` | 是 | 粗粒度大小描述。使用相对占比、元素间对比等自然语言 |
| `color` | 否 | 仅在 spec 中指定了颜色时填写 |
| `layout` | 否 | 仅对容器类元素，描述子元素的排列方式 |
| `notes` | 否 | 任何有助于对比判断的补充观察 |

### 4. 逐元素对比

对每个 element，将 `expected`（来自 spec）与 `observed`（来自截图分析）进行语义对比。

**对比规则：**

| 维度 | 通过条件 | 失败示例 |
|------|---------|---------|
| `visible` | 精确匹配 | spec 要求 visible=true，截图看不到 |
| `position` | 语义一致 | spec "左侧"，截图 "右侧" |
| `size` | 量级一致 | spec "约占屏幕 1/3"，截图 "约占屏幕 1/10" |
| `relative_to` | 关系成立 | spec "与标题左对齐"，截图明显不对齐 |
| `layout` | 排列方式一致 | spec "水平排列"，截图是纵向堆叠 |

**判定原则：**

- 语义相近视为通过。"上半部分" ≈ "顶部偏上" ≈ "屏幕上三分之一处"
- 量级差异超过一个量级（如 1/3 vs 1/10、1/2 vs 满屏）视为不通过
- 关系性描述（relative_to）是硬约束——对齐关系、包含关系、前后关系必须成立

### 5. 输出结果

**PASS 时：**

```
## VISUAL-COMPARE: PASS

{screen}: 全部 {N} 个元素视觉达标。
```

**FAIL 时：**

```
## VISUAL-COMPARE: FAIL

**不达标项：{M}/{N}**

### {element_id} — {维度}不达标

- **期望:** {spec 中的 expected 原文}
- **实际:** {observed 中的内容}
- **差异:** {一句话说明哪里不对}

### {element_id} — 未显示

- **期望:** visible=true, {spec 中的描述}
- **实际:** 截图中不可见。可能原因：未渲染 / 被遮挡 / 位置超出可视区域
```

## 重要约束

- **不要提出修复建议。** 只报告对比结果。修复是 coding agent 的事。
- **不要评价设计。** spec 是基准，不讨论它好不好。
- **不要猜测意图。** 截图看不到就是看不到，不说"可能在其他界面"。
- **粗粒度容忍。** spec 说"上半部分"，截图显示在 40% 位置 → 通过。spec 说"左侧"，截图显示在中间 → 失败。
