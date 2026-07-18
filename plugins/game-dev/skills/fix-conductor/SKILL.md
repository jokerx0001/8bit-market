---
name: game-dev:fix-conductor
description: |
  工作流状态机，协调游戏项目 BUG 修复的完整周期。
  行为澄清 → test agent 写 BUG 复现测试 → fix-agent (fix-loop + debug-root-cause) → VERIFY。

  <example>
  Context: 用户报告了一个 BUG
  user: "/game-dev:fix 角色选择界面点击确认后闪退"
  assistant: "行为澄清 → BUG 复现测试 → fix-agent 修复循环 → VERIFY。"
  <commentary>
  先澄清正确行为，再用测试复现 BUG，然后逆向追踪找根因，最后 coding agent 修复循环。
  </commentary>
  </example>

  <example>
  Context: 全自动模式
  user: "/game-dev:fix 存档加载后数据丢失 --auto"
  assistant: "全自动模式启动。将完成 行为澄清 → BUG 复现测试 → fix-agent 修复循环 → VERIFY，不在中间暂停。"
  <commentary>
  --auto 标志表示全自主模式，不等人工审查。
  </commentary>
  </example>
---

# Game Dev Fix Conductor — BUG 修复状态机

## 工作流

```
[检测技术栈] → 行为澄清 → test agent 写 BUG 复现测试 → fix-agent (fix-loop + debug-root-cause) → VERIFY → completed
    ↑ 预期行为      ↑ 确认 BUG 存在 + 可复现          ↑ 诊断→修复→验证循环             ↑ 独立验证
```

与另外两个 conductor 的区别：

| | orchestrator | refactor-conductor | fix-conductor |
|--|:--:|:--:|:--:|
| 分析手段 | brainstorming | 代码分析 + brainstorming | 逆向追踪（debug-root-cause） |
| 前置产物 | — | impact.md | BUG 复现测试 |
| 执行 | exec --mode feat | exec --mode refactor | fix-agent (fix-loop) |

---

### 阶段 0：检测技术栈 + 创建上下文

**Step 0a — 读 CLAUDE.md 确定 tech**

**Step 0b — 读 config 获取 dev_dir（硬门）：**

1. 读 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md` 的 `## 产物目录` 节
2. 提取 `dev_dir` 值
3. 回显确认后才能调用 artifact-manager。**不猜测不缩写。**

**Step 0c — 创建任务目录：**

```
Skill({skill: "game-dev:artifact-manager", args: "--task-dir {dev_dir}/fix-{N} --kind fix --dev-dir {dev_dir}"})
```

返回 `task_dir`。

**Step 0d — 创建 .work：**

```bash
mkdir -p {task_dir}/.work
```

### 阶段 1：行为澄清（Behavior Clarification）

在动手之前，先搞清楚**正确的行为应该是什么**。没有行为基准，根因分析无法判断什么算"错"。

**执行步骤：**

1. 解析用户的 BUG 描述，检查是否已包含预期行为
2. 向用户询问预期行为：

```
## 行为澄清

在开始调试之前，需要先确认：**这个功能的正确行为应该是什么？**

{根据 BUG 描述提出 2-4 个具体问题，例如：}
- 正常情况下，应该显示什么内容？
- 用户执行这个操作后，应该发生什么？
- 这个变量的有效值/有效范围是什么？
- 如果这是个边界情况，正确的降级/兜底行为是什么？
```

3. 用户无法确定时，基于代码分析给出 2-3 个合理选项供选择
4. 将用户确认的预期行为整理为清单，回显确认：

```
## 预期行为确认

请确认以下正确行为描述是否准确：

1. {行为 1 — 用户可见/系统可感知的}
2. {行为 2}
3. ...

确认后回复"OK"继续。
```

5. **硬门：** 未确认预期行为前，不得进入阶段 2
6. 用户自己也无法确定预期行为 → 暂停，建议先搞清楚功能需求再继续

### 阶段 1b：视觉验证检测

预期行为确认后，检测 BUG 是否涉及视觉验证。视觉 BUG 需要额外增加截图验证，不能只看 GUT 测试结果。

**自动检测规则：** 扫描 BUG 描述和预期行为文本，匹配视觉关键词（不区分大小写）：

```
中文: 显示|渲染|画面|布局|颜色|位置|大小|UI|界面|样式|字体|图标|动画|特效|遮挡|重叠|偏移|消失|闪烁|错位|裁剪|拉伸|变形|对齐|间距|尺寸|透明度|层级|视觉|UI|像素
英文: display|render|layout|color|position|size|visual|appear|look|style|font|icon|animation|effect|overlap|offset|clip|stretch|align|spacing|opacity|layer|pixel|z-order
```

**判定逻辑：**

```
匹配到视觉关键词 → 标注为包含视觉验证 BUG
├── 自动在已有行为验证基础上增加一条视觉验证case
│   ├── 行为涉及视觉状态（如"面板显示在屏幕中央""按钮颜色变为红色"）→ 增加一条screenshot测试验证
├── 向用户确认：
│   ```
│   ## 视觉验证需求确认
│
│   此 BUG 涉及视觉问题。以下预期行为建议增加截图验证：
│
│   1. {行为 1} — 验证方式: screenshot（截图验证）
│   ...
│
│   请确认：
│   - 截图验证的行为是否正确？
│   - 需要截图验证的行为，具体的视觉检查点是什么？
│       例如："确认按钮是否显示在面板右下角""确认角色头像是否正确渲染"
│   ```
└── 用户确认后，记录每条行为的验证方式 + screenshot 行为的问题描述

```

