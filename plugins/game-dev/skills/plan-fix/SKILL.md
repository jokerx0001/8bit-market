---
name: game-dev:plan-fix
description: "Plan BUG fix development. trigger when fix-conductor calls plan phase. Reads debug-analysis.md (root cause + expected behaviors), produces plan.md with task list for TDD fix execution. Only writes design documents — NEVER writes implementation code."
---

# Game Dev Fix — 设计阶段

分析 BUG 根因和修复方向，生成 plan.md。**铁律：只做分析和规划并输出文档，不写实现代码。**

**文档查询：** 需要技术栈 API 语法、属性和最佳实践时，读 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/docs.md` 获取约定，用 `WebFetch` 查 config.md 中的 docs_url。

---

## 工作流

### 1. 确定任务目录

`task_dir` 由调用者（fix-conductor）传入。kind 固定为 `fix`。

确保 `.work/` 子目录存在：

```bash
mkdir -p {task_dir}/.work
```

### 2. 读取 debug-analysis.md

从 `{task_dir}/.work/debug-analysis.md` 提取：

- **根因** → plan.md 概述段必须包含（精确到代码位置 + 因果链）
- **预期行为列表** → plan.md 行为列表段逐条列出（用户已在 fix-conductor 阶段 2 确认，plan-fix 不再重复询问）
- **影响范围** → 约束 plan.md 的影响范围表
- **修复方向** → 概要方案（一两句话），plan-fix 负责展开为具体任务列表

**重要：** debug-analysis.md 只包含根因和预期行为，**不包含测试实现细节**。如果出现 testcase 名称或 assertion 策略，那是调试过程中误写入的——忽略，只提取根因和预期行为。

### 3. 加载格式契约 + 技术栈上下文

读取 `${CLAUDE_PLUGIN_ROOT}/references/plan-format.md`。所有输出必须遵守此格式规范，exec skill 依赖此格式解析。

**读取技术栈上下文：**

```
${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md
```

### 4. 任务拆分与排序

**拆分原则：按功能模块拆分，不按文件/阶段拆分。**

核心规则：**任务描述 = 可验证的功能行为，不含文件路径。**

**好/坏对照：**

```
❌ 坏: "修改脚本文件，修复 select_character 中 index 越界"
     → 问题：描述了文件操作，不是功能修复。不知道修复后行为是什么。

❌ 坏: "在界面文件中给角色选择添加边界检查"
     → 问题：文件路径+技术方案，不是功能行为。

❌ 坏: "修改 QteController.on_key 方法，修复按键不匹配时没有标记 fail 的问题"
     → 问题：描述的是代码符号（class 名 QteController、方法名 on_key），不是玩家可感知的行为。

❌ 坏: "在动画系统的 start() 中添加 keys 参数校验"
     → 问题：方法名+参数，不是行为。

✅ 好: "修复角色列表越界：选中最后一个角色后不再触发 IndexError，回退到第一个角色"
     → 可验证：选中最后一个角色→不会崩溃，回退到第一个角色

✅ 好: "修复空状态渲染：角色列表为空时显示 placeholder 文本而非空白界面"
     → 可验证：角色列表为空→看到 placeholder 提示文本

✅ 好: "修复按键不匹配时的失败反馈：按错键后显示 MISS 而非无响应"
     → 可验证：按错键→看到 MISS 文字和红色粒子
```

**描述写作规则：**

| 规则 | 说明 |
|------|------|
| 用行为语言 | 描述"用户做什么 → 看到什么/发生什么"，不以技术名词开头 |
| 可独立验证 | 读完描述能回答"怎么确认这个修复做完了？" |
| 不含文件路径 | 源码文件名不出现在描述中 |
| 不含代码符号 | class 名、方法名、函数名不出现在描述中——那些是实现方案，不是行为 |
| 不含"测试" | 没有"编写/更新测试"任务——测试在各模块的 TDD 循环中自然产出 |
| 回归优先 | 修复 BUG 的任务前，先有一个"锁定当前行为"的回归测试任务 |

**排序规则：**
- 回归测试任务（锁定现有行为）排在修复任务前面
- 修复任务按依赖排序（先修根因，再修连锁影响）

### 5. 编写 plan.md

**自己编写，不委托外部 skill。** 基于步骤 2 读取的 debug-analysis.md（根因 + 预期行为 + 修复方向）直接编写。fix 不需要 architecture.md / design.md 中间产物。

**模板和格式约束：** 以 `${CLAUDE_PLUGIN_ROOT}/references/plan-format.md` 为唯一权威来源。使用其中的 "plan.md 模板（fix 模式）"，遵守格式校验清单和禁止内容清单（跳过 "plan 专属" 段的 html: 标注检查）。

### 6. 格式自检

输出前对照 `plan-format.md` 的"格式校验清单"逐项确认，然后执行"禁止内容清单"中的所有 grep 命令（跳过 "plan 专属" 段）。全部零命中方可输出。

### 7. 输出摘要

```
## Plan: Fix {bug-summary}

**审查文件：** {task_dir}/plan.md
**根因：** {debug-analysis.md 中的根因摘要}
**AI 任务：** N 个
**人工任务：** N 个
**测试覆盖：** `{test_runner} project test`

---
人类审查 plan.md 通过后进入 exec --mode fix。
exec 只读 plan.md，不读 .work/。
```

---

## Completion Gate

永远不要声称任务完成，除非：

1. 执行了工作流的所有步骤
2. plan.md 已写入 `{task_dir}/`
3. plan.md 通过格式校验清单所有项目
4. 所有 grep 扫描零命中
5. 输出了所有文档路径供人类确认
