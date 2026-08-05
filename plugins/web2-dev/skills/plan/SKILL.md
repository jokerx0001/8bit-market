---
name: web2-dev:plan
description: |
  任务分解 skill。读取 design.md（按模块组织的详细设计），
  将模块分解为粗粒度任务清单写入 plan.md。
  plan.md 不包含设计内容——只列出任务，exec 去 design.md 中按模块名查找详细设计。
  Iron Law: 只做分析和规划并输出文档，不写实现代码。

  <example>
  Context: orchestrator 在设计完成后调用 plan 做任务分解
  assistant: "读取 design.md 中的模块列表，生成 plan.md 任务清单。"
  </example>
---

# Plan — 任务分解

## Iron Law

```
PLAN WRITES ZERO CODE. PLAN ONLY WRITES PLAN.MD.

Plan reads: design.md, architecture.md, requirements.md.
Plan produces: plan.md (task list ONLY — no design content).
Plan NEVER: writes implementation code, writes design content into plan.md.
```

## 数据来源

**必须读取：**
- `{task_dir}/.work/design.md` — 按模块的详细设计
- `{task_dir}/.work/architecture.md` — 架构设计
- `{task_dir}/.work/requirements.md` — 行为清单
- `{task_dir}/.work/user-prompt.md` — 用户原始输入

## 产出

`{task_dir}/plan.md` — 简洁任务清单。

### 格式

```markdown
# Plan — 任务清单

## 元信息
- 模式: {new|feat|refactor}
- 技术栈: {语言/框架}
- 模块数: {N}

## 任务列表

| # | 模块 | 简要说明 | 涉及路径 |
|---|------|---------|---------|
| 1 | {模块名} | {一句话描述} | {源码路径}, {测试路径} |

## 前端

开发方式: {从 layouts/ 设计稿编码 | 无前端}
前端入口: {路径}
```

## 硬约束

- **粒度 = 模块（微服务级别）。** 一个模块一个任务。
- **全部项目只有 1 个微服务 → plan.md 中只有 1 个任务。**
- **前端不拆分**——始终作为一个整体。
- **排序：** 被依赖的模块排在前面。
- **不包含设计内容**——exec 去 design.md 中按模块名查找。
- **任务数量 = design.md 中的模块数。**

## 格式自检

产出 plan.md 后执行：

```bash
# 确认任务列表非空
grep -c '^|' {task_dir}/plan.md | xargs -I{} test {} -gt 1 && echo "TASK_OK" || echo "TASK_MISSING"

# 确认前端章节存在
grep -c '## 前端' {task_dir}/plan.md | xargs -I{} test {} -eq 1 && echo "FRONTEND_OK" || echo "FRONTEND_MISSING"
```

任何检查失败 → 补全后重新自检。
