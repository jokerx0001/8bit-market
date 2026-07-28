---
name: game-dev:integration-test-loop-godot
description: |
  Godot 集成测试执行循环。
  启动真实 Godot 游戏，通过 MCP Runtime TCP 操作游戏，每步截图 + visual-qa + 控制台错误检查。
---

# Integration Test Loop — Godot E2E 测试循环

从设计文档推导玩家路径，在真实游戏中逐步骤执行 E2E 验证。控制台错误和 visual-qa 失败均触发诊断修复循环。

## 输入

| 输入 | 说明 |
|------|------|
| task_dir | 任务目录路径 (含 .work/ 下的设计文档) |
| project | Godot 项目路径 |

## Iron Law

```
EVERY STEP IS SCREENSHOT + VISUAL-QA. NO CODE-LEVEL CHECKS.

控制台 ERROR 必须修复。visual-qa FAIL 必须修复。
Either one fails → diagnose root cause → fix → re-run the ENTIRE path from step 1.
```

**为什么必须从第 1 步重跑？** 修复可能改变游戏状态。步骤 3 的截图通过不代表修复后步骤 1-2 仍然通过。E2E 的意义是验证完整玩家路径——不从头跑 = 测试不完整。

---

## 阶段 1: 推导玩家路径并写入文件

### 1a. 读取设计文档

读取 4 份文档建立完整上下文：

```
{task_dir}/.work/requirements.md     — 行为清单（含验证描述，指导视觉检查点）
{task_dir}/.work/domain-design.md    — 领域模型 (状态机、资源管理、事件流)
{task_dir}/.work/architecture.md     — 文件/模块结构、数据流、信号契约
{task_dir}/.work/design.md           — 引擎层实现 (节点路径、API 选择、信号名)
```

**不要跳过任何一份。** 缺少 domain-design 你不知道状态机边界条件。缺少 architecture 你不知道信号契约。缺少 design 你不知道节点路径——无法写出正确的 MCP 工具调用。

### 1b. 从行为清单推导玩家路径

**告诉自己：你是玩家。** 从启动游戏的那一刻开始，沿着自然流程走——标题画面 → 菜单 → 核心玩法 → 结算。不要按代码结构设计路径，按玩家体验设计。

**路径设计规则：**

1. 每条行为至少在一个路径的某个步骤中被验证
2. 一个步骤的截图可以同时验证多个行为——合并 `.question` 减少 visual-qa 调用
3. 路径按玩家自然流程设计 (标题→菜单→游戏→结算)
4. 每一步都用截图 + visual-qa 验证 (E2E: 真实画面才有信服力)

**确认点映射示例：**

读 requirements.md 行为清单，按场景/模块分组，设计若干条路径:

```
行为清单:
  E1 :   标题画面有"开始游戏"按钮
  E2 :   点击"开始"进入角色选择
  E3 :   角色选择画面展示 3 个可选角色，每个有名称和头像
  E4 :   选择角色确认后进入关卡
  E5 :   关卡中角色可左右移动和跳跃
  E6 :   HUD 显示生命值、能量条、武器图标
  E7 :   角色移动时播放行走动画

→ 路径 1: 标题 → 角色选择 → 关卡 → 移动
    步骤 1.1: 等画面渲染 → 截图 → visual-qa 确认 E1
    步骤 1.2: inject_action "ui_accept" → 截图 → visual-qa 确认 E2
    步骤 1.3: 截图 → .question 合并确认 E3
    步骤 1.4: inject_action "right"+"ui_accept" → 截图 → visual-qa 确认 E4
    步骤 1.5: inject_action "right"×1.5s+"jump" → 截图 → visual-qa 确认 E5
    步骤 1.6: inject_action "right"×0.5s → 截图 → 合并确认 E6+E7
```

**硬门 — 确认点覆盖检查（不可跳过）：**

每条 requirements.md 中的行为必须至少出现在一个路径步骤的确认点中。输出覆盖表:

```
| 行为 | 路径.步骤 | 验证方式 |
|------|----------|---------|
| E1   | 1.1      | screenshot |
| E2   | 1.2      | screenshot |
| E3   | 1.3      | screenshot |
| E4   | 1.4      | screenshot |
| E5   | 1.5      | screenshot |
| E6   | 1.6      | screenshot |
| E7   | 1.6      | screenshot |
```

