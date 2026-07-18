---
name: game-dev:fix-loop
description: "BUG 修复循环。诊断→修复→验证循环，直到 BUG 复现测试通过。每次迭代记录到 fix-attempts.md"
---

# Fix Loop — BUG 修复循环

执行修复循环直到 BUG 修复或超过重试上限。

## 输入

| 输入 | 说明 |
|------|------|
| task_dir | 任务目录路径 |
| bug_description | 用户报告的 BUG，原样引用 |
| expected_behaviors | 用户确认的预期行为，逐条列出，每条标注验证方式（`behavior` 或 `screenshot: 问题描述`） |
| testsuite | test-agent 创建的 testsuite 名称 |
| testcases | testcase 名列表（含 GUT 和 screenshot 两类——screenshot testcase 通过命名约定区分：`test_{描述}_screenshot`） |

### 准备

确保 `.work/` 下存在必要的目录：

```bash
mkdir -p {task_dir}/.work/screenshots
```

### 每轮迭代

#### Step 1: 读取失败经验

检查 `{task_dir}/.work/fix-attempts.md` 是否存在。存在则读取。

**告诉自己：读取的是前面尝试但未成功的分析，不要反复做同样的错误尝试。必须换思路。**

#### Step 2: 根因分析

调用 `Skill("game-dev:debug-root-cause")` 进行根因分析。

传入 `before_attempts={task_dir}/.work/fix-attempts.md`——debug-root-cause 自行读取，在逆向追踪时避开已验证为错误的路径。

#### Step 3: 获取根因

debug-root-cause 产出 `{task_dir}/.work/debug-analysis.md`。读取分析结果

#### Step 4: 记录本轮诊断

追加到 `{task_dir}/.work/fix-attempts.md`：

```markdown
## 第 {N} 轮 — {timestamp}

### 根因
{从 debug-analysis.md 提取的根因}

### 修复思路
{本轮打算怎么修}
```

#### Step 5: 实施修复

基于根因，实施正式修复。与 debug-root-cause 的临时修改不同：

- **考虑项目上下文：** 修复要符合现有代码模式、命名惯例、架构约定
- **考虑最佳实践：** 不是最小 hack，是正确、可维护的修复
- **考虑连锁影响：** 修复是否影响其他功能？是否需要同步修改关联代码？
- **考虑边界情况：** 修复是否覆盖了所有边界？

**代码修改规则：**
- 遵循已读取的规范文件（coding.md、style-guide.md 等）
- 不修改测试文件
- 不写空壳/假代码
- API 不确定时查官方文档
- 3D 资源缺失时按 3d-construction.md 构造。是在无法构造则必须说明原因然后才能用占位体

#### Step 6: 验证

跑 BUG 复现测试：

**GUT 测试：** 使用 fix-agent 启动初始化中解析的测试执行方法，跑目标 testsuite。

**Screenshot 测试（如有）：** 执行截图脚本 → base64 解码保存 → 读 .question → 调用 `Skill("game-dev:visual-qa")` → 判断 Answer。

#### Step 7: 判定

- **全部 PASS → 退出循环。** 跳转到"完成"。
- **任一 FAIL → 继续下一轮。** 追加失败详情到 fix-attempts.md：

```markdown
### 验证结果
❌ 失败

#### 失败详情
{具体 testcase 失败信息 + screenshot visual-qa 结论}

#### 失败原因分析
{为什么没修好——根因判断错误？修复不完整？引入了新问题？}
```

回到 Step 1。

---

## 完成

所有测试通过后：

### 1. 写修复总结

写入 `{task_dir}/.work/fix-summary.md`：

```markdown
# 修复总结

## BUG
{用户报告的 BUG}

## 根因
{debug-analysis.md 的根因}

## 修复
{实际做了什么修改——文件、变更、为什么这样修}

## 验证
- GUT: {N}/{N} 通过
- Screenshot: {如有} PASS

## 尝试轮次
{共 N 轮，每轮简述尝试了什么、为什么失败}
```

### 2. 报告

```
## Fix Complete

**BUG:** {简述}
**根因:** {简述}
**修复:** {修改了哪些文件，做了什么}
**轮次:** {N} 轮
**验证:** 全部通过 ✅
```

---

## 重试上限

**最多 5 轮。** 第 5 轮仍失败 → 输出以下内容并停止：

```
## Fix Blocked

**BUG:** {简述}
**已尝试:** {轮次}
**最后一轮失败原因:** {简述}
**建议:** {需要人工介入的原因和建议}
```

记录到 fix-attempts.md 并标记为 🚫 BLOCKED。

---

## Red Flags

- "上一轮差不多对了，微调一下就行" → STOP。如果根因相同但修复不完整，说明根因分析不够精确。重新诊断。
- "debug-root-cause 的临时修改直接拿来用就行" → STOP。临时修改是最小 hack——正式修复要考虑完整性和可维护性。
- "跳过诊断直接改代码试试" → STOP。必须走 Step 2 根因分析。
- "这轮和上轮诊断结论一样" → STOP。如果诊断结论没变但修复没通过，诊断有遗漏——深入一层。
