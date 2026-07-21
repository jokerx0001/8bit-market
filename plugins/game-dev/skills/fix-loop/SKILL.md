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

`{task_dir}/.work/generated-assets.md` — 跨轮累积的资产生成记录。每轮 Step 3c 读取此文件做去重，Step 3g 追加本轮结果。文件不存在表示第一轮，无需额外初始化。

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

#### Step 3b: 检测缺失资产

检查 `debug-analysis.md` 是否存在 `## 缺失资产` 章节且有实质条目。

无此章节或条目为空 → 跳过 Step 3c-3g，直接进入 Step 4。根因不涉及资产缺失。

#### Step 3c: 去重 + 写 resources.md

**读取已生成记录：**

```bash
cat {task_dir}/.work/generated-assets.md 2>/dev/null || echo "EMPTY"
```

`EMPTY` 表示第一轮。否则从文件中提取所有已标记 `✅` 或 `[PLACEHOLDER]` 的资产名称。

**排除已完成的资产：** 将 `debug-analysis.md` 中 `## 缺失资产` 的每条与 `generated-assets.md` 中的已完成条目对比（按资产名称匹配）。排除已完成的条目。

**如果本轮无待生成资产（全部已生成过）→ 跳过 Step 3d-3g，直接进入 Step 4。**

**写入 resources.md（清空重写，非追加）：**

按 `asset-extract-doc` 的格式，只写入本轮需要生成的新资产：

```bash
cat > {task_dir}/.work/resources.md << 'EOF'
# 资源需求清单（BUG 修复 — 缺失资产补充）

## 风格方向
{从 debug-analysis.md 缺失资产条目的视觉要求 + 项目现有资产推断}

## 资源列表

### {模块名}

#### {资产名称}
- **用途**: {从 debug-analysis.md 提取}
- **类型**: {精灵/纹理/背景/模型/UI素材/材质}
- **尺寸**: {从 debug-analysis.md 提取}
- **策略**: {按 asset-extract-doc 判定规则: code-only / pillow / mmx / CSG构造 / [HUMAN]}
- **视觉要求**: {从 debug-analysis.md 提取}

{下一条资产...}
EOF
```

#### Step 3d: 调用 art-resources-conductor

```
Skill({skill: "game-dev:art-resources-conductor", args: "--task-dir {task_dir} --tech {tech}"})
```

#### Step 3e: CSG 构造

读取 resources.md 的 `## 生成结果汇总` 表格。对每条标记为 `策略: CSG构造` 的资产：

1. 读 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/3d-construction.md`
2. 根据资产描述构造几何体（Box/Sphere/Cylinder/CSG 组合），写出 `.tscn` 或代码
3. 构造成功 → 标记 `✅`
4. 复杂到无法用 CSG 组合完成 → 标记 `[HUMAN]`，进入 Step 3f

#### Step 3f: 占位体

对 Step 3d 和 3e 之后仍标记为 `[HUMAN]` 的资产，创建最低限度占位体：

- **3D 模型占位体**: 单一颜色的 BoxMesh/SphereMesh，尺寸匹配目标尺寸

占位体命名约定：`{资产名称}_placeholder.{ext}`。在 `generated-assets.md` 中标注 `[PLACEHOLDER]`。

#### Step 3g: 记录生成结果

将 resources.md 的 `## 生成结果汇总` 表格内容追加到 `generated-assets.md`：

```bash
{提取 resources.md 中 ## 生成结果汇总 的表格行}
cat >> {task_dir}/.work/generated-assets.md << 'EOF'

## 第 {N} 轮生成 — {timestamp}

| 资产名称 | 策略 | 结果 | 输出路径 |
|----------|------|------|----------|
{逐条结果}
EOF
```

#### Step 4: 记录本轮诊断

追加到 `{task_dir}/.work/fix-attempts.md`：