**所有行为覆盖完毕 → 进入 1d。有任何未覆盖的行为 → 回到 1b 补充路径。**

### 1c. 确定产物目录

从 task_dir 推断任务编号:

```bash
TASK_NAME=$(basename {task_dir})   # e.g., "feat-1", "refactor-2", "fix-3"
INTEGRATION_DIR="test/integration/$TASK_NAME"
mkdir -p {project}/$INTEGRATION_DIR
```

### 1d. 写入 .question 文件

对每条路径的每个确认步骤，编写 `.question` 文件。放在:

```
{project}/test/integration/{task_name}/path-{N}-{slug}/step-{M}-{slug}.question
```

**合并原则：** 同一步骤的截图能同时看到的确认点，合并到一个 `.question`。减少 visual-qa 调用次数。

`.question` 格式 (与 test-agent screenshot `.question` 一致):

```markdown
## Requirement
{从 requirements.md 原样复制该行为条目的验证描述}

## Expected Visual State
{描述截图应展示的视觉状态: 哪个界面、截图前执行了什么交互、期望看到哪些元素}

## Questions
{针对该步骤要确认的视觉条件，逐条列出。涉及多个行为时合并所有问题}
- 画面中能看到 XXX 吗？
- ...
```

### 1e. 写入 paths.md

```
{project}/test/integration/{task_name}/paths.md
```

格式:

```markdown
# 集成测试路径 — {task_name}
- 行为总数: {N}
- 路径数: {M}

## 路径 1: {路径描述}

### 步骤 1.1: {步骤描述}
- 确认点: {E1, E2, ...}
- 操作: {inject_action / inject_key / 等待}
- 等待: {等待时长}
- question: {path-slug}/step-{N}-{slug}.question
- 截图: {screenshot 文件名}

### 步骤 1.2: ...
...

## 路径 2: ...
```

**硬门 — paths.md 和所有 .question 文件写入完成后才能进入阶段 2。** 文件不完整 = 执行时无法知道做什么操作、验证什么。

---

## 阶段 2: 启动游戏

### 2a. 读取集成测试协议

```
Read ${CLAUDE_PLUGIN_ROOT}/references/godot/integration-test-protocol.md
```

该文件是集成测试的 MCP 工具使用规范。截图失败时必须回到此文件逐条确认操作是否符合协议——详见阶段 3 "截图失败必做行为"。

### 2b. 确认 MCP 工具可用

确认以下 MCP 工具组已激活:

- `testing` 组: `capture-screenshot`, `inject-action`, `inject-key`
- `runtime` 组: `inspect-runtime-tree`, `call-runtime-method`

如未激活:
```
mcp__godot__tool-groups(action: "activate", group: "testing")
mcp__godot__tool-groups(action: "activate", group: "runtime")
```

### 2c. 创建日志目录

```bash
mkdir -p {task_dir}/.work/logs/integration-test
```

### 2d. 启动 Godot 进程

```bash
GODOT=$(which godot 2>/dev/null || echo "/Applications/Godot.app/Contents/MacOS/Godot")
$GODOT --path {project} 2>&1 | tee {task_dir}/.work/integration-console.log &
GODOT_PID=$!
```

记录 GODOT_PID。

### 2e. 等待 MCP Runtime 就绪

轮询 `mcp__godot__runtime-status(projectPath: {project})`，或直接试调 `mcp__godot__capture-screenshot`。

首次成功响应 → 进入阶段 3。超时 15s → 报错停止，kill Godot 进程。

---

## 阶段 3: 逐路径执行

paths.md 中的每条路径都是独立验证目标。**路径之间不互相阻塞**——路径 1 失败不影响路径 2 开始执行。但**每条路径内部步骤必须顺序通过**。

### 每条路径的执行流程

按 paths.md 顺序处理每条路径。对于每条路径:

1. **读取该路径所有步骤的 .question 文件**——一次性加载到上下文，避免每步重复读文件
2. **从第一步开始，逐步执行**（详见下方"单步执行"）
3. **全部步骤通过 → 路径通过，进入下一条路径**
4. **任一步骤失败 → 进入阶段 4 诊断修复 → 修复后从该路径第一步重新开始**

