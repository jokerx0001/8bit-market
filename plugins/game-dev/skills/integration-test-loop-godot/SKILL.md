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

---

## 阶段 0: 推导玩家路径 + 写入文件

### Step 0a: 读取 4 份设计文档

```
{task_dir}/.work/requirements.md     — 行为清单 (含验证方式: behavior / screenshot)
{task_dir}/.work/domain-design.md    — 领域模型 (状态机、资源管理、事件流)
{task_dir}/.work/architecture.md     — 文件/模块结构、数据流、信号契约
{task_dir}/.work/design.md           — 引擎层实现 (节点路径、API 选择、信号名)
```

### Step 0b: 从行为清单推导玩家路径

**路径设计规则:**

1. 每条行为至少在一个路径的某个步骤中被验证
2. 一个步骤的截图可以同时验证多个行为 (合并 .question 减少 visual-qa 调用)
3. 路径按玩家自然流程设计 (标题→菜单→游戏→结算)
5. **每一步都用截图 + visual-qa 验证** (E2E: 真实画面才有信服力)

**确认点映射:**

读 requirements.md 行为清单，按场景/模块分组，设计若干条路径:

```
行为清单:
  E1 :     标题画面有"开始游戏"按钮
  E2 :     点击"开始"进入角色选择
  E3 :   角色选择画面展示 3 个可选角色，每个有名称和头像
  E4 :     选择角色确认后进入关卡
  E5 :     关卡中角色可左右移动和跳跃
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

**Hard Gate — 确认点覆盖检查:**

每条 requirements.md 中的行为必须至少出现在一个路径步骤的确认点中。输出覆盖表:

```
| 行为 | 路径.步骤 | 验证方式 |
|------|----------|---------|
| E1 | 1.1 | screenshot |
| E2 | 1.2 | screenshot |
| E3 | 1.3 | screenshot |
| E4 | 1.4 | screenshot |
| E5 | 1.5 | screenshot |
| E6 | 1.6 | screenshot |
| E7 | 1.6 | screenshot |
```

所有行为覆盖完毕 → 进入 Step 0c。

### Step 0c: 确定产物目录

从 plan.md 或 task_dir 推断 feat/refactor/fix 编号:

```bash
TASK_NAME=$(basename {task_dir})   # e.g., "feat-1", "refactor-2", "fix-3"
INTEGRATION_DIR="test/integration/$TASK_NAME"
mkdir -p {project}/$INTEGRATION_DIR
```

### Step 0d: 写入 .question 文件

对每条路径的每个确认步骤，编写 .question 文件。放在:

```
{project}/test/integration/{task_name}/path-{N}-{slug}/step-{M}-{slug}.question
```

**合并原则**: 同一步骤的截图能同时看到的确认点，合并到一个 .question。减少 visual-qa 调用次数。

.question 格式 (与 test-agent screenshot .question 一致):

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

### Step 0e: 写入 paths.md

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

**Hard Gate — paths.md 和所有 .question 文件写入完成后才能进入阶段 1。**

---

## 阶段 1: 启动游戏

### Step 1a: 读取协议参考 + 确认 MCP 工具可用

```
Read ${CLAUDE_PLUGIN_ROOT}/references/godot/
```

确认以下 MCP 工具组已激活 (gopeak 动态工具组):

- `testing` 组: `capture-screenshot`, `inject-action`, `inject-key`
- `runtime` 组: `inspect-runtime-tree`, `call-runtime-method`

如未激活，执行:
```
mcp__godot__tool-groups(action: "activate", group: "testing")
mcp__godot__tool-groups(action: "activate", group: "runtime")
```

### Step 1b: 启动 Godot 进程

```bash
GODOT=$(which godot 2>/dev/null || echo "/Applications/Godot.app/Contents/MacOS/Godot")
$GODOT --path {project} 2>&1 | tee {task_dir}/.work/integration-console.log &
GODOT_PID=$!
```

记录 GODOT_PID。

### Step 1c: 等待 MCP Runtime 就绪

用 MCP 工具轮询:

```
mcp__godot__runtime-status(projectPath: {project})
```

或直接试调 `mcp__godot__capture-screenshot`。成功 → 阶段 2。超时 15s → 报错停止，kill Godot 进程。

---

## 阶段 2: 逐路径执行

```
for 每条路径 (按 paths.md 顺序):
  ROUND = 0
  while ROUND < 5:
    ROUND++
    从该路径第一步开始执行
    
    for 每条步骤:
      
      1. 执行[操作] (使用 MCP 工具):
         - `mcp__godot__inject-action(action: "xxx", pressed: true/false)`
         - `mcp__godot__inject-key(keycode: "Enter", pressed: true/false)`
         - 等待: Bash `sleep N`
         具体参数从 paths.md 该步骤的"操作"和"等待"字段读取
      
      2. 等待游戏响应 (按步骤指定的等待时长)
      
      3. 控制台增量检查:
         START_LINE = wc -l < integration-console.log (本轮开始前记录)
         tail -n +$START_LINE integration-console.log | grep -iE '(ERROR|push_error|SCRIPT ERROR|CRITICAL)'
         
         → 有 ERROR: 立即进入阶段 3 诊断修复 (不继续后续步骤, 不调 visual-qa)
         → 有 WARNING: 记录到报告，继续
         → clean: 继续
      
      4. capture_screenshot:
         - 额外等待 0.5s (防角色闪烁)
         - `mcp__godot__capture-screenshot(width: 640, height: 360)`
         - 返回 base64 PNG → 解码保存到 {project}/test/integration/{task_name}/{screenshot 文件名}
      
      5. 截图预检:
         - file {png} | grep 'PNG image data' → PNG_OK / PNG_INVALID
         - identify -format "%[standard-deviation]" {png} → IS_BLANK (std < 0.02)
         
         → PNG_INVALID 或 BLANK: 标记 FAIL, 进入阶段 3
         → 通过: 继续
      
      6. 读该步骤的 .question 文件
      
      7. Skill("game-dev:visual-qa"):
         传入截图路径 + .question 内容
         → pass: 步骤通过 ✅ → 下一步
         → fail: 进入阶段 3
    
    全部步骤通过 → 路径通过 ✅ → 下一条路径
    有步骤失败 → 进入阶段 3 → 修复后重跑路径 (ROUND++)
  
  ROUND == 5 仍未通过 → 标记 BLOCKED, 跳过此路径继续下一条
