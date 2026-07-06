# game-dev - feat 诊断结果
## 日期：2026-07-06

### 链路拓扑

```
commands/start.md → game-dev:orchestrator (skills/orchestrator/SKILL.md)
├── game-dev:artifact-manager (skills/artifact-manager/SKILL.md)
├── game-dev:plan (skills/plan/SKILL.md)
│   ├── references/plan-format.md
│   ├── references/godot/config.md
│   ├── references/godot/docs.md
│   ├── references/godot/patterns.md
│   ├── references/godot/coding.md
│   ├── references/godot/design.md
│   ├── references/godot/nodes-3d.md
│   └── (design-resources-3d.md — 仅在生成资源时引用)
├── [design-ui — 3D 游戏玩法任务，跳过]
├── [art-resources-conductor — 无新资源需求(Zombie_Basic.gltf 已有)，跳过]
└── game-dev:exec (skills/exec/SKILL.md)
    ├── skills/exec/references/exec-prompts.md
    ├── skills/exec/references/exec-logging.md
    ├── references/plan-format.md
    ├── references/godot/config.md
    ├── references/godot/coding.md
    ├── game-dev:test-agent (agents/test-agent.md)
    │   └── references/godot/testing.md
    └── game-dev:coding (agents/coding.md)
        └── references/godot/style-guide.md, project-organization.md, coding.md
```

执行日志来源：`/mnt/c/Users/joker/.claude/projects/D--project-godot-zombies-demo/ef125979-9fc4-43bb-acd9-fcb25b25020c/subagents/`（27 个 agent spawn）
产物目录：`/mnt/d/project/godot/zombies-demo/.godot-dev/feat-3/`

### 逐步骤诊断