**为什么从第一步重新开始而不是从失败步骤继续？** 游戏是有状态的。修复可能改变场景加载、信号连接、初始化逻辑。步骤 3 的失败修复后，步骤 1-2 的验证结论可能已失效。不重跑 = 拿旧结论欺骗自己。

### 单步执行流程

对每个步骤，按以下顺序执行。**顺序不可变**——控制台检查必须在 visual-qa 之前，因为控制台 ERROR 说明代码层面出了问题，此时 visual-qa 的结果不可信。

**Step A — 执行操作：**

从 paths.md 读取该步骤的"操作"和"等待"字段，使用 MCP 工具执行:

- 输入动作: `mcp__godot__inject-action(action: "xxx", pressed: true/false)`
- 键盘输入: `mcp__godot__inject-key(keycode: "Enter", pressed: true/false)`  
- 纯等待: `sleep N` (用于等待动画、场景切换等)

**Step B — 等待游戏响应：**

按步骤指定的等待时长等待。**不要缩短等待时间**——动画、场景切换、物理结算都需要时间。等不够 = 截到过渡帧 = 误报。

**Step C — 控制台增量检查（不可跳过）：**

**告诉自己：先检查控制台。控制台有 ERROR 说明代码崩了——此时截图的 visual-qa 结果可能来自崩溃前的残留画面，不可信。**

检查本轮开始后新增的控制台日志行，grep ERROR 级别信息 (`ERROR`, `push_error`, `SCRIPT ERROR`, `CRITICAL`):

- **有 ERROR → 立即进入阶段 4。** 不继续后续步骤，不调 visual-qa。代码层面已经崩了，visual-qa 看崩溃残留画面没有意义。
- **有 WARNING → 记录到报告，继续执行。** WARNING 不影响功能但需要在报告中体现。
- **clean → 继续下一步。**

增量检查的具体实现：在每条路径开始执行前记录当前日志行数作为基线，每个步骤后只检查新增行。这样不会重复处理旧错误。

**Step D — 截图：**

截图前额外等待 0.5s（防角色闪烁、防半帧渲染）。movement 类操作后等待更久（1-2s），确保物理结算和动画到位。

```
mcp__godot__capture-screenshot(width: 640, height: 360)
```

返回 base64 PNG → 解码保存到 `{project}/test/integration/{task_name}/{screenshot 文件名}`。同时保存一份到 `{task_dir}/.work/logs/integration-test/path-{N}-step-{M}.png`（用于诊断追溯）。

**Step E — 截图预检（不可跳过，在调用 visual-qa 前强制执行）：**

**告诉自己：空白截图 = 渲染没完成就截了，或游戏根本没有渲染任何东西。无效 PNG = 截图脚本本身失败了。这两种情况 visual-qa 都无法给出有效结论。** 必须先排除，避免浪费 API 调用和拿到误导性结果。

执行两项预检（参见 `integration-test-protocol.md` 截图预检章节）：

```bash
# 1. PNG 有效性
file {png} | grep -q 'PNG image data' && echo "PNG_OK" || echo "PNG_INVALID"

# 2. 空白检测
STD=$(identify -format "%[standard-deviation]" {png} 2>/dev/null || echo "0")
IS_BLANK=$(echo "$STD < 0.02" | bc -l 2>/dev/null || echo "0")
```

预检结果处理：

- **PNG_INVALID → 不调 visual-qa。** 直接写 `### Verdict: fail` + `### Answer: PNG_INVALID — screenshot capture failed` 到 `{task_dir}/.work/logs/integration-test/path-{N}-step-{M}-qa.log`。标记 FAIL，进入阶段 4。
- **IS_BLANK=1 → 不调 visual-qa。** 进入"空白截图重试循环"（见下方）。重试仍空白 → 写 `### Verdict: fail` + `### Answer: blank_screenshot — std too low after retries` 到 qa.log。标记 FAIL，进入阶段 4。
- **两项都通过 → 进入 Step F。**

**空白截图重试循环：**

空白截图可能只是帧等待不足——渲染管线需要更多时间。不要直接进入根因分析，先尝试重截：

