# game-dev - feat 链路诊断结果
## 日期：2026-07-11

### 链路拓扑

```
skills/orchestrator/SKILL.md (入口)
├── game-dev:artifact-manager → skills/artifact-manager/SKILL.md ✓
├── game-dev:design-ui → skills/design-ui/SKILL.md ✓ (本次未触发，无UI)
├── game-dev:concept-art → skills/concept-art/SKILL.md ✓ (本次未触发，纯逻辑)
├── game-dev:asset-extract → skills/asset-extract/SKILL.md ✓ (本次未触发)
├── game-dev:plan → skills/plan/SKILL.md ✓
│   ├── references/plan-format.md ✓
│   ├── references/visual-spec-format.md (本次未触发，无visual任务)
│   ├── references/godot/config.md ✓
│   └── references/godot/patterns.md (存在但非诊断关键)
├── game-dev:art-resources-conductor → skills/art-resources-conductor/SKILL.md ✓ (本次跳过，无资源)
├── game-dev:exec → skills/exec/SKILL.md ✓
│   ├── skills/exec/references/exec-prompts.md ✓ (经路径解析验证)
│   ├── skills/exec/references/exec-logging.md ✓ (经路径解析验证)
│   ├── agents/coding.md ✓
│   ├── agents/test-agent.md ✓
│   └── references/godot/config.md ✓
├── game-dev:architecture → skills/architecture/SKILL.md (阶段5b，未执行到)
├── game-dev:collect-lessons → skills/collect-lessons/SKILL.md (未执行到)
└── game-dev:write-tutorial → skills/write-tutorial/SKILL.md (未执行到)
```

### 逐步骤诊断

