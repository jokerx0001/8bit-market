---
name: renpy-dev:review
description: "Review Ren'Py code for boundary violations. Use when asked to 'review code', 'check compliance', 'audit changes'. Checks hard boundaries: test file isolation, widget ids, jump/call targets. Does NOT review code quality — that's REFACTOR's job."
---

# Ren'Py AI 开发 — 边界审查

审查 coding-agent 是否违反了硬边界。不审查代码质量（REFACTOR 是 coding-agent 的职责）。

---

## 工作流

### 1. 确定审查范围

```bash
git diff --name-only HEAD
```

如果没有 git 变更，检查 `progress.json` 中最近完成的任务涉及的文件。

### 2. 审查

#### 审查 A：测试文件隔离（零容忍）

coding-agent 绝对不能修改测试文件。

```bash
git diff --name-only HEAD | grep "game/tests/" && echo "❌ VIOLATION: test files modified"
```

#### 审查 B：widget id 检查

新增 screen 中的交互 widget 必须有 `id` 属性。

```bash
# 找到新增/修改的 screen 定义
# 检查其中是否有关键交互 widget 缺少 id
```

#### 审查 C：jump/call 目标

所有 jump/call 的目标 label 必须存在。

```bash
# 提取 jump/call 目标
grep -roh "\(jump\|call\) [a-z_][a-z0-9_]*" game/ --include="*.rpy" | sort -u > /tmp/jump_targets.txt
# 提取已定义的 label
grep -roh "^label [a-z_][a-z0-9_]*" game/ --include="*.rpy" | sort -u > /tmp/defined_labels.txt
# 交叉验证
comm -23 /tmp/jump_targets.txt /tmp/defined_labels.txt
```

#### 审查 D：空代码/假代码

```bash
grep -rn "pass\|# TODO\|NotImplemented" game/ --include="*.rpy" | grep -v "game/tests/"
```

#### 审查 E：UI 原则合规（type: ui 任务必查）

当当前任务列表包含 `type: ui` 任务时，额外检查 UI 编码原则（参见 `plugins/renpy-dev/references/renpy-ui-principles.md`）：

**E1. 样式重复定义检查：**
```bash
# 同一 screen 文件中同一属性的多次出现
grep -n "background\|color\|size\|xalign\|yalign" {modified_screen_file} | sort -t: -k2
```

**E2. 互斥属性检查：**
```bash
# xalign 与 xpos 不能同时出现
grep -l "xalign" {modified_screen_file} | xargs grep -l "xpos" && echo "⚠️ 互斥属性: xalign + xpos"
# xsize 与 xfill 不能同时出现
grep -l "xsize" {modified_screen_file} | xargs grep -l "xfill" && echo "⚠️ 互斥属性: xsize + xfill"
```

**E3. textbutton 外嵌套 frame：**
```bash
# frame 内嵌 textbutton 是无意义冗余（textbutton 自带 window 属性）
grep -A2 "frame:" {modified_screen_file} | grep "textbutton" && echo "⚠️ 冗余嵌套: frame 包 textbutton"
```

**E4. 布局容器零样式：**
```bash
# vbox/hbox 不应有 background/xpadding 等视觉属性
grep -B1 -A5 "^[[:space:]]*vbox:" {modified_screen_file} | grep "background\|xpadding\|ypadding\|foreground" && echo "⚠️ 布局容器被视觉属性污染"
```

### 3. 输出

零违规：
```
## 边界审查：通过 ✅
所有硬边界检查通过。
```

有违规：
```
## 边界审查：❌ N 项违规

### ❌ {file}:{line} — {违规描述}
**修复：** {具体修复建议}
```

---

## 严重级别

- **🔴 严重**：修改了测试代码、超出 plan.md 范围修改无关文件
- **🟡 警告**：新增 screen 缺少 widget id、互斥属性同时出现、textbutton 外嵌 frame
- **🟢 建议**：样式重复定义、布局容器被视觉属性污染、命名改进（不阻塞）