1. 检查 `integration-test-protocol.md` 中的帧等待建议。当前步骤的等待时长是否足够？
2. **增加帧等待：** 将等待时长翻倍（0.5s → 1s，1s → 2s），确保 GPU 提交完成
3. 重新截图：`mcp__godot__capture-screenshot` → 解码保存 → 重新预检
4. 预检通过 → 进入 Step F
5. 仍然空白 → **连续 2 次空白 → 标记 BLOCKED。** 不再浪费时间——可能是环境无 GPU、渲染后端异常、或场景根本没有渲染任何内容

**Step F — Visual QA：**

**告诉自己：visual-qa 的返回必须用机械方式判定，不能靠读自然语言自己判断。** 历史上 coding-agent 就是因为自己读 Answer 文本，把"看不到"、"纯黑场景"判定为 PASS。

1. 读取该步骤的 `.question` 文件
2. 调用 `Skill("game-dev:visual-qa")`，传入截图路径 + `.question` 内容
3. **将 visual-qa 的完整原始输出保存到 `{task_dir}/.work/logs/integration-test/path-{N}-step-{M}-qa.log`**（不保存日志 = 本轮验证无效，无法追溯）
4. **机械判定结果**——grep qa.log 的 `### Verdict` 字段：
   - `### Verdict: pass` → PASS ✅ → 步骤通过，进入下一步骤
   - `### Verdict: fail` → FAIL ❌ → 进入阶段 4
   - **Verdict 字段缺失 → INCOMPLETE ⚠️**（不要标记为 PASS，不要标记为 FAIL）。visual-qa 未正常完成——可能是 API 错误、输出格式异常。进入"截图失败必做行为"检查后重试本步骤

**Step G — 截图验证硬门（Step F 之后强制执行）：**

每次 visual-qa 调用后检查以下项目。**任何 ❌ → 截图验证标记为 INCOMPLETE（不得标记为 PASS，不得标记为 FAIL 后进入诊断）。**

| # | 检查项 | 状态 |
|---|--------|------|
| 1 | `path-{N}-step-{M}-qa.log` 已写入 `.work/logs/integration-test/`（文件存在且非空） | ✅ / ❌ |
| 2 | qa.log 中包含 `### Verdict` 行（visual-qa 返回了有效结果，非 API error） | ✅ / ❌ |
| 3 | `### Verdict: pass`（通过）或失败原因已记录 | ✅ / ❌ |
| 4 | 如 qa.log 的 Answer 包含 `blank_screenshot: true` → 回到 Step E 的空白截图重试循环，重试后从 Step D 重新走 | ✅ / ❌ |

**全部 ✅ → 步骤通过。** 进入下一步骤。
**任何 ❌ → INCOMPLETE。** 进入"截图失败必做行为"，然后重试本步骤（从 Step D 开始）。

**截图失败必做行为（硬门——Step G 任何 ❌ 时必须全部执行）：**

**告诉自己：截图失败不是"运气不好"。** 必须逐项排查——是操作问题、环境问题、还是 visual-qa 本身的问题。不排查就重试 = 浪费 API 调用。

| # | 检查项 | 状态 |
|---|--------|------|
| 1 | 已重新 `Read ${CLAUDE_PLUGIN_ROOT}/references/godot/integration-test-protocol.md` 的截图章节和已知坑 | ✅ / ❌ |
| 2 | 已逐条对照 `integration-test-protocol.md` 确认截图命令合规（`capture-screenshot` 参数、截图前等待时长、是否用了直接启动而非 `run-project`） | ✅ / ❌ |
| 3 | 已检查 Godot 进程仍在运行（`ps -p $GODOT_PID`）且 MCP Runtime 仍连接（`runtime-status`） | ✅ / ❌ |
| 4 | 如 Godot 进程或 MCP 已断开 → 已记录原因到报告，标记环境异常 | ✅ / ❌ |
| 5 | 已检查 qa.log 是否含 `blank_screenshot: true`（visual-qa 的 blank 报告）或 `API error` | ✅ / ❌ |

**此硬门不可跳过。** 截图失败不做此检查 = 本轮验证无效。

### 步骤结果状态

每个步骤有三种可能的结果：

