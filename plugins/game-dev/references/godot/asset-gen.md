# Godot 资产生成参考

此文件是 art-prompt-builder 和 art-resource-creator 生成资产 prompt 时的技术约束参考。

---

## 后端

使用 `mmx image generate`。

**两个模型：**

| 模型 | 自定义尺寸 | subject-ref | 适用 |
|------|----------|-------------|------|
| `image-01` | ✓ `--width` `--height` (512-2048, 8的倍数) | ✓ `type=character` | 精确控制、角色一致性 |
| `image-01-live` | ✗ 仅 `--aspect-ratio` | ✗ | 快速生成、纹理/背景 |

**风格一致性限制：** `--subject-ref` 仅支持 `type=character`。角色资源可用第一个生成的角色图当锚点。非角色资源（纹理、背景、道具）无法通过 mmx 实现图生图风格锚定——只能通过 prompt 文字描述保持风格一致。

---

## 快捷参考表

### 背景 / 大场景图

用途：标题画面、天空全景、视差层、环境美术。

```
{description in the art style}. {composition instructions}.
```
`mmx image generate --prompt "..." --aspect-ratio 16:9 --out path.png`（image-01-live 可用）

不需要后处理 — 直接用。

### 纹理

用途：可平铺表面——地面、墙壁、地板、UI 面板。

```
{name}, {description}. Top-down view, uniform lighting, no shadows, seamless tileable texture, suitable for game engine tiling, clean edges.
```
`mmx image generate --prompt "..." --out path.png`

不需要背景去除 — 整张图就是纹理。

### 单个对象 / 精灵

**简单对象**（道具、物品、图标）：
```
{name}, {description}. Centered on a solid {bg_color} background.
```
`mmx image generate --prompt "..." --out path.png`（image-01-live 可用）

背景色的选择：选一个跟主体**区分度高**、接近**预期游戏内背景**的颜色。森林游戏 → `dark-green`，天空/水面 → `steel-blue`，地牢 → `dark-gray`，通用 → `medium-gray`。**不要用纯 chromakey 色**（`#00FF00`）——会产生不自然的边缘色散。

**角色设计**（需要用 image-01 精确控制）：
```
{name}, {description}. Centered on a solid {bg_color} background.
```
`mmx image generate --model image-01 --prompt "..." --out path.png`

**变体（从参考图生成，仅角色可用 image-01）：**
```
{what to change: different angle, pose, color, etc.}
```
`mmx image generate --model image-01 --prompt "..." --subject-ref type=character,image=path_ref.png --out path_variant.png`

`--subject-ref` 传入参考图后，prompt 只描述**变化的部分**（动作、角度、颜色），不要重新描述角色外观——重复描述跟视觉引用竞争，削弱一致性。

### 物品套件（多个物品一张图）

生成多个物品在一张图上，然后用 ImageMagick 切割。比逐个生成便宜。

```
{item1}, {item2}, {item3}, {item4}. 2x2 grid layout, each item centered in its cell, solid {bg_color} background. {art style}.
```
`mmx image generate --prompt "..." --out path_grid.png`

切割：
```bash
magick path_grid.png -crop 50%x50% +repage assets/img/items/item_%d.png
```

### 3D 模型参考

mmx 不支持图片→3D 转换。该能力需外部 API（Tripo3D 等）。如需此能力，需单独配置。

如果仅为外观参考生成正面/侧面/3/4 视角图：

```
3D model reference of {name}. {description}. 3/4 front elevated camera angle, solid white background, soft diffused studio lighting, matte material finish, single centered subject, no shadows on background.
```
`mmx image generate --model image-01 --prompt "..." --out path.png`

---

## 资产尺寸标注

生成的资产必须标注目标游戏内尺寸。不同资产类型标注方式不同：

| 类型 | 尺寸标注格式 | 示例 |
|------|-------------|------|
| 3D 模型 | 目标尺寸（米） | `4m long`（车），`1.8m tall`（角色） |
| 纹理 | tile 尺寸（米） | `2m tile`（每 2m 通过 UV 重复一次） |
| 背景 | 显示像素 | `1920x1080`（全屏），`2560x720`（视差层） |
| 精灵 | 游戏内显示像素 | `128x128 px`（玩家），`64x64 px`（物品） |

**精灵尺寸陷阱：** 最小生成分辨率是 1K (1024px)。一张 1024px 的精灵缩到 64px 会模糊到失去所有细节。

缓解方法：
1. 避免过小的游戏内显示尺寸。精灵至少 128px
2. 生成套件图——多个物品共享一张 1K 图（2×2 布局 = 每个物品 ~512px），然后切割
3. prompt 要求**粗犷简洁的造型**——粗轮廓、平涂色、极简细节、夸张比例。这些能经受住缩小

---

## 视觉陷阱

### 方向和朝向

图片生成器不能可靠地区分左右朝向，或生成正确的旋转。"面向 NE"和"面向 NW"的 prompt 经常产出相同的图。

**解决方案：** 只生成一个方向（精灵通常面朝右），需要反向时用 `magick` 水平翻转：

```bash
magick input.png -flop output.png
```

### 用代码绘制的场景不用生成

纯几何图形（血条纯色矩形、单色球、直线分隔线）应在代码中绘制。但任何有纹理、细节或艺术风格的——角色、背景、地形、物体、图标——应使用生成资产。

### 视频帧尺寸一致性

从视频提取的帧（~720px）和图片生成资产（1024px）混合使用时，先把大的缩放到跟小的一致。

```bash
magick identify input.png                           # 查看尺寸
magick input.png -resize 720x720 -filter Lanczos output.png  # 缩放
```

### 用纹理做背景的陷阱

不要把一个小的重复纹理拉伸成背景。需要单个场景背景时用 `--aspect-ratio 16:9` 直接生成大图。需要平铺时才用纹理 prompt。
