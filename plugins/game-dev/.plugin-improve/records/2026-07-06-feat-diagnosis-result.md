# game-dev - feat 诊断结果
## 日期：2026-07-06

### 链路拓扑

```
skills/orchestrator/SKILL.md (入口 — /game-dev:start)
├── skills/artifact-manager/SKILL.md
├── skills/design-ui/SKILL.md
│   └── (外部: superpowers:brainstorming, frontend-design)
├── skills/plan/SKILL.md
│   ├── references/plan-format.md
│   ├── references/godot/config.md
│   ├── references/godot/docs.md
│   ├── references/godot/patterns.md
│   ├── references/godot/design.md
│   ├── references/godot/coding.md
│   └── references/godot/nodes-3d.md
├── skills/art-resources-conductor/SKILL.md
│   └── agents/art-resource-creator.md
│       ├── skills/art-spec-builder/SKILL.md
│       └── skills/art-prompt-builder/SKILL.md
├── skills/exec/SKILL.md
│   ├── references/exec-prompts.md ← ❌ 文件不存在
│   ├── references/exec-logging.md ← ❌ 文件不存在
│   ├── references/godot/config.md
│   ├── references/godot/coding.md
│   ├── agents/test-agent.md
│   │   ├── references/godot/testing.md
│   │   └── references/godot/config.md
│   ├── agents/coding.md
│   │   ├── references/godot/config.md
│   │   ├── references/godot/coding.md
│   │   ├── references/godot/style-guide.md (存在)
│   │   ├── references/godot/project-organization.md (存在)
│   │   ├── references/godot/docs.md
│   │   └── references/godot/ui.md
│   ├── skills/collect-lessons/SKILL.md
│   └── skills/write-tutorial/SKILL.md
└── (外部: ${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md)
```

### 逐步骤诊断

