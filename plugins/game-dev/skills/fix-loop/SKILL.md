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
| test_cmd_full | 全量测试命令（fix-agent 从 config.md 解析传入） |
| test_cmd_suite | 指定 testsuite 的命令模板（`{suite}` 占位符由 fix-loop 替换） |
| test_cmd_single | 单个 testcase 的命令模板（`{suite}`、`{case}` 占位符由 fix-loop 替换） |
| test_failure_grep | 从日志提取失败详情的 grep 命令（`{log_path}` 占位符由 fix-loop 替换） |

### 准备

确保 `.work/` 下存在必要的目录：

```bash
mkdir -p {task_dir}/.work/logs/screenshots
```

**解析测试执行方法（以下方法在每轮验证步骤中只按名称引用）：**

- 全量执行：`{test_cmd_suite} > {task_dir}/.work/logs/{suite}_run{N}.log 2>&1`（`{suite}` 替换为实际 testsuite 名，`{N}` 为当轮修复尝试编号）
- 单case执行：`{test_cmd_single} > {task_dir}/.work/logs/{case}_run{N}.log 2>&1`（`{case}` 替换为实际 testcase 名）
- 结果提取：`{test_failure_grep}`，`{log_path}` 替换为对应的日志文件路径

**Hard Gate：每次测试运行必须保存原始输出到 `.work/logs/`。** 不保存日志 = 本轮验证无效。管道可用于二次提取，但原始输出必须先完整保存到对应日志文件。

**解析Screenshot 测试方法（以下方法在每轮验证步骤中只按名称引用）：**

`Read ${CLAUDE_PLUGIN_ROOT}/references/{tech}/screenshot.md`
- 截图命令: {从screenshot.md中提取}
- 截图约束: {从screenshot.md中提取}
 
**Hard Gate
- 每次运行截图命令,并且调取visual-qa skill获取结果后，必须保存visual-qa原始输出到 `.work/logs/`。** 不保存日志 = 本轮验证无效。
- screenshot.md中的约束必须遵守。

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

**GUT 测试：** 使用[准备]中解析的**全量执行**方法跑目标 testsuite。使用[准备]中解析的**结果提取**方法获取失败详情。

**Screenshot 测试：**
步骤如下:
1. 使用[准备]中解析的**截图命令**逐个 testcase 执行截图脚本
参数: {output_path}: | {task_dir}/.work/logs/screenshots/{testcase_name}.png
2. 读对应的 `.question` 文件，调用visual-qa skill 
```
Skill({skill: "game-dev:visual-qa", args: "--reference_image_path {截图路径} --question {.quistion文件内容}"})
```
3. 将 skill 输出写入 `{task_dir}/.work/logs/{testcase_name}_qa.log`
- 结果提取：从 qa 日志文件中 visual-qa 的 `### Answer` 内容判断是否通过
- 截图失败必做行为: `Read ${CLAUDE_PLUGIN_ROOT}/references/{tech}/screenshot.md`, 输出内容, 逐条确认失败时候执行的命令是否符合文件内容指引，不符合则必须按照文件内容执行。如果已经遵守文件内容,则要检查环境问题。

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
