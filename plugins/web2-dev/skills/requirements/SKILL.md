---
name: web2-dev:requirements
description: |
  需求管理 skill。被 orchestrator 在 plan 阶段调用。
  三种模式：--init(新项目) / --update(追加需求) / --reverse(从代码反推)。
  产出项目级 requirements.md + per-task 行为确认清单。

  <example>
  Context: new-orchestrator 阶段 3
  assistant: "使用 requirements skill 初始化项目需求文档，生成行为确认清单。"
  </example>
---

# Requirements Management

管理项目需求和 per-task 需求文档。

## 调用格式

```
Skill({skill: "web2-dev:requirements", args: "--task-dir {task_dir} --tech {tech} --mode {init|update|reverse}"})
```

## 模式判定

| 条件 | mode |
|------|------|
| `{dev_dir}/requirements.md` 不存在且为新项目 | `init` |
| `{dev_dir}/requirements.md` 存在 | `update` |
| `{dev_dir}/requirements.md` 不存在但有源码 | `reverse` |

## 前置读取（不可跳过）

**必须读取以下文件，综合理解用户意图：**
- `{task_dir}/.work/user-prompt.md` — 用户原始输入
- `{task_dir}/.work/grill-interview.md` — grilling 采访记录
- 若 mode 为 update，同时读取已有的 `{dev_dir}/requirements.md`

grill-interview.md 必须按原样读取——"不假设它有固定结构，它是什么格式就是什么格式，自己去读。"

## 产出

### 项目级（跨任务持久）
`{dev_dir}/requirements.md` — 全量功能需求清单。每条需求包含：
- 功能描述（用户视角）
- 验证方式（可被测试断言的事实）
- 优先级（P0/P1/P2）

### Per-task
`{task_dir}/.work/requirements.md` — 本次需求，包含行为确认清单。

## 行为确认清单（强制门）

**在所有模式下，写入前必须提取行为清单并与用户确认：**

```
## 确认以下行为是否准确

这些是可被测试验证的行为，每条对应一个 testcase：

1. 用户注册成功 → API 返回 201 + 数据库中新增用户记录
2. 重复邮箱注册被拒绝 → API 返回 409 + "Email already exists"
3. 密码少于8位被拒绝 → API 返回 422 + 验证错误详情

是否有遗漏或不需要的行为？
```

**理由：** 行为描述的是需求（一条行为 = 一个真相来源），设计文档描述的是方案。code-review 依据此清单检查测试覆盖。

用户确认后写入 `{task_dir}/.work/requirements.md` 的"行为清单"节。

**hard gate（所有模式）：** 行为清单非空且每行有对应的验证描述。

## 行为清单格式

```markdown
## 行为清单

| # | 行为 | 验证描述 | 优先级 |
|---|------|---------|--------|
| 1 | {行为描述} | {可被测试断言的具体事实} | P0 |
```

验证描述必须是可被测试框架断言的具体事实，不是模糊的"功能正常"。

## update 模式额外约束

**严禁末尾盲追加。** 追加的行为清单必须合并到已有 `{dev_dir}/requirements.md` 的正确章节中。

## 约束

- 行为清单是 testcase 的唯一来源——不包含实现细节
- 验证描述 ≠ 实现方式——"API 返回 201"不是"调用 createUser() 方法"
- 每条行为必须有明确的验证方式