```

**控制台增量检查实现:**

每轮执行前记录 `integration-console.log` 行数。步骤 3 只 grep 新增行。避免重复处理旧错误。

```bash
# 在路径开始前
CONSOLE_LINE=$(wc -l < {task_dir}/.work/integration-console.log)

# 每个步骤后
NEW_ERRORS=$(tail -n +$CONSOLE_LINE {task_dir}/.work/integration-console.log | grep -iE '(ERROR|push_error|SCRIPT ERROR)' || echo "")
# 更新基线
CONSOLE_LINE=$(wc -l < {task_dir}/.work/integration-console.log)
```

---

## 阶段 3: 诊断修复

步骤失败 (控制台 ERROR 或 visual-qa fail) 时触发。

### Step 3a: 收集失败上下文

- visual-qa 的 Answer + Visual Evidence (如果是 visual-qa fail)
- 新增的控制台错误行 (如果是控制台 ERROR)
- 该步骤的确认点 (requirements.md 对应行为条目)
- 当前场景树 (get_tree，用于理解游戏状态)

### Step 3b: 根因分析

调用 `Skill("game-dev:debug-root-cause")`:

将失败描述、预期行为、场景状态传入。debug-root-cause 产出 `{task_dir}/.work/debug-analysis.md`。

### Step 3c: 实施修复

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

**不自行修改代码。** spawn coding-agent 是唯一修复路径。

### Step 3d: 重跑路径

修复完成后，**从该路径第一步重新开始执行**。不等其他路径——立即重跑当前路径。

同一原因连续 3 轮仍失败 → 标记 BLOCKED，跳过此路径，继续下一条。

---

## 阶段 4: 停止游戏 + 报告

### Step 4a: 停止游戏

```bash
kill $GODOT_PID 2>/dev/null
# 确认进程退出
sleep 1
ps -p $GODOT_PID > /dev/null 2>&1 && kill -9 $GODOT_PID
```

### Step 4b: 写入报告

写入 `{task_dir}/.work/integration-test-report.md`:

```markdown
# 集成测试报告 — {task_name}

## 路径 1: {描述} ({N} 轮)
| 步骤 | 操作 | visual-qa | 控制台 | 结果 |
|------|------|-----------|--------|------|
| 1.1 | 等待标题 | ✅ PASS | ✅ | ✅ |
| 1.2 | ui_accept | ✅ PASS | ✅ | ✅ |
| 1.3 | 截图 | ✅ PASS | ✅ | ✅ |
| 1.4 | right+accept | ✅ PASS | ⚠️ WARNING: unused param | ✅ |
| 1.5 | right+jump | ✅ PASS | ✅ | ✅ |
| 1.6 | right+截图 | ✅ PASS | ✅ | ✅ |
| **路径结果** | | | | **✅ 通过** |

## 路径 2: {描述} (3 轮后阻塞)
| 2.1 | ... | ✅ PASS | ✅ | ✅ |
| 2.2 | shoot+截图 | ❌ FAIL: 刀光不可见 | ERROR: null texture | ❌ |
| ... | (第 3 轮仍 FAIL) | | | 🚫 BLOCKED |

## 汇总
- 路径通过: {N}/{M}
- 路径阻塞: {K}
- 总轮次: {R}
- 修复 spawn: {S} 次 coding-agent
- 控制台 WARNING: {W} 条

## 阻塞详情 (如有)
### 路径 {X} — 步骤 {Y}: {BLOCKED 原因}
- 根因: {debug-analysis.md 结论}
- 尝试: {N} 轮
- 建议: {需人工介入的原因}
```

### Step 4c: 输出完成摘要

```
## 集成测试完成 — {task_name}
- 路径: {N}/{M} 通过
- 阻塞: {K} ({BLOCKED 详情如有})
- 轮次: {R}
- 报告: {task_dir}/.work/integration-test-report.md
```

---

## 重试上限

- 每个路径 ≤ 5 轮
- 同一步骤同一原因 ≤ 3 轮 → BLOCKED
- 阻塞路径继续下一条路径，不互相阻塞

## Red Flags

| 中文 | English |
|------|---------|
| "控制台 WARNING 不影响功能，继续就行" | "Console warning doesn't matter, keep going" |
| "visual-qa 不太确定，但我觉得 PASS" | "visual-qa is unsure but I think it's PASS" |
| "同一个原因失败了，但不一定是代码问题" | "Same reason failed again, but maybe not a code issue" |
| "跳过预检直接调 visual-qa 更快" | "Skip pre-check, go straight to visual-qa" |
| "get_tree 也能验证，不用每步都截图" | "get_tree can verify, no need to screenshot every step" |
| "代码简单我自己修，不用 spawn coding-agent" | "The fix is simple, I'll do it myself without coding-agent" |

**以上任一条 → STOP。E2E 意味着每步截图验证。控制台 ERROR 必须修。修复必须走 coding-agent。**
