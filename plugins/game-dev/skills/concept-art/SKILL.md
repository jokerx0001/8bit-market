---
name: game-dev:concept-art
description: |
  Generate a reference image of what the finished game looks like.
  Anchors art direction for plan, visual-qa, and downstream agents.
  Called by plan phase after requirements are confirmed.
---

# Concept Art — 参考图生成

根据用户需求生成游戏参考图。锚定美术方向。

## 输入来源

从以下文档读取需求上下文：

- `{task_dir}/.work/user-prompt.md` — 用户原始输入（原语），检查用户是否直接指示了美术风格偏好
- `{task_dir}/.work/grill-interview.md` — grilling 采访记录, 对用户原始输入的偏差确认，防止理解错误
- `{dev_dir}/requirements.md` — 项目级全量需求文档（如果存在），了解游戏全貌
- `{task_dir}/.work/requirements.md` — 本次 feat 的行为清单和边界规则

## 已有资源分析（可选 `--from-assets`）

当开发中的项目已有美术资源（sprites、纹理、角色图），可通过 `--from-assets <path>` 传入资源目录或代表性文件路径。skill 会先分析现有资源的美术风格，将其注入 prompt 的 `{Art style, color palette}` 段，确保生成的参考图与已有资源风格一致。

**分析步骤：**

1. 列出 `--from-assets` 指向的目录，选出 1-3 张代表性文件
2. 对每张调用 `mmx vision describe`：

```bash
mmx vision describe --image <asset_path> \
  --prompt "Describe the art style, color palette, proportions, and rendering technique in detail. Focus on visual characteristics transferable to a text-to-image prompt. Describe in 3-5 sentences."
```

3. 将输出汇总为风格描述段，填入 prompt 骨架的 `{Art style, color palette}` 位置

未传 `--from-assets` 时跳过此步，`{Art style, color palette}` 从 requirements.md 的功能描述推导。

## CLI

```bash
mmx image generate \
  --prompt "{prompt}" \
  --aspect-ratio 16:9 \
  --out {task_dir}/reference.png
```

## Prompt

必须看起来像游戏截图，不是概念艺术。每一个可见对象都会成为下游的资源需求——下游 agent 必须生成并放置它。只 prompt 你会实际构建的元素。一个干净的游戏截图，展示每个游戏对象在正确比例和位置，才能驱动 pipeline；美丽的大气氛图会浪费预算。

### Prompt 规则

- **枚举每个游戏对象** — 玩家角色、每种敌人类型、障碍物、收集品、弹射物、平台、道具。每个对象标注屏幕位置和大致大小。图上出现什么，下游就生成什么；图上不出现的东西下游会忘掉。
- **反映真实技术约束。** 如果计划使用 tiling 背景，prompt 一个适合平铺的构图。如果 sprite 是独立层，把它们显示为背景上的独立对象，而不是融合的写实渲染。
- **不要 prompt 降级品质**（"lowpoly"、"pixel art"、"retro"）。这没有帮助——生成器产出的东西更差，但没有更接近游戏。prompt 你真正需要的构图的清晰锐利渲染。
- **聚焦最重要的 gameplay 时刻** — 最能展示空间布局、核心机制和玩家最常看到的相机视角的那一帧。
- **排除你不会构建的。** 体积光照、运动模糊、景深、大气雾、复杂反射、镜头光晕、细节投影——除非游戏确实会实现它们。它们会制造没人能实现的需求。
- **展示 HUD/UI 元素。** 血条、分数计数器、小地图、物品槽——包含每个 UI 元素及屏幕位置。这些也是实现需求。

```
Screenshot of a {2D/3D} video game. {Camera: angle, distance, perspective}.
Game objects: {player — appearance, position, size vs screen}. {enemies/NPCs — each type, position}. {obstacles}. {collectibles/pickups}. {projectiles if any}.
Environment: {background layers — sky, distant, mid}. {playfield surface — material, tiling}. {foreground elements}. {boundaries/edges}.
HUD: {each UI element — type and screen position}.
{Art style, color palette}. Clean sharp digital rendering, game engine output.
```

这张图会成为 visual QA 的对比基准——你固化进去的每个空间和风格选择都会变成下游的需求。

## 输出

`{task_dir}/reference.png` — 16:9 图片。

将美术方向写入 `{task_dir}/.work/art-direction.md`——下游 agent 在构思各自的资源 prompt 时以此为参考（不是机械地拼接，而是转化为各资源类型适用的描述）：

```markdown
# Art Direction

**Art direction:** <美术风格描述>
```

## mmx CLI 参数说明

- `--prompt`: 必填，图片描述
- `--aspect-ratio`: 默认 `16:9`
- `--out`: 保存路径
- `--width` / `--height`: 可选，自定义尺寸（512-2048，8 的倍数）。不传则用 `--aspect-ratio`
- `--prompt-optimizer`: 可选，自动优化 prompt。默认不加，因为我们已手工构造了精确的 prompt