| 状态 | 含义 | 触发条件 | 处理 |
|------|------|---------|------|
| **PASS** ✅ | 验证通过 | 控制台 clean + 预检通过 + `### Verdict: pass` + 硬门全部 ✅ | 进入下一步骤 |
| **FAIL** ❌ | 验证失败 | 控制台 ERROR / 预检 PNG_INVALID / `### Verdict: fail` | 进入阶段 4 诊断修复 |
| **INCOMPLETE** ⚠️ | 验证未完成 | 预检连续 BLANK / Verdict 缺失 / qa.log 未保存 / 硬门 ❌ | 执行截图失败必做行为 → 重试本步骤（最多 2 次）→ 仍 INCOMPLETE → 升级为 FAIL |

**INCOMPLETE 不是 PASS。** visual-qa 没有产生有效结果时，你不能声称验证通过。把 INCOMPLETE 当 PASS = 欺骗自己。

### 重试控制

每条路径最多 5 轮（每轮 = 从步骤 1 开始完整执行一次）。达到 5 轮仍未通过 → 标记 BLOCKED，跳过此路径继续处理下一条。

同一失败原因连续出现 3 轮 → 标记 BLOCKED，不等 5 轮上限。同原因反复失败说明修复方向错误——继续重试只会浪费 token。

同一步骤连续 2 次 INCOMPLETE → 升级为 FAIL，进入阶段 4。INCOMPLETE 说明验证本身出了问题——可能是环境、MCP 连接、或 visual-qa 后端异常。重试 2 次仍然无法完成验证 → 当作失败处理，需要诊断。

---

## 阶段 4: 诊断修复

步骤失败（控制台 ERROR、截图预检失败、或 visual-qa fail）时触发。

### 4a. 收集失败上下文

在进入诊断之前，**必须先收集以下全部信息**:

- **qa.log 完整内容**（`{task_dir}/.work/logs/integration-test/path-{N}-step-{M}-qa.log`）——包含 visual-qa 的 `### Verdict`、`### Answer`、`### Visual Evidence`。如果 qa.log 不存在（控制台 ERROR 场景，未走到 Step F），标注 "N/A — 控制台 ERROR 触发，未执行 visual-qa"
- 新增的控制台错误行（如果是控制台 ERROR）
- 该步骤的确认点（requirements.md 对应行为条目）
- 当前场景树（通过 `inspect-runtime-tree` 获取，用于理解游戏运行时状态）
- 该步骤的截图文件（`{task_dir}/.work/logs/integration-test/path-{N}-step-{M}.png`）和预检结果（PNG_OK / BLANK / PNG_INVALID）

**收集不全就开始诊断 = 基于不完整信息做判断。** 缺信息时诊断结论不可信。

### 4b. 根因分析

调用 `Skill("game-dev:debug-root-cause")`:

将失败描述、预期行为、场景状态传入。debug-root-cause 产出 `{task_dir}/.work/debug-analysis.md`。

### 4c. 实施修复

**告诉自己：我是测试者，不是开发者。修复必须走 coding-agent——我自己改代码违反了 agent 隔离规则。**

基于 debug-analysis.md 的根因，spawn `game-dev:coding` agent 修复:

```
Spawn game-dev:coding agent:
  模式: GREEN
  project: {project}
  task_dir: {task_dir}
  任务: 修复集成测试路径失败
  失败描述: {visual-qa Answer + 控制台错误}
  根因: {debug-analysis.md 的根因}
  目标: {requirements.md 中对应的行为条目}
  需要读取的文档: architecture.md, design.md
```

**不自行修改代码。** spawn coding-agent 是唯一修复路径。这条规则和 exec 阶段的 agent 隔离一致——集成测试 agent 的职责是发现问题和验证，不是写代码。

### 4d. 重跑路径

修复完成后，**从该路径第一步重新开始执行**。不等其他路径——立即重跑当前路径。

同一原因连续 3 轮仍失败 → 标记 BLOCKED，跳过此路径，继续下一条。

---

## 阶段 5: 停止游戏 + 报告

### 5a. 停止游戏

```bash
kill $GODOT_PID 2>/dev/null
sleep 1
ps -p $GODOT_PID > /dev/null 2>&1 && kill -9 $GODOT_PID
```