| # | 所属节点 | 应有步骤 | 要求(来自plugin文件) | 实际步骤(来自log) | 达标? | 达标证据 / 不达标点 |
|---|---------|---------|---------------------|------------------|-------|-------------------|
| 1 | skills/orchestrator/SKILL.md (L41-47) | 正常模式：plan后等待审查 | "**正常模式（默认）** plan → 输出设计文档 → 等待用户审查 ├── 用户批准 → 自动进入 exec └── 用户拒绝 → 修改 plan，重新提交" | plan.md 于 15:50 生成（产物时间戳），exec 的第一个子 agent 在 07:57:43Z（≈15:57 CST）被 spawn——plan 完成后约 7 分钟即进入 exec，中间无任何 AskUserQuestion 或用户确认交互 | ❌ | 未检测到任何暂停/等待审查的机制执行。第一个 spawn 的 agent（agent-aac33a5ebc354ed9d）元数据显示 `attributionSkill: "game-dev:exec"`，确认 exec 已启动。orchestrator 描述了"等待用户审查"但没有实现机制来强制执行此暂停。 |
| 2 | skills/orchestrator/SKILL.md (L39-54) | --auto 模式检测 | "### 全自动模式（`--auto`）plan → 直接进入 exec → 完成" — 区分两种模式的关键是检测 `--auto` flag | 未传递 `--auto` 参数（用户确认未加），但行为等同于全自动模式 | ❌ | orchestrator 的"两种模式"描述了概念差异但**没有实现 --auto 检测/传递机制**。整个 SKILL.md 中没有任何 `if --auto then else` 逻辑、没有 flag 解析步骤、没有将 mode 传给下游的规则。模式区分仅存在于描述性文字中，不存在于执行逻辑中。 |
| 3 | skills/orchestrator/SKILL.md (L95-103) | 阶段1：创建任务目录 | "Skill({skill: "game-dev:artifact-manager", args: "--task-dir {dev_dir}/{kind}-{N} --kind feat --dev-dir {dev_dir}"})" + "返回 `task_dir`" | artifact-manager 被调用，task_dir 被设为 `.godot-dev/feat-6`。progress.json 记录 `"task_dir": ".godot-dev/feat-6"`（相对路径） | ⚠️ | 风险：orchestrator 向 artifact-manager 传入 `--task-dir {dev_dir}/{kind}-{N}` 参数，但 artifact-manager SKILL.md (L16-18) 只声明了入参 `--kind` 和 `--dev-dir`，**未声明 `--task-dir`**。未使用的多余参数可能造成混淆。此外 task_dir 被存储为相对路径（`.godot-dev/feat-6`），是后续嵌套目录问题的上游因素。 |
| 4 | skills/orchestrator/SKILL.md (L146-156) | 阶段3：Plan 设计阶段 | "**正常模式：** 暂停，等待用户审查 plan.md。**全自动模式：** 直接进入阶段 4。" | plan.md 生成后 orchestrator 直接进入 exec 阶段，无暂停。 | ❌ | 见 #1 — 无暂停机制。plan 阶段（L146-156）只是描述了"暂停，等待"，但没有 AskUserQuestion / "停止并等待用户输入"的指令。对 LLM 而言，"暂停"一词不是可执行的操作。 |
| 5 | skills/plan/SKILL.md (L161-235) | 步骤6：任务拆分与排序 | 8 条独立约束（来自好/坏对照 + 描述写作规则表），逐一验证如下 | 产出的 plan.md 有 6 个 AI 任务 (AI-1 ~ AI-6) | — | 见下行展开 |
| 5a | skills/plan/SKILL.md (L177-178) | 步骤6：不含 class 名 | "❌ 坏: 'QteController 状态对象 + 状态常量定义（class QteController + class QtePhase）'" | plan.md AI-2: "一个无视觉无碰撞的 Node3D" — 含引擎类型名 | ❌ | "Node3D" 是 Godot 引擎类型名，出现在任务描述中。违反了"不含代码符号"规则。 |
| 5b | skills/plan/SKILL.md (L175-176) | 步骤6：不含方法名 | "❌ 坏: '在脚本文件中添加 select_character 入口函数'" | plan.md AI-3: "实例化"、"emit died 信号"等概念性描述，未出现方法名 | ✅ | AI-3 描述以行为语言为主。但见 5k。 |
| 5c | skills/plan/SKILL.md (L214) | 步骤6：用行为语言 | "描述'用户做什么 → 看到什么/发生什么'，不用技术名词开头" | plan.md AI-1: "用一个独立资源类型定义..." — 以技术名词开头 | ❌ | AI-1 以"实现刷新点的数据描述层"开头，随后用"用一个独立资源类型定义"——这是技术方案描述而非玩家可感知的行为。"Inspector 可编辑,关卡 designer 通过选文件即可配置" 勉强描述了设计者行为，但不是玩家行为。 |
| 5d | skills/plan/SKILL.md (L215) | 步骤6：可独立验证 | "读完描述能回答'怎么确认这个任务做完了？'" | plan.md AI-1: 需要确认 3 个 Resource 类的字段完整性 | ⚠️ | AI-1 的验证依赖"读代码确认字段存在"，这在 TDD 循环中通过 test-agent 的 RED 测试来实现（test_spawn_point_data.gd 的 16 个 testcase）。但 plan.md 中没有为 AI-1 明确区分"数据 schema 测试在 AI-1 TDD 中自然产出"这一事实。 |
| 5e | skills/plan/SKILL.md (L216) | 步骤6：不含文件路径 | "文件名不出现在描述中" | 逐一检查 6 个 AI 任务 | ✅ | AI-1~AI-6 的 `[AI-N]` 行均未包含 `.gd`、`.tscn`、`.tres` 等文件路径。 |
| 5f | skills/plan/SKILL.md (L217) | 步骤6：不含代码符号 | "class 名、方法名、函数名、动画名不出现在描述中" | AI-2 含 "Node3D"，AI-1 含 "Inspector" | ❌ | "Node3D" 出现在 AI-2 描述中（见 5a）。"Inspector" 虽非代码符号但暗示编辑器操作。 |
| 5g | skills/plan/SKILL.md (L218) | 步骤6：不含"测试" | "没有'编写/更新测试'任务——测试在各模块的 TDD 循环中自然产出" | plan.md AI-6: "编写通用性回归测试,覆盖刷新点数据 schema 完整性、单刷新点单波/多波推进..." | ❌ | AI-6 明确以"编写通用性回归测试"开头，是将测试作为独立 AI 任务。这直接违反了 plan 自身的核心规则："不含'测试'"、"测试在各模块的 TDD 循环中自然产出"。如果在 AI-1~AI-5 的 TDD 循环中 test-agent 已编写了这些测试，AI-6 将没有新测试可写——或者更糟，它会重复编写已有测试。 |
| 5h | skills/plan/SKILL.md (L219) | 步骤6：类型标注 | "每个任务必须标注类型——logic / visual / ui" | 6 个任务均标注为 `(type: logic)` | ✅ | 类型标注完整。 |
| 5i | skills/plan/SKILL.md (L98) | 步骤6：单一类型 | "每个 task 只能是单一类型。logic / visual / ui 不允许合并" | 6 个任务均为 logic 类型 | ✅ | 类型未合并。 |
| 5j | skills/plan/SKILL.md (L227-235) | 步骤6：分类判定 | "对行为清单逐条判定" → logic/visual/ui 分类 | 行为清单有 7 条行为。任务列表有 6 个任务。AI-5 "在主场景实例化若干刷新点,绑定不同的刷新点配置,验证关卡 designer 通过选文件即可配置" 未对应任何行为清单中的具体行为 | ❌ | AI-5 是"集成验证"任务，实际内容是行为 7（新增刷新点 = .tres + 放节点）的集成场景展开。但行为 7 已在 AI-1（数据层）+ AI-2（节点层）中覆盖。AI-5 作为独立任务存在冗余。AI-6 更是纯测试任务（见 5g），不在行为清单中。 |
| 5k | skills/plan/SKILL.md (L230-235) | 步骤6：判定辅助信号词 | "计算、判定、存储、传递" → logic | AI-3 "实例化该轮所有敌人" + AI-4 "接入现有敌人系统" 中的 "实例化" 和 "接入" 是行为词 | ⚠️ | AI-3 和 AI-4 的拆分边界模糊。行为清单中行为 1-5（刷新点生命周期）在 AI-3 中实现，但 AI-4（接入现有敌人系统）本质上是 AI-3 的一部分——"实例化出的敌人自动接入 targets 组"本可以在 AI-3 的状态机流程中一起实现。拆分为两个任务增加了不必要的依赖链。 |
| 6 | skills/exec/SKILL.md (L68-76) | exec 步骤1：定位任务目录 | "从 args 解析 `--task-dir` 和 `--mode`" + "dev_dir 从 config.md 读取" | task_dir 被解析为 `.godot-dev/feat-6`（相对路径）。progress.json 存储了此相对路径。 | ⚠️ | 风险：exec 使用相对路径作为 task_dir 是后续嵌套目录问题的前提条件。exec 没有将相对路径解析为绝对路径的步骤。 |
| 7 | skills/exec/SKILL.md (L156-161) | exec 步骤6a：创建 coding 日志目录 | "mkdir -p {task_dir}/.work/coding" — 使用 `{task_dir}` 变量 | 目录创建发生了两次：正确位置 `.godot-dev/feat-6/.work/coding/` 存在，嵌套位置 `.godot-dev/feat-6/.godot-dev/feat-6/.work/coding/` 也存在 | ❌ | 嵌套目录 `.godot-dev/feat-6/.godot-dev/feat-6/.work/` 包含了部分 tdd-iterations.md 内容和 coding/ 子目录。这些是由 exec 的日志写入步骤创建的（tdd 文件头 + RED/GREEN/VERIFY 摘要）。最可能的根因：exec 在写入日志时，其 shell 的 CWD 被设置为 task_dir（`.godot-dev/feat-6/`），此时 `{task_dir}/.work/...` 如果被解释为相对路径拼接 `.godot-dev/feat-6/.work/...`，则解析为 `.godot-dev/feat-6/.godot-dev/feat-6/.work/...`。 |
| 8 | skills/exec/SKILL.md (L126-142) | exec 步骤"回显确认" | "exec 初始化确认 — exec-prompts.md: ...已加载 / {tech}/config.md: ... / {tech}/coding.md: ..." | tdd-iterations.md 无 exec 初始化确认回显 | ⚠️ | 风险：exec 要求回显确认后再进入 TDD 循环，但产物中没有 exec 初始化确认的记录。无法验证是否真的执行了此步骤。 |
| 9 | skills/exec/SKILL.md (L100-115) | exec 步骤5：信息隔离清单 | "从 game-dev:test-agent → game-dev:coding 可以传：行为级失败描述 + 具体失败 testcase 名称和错误信息、设计文档路径。禁止传：测试源码、测试文件路径" | 第一个 RED agent 的 spawn prompt 中含有完整的 RED 报告，传给了 GREEN agent | ✅ | exec-prompts.md GREEN 模板 (L89-98) 使用 testsuite 名称和 testcase 名称列表——不含测试源码。实际日志中 coding agent 的 GREEN 报告引用了 "test_spawn_point_data 16 testcases" 而不含测试代码，符合隔离规则。 |
| 10 | skills/exec/SKILL.md (L220-256) | exec 步骤6e：边界检查 | "对每个任务强制执行" + 检测 "测试文件隔离"、"空代码/假代码"、"技术栈专属" | tdd-iterations.md 中 Iter 4 和 Iter 9 有 BOUNDARY-CHECK 条目 | ✅ | AI-1 的边界检查 (Iter 4) 和 AI-2 的边界检查 (Iter 9) 均存在且格式正确，包含测试文件隔离、空代码/假代码、技术栈专属三项检查。 |
| 11 | skills/exec/SKILL.md (L268-288) | exec 步骤6f：REFACTOR 触发判定 | "边界检查有违规 → 必须 REFACTOR; GREEN 修改 >1 个文件 → 必须 REFACTOR; GREEN >1 轮自我验证 → 必须 REFACTOR" | AI-1 触发 REFACTOR（3 个文件修改），AI-2 触发 REFACTOR（2 个文件修改） | ✅ | AI-1 和 AI-2 的 REFACTOR 判定在 tdd-iterations.md 中均有记录，触发逻辑符合规则。 |
| 12 | skills/exec/SKILL.md (L303-309) | exec 步骤9：收集开发经验 | "调用 `game-dev:collect-lessons` skill" | AI-3 状态为 in_progress，exec 未完成全部任务 | ⏭️ 不在范围 | 会话中断在 AI-3 in_progress，步骤 9 尚未执行到。属于正常中断，不是插件问题。 |
| 13 | skills/artifact-manager/SKILL.md (L16-18) | artifact-manager 入参定义 | "--kind feat --dev-dir .godot-dev" — 只有两个参数 | orchestrator (L98) 传入了三个参数: "--task-dir {dev_dir}/{kind}-{N} --kind feat --dev-dir {dev_dir}" | ⚠️ | `--task-dir` 不在 artifact-manager 声明的入参列表中（只声明了 `--kind` 和 `--dev-dir`）。多余的参数可能被忽略但也可能造成混淆。orchestrator 和 artifact-manager 的接口约定不一致。 |

