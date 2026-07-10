---
name: game-dev:asset-extract
description: |
  Analyze reference.png to identify visual elements and write resource requirements.
  Called by orchestrator after concept-art generates reference.png, before plan phase.
  Uses mmx vision to extract object types, sizes, proportions, and spatial relationships.
---

# Asset Extract — 从参考图提取资源需求

分析 `{task_dir}/reference.png`，识别所有视觉对象，判定生成策略，写入 `{task_dir}/.work/resources.md`。

## Setup

Read `${CLAUDE_PLUGIN_ROOT}/references/godot/asset-gen.md` for prompt templates and per-asset-type constraints.

## Workflow

### 1. Analyze reference.png → identify visual elements

用 mmx vision 读取 `reference.png`，理解视觉构成：哪些对象可见、比例关系、环境结构、前景/背景分层。以此判断需要什么资源、什么尺寸。

```bash
mmx vision describe --image {task_dir}/reference.png \
  --prompt "Analyze this game reference image in detail. For every distinct visual object visible in the frame, identify:
1. What type of asset it is (3D model, texture, sprite, background, UI element)
2. Its approximate size relative to the screen/playfield
3. Its position and spatial role in the scene
4. Whether it could be constructed with simple geometry (boxes, cylinders, planes) or requires a custom model

Also describe:
- The camera angle, distance, and perspective
- The environment layers (background, midground, foreground)
- The art style and color palette
- Any HUD/UI elements and their screen positions

Be specific about proportions and spatial relationships. Every object you mention should become a resource requirement."
```

读 `{task_dir}/.work/requirements.md`（用户的 game description）和 `{task_dir}/.work/architecture.md`（如果已存在）。将参考图的视觉分析与需求描述和架构交叉对照，构建完整的资源列表：

- **3D 模型**: 角色、载具、关键道具、建筑 — 任何需要几何体的
- **纹理**: 地面、墙壁、UI 面板 — 平铺材质
- **背景**: 天空全景、视差层、标题画面 — 大场景图
- **精灵**: 角色、物品、图标 — 2D 视觉元素

### 2. 判定生成策略

对每个识别出的资源，判定：

| 条件 | 策略 | 标注 |
|------|------|------|
| 复杂图片（角色/场景/插画） | mmx image generate | `生成: mmx` |
| 简单 UI 几何（纯色块/渐变/边框） | Python Pillow 生成 | `生成: pillow` |
| 3D 能用 CSG/Primitive/Noise 构造 | coding agent 运行时构造 | `策略: CSG构造`，不生成文件 |
| 3D 复杂（角色/有机形状） | 无法自动生成 | `[HUMAN]` |
| 纯代码可实现（直线/纯色块） | 不生成资源 | `策略: code-only` |

CSG/Primitive 构造判定参考：
- 能用 Box/Sphere/Cylinder/Capsule 组合完成 → CSG构造
- 需要自定义顶点/有机形状 → [HUMAN]

### 3. 标注尺寸

每个资源**必须**有 Size 列。没有这个，coding agent 会统一缩放到错误尺寸。

- **3D 模型:** 目标尺寸（米），如 `1.8m tall`（角色）、`0.3m`（金币）
- **纹理:** tile 尺寸（米），如 `2m tile`（每 2m 通过 UV 重复一次）
- **背景:** 显示像素，如 `1920x1080`（全屏）
- **精灵:** 游戏内显示像素，如 `128x128 px`、`64x64 px`

### 4. 写入 resources.md

```markdown
# 资源需求清单

## 风格方向
{从 reference.png 提取的美术风格描述}

## 资源列表

### {资源名称}
- **用途**: {使用场景}
- **类型**: {精灵/背景/UI素材/纹理/材质/模型}
- **尺寸**: {详见 Size 列规则}
- **格式**: {PNG/GLB/tres}
- **策略**: {mmx / pillow / CSG构造 / [HUMAN] / code-only}
- **风格要求**: {具体视觉要求}
- **输出目录**: {从 ${CLAUDE_PLUGIN_ROOT}/references/{tech}/design-resources-{2d,3d}.md 获取}
```

## 常见错误

- **小精灵退化** — 生成分辨率最低 1K。1024px 缩到 64px 会糊。避免极小显示尺寸，或生成套件图（多个物品共享一张 1K 图），或 prompt 粗犷简洁造型（粗轮廓、平涂色）
- **纹理当背景** — 不要把重复纹理拉伸成单张背景。需要大场景图时直接用 `--aspect-ratio 16:9` 生成
- **代码能画的不用生成** — 纯色矩形血条、单色球、直线分隔线应在代码中绘制
