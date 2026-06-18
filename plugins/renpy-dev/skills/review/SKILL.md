---
name: renpy-dev:review
description: "Review Ren'Py code against plan documents and boundary rules. Use when asked to 'review code', 'check compliance', 'audit changes'. Checks that implementation follows the plan, not a safety audit."
---

# Ren'Py AI 开发 — 合规审查

审查 agent 产出是否遵守 plan 文档约定和边界规则。只读审计，不修改代码。

---

## 工作流

### 1. 加载上下文

读取相关设计文档：
- `{task_dir}/plan.md` — 任务定义和约束
- `{task_dir}/design.md` — 详细设计
- `{task_dir}/architecture.md` — 架构约定

### 2. 确定审查范围

获取最近变更的文件列表：
```bash
git diff --name-only HEAD
```

如果没有 git 变更，检查 `progress.json` 中最近完成的任务涉及的文件。

### 3. 审查维度

#### 审查 A：test agent 合规性

对每个新增/修改的测试文件（`game/tests/` 下）：

| 检查项 | 方法 |
|--------|------|
| 测试是否覆盖了 plan.md 中的测试策略？ | 对比 plan.md 测试策略段与实际测试 label |
| 测试是否断言目标行为？ | 检查 `assert_*` 调用的 expected 值是否匹配设计文档 |
| 测试命名和结构是否遵循 test skill 方法论？ | `test_b_*` / `test_v_*` 前缀，label 结构 |

```bash
# 提取测试 label 名称
grep "^label test_[bv]_" game/tests/test_*.rpy
```

#### 审查 B：coding agent 合规性

对每个新增/修改的源码文件（`game/` 下，排除 `game/tests/`）：

| 检查项 | 方法 |
|--------|------|
| 实现范围是否在 plan.md 的任务列表中？ | 对比变更文件与 plan.md `[AI-N]` 输出路径 |
| 是否修改了测试代码？ | 检查 game/tests/ 下的变更 — 零容忍 |
| 是否写了空代码/假代码？ | grep `pass`、`TODO`、`NotImplementedError` |
| 实现是否遵循设计文档？ | 对比 screen 结构、widget tree、数据流是否匹配 design.md |

```bash
# 检查空代码
grep -rn "pass\|# TODO\|NotImplemented" game/ --include="*.rpy" | grep -v "game/tests/"
# 检查是否修改了测试文件（零容忍）
git diff --name-only HEAD | grep "game/tests/" && echo "❌ 测试文件被修改"
```

#### 审查 C：边界检查

| 检查项 | 方法 |
|--------|------|
| 新增 screen 的关键交互 widget 是否有 `id`？ | 检查 screens.rpy 中新增 screen 的 widget |
| 跨文件 `jump/call` 目标是否存在？ | 提取所有 jump/call，验证目标 label 存在 |
| `OWN_MANIFEST.json` 是否更新？ | 新增 screen/script 未在 manifest 中则违规 |

```bash
# 提取 jump/call 目标
grep -roh "\(jump\|call\) [a-z_][a-z0-9_]*" game/ --include="*.rpy" | sort -u
# 提取已定义的 label
grep -roh "^label [a-z_][a-z0-9_]*" game/ --include="*.rpy" | sort -u
# 交叉验证
```

### 4. 输出审查报告

```markdown
## 合规审查

### test agent 审查
- ✅ / ❌ {具体检查项}

### coding agent 审查
- ✅ / ❌ {具体检查项}

### 边界检查
- ✅ / ❌ 新增 screen widget id
- ✅ / ❌ jump/call 目标
- ✅ / ❌ OWN_MANIFEST.json

### 违规详情

#### ❌ {file}:{line} — {违规描述}
**预期：** {plan 文档中的约定}
**实际：** {代码中的实际情况}
**修复：** {具体修复建议}

### 汇总
- test agent 违规: N
- coding agent 违规: N
- 边界违规: N
```

零违规时输出：
```
## 合规审查：通过 ✅

所有 agent 产出符合 plan 文档约定和边界规则。
```

---

## 严重级别

- **🔴 严重**：修改了测试代码、超出 plan.md 范围修改无关文件
- **🟡 警告**：新增 screen 缺少 widget id、OWN_MANIFEST 未更新
- **🟢 建议**：命名改进、代码风格