确认进程退出。**不要让 Godot 进程残留**——会占用端口影响下次运行。

### 5b. 写入报告

写入 `{task_dir}/.work/integration-test-report.md`:

```markdown
# 集成测试报告 — {task_name}

## 路径 1: {描述} ({N} 轮)
| 步骤 | 操作 | 预检 | visual-qa | 控制台 | 结果 |
|------|------|------|-----------|--------|------|
| 1.1  | 等待标题        | PNG_OK | ✅ PASS | ✅     | ✅ |
| 1.2  | ui_accept       | PNG_OK | ✅ PASS | ✅     | ✅ |
| 1.3  | 截图            | PNG_OK | ✅ PASS | ✅     | ✅ |
| 1.4  | right+accept    | PNG_OK | ✅ PASS | ⚠️ WARNING: unused param | ✅ |
| 1.5  | right+jump      | PNG_OK | ✅ PASS | ✅     | ✅ |
| 1.6  | right+截图      | PNG_OK | ✅ PASS | ✅     | ✅ |
| **路径结果** | | | | | **✅ 通过** |

## 路径 2: {描述} (3 轮后阻塞)
| 2.1  | ...             | PNG_OK | ✅ PASS | ✅     | ✅ |
| 2.2  | shoot+截图      | PNG_OK | ❌ FAIL: 刀光不可见 | ERROR: null texture | ❌ |
| ...  | (第 3 轮仍 FAIL) |         |       |       | 🚫 BLOCKED |

## 路径 3: {描述} (INCOMPLETE 后失败)
| 3.1  | 等待标题        | PNG_OK | ✅ PASS | ✅     | ✅ |
| 3.2  | 截图            | BLANK   | N/A (预检拦截) | ✅ | ⚠️ INCOMPLETE → 重试 → BLANK ×2 → ❌ FAIL |

## 汇总
- 路径通过: {N}/{M}
- 路径阻塞: {K}
- 总轮次: {R}
- 修复 spawn: {S} 次 coding-agent
- 控制台 WARNING: {W} 条
- INCOMPLETE 事件: {I} 次（重试后恢复: {R} 次 / 升级为 FAIL: {F} 次）

## 阻塞详情 (如有)
### 路径 {X} — 步骤 {Y}: {BLOCKED 原因}
- 根因: {debug-analysis.md 结论}
- 尝试: {N} 轮
- 建议: {需人工介入的原因}
```

### 5c. 输出完成摘要

```
## 集成测试完成 — {task_name}
- 路径: {N}/{M} 通过
- 阻塞: {K} ({BLOCKED 详情如有})
- 轮次: {R}
- 报告: {task_dir}/.work/integration-test-report.md
```

---

## 重试上限

| 限制 | 值 | 原因 |
|------|-----|------|
| 每条路径最多 | 5 轮 | 超过 5 轮仍然失败 = 问题不是几轮修复能解决的，需要人工介入 |
| 同原因连续失败 | 3 轮 → BLOCKED | 同一修复方向反复失败 = 方向错了，继续浪费 token |
| Runtime 就绪超时 | 15s | Godot 启动通常 5-10s，15s 还没响应 = 项目配置或 MCP 有问题 |
| 空白截图连续 | 2 次 → BLOCKED | 连续空白 = 渲染管线问题，不是帧等待能解决的 |

**阻塞路径不阻塞其他路径。** 路径 2 BLOCKED 不影响路径 3 继续执行。每条路径独立验证。

---

## Red Flags

如果你发现自己在想：

