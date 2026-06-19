---
name: renpy-dev:exec
description: "Execute a Ren'Py implementation plan with TDD. Use when asked to 'execute the plan', 'start implementation', 'build the feature'. Reads plan documents, spawns subagents for test/code, tracks progress for resume support."
---

# Ren'Py AI 开发 — 执行阶段

读取实现计划，按 TDD 循环逐任务执行，支持断点续跑。

## 核心原则

**TDD 铁律：没有失败测试就不允许写生产代码。**
**子代理铁律：coding agent 只写实现，不改测试。test agent 只写测试，不写实现。**
**任务铁律：不限重试次数，必须完成。连续 5 轮无进展才切换策略。**

---

## 工作流

### 1. 定位任务目录

如果参数提供了 plan 文件路径，使用对应目录。否则查找最近的计划：

```bash
ls -d .renpy-dev/feat-*/ 2>/dev/null | sort -V | tail -5
```

确定 `task_dir`（如 `.renpy-dev/feat-1/`）。

### 2. 加载 plan.md

**只读取 `{task_dir}/plan.md`**。plan.md 是自包含的——概述、设计摘要、影响范围、任务列表、测试策略全部在此文件中。不读 `.work/` 下的任何中间产物。

### 3. 加载进度追踪

读取 `{task_dir}/progress.json`。如果不存在，创建：

```json
{
  "task_dir": ".renpy-dev/feat-1",
  "started_at": "{ISO timestamp}",
  "last_updated": "{ISO timestamp}",
  "tasks": {}
}
```

### 4. 解析任务列表和测试策略

按 `plan-format.md` 的解析规则提取 `[AI-N]` 任务：

1. 匹配 `- \[AI-(\d+)\]` 提取序号和描述
2. 匹配 `→ \`(.+)\`` 提取目标文件路径
3. 匹配 `(依赖: (.+))` 确定执行顺序
4. 按依赖拓扑排序，无依赖的优先执行
5. `[HUMAN]` 任务收集但不执行

**同时解析测试策略表** — 提取每行（测试文件、覆盖内容），按测试文件路径与 `[AI-N]` 输出路径匹配。RED phase 传测试文件路径和覆盖内容给 test agent，test agent 自行读 `.work/design.md` 获取细节。

对每个任务，检查 `progress.json`：
- `done` → 跳过，输出 `⏭️ [AI-N] 已完成，跳过`
- `pending` 或无记录 → 待执行
- `in_progress` → 上次中断点，从此任务继续

### 5. 确认测试可用性

```bash
ls tools/test.py 2>/dev/null && echo "READY" || echo "MISSING"
```

如果 `tools/test.py` 不存在，提示用户从 `assets/test-infra/` 安装测试基础设施。

### 6. TDD 循环执行每个任务

对每个待执行的 `[AI-N]` 任务：

#### 7a. 标记开始

更新 `progress.json`：
```json
{..., "tasks": {..., "AI-N": {"status": "in_progress", "started_at": "..."}}}
```

#### 7b. RED — spawn test agent

test agent 自己读文件获取写测试所需的一切信息。主会话只传任务目标和文件路径。

```
Agent({
  subagent_type: "renpy-dev:test-agent",
  prompt: `
## 任务
为 [AI-N] {任务描述} 编写测试。

## 测试目标
{从 plan.md 测试策略表提取的本行覆盖内容，如 "behavior: 角色选择交互（选中/取消/确认）"}

## 测试文件
{从 plan.md 测试策略表提取的本行测试文件路径}

## 需要读取的文件
- .renpy-dev/{kind}-{N}/.work/design.md  — 获取 widget 树、变量定义、交互流程
- .renpy-dev/{kind}-{N}/plan.md 的"设计摘要"段  — 获取 screen 结构、数据流设计
- game/tests/_framework.rpy  — 获取可用的 test_framework helper API
- game/tests/test_*.rpy（已有测试文件） — 了解命名惯例和代码风格
- game/ 下相关的 .rpy 源文件 — 了解已有代码模式和约定

## 编写要求
1. 从 design.md 提取变量名、screen 名、widget ID 写入测试 — 不凭空编造
2. 测试断言的是目标行为（design.md 中设计的交互结果），不是当前行为
3. 测试预期失败（因为功能尚未实现）
4. 只写 game/tests/ 下的测试代码，不写 game/ 下的业务代码
5. 使用 test_framework helper API
6. behavior 测试：验证"给定输入 → 产生正确状态/输出"，不检查 widget ID 是否存在
7. visual 测试：从 design.md 获取 widget ID，对 screen 截图做像素 diff

## 约束
- 不允许 mock、假代码、硬编码预期值来让测试通过
- 只执行逻辑，比对结果
  `
})
```

#### 7c. 评估 RED 结果

