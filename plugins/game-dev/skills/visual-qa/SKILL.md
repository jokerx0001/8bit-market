---
name: game-dev:visual-qa
description: |
  Visual quality assurance — analyze game screenshots for defects, compare against reference.
  Uses mmx vision for image analysis. Supports static and question modes.
---

# Visual QA

$ARGUMENTS

CRITICAL: Your job is to find problems, not confirm things look fine. Do not rationalize, justify, or explain away what you see. If it looks wrong, report it.

## Backend

Uses `mmx vision describe` for all image analysis.

## Capability Detection

当前后端 `mmx vision` 不支持多图输入，**dynamic 模式暂不可用**。

调用 dynamic 时 → 输出：
```
Dynamic mode unavailable: current backend does not support multi-image input.
```
未来更换为支持多图的后端时，删除此段，dynamic 自动生效。

## Mode Detection

From the arguments — freeform text with file paths:
- Reference image mentioned + 1 screenshot → Static mode
- Reference image + multiple frames → Dynamic mode — 暂不可用（见 Capability Detection）
- No reference, just a question about screenshots → Question mode

## Blank Screenshot Detection

截图为空白或无效时，`mmx vision` 会返回 `API error: input new_sensitive, input image sensitive (HTTP 200)`。这类截图不能用于验证，必须识别并报告给调用方。

### 统一输出格式

无论预检还是 API 错误触发，**统一输出以下格式**（调用方只需检查 `blank_screenshot: true`）：

```
### Answer
**blank_screenshot**: true
**diagnosis**: {具体原因}
```

### 预检（API 调用前）

对每张截图执行：

```bash
STD=$(identify -format "%[standard-deviation]" {screenshot.png} 2>/dev/null || echo "0")
IS_BLANK=$(echo "$STD < 0.02" | bc -l 2>/dev/null || echo "0")
```

如果 `$IS_BLANK` 为 `1`（标准差 < 0.02），**不要调用 API**，直接输出 blank_screenshot 响应。diagnosis 写明 std 值。

Static 模式下只对 screenshot 做预检，不对拼接后的图做检查。

### API 错误捕获（API 调用后）

`mmx vision` 的返回结果如果包含以下内容，说明截图对 API 无效（即使预检通过——例如几乎透明、仅顶部有少量内容的图）：

```
"error": {
  "code": 1,
  "message": "API error: input new_sensitive, input image sensitive (HTTP 200)"
}
```

**将此错误等同于 blank_screenshot。** 不要重试 API 调用，直接输出 blank_screenshot 响应。diagnosis 写明 `API returned input_sensitive`。

## Execution

### Static Mode

将参考图和截图水平并排拼接为单张，然后调用 mmx vision：

```bash
magick +append {reference.png} {screenshot.png} /tmp/qa_static.png
mmx vision describe --image /tmp/qa_static.png \
  --prompt "$(cat ${CLAUDE_PLUGIN_ROOT}/skills/visual-qa/prompts/static.md)

## Task Context

Goal: {goal}
Requirements: {requirements}
Verify: {verify}"
```

### Dynamic Mode

暂不可用。输出 capability 提示后退出。

### Question Mode

```bash
mmx vision describe --image {screenshot.png} \
  --prompt "$(cat ${CLAUDE_PLUGIN_ROOT}/skills/visual-qa/prompts/question.md)

## Question

{the question}"
```

多张截图时逐张调用，汇总结果。

## Analysis Criteria

### Implementation Quality (static)

Assets are usually fine — what breaks is how they're placed, scaled, composed:
- Grid/uniform placement when reference shows organic arrangement
- Uniform/default scale when reference shows varied, purposeful sizing
- Flat composition when reference has depth and layering
- Stretched, tiled, or carelessly applied materials
- Objects unrelated to environment (just placed on a flat plane)
- Camera framing doesn't match reference perspective

### Visual Bugs

- Z-fighting (flickering overlapping surfaces)
- Texture stretching, tiling seams, missing textures (magenta/checkerboard)
- Geometry clipping (objects visibly intersecting)
- Floating objects that should be grounded
- Shadow artifacts (detached, through walls, missing)
- Lighting leaks through opaque geometry
- Culling errors (missing faces, disappearing objects)
- UI overlap, truncated text, offscreen elements

### Logical Inconsistencies

- Impossible orientations (sideways, upside-down, embedded in terrain)
- Scale mismatches (tree smaller than character, door too small)
- Misplaced objects (furniture on ceiling, rocks in sky)
- Broken spatial relationships (bridge not connecting, stairs into wall)

### Placeholder Remnants

- Untextured primitives contrasting with surrounding detail
- Default Godot materials (grey StandardMaterial3D, magenta missing shader)
- Debug artifacts (collision shapes, nav mesh, axis gizmos)

### Motion & Animation (dynamic mode only — 暂不可用)

Compare consecutive frames (0.5s apart):
- Stuck entities (same position/pose across frames when movement expected)
- Jitter/teleportation (large position jumps between frames)
- Sliding (position changes but pose frozen — ice-skating)
- Physics breaks (objects through walls, endless bouncing, unnatural acceleration)
- Animation mismatches (walk anim at running speed, idle while moving)
- Camera issues (sudden jumps, clipping through geometry)
- Collision failures (overlapping objects that should collide)

## Output Format

### Static / Dynamic

```
### Verdict: {pass | fail | warning}

### Reference Match
{1-3 sentences: does the game capture the reference's *intent* — placement logic, scaling, composition, camera? Distinguish lazy implementation (fail) from asset/engine limitations (acceptable).}

### Goal Assessment
{1-3 sentences from Task Context. "No task context provided." if none.}

### Issues

{If none: "No issues detected." Otherwise:}

#### Issue {N}: {short title}
- **Type:** style mismatch | visual bug | logical inconsistency | motion anomaly | placeholder
- **Severity:** major | minor | note
- **Frames:** {dynamic only: which frames}
- **Location:** {where in frame}
- **Description:** {1-2 sentences}

### Summary
{One sentence.}
```

Severity: major/minor = must fix. note = cosmetic, can ship.

### Question Mode

```
### Answer
{Direct, specific, actionable answer. Reference locations, frames, colors, objects.}

### Visual Evidence
{What in the screenshots supports the answer. Reference specific frames and locations.}
```