**硬门：** 匹配到视觉关键词但用户未确认截图验证需求前，不得进入阶段 2。

### 阶段 2：Test Agent 写 BUG 复现测试

用 test agent 编写一个专门复现 BUG 的测试文件。这个测试当前必然 FAIL（BUG 存在），它是后续根因分析的**可运行输入**。这个测试必须是依据预期行为来写，要体现出预期行为失败。

```
Agent({
  subagent_type: "game-dev:test-agent",
  description: "Write BUG reproduction test",
  prompt: "
    为以下 BUG 编写复现测试：

    BUG 描述：{用户报告的 BUG}

    预期行为（含验证方式）：
    1. {行为 1}  — 验证方式: {behavior | screenshot: 问题描述}
    2. {行为 2}  — 验证方式: {behavior | screenshot: 问题描述}
    3. ...

    要求：
    - 测试文件写入 {test_dir}/
    - 测试必须复现 BUG——当前应 FAIL
    - 测试通过的标准是：实际行为 = 预期行为
    - 只写测试，不修改源代码
    - 标注为 screenshot 的行为必须创建截图脚本 + .question 文件，放入 {test_dir}/visual/
    - 截图 testcase 命名: test_{描述}_screenshot
  "
})
```

**硬门：**
- 测试必须 FAIL。如果 PASS → 检查测试是否真正覆盖了 BUG 场景，修正后重试。
- 标注为 screenshot 的行为必须有对应的截图脚本 + .question 文件产出。缺失 → 重新 spawn test-agent。

**硬门通过后 — 记录测试目标：**

从 test-agent 的 report 提取 testsuite 名和 testcase 名列表（含 GUT + screenshot），在后续阶段 3 传入 fix-agent。

### 阶段 3：Fix Agent — 诊断→修复→验证循环

Spawn fix-agent，由它调用 fix-loop skill 进行修复循环（fix-loop 内部调用 debug-root-cause 做根因分析）。

从阶段 2 的 RED report 提取 testsuite 名和 testcase 名列表（含 GUT 和 screenshot 两类——screenshot testcase 通过命名约定 `test_{描述}_screenshot` 区分）。

```
Agent({
  subagent_type: "game-dev:fix-agent",
  description: "BUG fix loop",
  prompt: "
## project
{project 名称}

## task_dir
{task_dir}

## BUG 描述
{用户报告的 BUG}

## 预期行为（含验证方式）
1. {行为 1}  — 验证方式: {behavior | screenshot: 问题描述}
2. {行为 2}  — 验证方式: {behavior | screenshot: 问题描述}
3. ...

## 目标 testsuite
{从 RED report 提取的 suite 名}

## 目标 testcase
{从 RED report 提取的 testcase 名列表（含 GUT + screenshot）}
  "
})
```

fix-agent 启动后读取参考文件 → 调用 `Skill("game-dev:fix-loop")` 开始修复循环 → 完成后返回。

**修复循环最多 5 轮。** 超过 → 报告用户，请求人工介入。

### 阶段 4：VERIFY — 独立验证

Spawn test-agent 独立验证修复结果：

```
Agent({
  subagent_type: "game-dev:test-agent",
  prompt: "
## 模式
GREEN

## project
{project 名称}

## task_dir
{task_dir}

## 任务
独立验证 — 跑全量测试确认修复完成且无回归。
  "
})
```

**验证标准：**
- 全量测试全部通过（`test_cmd_full` 退出码 0）
- BUG 复现测试 PASS
- 已有测试全部通过（无回归）
- 有 screenshot 验证方式的行为：截图验证通过 visual-qa

---

## 状态存储

状态由 `game-dev:artifact-manager` 统一管理，详见 `skills/artifact-manager/SKILL.md`。conductor 不直接操作 `current-state.json`。

## 错误处理

- **BUG 复现测试 PASS（BUG 未复现）**：检查测试覆盖是否准确，修正后重试。确认无误后可能是用户环境问题，报告用户。
- **fix-agent 修复循环超过 5 轮**：fix-loop 自行停止并输出阻塞报告。conductor 将报告呈现给用户，请求人工介入。
- **用户无法确定预期行为**：暂停，建议用户先搞清楚功能需求再继续。给出基于代码推断的 2-3 个合理选项供参考
- **用户中断**：progress.json 保存当前状态，下次启动可继续

## Red Flags

- "dev_dir 大概就是 .dev 吧，不用读 config"
- "记得是 .dev，不用再读 config"
- 没有回显 dev_dir 值就直接调用 artifact-manager

**以上任一条 → STOP。回到 Step 0b，读 config 并回显。**

## 约束

- 预期行为未经用户确认前，不得进入阶段 2
- BUG 复现测试未 FAIL 前，不得进入阶段 3
- fix-agent 绝不修改测试代码
- 所有已有测试必须继续通过（无回归）
- BUG 复现测试必须在修复后 PASS