| # | 所属节点 | 应有步骤 | 要求(来自plugin文件) | 实际步骤(来自log) | 达标? | 达标证据 / 不达标点 |
|---|---------|---------|---------------------|------------------|-------|-------------------|
| 1 | skills/orchestrator/SKILL.md | 阶段 0b: 读 config 获取 dev_dir | "读 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md` 的 `## 产物目录` 节。提取 `dev_dir` 值。回显确认后才能调用 artifact-manager"（L173-187） | orchestrator 正确检测 godot 技术栈，产物目录 `.godot-dev/feat-3/` 已创建 | ✅ | 产物目录 `.godot-dev/feat-3/` 存在，结构符合 config.md 声明 |
| 2 | skills/orchestrator/SKILL.md | 阶段 1: 创建任务目录 | "调用 `Skill({skill: "game-dev:artifact-manager", args: "--task-dir {dev_dir}/{kind}-{N} --kind feat --dev-dir {dev_dir}"})`"（L198-200） | feat-3 目录已创建，progress.json 计数器正确 | ✅ | `feat-3/progress.json` 存在，current_state.json 中 feat 计数器递增至 3 |
| 3 | skills/orchestrator/SKILL.md | 阶段 2: UI 检测 | "只对 Control UI 场景触发…涉及 2D 关卡、3D 世界、物理、游戏玩法逻辑 → 跳过"（L210-213） | 3D 僵尸敌人任务，正确跳过 design-ui | ✅ | 无 `.work/layouts/` 目录，无 style-decision.md，符合"跳过"声明 |
| 4 | skills/orchestrator/SKILL.md | 阶段 3: Plan | "`Skill({skill: "game-dev:plan", args: "--task-dir {task_dir}"})`"（L231-232） | plan.md 已生成，包含完整的领域模型、行为列表、任务列表、测试策略 | ✅ | `feat-3/plan.md` 存在（8296 bytes），8 个 AI 任务完整，领域模型含状态机边界，行为列表 10 条 |
| 5 | skills/orchestrator/SKILL.md | 阶段 4: 资源检测 | "当 `{task_dir}/.work/resources.md` 存在且包含未处理的资源条目时触发"（L243） | `resources.md` 存在但内容为"无新资源"，正确跳过 art-resources-conductor | ✅ | `.work/resources.md` 存在，内容声明"无新资源。Zombie_Basic.gltf 含 6 段目标动画"，跳过资源生成 |
| 6 | skills/orchestrator/SKILL.md | 阶段 5: Exec | "`Skill({skill: "game-dev:exec", args: "--mode feat --task-dir {task_dir}"})`"（L255） | exec 执行了 AI-0 到 AI-7 共 8 个任务的 TDD 循环，27 个 agent spawn（RED+GREEN+VERIFY+REFACTOR） | ✅ | progress.json 全部 done，98/98 测试通过，tdd-iterations.md 完整记录循环 |
| 7 | skills/plan/SKILL.md | 步骤 5: 行为确认 | "确认行为清单（强制门）：从需求中提取玩家可见的行为列表，向用户确认"（L166-170） | plan.md 的行为列表含 10 条玩家可见行为 | ⚠️ | 行为列表存在且内容正确，但 log 中未见"向用户确认"步骤的直接证据。log 中的 agent spawn 从 AI-0 直接开始，未显示用户确认环节。风险：`--auto` 模式跳过了确认。 |
| 8 | skills/plan/SKILL.md | 步骤 6: 任务描述不含 class 名 | "class 名不出现在任务描述中"（来自 ❌ 例1, L160-161） | plan.md AI-1: "实现僵尸数据 Resource schema：数值字段、动画表、character_scene / animation_player_path 引用字段" — "Resource schema" 不是 class 名，但 `character_scene` / `animation_player_path` 是字段名 | ✅ | 整体符合。AI-1~AI-7 任务描述未出现 `ZombieData`、`ZombieBase`、`ZombieBasic` 等 class 名。字段名出现在 AI-1 是描述数据 schema 的必要内容。 |
| 9 | skills/plan/SKILL.md | 步骤 6: 任务描述不含方法名 | "方法名/函数名不出现在任务描述中"（来自 ❌ 例2, L163-164） | 扫描 plan.md 任务列表，未发现方法名/函数名 | ✅ | grep 检查确认：`[AI-N]` 描述中未出现 `_transition_to`、`take_damage`、`play_animation` 等方法名 |
| 10 | skills/plan/SKILL.md | 步骤 6: 任务描述用行为语言 | "描述 = 可验证的功能行为，用户操作后能看到什么"（来自 ✅ 例1, L172-173） | AI-1 "实现僵尸数据 Resource schema" — 偏技术描述。AI-5 "实现攻击命中管线：ATTACK 状态下 _attack_timer 倒计时，归零时通过现有 combat 工具对玩家应用伤害" — 含状态名和技术细节 | ⚠️ | AI-1 描述偏技术实现（"schema"、"字段"），验证方式是"字段存在且可读写"而非玩家可感知行为。AI-5 含 `_attack_timer`（私有变量名）和 `ATTACK`（状态名）。风险：这可能导致 test-agent 将测试聚焦在字段存在性而非行为。但 log 显示 test-agent 最终覆盖了行为（如 AI-5 的 12 个 testcase 测试了攻击伤害、冷却、状态约束），未造成实际损害。 |
| 11 | skills/plan/SKILL.md | 步骤 6: 交互描述含反馈 | "交互描述必须包含视觉/状态反馈"（来自 ✅ 例2, L175-176） | 行为列表含状态信号 + visual 验证方式 | ✅ | 行为列表每条有"验证方式"列（状态信号 / visual），如"状态信号 + visual: 接近动画"、"僵尸 died 信号 + scene 移除" |
| 12 | skills/plan/SKILL.md | 步骤 6: 任务描述不含引擎类型名 | 描述不含引擎特定类型名（来自好/坏对照隐含约束） | AI-1 含 `character_scene`（PackedScene 类型暗示）、AI-2 含"状态枚举、状态机" | ⚠️ | plan-format.md 禁止"代码级 API 调用（引擎特定 API、`scope[`、`assert len(` 等）"，但 plan.md 任务描述中未出现 API 调用。`character_scene` 是 domain term（不是 API），风险较低。 |
| 13 | skills/plan/SKILL.md | 步骤 9/10: 格式自检 | "输出前对照 plan-format.md 的'格式校验清单'逐项确认，然后执行'禁止内容清单'中的所有 grep 命令"（L322） | plan.md 通过了大部分格式校验：有概述、领域模型、行为列表、设计摘要、影响范围、任务列表、测试策略 | ⚠️ | 无法从 log 确认 plan 阶段执行了 "禁止内容清单中的所有 grep 命令"。log 中 plan 阶段发生在 exec 之前，agent 日志不包含 plan 阶段的 grep 输出。但 plan.md 内容未见禁止短语（"lint 代替测试"、"人工验证"等），推测自动检查通过。 |
| 14 | skills/exec/SKILL.md | 步骤 4: 确认测试环境 | "硬门：测试运行器必须可用。测试目录必须存在。已知坑必须处理。"（L189-190） | AI-0 RED agent 创建了 GUT smoke test 并确认可运行。但 config.md 的"已知坑"中未提及 GUT 默认将 engine error 视为 test failure 的问题 | ❌ | config.md 已知坑列出 3 条（-gexit 必须存在、headless 无 DisplayServer、assert_not_null($NodeName) 行为不确定），但未列出"GUT 默认 treat_engine_errors_as = FAILURE"。这导致 AI-2 GREEN 阶段需要创建 `.gutconfig.json` 才能通过 11 个因 `_make_mock_player` 中 `global_position = pos` before `add_child` 而失败的测试。config.md 已知坑不完整。 |
| 15 | skills/exec/SKILL.md | 步骤 6b: RED spawn | "使用 `references/exec-prompts.md` 的 RED prompt 模板组装 spawn prompt"（L247） | 8 个 RED agent 被 spawn（AI-0 到 AI-7），每个对应 plan.md 中的一个 AI 任务 | ✅ | agent meta.json 显示 8 个 RED agent spawn，测试文件已创建且所有 testcase 在 RED 阶段失败 |
| 16 | skills/exec/SKILL.md | 步骤 6b: RED 检查 | "exec 检查 RED 结果：测试文件已创建、RED report 中所有 testcase 都失败了且原因正确、没有 mock/假代码"（exec-prompts.md L47-49） | AI-2 RED agent 返回 test_zombie_base.gd（24 testcases），其中 11 个因 engine error 失败（非行为原因）。exec 接受了这个结果并进入 GREEN | ⚠️ | exec-prompts.md 要求"失败原因正确"。AI-2 RED 中 11 个 testcase 失败原因是 `!is_inside_tree()` engine error（测试写法问题），不是"功能未实现"。严格来说这不是"正确的 RED 失败"。exec 接受了它，因为 assertion 本身确实会失败。风险：边界模糊——engine error 失败算不算"原因正确"没有明确规则。 |
| 17 | skills/exec/SKILL.md | 步骤 6c: GREEN spawn | "使用 GREEN prompt 模板。从 test-agent 的 RED report 提取 testsuite 名称和 testcase 名称。"（L256-257） | 8 个 GREEN agent spawn，各自实现了对应任务 | ✅ | agent meta.json 显示 AI-1~AI-7 各有 GREEN agent。tdd-iterations.md 记录了每个 GREEN 阶段的 testcase 结果和修复过程 |
| 18 | skills/exec/SKILL.md | 步骤 6c: GREEN 检查 | "coding-agent 自验证报告显示目标 testsuite 全部通过、未修改 game/tests/ 下文件、无 pass / TODO / NotImplemented 残留"（exec-prompts.md L102-105） | AI-2 GREEN 因 `test_zombie_base_is_abstract` 无法通过（Godot 4.7 framework 限制）。AI-4 GREEN 首次失败（UID collision），redo 后通过 | ❌ | AI-2 GREEN 最终 23/24 通过，`test_zombie_base_is_abstract` 永久无法通过。exec-prompts.md 要求"目标 testsuite 全部通过"，未达到。exec 接受了 23/24 + 解释。这暴露了"framework 限制导致无法通过的测试"缺乏处理流程。另：AI-6 GREEN 后 VERIFY agent 发现 anti-pattern（`play_animation()` 中 lazy-register AnimationLibrary 的 dead branch），触发了额外的 REFACTOR。 |
| 19 | skills/exec/SKILL.md | 步骤 6d: VERIFY spawn | "使用 VERIFY prompt。检查结果：全量测试全部通过"（exec-prompts.md L132-134） | AI-3~AI-7 各有 VERIFY agent | ✅ | tdd-iterations.md 记录 VERIFY 全部通过。AI-6 VERIFY 发现 anti-pattern 并触发 REFACTOR |
| 20 | skills/exec/SKILL.md | 步骤 6e: 边界检查 | "通用检查：测试文件隔离(coding agent 是否修改了测试文件?)、空代码/假代码(是否有 pass/TODO/NotImplemented 残留?)"（L280-283） | tdd-iterations.md 中 REFACTOR 阶段记录了边界检查（grep pass/TODO/NotImplemented/print），0 命中（非 abstract stub 的合法 pass） | ⚠️ | 检查了 pass/TODO/NotImplemented，但未检查测试文件质量——`_make_mock_player` 在 `add_child` 前调 `global_position = pos` 导致 engine error（见 test log L31-40）。这是测试代码质量问题，exec 的边界检查未覆盖。风险：当前通过 `.gutconfig.json` 绕过，但 engine error 可能掩盖真正的测试问题。 |
| 21 | skills/exec/SKILL.md | 步骤 6f: REFACTOR | "使用 REFACTOR prompt + 边界违规清单（如有）"（L312） | AI-5 和 AI-6 有 REFACTOR agent spawn | ✅ | AI-5 REFACTOR 抽取 `_tick_attack_cooldown` helper，98/98 通过。AI-6 REFACTOR 清理 anti-pattern（AnimationLibrary lazy-register dead branch），106/106 通过 |
| 22 | skills/exec/SKILL.md | 步骤 8: 最终验证 | "从 config.md 读取 test_cmd_full 并执行。验证全部通过。"（L340） | 全量测试执行：98/98 passed, 6 scripts, 162 asserts (tool-results/brjhgjy2s.txt L616-624) | ✅ | 测试输出确认 98/98 passed，0 failures。All tests passed! |
| 23 | skills/exec/SKILL.md | 步骤 9: 收集开发经验 | "调用 `game-dev:collect-lessons` skill，传入 tech：`Skill("game-dev:collect-lessons", "tech={tech}")`"（L344-346） | collect-lessons 被执行，`test-lessons.md` 和 `coding-lessons.md` 均已写入 `.godot-dev/` 目录，`.work/collect-lessons-summary.md` 为额外汇总产物 | ✅ | `.godot-dev/test-lessons.md` 存在（3 条经验），`.godot-dev/coding-lessons.md` 存在（5 条经验），均符合 collect-lessons/SKILL.md 步骤 7 的声明路径。`.work/collect-lessons-summary.md` 是额外汇总，CLAUDE.md 也已更新（6 条一行摘要）。 |
| 24 | skills/exec/SKILL.md | 步骤 10: 编写教学文档 | "仅 feat 和 refactor 任务执行。调用 `game-dev:write-tutorial` skill"（L352-356） | TUTORIAL.md 存在于项目根目录 | ✅ | TUTORIAL.md 已创建，write-tutorial 被执行 |
| 25 | agents/test-agent.md | Startup: 一次性读取 | "一次性读取以下文件：`${CLAUDE_PLUGIN_ROOT}/references/{tech}/testing.md`、`${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md`"（L36-38） | test-agent 正确读取了 testing.md 和 config.md，使用了 GUT API | ✅ | test 文件使用 `extends GutTest`、`assert_eq`、`assert_not_null` 等符合 testing.md 的 API |
| 26 | agents/test-agent.md | RED Step 4: Report | "输出结构化 RED report，格式见 exec prompt 中的模板"（L105） | exec 用 RED report 提取 testsuite/testcase 名称传递给 GREEN agent | ✅ | GREEN agent 的 prompt 中包含 "目标 testsuite" 和 "目标 testcase" 字段，证明 RED report 被正确解析和传递 |
| 27 | agents/coding.md | 启动初始化: 读取规范文件 | "启动时检查并读取：style-guide.md、project-organization.md、coding.md"（L43-45） | 代码符合 snake_case、类型注解、@onready 节点引用等规范 | ✅ | zombie_base.gd、zombie_basic.gd 使用 snake_case 变量名、`@export` 集中、`@onready` 延迟初始化、完整类型注解——符合 coding.md 和 style-guide.md |
| 28 | agents/coding.md | 自我验证协议 | "先诊断，再动手。先记日志，再改代码。逐个击破，不一锅端。"（L101-105） | tdd-iterations.md 显示 AI-3 GREEN 诊断→修复→验证循环（eager 解析 → lazy 解析），AI-2 GREEN 3 轮迭代 | ✅ | tdd-iterations.md 记录详细诊断过程："问题分类"、"根因"、"影响范围"，符合 coding.md 的诊断模板格式 |
| 29 | agents/coding.md | GREEN 重试上限 | "每个任务最多 5 轮，每个 testcase 最多 3 轮子循环"（L158-159） | 所有任务在 1-3 轮内完成 | ✅ | AI-2: 3 轮。AI-3: 2 轮。AI-4: 2 轮。其余：1 轮。未超限 |
| 30 | agents/coding.md | 禁止空壳/假代码 | "不允许 pass、# TODO 或 NotImplementedError"（L280） | `zombie_base.gd` L251 有 `pass` 在 abstract stub 中 | ⚠️ | `zombie_base.gd` 是 `@abstract` 类，abstract method stub 中的 `pass` 是 Godot 惯用法。coding.md 禁止 `pass` 语句（L89），但 abstract 类的 `pass` stub 是必要且合法的。规则未区分"合法 pass"和"非法 pass"。实际执行中边界检查正确识别了此 pass 为合法（见 tdd-iterations.md L253: "zombie_base.gd:251 `pass` abstract stub — 保留(原 GREEN 已合法)"）。风险低。 |

