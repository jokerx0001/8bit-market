# Plan 文件格式规范

此文件定义 plan skill 输出和 exec skill 解析的共享契约。

---

## 文件路径

```
.renpy-dev/feat-{N}/plan.md
```

---

## 完整结构

```markdown
# Plan: {feature-name}

## 概述

{一段话描述要构建什么功能}

## 项目环境

- **Ren'Py 版本：** {检测到的版本}
- **项目根：** {game/ 目录路径}
- **OWN_MANIFEST.json：** {路径}

## 影响范围

| 类型 | 文件 | 操作 |
|------|------|------|
| script | game/script.rpy | 修改 — 新增 label |
| screen | game/screens.rpy | 新增 screen |
| 新建 | game/{feature}.rpy | 创建 |

## 设计摘要

{引用 architecture.md 和 design.md 的关键设计决策}

## 任务列表

### [AI] 任务

格式：
- `[AI-N]` {描述} → `{输出文件路径}` (依赖: AI-X, AI-Y)

示例：
- `[AI-1]` 创建 CharacterSelectScreen → `game/character_select.rpy` (依赖: AI-3)
- `[AI-2]` 创建 CharacterSelect 测试 → `game/tests/test_character_select.rpy` (依赖: AI-1)

### [HUMAN] 任务

- `[HUMAN]` {具体操作步骤}
- `[HUMAN]` 在 OWN_MANIFEST.json 中注册新增的 screen

## 测试策略

| 层级 | 覆盖内容 | 测试文件 |
|------|---------|---------|
| structure | lint + AST 检查 | — |
| behavior | {行为描述} | game/tests/test_{name}.rpy |
| visual | {视觉描述} | game/tests/test_{name}.rpy |
```

---

## exec 解析规则

1. **提取 AI 任务**：匹配 `- \[AI-(\d+)\]` 提取序号和描述
2. **提取输出路径**：匹配 `→ \`(.+)\`` 提取目标文件
3. **提取依赖**：匹配 `(依赖: (.+))` 确定执行顺序
4. **按依赖拓扑排序**：无依赖优先，有依赖等前置完成
5. **[HUMAN] 任务不执行**：最终汇总提醒用户
6. **测试策略段**：用于确定每个任务该跑什么测试层

## 格式校验清单

plan 输出前自检：
- [ ] 每个 AI 任务有唯一编号 `[AI-N]`
- [ ] 每个 AI 任务有明确输出文件路径（`→` 后面）
- [ ] 依赖关系引用的编号存在
- [ ] 无循环依赖
- [ ] HUMAN 任务标注了具体操作步骤
- [ ] 影响范围表列出了所有涉及的文件