| 中文 | English |
|------|---------|
| "控制台 WARNING 不影响功能，继续就行" | "Console warning doesn't matter, keep going" |
| "visual-qa 不太确定，但我觉得 PASS" | "visual-qa is unsure but I think it's PASS" |
| "同一个原因失败了，但不一定是代码问题" | "Same reason failed again, but maybe not a code issue" |
| "跳过预检直接调 visual-qa 更快" | "Skip pre-check, go straight to visual-qa" |
| "get_tree 也能验证，不用每步都截图" | "get_tree can verify, no need to screenshot every step" |
| "代码简单我自己修，不用 spawn coding-agent" | "The fix is simple, I'll do it myself without coding-agent" |
| "从失败的步骤重新开始就行，不用重跑前面的" | "Just restart from the failed step, no need to re-run earlier ones" |
| "等不及了，截图等待时间减半试试" | "Can't wait, let's halve the screenshot wait time" |
| "控制台 ERROR 可能是旧的，先调 visual-qa 看看" | "Console ERROR might be old, let's check visual-qa first" |
| "visual-qa 返回了 Answer 但没有 Verdict，我看 Answer 内容判断一下就行" | "visual-qa returned Answer but no Verdict, I'll just read the Answer and decide" |
| "qa.log 没保存成功，但我记得 visual-qa 说什么" | "qa.log didn't save, but I remember what visual-qa said" |
| "预检 BLANK 了一次，但 visual-qa 可能还是能识别，直接调吧" | "Pre-check was BLANK once, but visual-qa might still recognize it, just call it" |
| "INCOMPLETE 和 FAIL 差不多，都进诊断就行了" | "INCOMPLETE and FAIL are basically the same, just go to diagnosis" |
| "截图失败必做行为太费时间，直接重试截图就行" | "Screenshot failure mandatory actions take too long, just retry the screenshot" |

**以上任一条 → STOP。** E2E 意味着每步截图验证。控制台 ERROR 必须修。修复必须走 coding-agent。失败必须从第一步重跑。visual-qa 结果必须机械判定——不靠人眼读 Answer。

## 常见自我合理化

| 借口 | 现实 |
|------|------|
| "这步就是等画面渲染，没做操作，跳过截图吧" | 没操作不等于状态没变。动画在播、物理在结算、信号在触发。不截图 = 不知道发生了什么。 |
| "控制台 ERROR 和我要验证的视觉行为无关" | 控制台 ERROR = 代码出了你不理解的异常。继续验证是在沙子上建房子。 |
| "visual-qa 说 fail 但我觉得是误报" | 你是测试者，不是辩解者。visual-qa 说 fail → 进入诊断。误报也是信息——说明画面和预期有差异，即使差异的原因不是 BUG。 |
| "都已经第 3 轮了，换个思路从步骤 3 开始试试" | 第 3 轮还失败 = 前两轮的修复方向有问题。从步骤 1 重跑是验证修复是否真的解决了问题。只跑步骤 3 = 你不知道步骤 1-2 是否被破坏了。 |
| "coding-agent 太慢了，这行代码我直接改就行" | 集成测试 agent 的职责是发现问题。写测试和写代码的是不同的 agent——这是 exec 阶段建立的隔离规则。打破隔离 = 破坏了整个 TDD 流程的可信度。 |
| "visual-qa 的 Answer 说'画面中看不到按钮'，但可能只是描述方式，我觉得算 PASS" | `### Verdict` 字段的存在就是为了防止这种自我合理化。Answer 说"看不到" → visual-qa 会标记 `### Verdict: fail`。如果你在手动判断 Answer 而不是 grep Verdict，你已经在违反规则了。Verdict 缺失 → INCOMPLETE，不是 PASS。 |
| "qa.log 忘了保存，但我记得 visual-qa 返回了什么，报告里写上就行" | 没有原始输出 = 没有可追溯性。后续诊断需要完整的 Answer + Visual Evidence，靠记忆写报告 = 信息丢失。不保存日志 = 本轮验证无效。 |
| "预检 BLANK 了但等 0.5s 重截就行，不用走完整的空白截图重试循环" | 空白截图重试循环要求增加帧等待翻倍，不是因为"等等就好"，而是因为渲染管线可能需要显著更长的 GPU 提交时间。0.5s 变成 1s 而不是 0.5s 变成 0.55s——这个翻倍是经过验证的有效策略。 |
| "截图失败必做行为 5 项太多了，直接重试截图就行" | 截图失败的原因可能是 Godot 进程挂了、MCP Runtime 断了、或者用了 `run-project` 的 dummy renderer。重试截图不会修复这些问题——你只是把同一个失败重复了一遍。 |
| "INCOMPLETE 就重试一次，不行就当 FAIL 处理，不用走必做行为" | INCOMPLETE 意味着验证本身出了问题。跳过必做行为直接降级为 FAIL = 你放弃了排查验证环境问题的机会。修复代码之前，先确认验证环境是健康的。 |