### 根因分析与解决方案

| # | 应有步骤 | 达标? | 根因 | 解决方案 | 解决方案来源 |
|---|---------|-------|------|---------|-------------|
| 14 | 确认测试环境: 已知坑完整 | ❌ | config.md 已知坑未覆盖 "GUT 默认 treat_engine_errors_as = FAILURE"。`_make_mock_player` 在 `add_child` 前调 `global_position = pos` 是测试 fixture 常见模式，engine error 被 GUT 视为测试失败导致 11 个 spurious failure。AI-2 GREEN 被迫创建 `.gutconfig.json` 绕过。根因是已知坑收集不完整——缺少 GUT engine error 处理机制。 | 在 `references/godot/config.md` 的 "已知坑" 节增加一条：**"GUT 默认将 engine error 视为测试失败（`treat_engine_errors_as = FAILURE`）。测试 fixture 中 `global_position` 赋值在 `add_child` 之前会触发 `!is_inside_tree()` engine error。解决方案：创建项目级 `.gutconfig.json`，将 `failure_error_types` 设为 `["gut", "push_error"]`（排除 engine）。"** | references/godot/config.md §已知坑；GUT 文档 https://gut.readthedocs.io/en/latest/ |
| 18 | GREEN 检查: 全部通过 | ❌ | exec-prompts.md 要求 "目标 testsuite 全部通过"，但 `test_zombie_base_is_abstract` 因 Godot 4.7 `GDScript.can_instantiate()` 不检查 `@abstract` 标志而永久无法通过。exec 没有 "framework 限制导致无法验证的测试" 的处理流程。根因是 exec 缺少对 framework 限制的容错机制。 | 在 exec-prompts.md GREEN 检查规则中增加一条豁免条款：**"如 coding-agent 报告某 testcase 因 framework 限制（如 Godot 引擎 API 行为与预期不符）无法通过，且提供了文档引用证明，该 testcase 标记为 `[FRAMEWORK_LIMITATION]`，不阻塞 GREEN 进入 VERIFY。"** 同时在 tdd-iterations.md 中要求记录 framework limitation 的详细信息（API 名称、官方文档引用、无法修复的原因）。 | references/godot/config.md §已知坑（增加 engine API 限制列表）；exec-prompts.md GREEN 检查规则 |
| 20 | 边界检查: test 文件隔离/质量 | ⚠️ | exec 的边界检查（步骤 6e）分"通用检查"和"技术栈专属检查"。通用检查只覆盖"coding agent 是否修改了测试文件"和"空代码/假代码"。技术栈专属检查从 coding.md 提取，但 coding.md 没有 "测试 fixture 质量" 规则。`_make_mock_player` 中 `global_position` before `add_child` 是测试代码质量问题，不在当前检查范围内。根因是边界检查未覆盖测试 fixture 的 engine error 模式。 | 在 exec/SKILL.md 步骤 6e 的 "通用检查" 表中增加一行：**"测试 fixture 质量：测试中是否有 engine error/warning 非预期输出？"** 检测方式：grep 测试输出日志中的 `ERROR:` 和 `WARNING:` 行，判断是否为测试 fixture 写法问题。违规写入 REFACTOR prompt 的边界违规清单。 | skills/exec/SKILL.md §步骤 6e；coding.md §禁止（扩展测试代码质量约束） |
| 23 | exec step 9: 收集经验 | ✅ | （已验证达标，无需根因分析） | 不适用——步骤达标。collect-lessons 按声明写入了 `test-lessons.md` 和 `coding-lessons.md`，额外产出的 `collect-lessons-summary.md` 是汇总格式。 | skills/collect-lessons/SKILL.md §步骤 7 |
| 16 | RED 检查: 失败原因正确 | ⚠️ | exec-prompts.md 要求 "RED report 中所有 testcase 都失败了且原因正确"，但未定义 "engine error 导致的失败" 是否算 "原因正确"。AI-2 的 11 个 testcase 失败原因是 `!is_inside_tree()` engine error（测试 fixture 问题），而不是 "功能未实现"。exec 接受了它。根因是 RED 检查规则缺少对 engine error 失败模式的分类标准。 | 在 exec-prompts.md RED 检查规则中增加分类：**"失败原因分为三类：① 功能未实现（正确 RED 失败）② 语法/API 错误（test-agent 需自修）③ engine/framework 副作用（如 `!is_inside_tree()` engine error）。类型③ 需评估：如果是测试 fixture 写法问题 → test-agent 修复后重跑；如果是 framework 已知限制 → 标记并进入 GREEN。"** | skills/exec/references/exec-prompts.md RED 检查规则；references/godot/testing.md §已知限制 |
| 30 | coding 禁止 pass: abstract stub | ⚠️ | coding.md L89 笼统禁止 `pass`，但 Godot `@abstract` 类的 abstract method stub 必须有 `pass`（GDScript 语法要求）。规则未区分"非法 pass（空分支/空方法体）"和"合法 pass（abstract stub / 接口定义）"。实际执行中边界检查正确识别了此 pass 为合法但用了 ad-hoc 判断。根因是 coding.md 的 pass 禁止规则缺少例外条款。 | 在 coding.md "禁止" 节修改 `pass` 规则：**"禁止 `pass` 语句（空方法/空分支），但 `@abstract` 类的 abstract method stub 中的 `pass` 除外。"** | references/godot/coding.md §禁止；GDScript 文档 https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_basics.html |
