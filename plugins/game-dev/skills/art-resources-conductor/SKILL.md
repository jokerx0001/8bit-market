---
name: game-dev:art-resources-conductor
description: |
  美术资源生成 conductor。由 orchestrator 在 plan 之后调用。
  读 resources.md → 逐个资源 spawn art-resource-creator agent（隔离上下文）→ 检查质量 → 不满足则重试(最多3次) → 汇总报告追加到 resources.md。
---

# Art Resources Conductor

## 输入

`{task_dir}/.work/resources.md` — plan 阶段写入。

## 工作流

### 步骤 1：读取

解析 `--task-dir`、`--tech`。读 resources.md。

### 步骤 2：逐个资源处理

对每个资源，spawn art-resource-creator agent 完成 spec→prompt→生成全流程。**用 agent 而非 skill，因为 spec-builder + prompt-builder + mmx-cli 三步会产生大量中间输出，隔离在主会话之外。**

```
Agent({
  subagent_type: "game-dev:art-resource-creator",
  prompt: `
## 资源需求
{resources.md 中该资源的完整条目}

## 风格方向
{resources.md 中 ## 风格方向 的内容}

## 约束
- 自动生成，不询问用户确认
- 先判工具(Pillow/mmx-cli/直接写入/[HUMAN])
- mmx-cli 路径: 读 skills/art-spec-builder/SKILL.md → 补全 Visual Spec → 读 skills/art-prompt-builder/SKILL.md → 生成 prompt → 调 mmx-cli
- **技术约束: 读 `${CLAUDE_PLUGIN_ROOT}/references/godot/asset-gen.md` 的快捷参考表和视觉陷阱**
- **风格一致性: 同类型多个资源时，先生成锚点资源（第一个），后续角色资源用 `--subject-ref type=character,image=<锚点>` 保持一致性。非角色资源只能通过 prompt 文字保持一致（mmx 不支持通用图生图）**
  `
})
```

**质量检查（conductor 负责）：** agent 返回后，读生成的文件，对照 resources.md 中的要求和 `${CLAUDE_PLUGIN_ROOT}/references/godot/asset-gen.md` 的视觉陷阱检查——尺寸是否正确、风格是否匹配、朝向是否一致、精灵小尺寸退化是否存在。满足 → 标记 ✅，记录结果。不满足 → 分析原因，重新 spawn agent 重试。最多 3 次。3 次仍不满足 → 标记 [HUMAN]。

### 步骤 3：汇总

所有资源完成后，在 resources.md 末尾追加：

```markdown
## 生成结果汇总

| # | 资源名称 | 输出路径 | AI可生成 | 生成成功 | 效果评分 | 存在问题 |
|---|---------|---------|:---:|:---:|:---:|---------|
| 1 | ... | ... | ... | ... | ... | ... |

**AI 生成**: {N}/{total} 个
**成功**: {N} 个
**待人工**: {N} 个
```
