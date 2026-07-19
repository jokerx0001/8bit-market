---
name: game-dev:asset-extract-doc
description: |
  Extract asset requirements from design.md and write resources.md with generation strategies.
  Called by orchestrator after plan phase. Reads design.md's inline asset declarations,
  classifies each asset (code-only/mmmx/pillow/CSG构造/[HUMAN]), and writes resources.md.
  Replaces asset-extract for engineering-scale incremental development — no reference image needed.
---

# Asset Extract from Design Doc

从设计文档提取资产需求，判定生成策略，写入 resources.md。

## 输入

`{task_dir}/.work/design.md` — plan 阶段产出，包含内联的 `**资产:**` 声明块。

## 工作流

### 1. 提取所有资产声明

扫描 design.md，提取所有 `**资产:**` 声明块的起始位置。每个声明块从 `**资产:` 开始，到下一个 `**资产:` 或所属模块节结束。

按 design.md 的 `###` 模块名分组——每个资产属于它所在的那个模块节。

### 2. 逐条判定生成策略

对每条资产，根据 **类型 + 视觉要求** 判定策略：

| 条件 | 策略 | 说明 |
|------|------|------|
| 纯色/渐变/圆角/边框，无纹理需求 | `code-only` | StyleBoxFlat / Theme 可绘制，不生成文件 |
| CSG 基本体 + 纯色材质 | `CSG构造` | Box/Sphere/Cylinder/Capsule 组合可构造 |
| 简单几何 UI（渐变多、需抗锯齿） | `pillow` | Python Pillow 生成简单图形 |
| 具象图形（图标/精灵/角色/场景） | `mmx` | 需要图像生成模型 |
| 复杂纹理/材质（非纯色） | `mmx` | 需要图像生成模型 |
| 3D 有机形状/骨骼动画 | `[HUMAN]` | 无法自动生成，需人工提供 |
| 3D 简单几何（Box/Sphere/Cylinder/CSG 组合） | `CSG构造` | coding agent 运行时构造 |

**判定优先级：**
1. 先看类型：`模型` → 判断 CSG构造 还是 [HUMAN]；`精灵/纹理/背景` → 一般是 mmx
2. 再看视觉要求：`StyleBoxFlat 可绘制` 或描述纯色/圆角/边框 → 降级为 code-only
3. UI素材 类型最灵活——从纯色块(code-only)到复杂纹理(pillow/mmmx)都有可能

**风格方向：** 从 design.md 中提取项目中已有的风格描述（如有 style-decision.md 则引用），写入 resources.md 的 `## 风格方向` 节。

### 3. 标注尺寸

尺寸从资产声明的 `尺寸:` 字段直接提取。如写"见上下文"，从所属模块的显示推导中推断：
- UI控件常见尺寸：48×48、64×64（槽位）、200×40（按钮）
- 精灵常见尺寸：32×32、64×64、128×128
- 纹理常见 tile：1m、2m（游戏内单位）
- 背景常见分辨率：1920×1080

### 4. 写入 resources.md

```markdown
# 资源需求清单

## 风格方向
{从 design.md / style-decision.md 提取的风格描述，文本形式——这是 mmx prompt 的风格锚点}

## 资源列表

### {模块名}

#### {资源名称}
- **用途**: {从资产声明提取}
- **类型**: {精灵/纹理/模型/背景/UI素材/材质}
- **尺寸**: {从资产声明提取}
- **策略**: {code-only / pillow / mmx / CSG构造 / [HUMAN]}
- **视觉要求**: {从资产声明提取——mmx prompt 的直接输入}

{下一条资源...}
```

输出路径和格式**不写**——那是 art-resources-conductor 和 coding agent 按约定自行决定的。

## 常见错误

- **code-only 误判为 mmx** — 视觉要求写"深色半透明圆角"但没提纹理 → code-only。只有确实需要图像内容（图标、纹理图、场景图）才走 mmx。
- **CSG构造 误判为 [HUMAN]** — "方形平台、圆柱柱子"是 CSG构造，不是 [HUMAN]。[HUMAN] 只用于有机形状和骨骼动画。
- **尺寸缺失** — 资产声明没写尺寸时，从上下文推断并标注"(推断)"，不生成模糊尺寸的 prompt。