检查点：
1. 测试文件已创建/修改？
2. 测试覆盖了 prompt 中"测试目标"列出的功能？
3. 测试中引用的变量名、screen 名与 `.work/design.md` 一致（不是凭空编造的）？
4. 没有 mock、假代码、硬编码预期值？
5. 测试语法有效？（运行 `python tools/test.py structure`）
6. 测试命名符合规范（`test_b_*` / `test_v_*`）？

不合格 → 反馈具体问题，重新 spawn test agent（不消耗重试计数）。
合格 → 进入 GREEN。

#### 7d. GREEN — spawn coding agent

```
Agent({
  subagent_type: "renpy-dev:coding",
  prompt: `
## 任务
[AI-N] {任务描述}

## 设计上下文
{从 plan.md 的"概述"和"设计摘要"段提取的关于此任务的关键设计决策和约束}

## 需要通过的测试
{7b 中 test agent 写的测试代码}

## 实现文件
{plan.md 中标注的输出文件路径}

## 约束
1. 只修改使测试通过所需的最少代码
2. 不修改任何测试代码（game/tests/ 下的文件）（绝对禁止）
3. 不修改 game/libs/、game/tl/ 等第三方代码
4. 不写空代码或假代码（pass、TODO、NotImplementedError）
5. 新增 screen 时必须给关键交互 widget 添加 id 属性
6. 确保代码语法正确（renpy 可加载）
7. 不得修改 plan.md 中未列出的文件
8. 实现必须基于设计文档中的设计，不得自行偏离

## 可用资源
- 测试方法论文档: plugins/renpy-dev/skills/test/SKILL.md
- 测试 helper API: game/tests/_framework.rpy
  `
})
```

#### 7e. VERIFY — 运行测试

使用 `python tools/test.py` 运行对应层的测试。

**验证原则（不可妥协）：**

任务完成的判定必须基于**真实的运行时输出** — 从 `tools/test.py` 的 stdout/stderr、`.last_results.json` 中获取的**实际文本**。绝不能凭代码逻辑推测"应该通过"。

1. 运行 `python tools/test.py behavior`（或 visual/structure）
2. 读取 `game/tests/.last_results.json` 获取测试结果
3. 对比期待值和实际值：

```
验证 [AI-N]:
  测试: test_b_character_select
  结果: ✅ PASS
  测试: test_v_character_select
  结果: ✅ PASS (baseline created)
  结论: ✅ 全部通过
```

**失败处理：**

1. 读取 `.last_results.json` 中的失败详情
2. 对比 expected vs actual，定位具体差异
3. 分析根因（不是猜测，基于失败事实推导）
4. 携带**实际输出 + 根因分析**重新 spawn coding agent
5. 重复直到验证通过

**如果连续 5 轮同一个错误没有进展：**
- 重新审视测试本身是否合理
- 检查依赖的前置任务是否有隐含 bug
- 简化实现方案再逐步扩展
- 向用户报告当前卡点和已尝试的方案，请求指导

#### 7f. REFACTOR — 主会话审查

调用 `renpy-dev:review` skill 审查代码变更：

1. coding agent 的实现是否符合 plan.md 的设计摘要？
2. 是否修改了测试代码？（零容忍）
3. 是否有超出 plan.md 影响范围的改动？
4. 新增 screen 的关键 widget 是否有 `id`？
5. 跨文件 `jump/call` 目标是否存在？
6. `OWN_MANIFEST.json` 是否已更新？

合格 → 标记任务完成。
不合格 → 反馈具体问题，重新 spawn coding agent。

#### 7g. 标记完成

更新 `progress.json`：
```json
{..., "tasks": {..., "AI-N": {"status": "done", "completed_at": "..."}}}
```

输出：
```
✅ [AI-N] {任务描述}
   测试: {通过的测试数量/总数}
   文件: {创建/修改的文件列表}
```

### 7. 提醒人工任务

所有 AI 任务完成后，汇总 `[HUMAN]` 任务：

```
## 待人工完成

- [ ] {HUMAN 任务 1}
- [ ] {HUMAN 任务 2}

完成人工任务后，运行 /renpy-dev:review 进行最终审查。
```

### 8. 最终验证

1. 运行 `python tools/test.py`（全部三层）检查回归
2. 输出完成摘要

---

## 断点续跑

当 exec 在新 session 中被调用时：

1. 读取 `progress.json`
2. 跳过 `done` 的任务
3. 找到第一个非 `done` 任务，从那里继续
4. `in_progress` 的任务被视为中断，重新执行（不信任中间状态）

---

## Completion Gate

永远不要声称任务完成，除非：

1. 所有 `[AI-N]` 任务在 `progress.json` 中标记为 `done`
2. `python tools/test.py` 全部三层通过
3. 输出下面的完成报告：

```
## 执行完成

**任务：** {done_count}/{total_count} 完成
**测试：** structure ✅ behavior ✅ visual ✅
**创建/修改文件：**
  - {file1}
  - {file2}

**待人工完成：**
- [ ] {HUMAN 任务列表}
```