| # | 所属节点 | 应有步骤 | 要求(来自plugin文件) | 实际步骤(来自log) | 达标? | 达标证据 / 不达标点 |
|---|---------|---------|---------------------|------------------|-------|-------------------|
| 1 | skills/orchestrator/SKILL.md | 阶段0a: 读CLAUDE.md确定tech | "grep -iE \"(Ren'Py\|renpy\|Godot\|godot)\" CLAUDE.md 2>/dev/null \| head -5" (orchestrator/SKILL.md:64-66行) | log中未直接捕获orchestrator主会话的grep操作，但产物目录为`.godot-dev/`，确认检测为godot | ✅ | 产物目录`.godot-dev/feat-3/` 证明tech=godot检测正确 |
| 2 | skills/orchestrator/SKILL.md | 阶段0b: 读config获取dev_dir | "读 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md` 的 `## 产物目录` 节...回显确认后才能调用artifact-manager" (orchestrator/SKILL.md:76-87行) | log中未直接捕获，但产物目录实际为`.godot-dev/feat-3/`，与config.md中`dev_dir: .godot-dev/`一致 | ✅ | config.md:27行明确`根目录: .godot-dev/`，产物目录与之匹配 |
| 3 | skills/orchestrator/SKILL.md | 阶段1: 创建任务目录 | "Skill({skill: \"game-dev:artifact-manager\", args: \"--task-dir {dev_dir}/{kind}-{N} --kind feat --dev-dir {dev_dir}\"})" (orchestrator/SKILL.md:97-98行) | 产物目录`.godot-dev/feat-3/`已创建，含plan.md + .work/ | ✅ | 任务目录`.godot-dev/feat-3/`存在且结构完整(plan.md, progress.json, .work/) |
| 4 | skills/orchestrator/SKILL.md | 阶段2: UI检测 | "分析用户的任务描述，判断是否涉及UI视觉设计...涉及UI视觉设计→调用design-ui...不是UI任务→直接进入阶段3" (orchestrator/SKILL.md:107-125行) | 产物中`.work/layouts/`不存在，`.work/resources.md`标注"无新资源"，确认跳过了design-ui | ✅ | 僵尸AI行为是纯逻辑功能(Godot 3D gameplay)，不涉及Control UI，按orchestrator/SKILL.md:113行规则正确跳过design-ui |
| 5 | skills/orchestrator/SKILL.md | 阶段3: Plan设计阶段 | "Skill({skill: \"game-dev:plan\", args: \"--task-dir {task_dir}\"})...输出plan.md路径" (orchestrator/SKILL.md:131-135行) | plan.md存在于`/mnt/d/project/godot/zombies-demo/.godot-dev/feat-3/plan.md`，8296字节 | ✅ | plan.md存在且包含：概述、领域模型、行为列表、设计摘要、影响范围、任务列表(AI-0~AI-7)、测试策略 |
| 6 | skills/orchestrator/SKILL.md | 阶段4: 资源检测与生成 | "当`{task_dir}/.work/resources.md`存在且包含未处理的资源条目时触发" (orchestrator/SKILL.md:142行) | resources.md内容为"无新资源。Zombie_Basic.gltf含6段目标动画..."，无AI可生成条目 | ✅ | resources.md标注无新资源需要生成，正确跳过了art-resources-conductor |
| 7 | skills/orchestrator/SKILL.md | 阶段5: Exec实现阶段 | "Skill({skill: \"game-dev:exec\", args: \"--mode feat --task-dir {task_dir}\"})" (orchestrator/SKILL.md:156行) | log中25个agent被spawn，覆盖AI-0到AI-7的RED/GREEN/VERIFY/REFACTOR | ✅ | progress.json显示8个AI任务全部done，tdd-iterations.md记录完整TDD循环 |
| 8 | skills/exec/SKILL.md | 步骤5: 信息隔离清单 | "从game-dev:test-agent到game-dev:coding: 行为级失败描述+具体失败testcase名称和错误信息、设计文档路径 \| 禁止传: 测试源码、测试文件路径" (exec/SKILL.md:93-96行) | log未直接捕获spawn prompt内容，但从tdd-iterations.md看coding-agent的修复是基于testcase行为描述的 | ⚠️ | 风险：无法从log验证spawn prompt是否遵守信息隔离规则。exec-prompts.md不存在(见#9)，spawn prompt模版不明确，信息边界可能被突破 |
| 9 | skills/exec/SKILL.md | 步骤5: 一次性读取参考文件 | "references/exec-prompts.md — agent spawn prompt 模板; references/exec-logging.md — TDD 迭代日志格式" (exec/SKILL.md:123-124行) | 这两个文件在`references/`目录下不存在 | ❌ | 要求: exec必须读取exec-prompts.md和exec-logging.md来获取prompt模板和日志格式。实际: 文件不存在于`/data/project/8bit-market/plugins/game-dev/references/`。exec被迫自行构造prompt和日志格式，失去了标准化的agent spawn规范和日志结构 |
| 10 | skills/exec/SKILL.md | 步骤6b: RED spawn test-agent | "使用 `references/exec-prompts.md` 的 **RED prompt** 模板组装 spawn prompt...按 references/exec-prompts.md RED 检查规则验收" (exec/SKILL.md:146-148行) | agent meta显示test-agent被spawn用于AI-0~AI-7的RED阶段，但prompt模板无标准来源 | ❌ | 要求: 使用exec-prompts.md的RED prompt模板。实际: exec-prompts.md不存在，spawn prompt为exec自行构造。缺少标准化的RED prompt模板意味着test-agent收到的prompt质量不稳定 |
| 11 | skills/exec/SKILL.md | 步骤6c: GREEN spawn coding-agent | "使用 **GREEN prompt** 模板...按 references/exec-prompts.md GREEN 检查规则验收" (exec/SKILL.md:156-158行) | agent meta显示coding-agent被spawn用于AI-1~AI-7的GREEN阶段 | ❌ | 同#10，exec-prompts.md不存在，GREEN prompt模板缺失 |
| 12 | skills/exec/SKILL.md | 步骤6d: VERIFY spawn test-agent | "使用 **VERIFY prompt**...按 references/exec-prompts.md VERIFY 检查规则验收" (exec/SKILL.md:166-168行) | agent meta显示test-agent被spawn用于VERIFY阶段(AI-3, AI-4, AI-5, AI-6, AI-7) | ❌ | 同#10，VERIFY prompt模板缺失 |
| 13 | skills/exec/SKILL.md | 步骤6e: 边界检查 | "VERIFY全部通过后、REFACTOR之前执行...通用检查: 测试文件隔离、空代码/假代码...技术栈专属检查: 资源引用完整性、节点路径有效性、信号连接有效性、文件路径有效性" (exec/SKILL.md:176-192行) | tdd-iterations.md中AI-5 REFACTOR段显示边界检查被执行：`grep pass\|TODO\|NotImplemented\|^\s*print\(` → 0命中 | ✅ | tdd-iterations.md:210行确认了边界检查执行：`Boundary check: grep pass\|TODO\|NotImplemented\|^\s*print\(` — 0 hits。AI-6 REFACTOR段(tdd-iterations.md:251行)也有边界检查 |
| 14 | skills/exec/SKILL.md | 步骤6f: REFACTOR spawn coding-agent | "使用 **REFACTOR prompt** + 边界违规清单(如有)...按 references/exec-prompts.md REFACTOR 检查规则验收" (exec/SKILL.md:212-214行) | agent meta显示coding-agent被spawn用于AI-5和AI-6的REFACTOR | ❌ | 同#10，REFACTOR prompt模板缺失。但实际执行中REFACTOR成功完成(AI-5: 1/5轮即通过，AI-6: 清理anti-pattern) |
| 15 | skills/exec/SKILL.md | 步骤6b-6g: 日志记录 | "按 exec-logging.md RED/GREEN/VERIFY/REFACTOR 格式追加" (exec/SKILL.md多处) | tdd-iterations.md存在且包含详细的TDD循环日志 | ⚠️ | 风险: exec-logging.md不存在，日志格式无标准来源。tdd-iterations.md的格式是exec自行决定的，可能与设计意图不同。但从产物看日志质量较高(GREEN表格+根因分析+验证结果) |
| 16 | skills/exec/SKILL.md | 步骤8: 最终验证 | "从config.md读取test_cmd_full并执行。验证全部通过" (exec/SKILL.md:240行) | tool-results/brjhgjy2s.txt为GUT全量测试输出，显示110/110 passed | ✅ | brjhgjy2s.txt: 全量GUT测试110/110 passed，162 asserts，0 failures |
| 17 | skills/exec/SKILL.md | 步骤9: 收集开发经验 | "调用game-dev:collect-lessons skill" (exec/SKILL.md:246-248行) | `.work/collect-lessons-summary.md`存在 | ✅ | collect-lessons-summary.md存在，2445字节，说明collect-lessons被执行 |
| 18 | skills/exec/SKILL.md | 步骤10: 编写教学文档 | "调用game-dev:write-tutorial skill...仅feat和refactor任务执行" (exec/SKILL.md:253-257行) | log中未直接捕获write-tutorial的调用 | ⚠️ | 风险: 无法从log确认write-tutorial是否被调用。feat任务应执行此步骤。需检查项目TUTORIAL.md是否存在来判断 |
| 19 | skills/plan/SKILL.md | 步骤4: 确认行为清单(强制门) | "从需求中提取玩家可见的行为列表，向用户确认...用户确认后，保存行为清单到requirements.md" (plan/SKILL.md:66-84行) | plan.md行为列表包含10条行为，requirements.md存在 | ⚠️ | 风险: log中未捕获用户确认行为的交互。plan.md行为列表(#43-54行)有10条行为，每条标注验证方式。requirements.md(2168字节)存在，但无法验证用户是否确认过 |
| 20 | skills/plan/SKILL.md | 步骤5: 领域设计 | "对每个功能行为，分析三层...输出domain-design.md" (plan/SKILL.md:88-148行) | domain-design.md存在(5689字节) | ✅ | `.work/domain-design.md`存在，包含领域模型识别 |
| 21 | skills/plan/SKILL.md | 步骤6: 任务拆分与排序 | "按功能模块拆分，不按文件/阶段拆分...任务描述=可验证的功能行为，不含文件路径...logic任务排在ui任务前面" (plan/SKILL.md:151-211行) | plan.md任务列表含8个AI任务，全部(type: logic)，无文件路径，无代码符号 | ✅ | plan.md:76-83行：8个任务全部logic类型，描述用行为语言(如"实现僵尸基类AI：状态枚举、状态机...")。grep确认无`.gd`/`.tscn`/`.tres`在任务描述中 |
| 22 | skills/plan/SKILL.md | 步骤6: 描述写作规则 | "不含代码符号 — class名、方法名、函数名、动画名不出现在描述中" (plan/SKILL.md:198行) | plan.md任务描述中含有技术术语如"CharacterBody3D"、"AnimationPlayer"、"ZombieData" | ❌ | 要求: class名不出现在任务描述中。实际: AI-2描述含"状态枚举、状态机、转换函数、受击接口、状态信号"这些虽非GDScript class名但是实现概念。AI-4描述含"CharacterBody3D根+CollisionShape3D胶囊+AnimationPlayer"这些是引擎节点类型名。这些介于行为描述和代码符号之间，判断为⚠️偏向违规 |
| 23 | skills/plan/SKILL.md | 步骤9: 编写plan.md | "基于.work/下的设计文档编写...以plan-format.md为唯一权威来源" (plan/SKILL.md:308-310行) | plan.md已写入，8296字节 | ✅ | plan.md结构完整，包含模板要求的所有章节 |
| 24 | skills/plan/SKILL.md | 步骤10: 格式自检 | "对照plan-format.md的格式校验清单逐项确认，然后执行禁止内容清单中的所有grep命令。全部零命中方可输出" (plan/SKILL.md:321行) | plan.md内容已检查 | ⚠️ | 风险: 无法验证plan是否执行了全部grep自检。人工复查plan.md: 无"lint代替测试"/"人工启动目视"/"源码契约"等禁止短语。但影响范围表(plan.md:58-68行)中列出了具体文件路径(如`resources/enemies/zombie_basic.tres`、`scripts/enemies/zombie_base.gd`)，这虽是"影响范围"节(非任务描述)，但plan-format.md:209行要求"影响范围描述功能影响面(不写文件路径)" |
| 25 | references/plan-format.md | plan.md: 影响范围不写文件路径 | "影响范围描述功能影响面(不写文件路径)" (plan-format.md:209行) | plan.md:58-68行影响范围表列出具体文件路径 | ❌ | 要求: "影响范围描述功能影响面(不写文件路径)"。实际: plan.md影响范围表(type/文件/操作)三列，列出了9个具体文件路径。违反了plan-format.md的明确规则 |
| 26 | skills/exec/SKILL.md | TDD循环: AI-0仅执行RED+GREEN(无REFACTOR) | "每个任务走完整RED→GREEN→VERIFY→边界检查→REFACTOR→VERIFY循环" (exec/SKILL.md:130行) | agent meta显示AI-0仅有RED(test-agent) spawn，无独立GREEN/VERIFY/REFACTOR spawn | ❌ | 要求: 每个[AI-N]任务走完整TDD循环。实际: AI-0(创建GUT测试基础设施+烟测)仅有RED spawn(agent-aba881f782aa01ff9)，无独立的coding-agent spawn。AI-0是bootstrap任务，其GREEN可能被合并到AI-1中，但按exec规范应独立走完整循环 |
| 27 | skills/exec/SKILL.md | TDD循环: AI-7仅执行RED→GREEN→VERIFY(无REFACTOR) | "每个任务走完整RED→GREEN→VERIFY→边界检查→REFACTOR→VERIFY循环" (exec/SKILL.md:130行) | agent meta和tdd-iterations.md显示AI-7仅到VERIFY(post-GREEN)，无REFACTOR spawn | ❌ | 要求: 每个任务完整循环含REFACTOR。实际: AI-7(main scene集成)仅有RED→GREEN→VERIFY，无REFACTOR。可能因为任务简单无需重构，但exec规范没有"可跳过REFACTOR"的例外条款 |
| 28 | agents/test-agent.md | RED Mode Step 2a: Tracer Bullet | "写一个最小测试证明目标可达(场景可加载、screen可到达等)。跑通这个测试后再加交互测试" (test-agent.md:91行) | tdd-iterations.md中未明确记录tracer bullet步骤 | ⚠️ | 风险: 无法从产物确认test-agent是否先写tracer bullet再逐步加交互测试。tdd-iterations.md从coding-agent视角记录，不包含test-agent内部步骤 |
| 29 | agents/coding.md | GREEN模式: 三层验证结构 | "Phase 1: 初步运行(testsuite级别)→Phase 2: 逐个Testcase系统性循环→Phase 3: 收尾" (coding.md:111-123行) | tdd-iterations.md中AI-2/AI-3/AI-5的GREEN日志明确记录了Phase 1(全量运行)→Phase 2(逐个case诊断)→Phase 3(收尾)结构 | ✅ | tdd-iterations.md:40-68行(AI-2)明确展示Phase结构：初次运行结果→失败分析表格→根因分析→实施摘要。AI-5:174-209行同样完整 |
| 30 | agents/coding.md | GREEN模式: 诊断模板 | "先诊断，再动手...必须先读执行测试的错误日志+对应代码位置+设计文档+文档找出根因" (coding.md:102行) | tdd-iterations.md中AI-5的GREEN日志展示完整诊断流程 | ✅ | tdd-iterations.md:181-188行(AI-5)明确展示：根因分析(实施前)→修复方案(3步)→验证结果。遵循了"先诊断再动手"原则 |
| 31 | agents/coding.md | GREEN模式: 先记日志再改代码 | "诊断完成后，必须立刻追加tdd-iterations.md，然后才能修改源代码" (coding.md:103行) | tdd-iterations.md包含按时间顺序的迭代日志 | ✅ | tdd-iterations.md中GREEN日志先记录诊断结果，再记录实施，符合"先记日志再改代码"顺序 |
| 32 | agents/coding.md | 关键规则: 绝不写空壳/假代码 | "不允许pass、# TODO或NotImplementedError" (coding.md:280行) | tdd-iterations.md:251行边界检查确认：`Boundary: pass/TODO/NotImplemented/print in zombie_basic.gd — 0 hits`；但zombie_base.gd:251有合法的abstract stub pass | ✅ | 边界检查确认无pass/TODO/NotImplemented违规，zombie_base.gd:251的pass是@abstract方法的合法stub |
| 33 | agents/coding.md | 关键规则: 绝不写入测试目录 | "绝不写入测试目录" (coding.md:279行) | tdd-iterations.md中AI-6 REFACTOR段修改了test/unit/test_zombie_death_flow.gd的fixture注释 | ❌ | 要求: coding-agent绝不写入测试目录。实际: AI-6 REFACTOR(tdd-iterations.md:236-238行)明确记录了"改动2: test/unit/test_zombie_death_flow.gd...fixture头注释更新...在add_child(ap)之前给AP挂AnimationLibrary"。coding-agent在REFACTOR阶段修改了测试文件！这直接违反了coding.md的核心规则#1 |
| 34 | agents/coding.md | REFACTOR模式: 改变结构不改变行为 | "在不改变可观察行为的前提下重组代码结构" (coding.md:225行) | AI-6 REFACTOR删除了zombie_basic.gd中的"防御性lazy-register"代码块并修改了测试fixture | ⚠️ | 风险: AI-6 REFACTOR不仅重组代码结构，还删除了功能代码(AnimationLibrary.new()+add_animation块)。虽然agent声称"行为等价"，但删除的是功能代码而非纯结构调整。加上修改了测试文件(#33)，REFACTOR的边界被突破 |

### 根因分析与解决方案

| # | 应有步骤 | 达标? | 根因 | 解决方案 | 解决方案来源 |
|---|---------|-------|------|---------|-------------|
| 9 | 步骤5: 一次性读取参考文件 | ❌ | **结构缺陷：引用文件未创建。** exec/SKILL.md:123-124行引用了`references/exec-prompts.md`和`references/exec-logging.md`，但这两个文件从未被创建。这是典型的"接口已定义但实现缺失"问题——skill声明了依赖但plugin打包时遗漏了这两个reference文件。skill-structure.md §1.3明确要求"references/中的文件在SKILL.md中被引用"，反之亦然——SKILL.md中引用的references/文件必须存在。 | 创建`references/exec-prompts.md`，定义RED/GREEN/VERIFY/REFACTOR四个spawn prompt模板和检查规则。创建`references/exec-logging.md`，定义TDD迭代日志的RED/GREEN/VERIFY/REFACTOR格式。两文件创建后更新`references/`目录清单。 | skill-structure.md §1.3 结构检查清单: "references/中的文件在SKILL.md中被引用" — 逆命题同样适用 |
| 10 | 步骤6b: RED spawn test-agent | ❌ | **级联影响：根因同#9。** RED prompt模板应来自exec-prompts.md，但该文件不存在。exec被迫自行构造spawn prompt，失去了标准化的prompt结构（包括任务上下文字段、信息隔离声明、RED检查规则）。harness-methodology.md 机制2(Red Flags)强调：缺少参考文件应"报错停止"而非自行构造。 | 同#9。在exec-prompts.md中定义RED prompt模板，明确：task_dir/project/tech传递格式、行为描述字段、禁止传测试源码的声明、RED验收标准(测试失败原因是否正确)。 | harness-methodology.md 机制2(Red Flags): exec/SKILL.md:56行(找不到references/exec-prompts.md说明路径有问题，应报错停止) |
| 11 | 步骤6c: GREEN spawn coding-agent | ❌ | **级联影响：根因同#9。** GREEN prompt模板缺失，coding-agent收到的prompt可能缺少：失败testcase名称和错误信息字段、设计文档路径、信息隔离声明。 | 同#9。在exec-prompts.md中定义GREEN prompt模板，明确：从test-agent RED report提取testsuite/testcase名称、失败描述传递格式、禁止传测试文件路径的声明、自验证协议要求。 | exec/SKILL.md §5 信息隔离清单: "行为级失败描述 + 具体失败testcase名称和错误信息" |
| 12 | 步骤6d: VERIFY spawn test-agent | ❌ | **级联影响：根因同#9。** VERIFY prompt模板缺失，VERIFY agent可能不知道这是独立验证门（不能看实现代码），导致验证失去独立性。 | 同#9。在exec-prompts.md中定义VERIFY prompt模板，明确：独立验证门声明（不能参考GREEN的实现）、仅跑测试不分析失败、通过/失败报告格式。 | exec/SKILL.md:16行 核心原则: "exec不做判断，只做传递...测试失败让coding自己看输出修" |
| 14 | 步骤6f: REFACTOR spawn coding-agent | ❌ | **级联影响但严重性较低：根因同#9。** REFACTOR prompt模板缺失，但由于coding-agent内置了REFACTOR模式（agents/coding.md:211-249行），实际执行仍然成功。 | 同#9。在exec-prompts.md中定义REFACTOR prompt模板，明确：边界违规清单格式(表格:文件:行/违规类型/描述)、已修改文件列表、结构重组约束、规范自查要求。 | agents/coding.md §REFACTOR模式: 完整的REFACTOR自验证协议已内置，prompt模板主要是补充exec传递的上下文格式 |
| 22 | 步骤6: 任务描述不含代码符号 | ❌ | **规则歧义：边界定义不清晰。** plan/SKILL.md:198行说"class名、方法名、函数名、动画名不出现在描述中"，但Godot节点类型名(CharacterBody3D, AnimationPlayer)介于"行为描述"和"代码符号"之间——它们是引擎提供的节点类型，既是技术名词也是场景构建的基本单元。plan/SKILL.md没有明确界定"引擎节点类型名"是否算代码符号。 | 在plan/SKILL.md §6"描述写作规则"表中增加一条："引擎节点类型名(如CharacterBody3D, AnimationPlayer, VBoxContainer)不出现在任务描述中。用行为语言替代：不用'CharacterBody3D根'，用'物理角色根节点'；不用'AnimationPlayer'，用'动画播放器'。" | plan/SKILL.md §6 好/坏对照示例: 所有✅示例均不含引擎节点类型名 |
| 25 | plan.md: 影响范围不写文件路径 | ❌ | **自检遗漏：格式自检未覆盖影响范围节。** plan-format.md:209行明确要求"影响范围描述功能影响面(不写文件路径)"，但plan/SKILL.md §10(格式自检)的grep命令仅扫描任务描述中的文件路径(`grep -nP '\[AI-\d+\].*\.(rpy\|gd\|tscn\|tres)\b'`)，未扫描影响范围节。plan在执行自检时grep零命中，但违规存在于影响范围表中。 | 在plan/SKILL.md §10增加一条grep检查：`grep -nP '^\|.*\|.*\.(gd\|tscn\|tres)\b' {task_dir}/plan.md` 扫描影响范围表中是否出现文件扩展名。同时在plan-format.md的禁止内容清单中增加此项扫描。 | plan-format.md §格式校验清单: "影响范围描述功能影响面(不写文件路径)" |
| 26 | TDD循环: AI-0 缺少完整循环 | ❌ | **规则过于绝对：无例外机制。** exec/SKILL.md:130行"每个任务走完整RED→GREEN→VERIFY→边界检查→REFACTOR→VERIFY循环"是绝对规则。但AI-0是bootstrap任务(创建test/目录+GUT smoke test)，本质是基础设施搭建而非功能开发，REFACTOR无实际意义。exec没有bootstrap/简单任务的例外条款。 | 在exec/SKILL.md §6增加例外规则："bootstrap任务(如AI-0:创建测试基础设施)可简化为RED→GREEN→VERIFY。如果GREEN后VERIFY全绿且边界检查零违规，可跳过REFACTOR。exec必须在日志中标注跳过原因。" | exec/SKILL.md §6f: REFACTOR仅在代码需要结构调整时执行——基础设施搭建任务无代码可重构 |
| 27 | TDD循环: AI-7 缺少REFACTOR | ❌ | **同#26：无例外机制。** AI-7是集成任务(修改main.tscn加一个节点实例)，改动极小(8行)。完整REFACTOR循环对这8行改动性价比极低。但exec规范无"极小改动可跳过REFACTOR"的条款。 | 同#26方案，扩展例外条款："单文件改动<20行且边界检查零违规的任务，可跳过REFACTOR。跳过必须在progress.json中标注skip_reason字段。" | exec/SKILL.md 核心原则: "垂直切片，不是水平切片" — 小改动也是垂直切片，但REFACTOR的门槛应与改动规模成正比 |
| 33 | 关键规则: 绝不写入测试目录 | ❌ | **规则冲突：REFACTOR的"修复边界违规"指令覆盖了"绝不写入测试目录"的铁律。** agents/coding.md:279行("绝不写入测试目录")是铁律级的规则，但coding.md:222行("如果prompt包含##边界违规节，REFACTOR必须逐条修复所有违规项")给了agent一个"必须修复所有违规"的指令。当agent在REFACTOR中判断测试fixture需要修正时，"修复所有违规"的优先级压过了"不写测试目录"。这是两个强制指令的优先级冲突。harness-methodology.md机制1(Iron Law)指出：铁律不可被任何其他规则覆盖。 | 1) 在agents/coding.md的REFACTOR模式开头增加铁律级声明："**REFACTOR绝不写入测试目录。** 如果边界违规涉及测试文件，将其报告给exec主会话，由exec决定是spawn test-agent修复还是标记为已知限制。coding-agent在REFACTOR模式下修改测试文件 = 本轮无效，必须回退。" 2) 在agents/coding.md §关键规则#1增加强调："**(含REFACTOR模式)** — 绝不写入测试目录。" | harness-methodology.md 机制1(Iron Law): 铁律不可被任何其他规则覆盖。agents/coding.md:279行规则#1应升级为Iron Law级别 |
| 34 | REFACTOR: 改变结构不改变行为 | ⚠️ | **级联影响：根因同#33。** AI-6 REFACTOR删除了zombie_basic.gd中的功能代码(AnimationLibrary动态创建块)，原因是边界违规清单促使agent"修复"测试fixture问题。agent将"测试fixture不完整"误解为需要修改测试文件+删除生产代码中的防御逻辑。 | 同#33方案。增加REFACTOR行为变更的硬门："任何删除>3行功能代码的操作必须在tdd-iterations.md中记录：删除理由、行为等价性证明、全量测试结果。未记录=本轮无效。" | agents/coding.md:225行 "在不改变可观察行为的前提下重组代码结构" |
| 8 | 信息隔离清单 | ⚠️ | **可观测性不足：log不捕获spawn prompt内容。** exec/SKILL.md §5定义了详细的信息隔离规则，但当前日志系统(agent JSONL + tool-results)只记录agent的操作和输出，不记录spawn prompt原文。无法从事后日志验证exec是否遵守了信息隔离。 | 在exec-logging.md(待创建，见#9方案)中增加要求：每次spawn agent时，将完整的spawn prompt写入`{task_dir}/.work/coding/{agent-id}-prompt.md`。这使信息隔离事后可审计。 | exec/SKILL.md §5 信息隔离清单: 定义了5条can/cannot规则，但无验证机制 |
| 15 | 日志记录格式 | ⚠️ | **根因同#9：exec-logging.md不存在。** 当前tdd-iterations.md的格式质量较高(表格+根因分析+验证结果)，但这是exec自行决定的，缺乏标准化。未来不同exec执行可能产生格式不一致的日志。 | 创建exec-logging.md(同#9方案)，定义标准日志格式。将当前feat-3的tdd-iterations.md作为事实标准(good baseline)，提炼为模板。 | 当前产物tdd-iterations.md 可作为事实标准提炼 |
| 18 | 步骤10: 编写教学文档 | ⚠️ | **可观测性不足：** write-tutorial的调用和输出在log中无记录。无法确认该步骤是否执行。 | 在exec-logging.md中增加步骤9/10的日志记录要求。exec完成后输出完成报告时确认write-tutorial是否成功执行。 | exec/SKILL.md §Completion Gate: 要求write-tutorial已完成 |
| 19 | 步骤4: 确认行为清单 | ⚠️ | **设计依赖用户交互：** plan/SKILL.md §4的"确认门"依赖用户回复"是否有遗漏或不需要的行为？"。log不捕获用户交互内容，无法验证确认是否真实发生。这是设计上的可观测性盲区。 | 在plan/SKILL.md §4增加要求：用户确认后，将确认结果(含用户回复摘要)写入requirements.md末尾的"## 用户确认"节。这使确认可追溯。 | plan/SKILL.md:84行 "用户确认后，保存行为清单到requirements.md" — 应扩展为保存确认结果 |
