---
name: web2-dev:code-review
description: |
  代码合规检查 skill。被 exec 在每次 coding agent 完成后调用。
  主 agent 读取 design.md 对比实际代码，列出所有不合格项 + 原因。
  全部问题必须一起修复，不区分严重程度。

  <example>
  Context: coding agent 完成模块 TDD，exec 调用 code-review
  assistant: "读取 design.md → 对比代码实现 → 列出所有不合格项 → spawn coding agent 全部修复。"
  </example>
---

# Code Review — 合规检查

检查代码是否与设计文档一致，testcase 是否覆盖了设计中描述的行为。

## Iron Law

```
CODE REVIEW LISTS EVERYTHING. EVERYTHING MUST BE FIXED.

No severity levels. No "minor issues can be skipped". No "this one is debatable".
If it deviates from the design, it goes on the list. Everything on the list gets fixed.
```

## 调用格式

```
Skill({skill: "web2-dev:code-review", args: "--task-dir {task_dir} --module {模块名}"})
```

## 执行者

**主 agent 执行。** 主 agent 自己读设计文档、读代码、做比对。不 spawn agent。

## 检查清单

### 1. 设计一致性

逐项比对 `{task_dir}/.work/design.md` 中当前模块的设计 vs 实际代码：

| 检查项 | 来源 |
|--------|------|
| API 路由和方法是否与 API 设计一致 | design.md → API 设计节 |
| 请求/响应格式是否与 API 设计一致 | design.md → API 设计节 |
| 状态码是否与 API 设计一致 | design.md → API 设计节 |
| 数据库表结构是否与 DB 设计一致 | design.md → 数据库设计节 |
| 模块间调用方向是否与交互设计一致 | design.md → 模块交互节 |
| 实体/模型定义是否与架构中的领域模型一致 | architecture.md → 领域模型节 |

### 2. 测试覆盖

逐条检查 `{task_dir}/.work/requirements.md` 中当前模块的行为清单：

| 检查项 | 判断标准 |
|--------|---------|
| 每条行为是否有对应 testcase | 在测试文件中找到对应测试 |
| testcase 是否验证了正确的行为 | 断言匹配 requirements.md 中的验证描述 |
| 是否有无效/无意义测试 | 纯 CRUD/透传/配置方法的独立测试不在 seam 上 |

### 3. 代码质量

| 检查项 |
|--------|
| 无空壳/假代码（pass、TODO、throw NotImplemented） |
| 无硬编码凭据/密钥 |
| 错误处理完整 |
| 命名符合语言惯例 |

## 输出格式

```markdown
# Code Review — {模块名}

## 不合格项

| # | 类型 | 位置 | 问题 | 原因 |
|---|------|------|------|------|
| 1 | 设计不一致 | user_service.py:42 | POST /register 返回 200 | design.md 要求返回 201 |
| 2 | 设计不一致 | user_service.py:89 | 缺少 email 格式验证 | design.md API 设计要求 422 响应 |
| 3 | 测试覆盖 | test_user.py | 缺少重复邮箱注册的 testcase | requirements.md 行为 #2 未覆盖 |
| 4 | 代码质量 | user_service.py:15 | 硬编码数据库密码 | 安全违规 |

## 结论

共 {N} 项不合格，必须全部修复。
```

**不合格项的"原因"必须具体——不是"不符合设计"这种废话，而是"design.md 第 X 节写明 Y，但代码实际做了 Z"。**

## 修复流程

产出不合格项列表后，exec spawn coding agent 一次性修复全部：

```
Agent({
  subagent_type: "coding",
  description: "Fix code review findings for {模块名}",
  prompt: "
## 模式
code-review-fix

## task_dir
{task_dir}

## 模块
{模块名}

## 不合格项（必须全部修复）
{逐条列出 code-review 报告中的每一项，含位置+问题+原因}

## 要求
逐条修复，修复后跑测试验证。全部通过后返回。
  "
})
```

修复后主 agent 再次 code-review。最多 3 轮——3 轮后仍有不合格项 → 报告阻塞。

## Red Flags — STOP

- "这个不合格项很小，我自己修一下就行" → STOP。spawn coding agent——exec 不写代码
- "有几项看起来不是问题，跳过吧" → STOP。没有分级，每一项都必须修复
- "设计文档可能写错了，我按代码是对的" → STOP。设计文档是真相来源——代码必须匹配设计
- "testcase 覆盖差但功能正常，先放行" → STOP。测试覆盖是硬要求
- "review 报告太长但实际没大问题" → STOP。列表每一项都有具体原因——逐项修复