### 根因分析与解决方案

| # | 应有步骤 | 达标? | 根因 | 解决方案 | 解决方案来源 |
|---|---------|-------|------|---------|-------------|
| 1 | 正常模式：plan后等待审查 | ❌ | **缺失执行机制**：orchestrator 用描述性文字定义了"等待用户审查"的行为，但没有对应的可执行机制（无 `AskUserQuestion` 调用、无 "停止输出并等待用户回复" 的显式指令）。对于 LLM agent，"暂停，等待"不是可执行操作——它需要一个具体的工具调用或明确的"不要继续下一阶段"约束来阻止继续执行。对比 exec 中的 Red Flags 和硬门机制（这些是有 grep/checklist 等可执行验证的），orchestrator 的模式切换完全是纯文本描述。 | 在 orchestrator 的阶段 3（plan 输出后）和阶段 2b（concept-art 输出后）增加显式的模式检查步骤。具体：1) 从 args 解析 `--auto` flag；2) 正常模式下，在 plan 输出摘要后调用 `AskUserQuestion` 询问 "审查 plan.md 后是否继续？"；3) 全自动模式下跳过 AskUserQuestion 直接进入下一阶段。 | `references/harness-methodology.md` M1 (Hard Gate) — 关键质量门必须有可执行的验证步骤而非文字描述。 |
| 2 | --auto 模式检测 | ❌ | **flag 解析缺失**：orchestrator 没有在任何步骤中解析 `--auto` 参数。阶段 0（检测技术栈）后没有 "解析运行模式" 步骤。"两种模式"的描述（L39-54）之后直接进入阶段执行步骤，模式的差异（等待 vs 自动）在步骤中完全没有体现。 | 在 orchestrator 阶段 0 和阶段 1 之间增加 "阶段 0e：解析运行模式"。从 `--auto` args 解析 mode，存储为变量传递给所有下游阶段的决策点。 | `references/skill-structure.md` — skill 的"执行步骤"必须是可操作的指令。"描述性概念"需要配套"执行机制"。 |
| 3 | 阶段1：创建任务目录 | ⚠️ | **接口不一致**：orchestrator 向 artifact-manager 传入 `--task-dir` 参数，但 artifact-manager 未声明此参数。这说明两个文件的接口约定不同步。虽然当前未造成错误（多余参数被忽略），但表明跨文件的参数传递缺乏统一规范。 | 1) 统一 orchestrator 和 artifact-manager 的参数约定：要么 artifact-manager 增加 `--task-dir` 入参声明，要么 orchestrator 停止传递此参数。2) 要求 artifact-manager 返回的 `task_dir` 必须是**绝对路径**（或由 orchestrator 在接收后解析为绝对路径）。 | `references/skill-structure.md` — skill 间接口约定应当明确且一致。 |
| 4 | 阶段3：Plan等待审查 | ❌ | 同 #1，#2。orchestrator 没有将 mode 传递给 plan 阶段或在 plan 后执行 mode 检查。 | 同 #1 方案。 | 同 #1。 |
| 5a | 步骤6：不含 class 名 | ❌ | **规则执行不足**：plan 在步骤 10 "格式自检"中要求用 grep 扫描 PascalCase 标识符。AI-2 中的 "Node3D" 是 Godot 引擎类型名——grep 命令（`grep -nP '\[AI-\d+\].*\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b'`）应该能匹配到。说明格式自检步骤未被严格执行或 grep 未命中（"Node3D" 的模式是 `[A-Z][a-z]+[0-9][A-Z]`，数字 "3" 打断了 PascalCase 检测正则）。 | 增强 plan 步骤 10 的禁止内容清单：在 PascalCase 检测正则中增加对 "数字+大写字母" 模式的支持（如 `\b[A-Z][a-z]+[0-9]*[A-Z][a-z]*\b`），或单独增加 Godot 引擎类型名的 grep 检查（`grep -nPi '\[AI-\d+\].*\b(Node3D|Node2D|MeshInstance3D|...)' `）。 | `references/plan-format.md` L293 — 禁止内容清单的 grep 命令需要覆盖引擎类型名模式。 |
| 5c | 步骤6：用行为语言 | ❌ | **规则表达不足**：plan 的"好/坏对照"和"描述写作规则"表提供了判断标准，但没有提供将技术需求转化为行为语言的系统方法。当任务涉及纯逻辑层（数据 schema、状态机）时，"玩家可感知的行为"较少，plan 难以找到行为锚点——于是退回到技术描述。AI-1 描述的是数据 schema 设计（3 个 Resource 的字段定义），这确实是需要做的事情，但 plan 没有提供"纯逻辑任务如何用行为语言描述"的范例。 | 在 plan 的好/坏对照表中增加纯逻辑任务的范例。例如：将 "定义 SpawnPointData Resource" 转化为 "刷新点配置文件的字段定义：designer 可以在编辑器中通过下拉菜单和数字输入框配置波次序列、每种敌人的数量——无需打开脚本文件"。 | `skills/plan/SKILL.md` L167-210 的好/坏对照表。 |
| 5g | 步骤6：不含"测试" | ❌ | **规则检测缺失**：plan 步骤 10 的禁止内容清单（plan-format.md L256-260）grep 扫描的是 "lint 代替测试"、"人工启动目视"、"测试缺失不阻塞" 等特定短语——**没有扫描任务描述本身是否以"测试"/"编写测试"开头**。AI-6 的任务描述以 "编写通用性回归测试" 开头——这是一个明确的以测试为独立 AI 任务的描述，但格式自检的 grep 命令不覆盖此模式。 | 在 plan-format.md 禁止内容清单中增加 grep 命令：`grep -nP '\[AI-\d+\].*\b(编写.*测试|.*回归测试|.*单元测试|.*集成测试)\b' {task_dir}/plan.md`。同时让此规则更显眼——在 plan SKILL.md 步骤 6 的好/坏对照表中增加一个 ❌ 示例："❌ 坏: '编写通用性回归测试,覆盖...'"。 | `references/plan-format.md` L237-301 禁止内容清单。 |
| 5j | 步骤6：分类判定 | ❌ | **行为清单→任务映射不严格**：plan 的步骤 6 要求"对行为清单逐条判定"后拆分任务，但实际执行中 AI-5 和 AI-6 不是从行为清单生成的——它们是"数据驱动契约验证"和"回归测试"概念被直接映射为独立 AI 任务。行为清单有 7 条，理想的任务拆分应该是 3-4 个递进的任务（数据层 → 节点层 → 状态机+集成），但实际拆分出了 6 个任务，其中 2 个（AI-5, AI-6）是验证/测试性质的。根因是 plan 缺少 "AI 任务必须严格来源于行为清单" 的硬约束。 | 在 plan SKILL.md 步骤 6 增加硬约束："每个 AI 任务必须能追溯到行为清单中的至少一条行为。无法追溯的任务 → 要么合入上游任务，要么删除。任务列表 = 行为清单的映射，不是行为清单的超集。" | `skills/plan/SKILL.md` L225-235 分类判定流程。 |
| 7 | exec：创建 coding 日志目录 | ❌ | **相对路径 + CWD 漂移**：两层问题。(1) `progress.json` 存储 task_dir 为相对路径 `.godot-dev/feat-6`；(2) 子 agent spawn 时 CWD 被设为 task_dir 本身（从 agent JSONL `"cwd":"D:\\project\\godot\\zombies-demo\\.godot-dev\\feat-6"` 证实）。当 exec 在日志写入时，如果 shell 命令使用相对 task_dir 且在 CWD=task_dir 的上下文中执行，路径会解析为嵌套的 `.godot-dev/feat-6/.godot-dev/feat-6/.work/...`。exec SKILL.md 没有"将 task_dir 解析为绝对路径"的步骤，也没有"检查 CWD 是否与 task_dir 一致"的安全检查。 | 三管齐下：1) exec 步骤 1 增加 task_dir 绝对化：`task_dir=$(realpath {task_dir})` 或将 args 中的相对路径转为绝对路径后再使用；2) exec 步骤 6a 在写入日志前验证目标路径不在 task_dir 内部嵌套了 dev_dir 结构；3) artifact-manager 返回绝对路径而非相对路径。 | `references/harness-methodology.md` M3 (Path Safety) — 所有路径变量在使用前必须绝对化。 |
| 9 | exec：信息隔离 | ✅ | 隔离规则执行正确。 | 无需修复。 | — |
| 13 | artifact-manager 入参 | ⚠️ | 接口定义不统一。参见 #3。 | 同 #3。 | 同 #3。 |
