# Exec Spawn Prompt Templates

exec 在 TDD 循环每个 phase 使用以下模板组装 agent spawn prompt。`{...}` 为 exec 必须填充的变量。

---

## RED — test-agent

```
Agent({
  subagent_type: "renpy-dev:test-agent",
  prompt: `
## 模式
RED

## 任务
为 [AI-N] {任务描述} 编写测试。

## 要验证的行为
{从 plan.md 测试策略表提取的覆盖内容}

## 测试文件
{从 plan.md 测试策略表提取的测试文件路径}

## 需要读取的文件
- {task_dir}/plan.md  — 设计摘要、影响范围
- {task_dir}/.work/design.md  — widget 树、变量定义、交互流程（仅 feat/refactor 模式）
- {task_dir}/impact.md  — 修改范围约束（仅 refactor 模式）
- {task_dir}/.work/debug-analysis.md  — 根因分析（仅 fix 模式）
- plugins/renpy-dev/references/renpy-testing.md  — Ren'Py testcase/testsuite 完整 API
- https://www.renpy.org/doc/html/testcases.html  — 官方测试文档（WebFetch 查询）
- game/ 下相关的 .rpy 源文件 — 了解已有 screen 名、widget id、变量名

## 约束
- 写完测试后必须自己跑测试确认失败原因正确
- 语法错误/标识符错误必须自己修复后重跑（最多 3 轮）
- 只写 game/tests/，不写 game/ 业务代码
  `
})
```

**exec 检查 RED 结果：**
- 测试文件已创建？
- RED report 中所有 testcase 都失败了且原因正确？
- 没有 mock、假代码？

不合格 → 指出具体问题，重新 spawn test-agent。合格 → 进入 GREEN。

---

## GREEN — coding-agent

```
Agent({
  subagent_type: "renpy-dev:coding",
  prompt: `
## 模式
GREEN

## 任务
[AI-N] {任务描述}

## 当前状态 — 以下行为尚未实现
{从 test-agent RED report 中提取的失败描述，用行为语言}

示例格式:
- Screen "character_select" 不存在 — 需要创建
- 点击角色卡片后 selected_index 变量没有更新 — 需要实现选中逻辑
- 点击"确认"按钮后没有跳转到 start_game — 需要实现确认跳转

## 项目
{project 名称，用于运行 renpy.sh <project> test}

## 实现文件
根据任务描述和设计文档自行确定需要修改的文件。
{若 plan.md 中任务标记为 type: ui，在此插入 UI 任务标记块}

## 需要读取的文件
- {task_dir}/plan.md  — 设计摘要、影响范围
- {task_dir}/.work/design.md  — widget 树、变量定义、交互流程（仅 feat/refactor 模式）
- {task_dir}/impact.md  — 修改范围约束（仅 refactor 模式）
- game/ 下相关的 .rpy 源文件 — 了解已有代码模式
- references/exec-logging.md  — AGENT PROGRESS 节（自验证日志格式）

## 约束
- 按设计文档实现行为，不是按测试要求实现
- 新增 screen 时必须给关键交互 widget 添加 id 属性
- 不修改 game/tests/、game/libs/、game/tl/
- 不写空代码或假代码

## 验证
- 实现完成后运行 renpy.sh <project> test
- 全部通过 → 报告成功
- 有失败 → 根据运行输出修复（不要读测试源码），重试最多 5 轮
- 5 轮后仍失败 → 报告阻塞，附上运行输出
  `
})
```

**exec 检查 GREEN 结果：**

```
├── ✅ 全部通过 → 进入 VERIFY
├── ❌ 有失败（≤5 轮）→ coding-agent 已自行重试修复
└── 🚫 阻塞（>5 轮）→ 向用户报告，附 coding-agent 的失败输出
```

### UI 任务标记块

仅当 plan.md 中任务类型为 `ui` 时，在 GREEN prompt 的 "实现文件" 段后插入：

```
## UI 任务
html: {task_dir}/{html_path}
```

coding-agent 检测到 `## UI 任务` + `html:` 后自动进入 UI 翻译模式。

---

## VERIFY — test-agent（实现后独立验证门）

```
Agent({
  subagent_type: "renpy-dev:test-agent",
  prompt: `
## 模式
GREEN

## 任务
独立验证 — 跑测试确认 coding-agent 的实现全部通过。

## 测试文件
{test-agent RED 阶段创建的测试文件路径}

## 项目
{project 名称}

## 要求
- 运行 renpy.sh <project> test
- 全部通过 → 报告成功
- 有失败 → 直接返回运行输出（不需要行为级翻译）
  `
})
```

**exec 检查 VERIFY 结果：**

```
├── ✅ 全部通过 → 进入 REFACTOR
└── ❌ 有失败 → 将 test-agent 返回的运行输出传给 coding-agent，回到 GREEN 再修
                （同一错误反复出现则由 exec 向用户报告）
```

---

## REFACTOR — coding-agent

**只有 VERIFY 全部通过后才执行。**

```
Agent({
  subagent_type: "renpy-dev:coding",
  prompt: `
## 模式
REFACTOR

## 已完成的任务
[AI-N] {任务描述} — 所有测试通过 ✅

## 项目
{project 名称，用于运行 renpy.sh <project> test}

## 要重构的文件
{从 coding-agent GREEN 阶段收集的已修改文件列表}

## 重构目标
- 消除重复代码/样式
- 改善命名（变量、函数、label）
- 提取可复用的公共逻辑
- 保持行为完全不变

## 需要读取的文件
- {task_dir}/plan.md（设计摘要，了解设计意图）
- references/exec-logging.md  — AGENT PROGRESS 节（自验证日志格式）

## 约束
- 不改任何 game/tests/ 下的文件
- 不改行为 — 所有已有测试必须继续通过
- 不添加新功能、新配置项
- 不改范围外的文件

## 验证
- 重构完成后运行 renpy.sh <project> test
- 全部通过 → 报告成功
- 有失败 → 修复后重试，最多 5 轮
- 5 轮后仍失败 → 报告阻塞，建议撤销重构
  `
})
```

**exec 检查 REFACTOR 结果：**

```
├── ✅ 全部通过 → 进入 VERIFY
├── ❌ 有失败（≤5 轮）→ coding-agent 已自行修复
└── 🚫 阻塞（>5 轮）→ 报告用户，建议撤销重构保持 GREEN 状态
```

---

## VERIFY — test-agent（重构后独立验证门）

```
Agent({
  subagent_type: "renpy-dev:test-agent",
  prompt: `
## 模式
GREEN

## 任务
独立验证 — 跑测试确认重构后行为不变。

## 测试文件
{test-agent RED 阶段创建的测试文件路径}

## 项目
{project 名称}

## 要求
- 运行 renpy.sh <project> test
- 全部通过 → 报告成功
- 有失败 → 直接返回运行输出
  `
})
```

**exec 检查 VERIFY 结果：**

```
├── ✅ 全部通过 → 任务完成，标记 done
└── ❌ 有失败 → 将运行输出传给 coding-agent，回到 REFACTOR 再修（最多 2 轮回退）
    2 轮回退仍失败 → 报告用户，建议撤销重构
```