```markdown
## 第 {N} 轮 — {timestamp}

### 根因
{从 debug-analysis.md 提取的根因}

### 资产生成
{如经历了 Step 3b-3g: 生成了哪些资产、策略、结果。如无资产缺失: 标注"本轮流无资产缺失"}
- {资产1}: {mmx / pillow / CSG构造 / 占位体} → {✅ / ❌ / [PLACEHOLDER]}

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
- **资产缺失的修复已在 Step 3b-3g 完成（调 art-resources-conductor + CSG构造 + 占位体）。** 本轮修复只负责：引用新生成的资产路径、或移除对已删除资源的无效引用。如果当前轮未走 Step 3b-3g（根因不是缺失资产），则此条不适用。

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

**Screenshot 验证硬门（强制执行）：** 每次截图验证后检查以下项目。任何 ❌ → 截图验证标记为 INCOMPLETE（不得标记为 PASS，不得退出循环）。

| # | 检查项 | 状态 |
|---|--------|------|
| 1 | `{testcase_name}_qa.log` 已写入 .work/logs/（文件存在且非空） | ✅ / ❌ |
| 2 | qa 日志中包含 `### Answer` 节（visual-qa 返回了有效结果，非 API error） | ✅ / ❌ |
| 3 | Answer 内容判断通过（PASS）或失败原因已记录 | ✅ / ❌ |

**截图失败必做行为（硬门——任一步骤失败必须全部执行）：**

| # | 检查项 | 状态 |
|---|--------|------|
| 1 | 已重新 `Read ${CLAUDE_PLUGIN_ROOT}/references/{tech}/screenshot.md` | ✅ / ❌ |
| 2 | 已逐条对照 screenshot.md 确认截图命令合规 | ✅ / ❌ |
| 3 | 已检查环境 | ✅ / ❌ |
| 4 | 如环境不支持 → 已找到不支持的原因 并更新 fix-attempts.md | ✅ / ❌ |

**此硬门不可跳过。截图失败不做此检查 = 本轮验证无效。**

#### Step 7: 判定

**判定前置条件（先检查，再判定）：**

| # | 条件 | 状态 |
|---|------|------|
| 1 | GUT 测试已执行且输出已保存到 .work/logs/ | ✅ / ❌ |
| 2 | 如有 screenshot testcase：每条有对应的 qa.log（文件存在且含 `### Answer`），或已标注 `环境不支持` | ✅ / ❌ |

**任何 ❌ → 本轮验证无效。** 返回 Step 6 补全缺失的日志/验证，或标注 BLOCKED。

- **全部 PASS（含 Screenshot visual-qa 全部 PASS 或已标注环境不支持）→ 退出循环。** 跳转到"完成"。
- **任一 FAIL 或 INCOMPLETE → 继续下一轮。** 追加失败详情到 fix-attempts.md：

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

**完成硬门（以下步骤不可跳过。未完成前不得返回 fix-conductor）：**

| # | 产出 | 状态 |
|---|------|------|
| 1 | `fix-summary.md` 已写入 `{task_dir}/.work/` | ✅ / ❌ |
| 2 | `## Fix Complete` 报告已输出（含 BUG/根因/修复/轮次/验证） | ✅ / ❌ |
| 3 | `fix-attempts.md` 最后一轮验证结果为 PASS（含 Screenshot 结果） | ✅ / ❌ |

**任何 ❌ → 返回补全对应产出。不完成硬门 = 本轮 fix-loop 未完成。**

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

## 资产生成（如有）
{从 generated-assets.md 汇总：生成了哪些资产、通过什么策略、占位体列表}

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
- "resources.md 不用清空重写，追加就行" → STOP。resources.md 必须清空重写，每轮只含待生成资产。conductor 读全量 resources.md，不清空会导致重复生成。
- "generated-assets.md 里有些资产这次没生成成功，resources.md 里不用再写了，反正 conductor 也生不出来" → STOP。每次都重新写入 resources.md 让 conductor 重试。generated-assets.md 是记录，不是阻塞原因。
- "CSG构造 的资产可以直接跳过，反正就是个几何体" → STOP。CSG构造 是硬步骤——必须按 3d-construction.md 实际构造并写出文件，不能跳过。
- "占位体随便写个空文件就行" → STOP。占位体必须遵守 3f 规则：3D = 纯色 BoxMesh/SphereMesh + 目标尺寸，2D = 纯色 PNG（主色或品红 `#FF00FF`）。
