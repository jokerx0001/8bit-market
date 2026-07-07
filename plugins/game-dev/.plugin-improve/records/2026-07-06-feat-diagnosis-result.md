# game-dev - feat 诊断结果
## 日期：2026-07-06

### 链路拓扑

```
skills/orchestrator/SKILL.md (entry — /game-dev:start)
├── skills/artifact-manager/SKILL.md
│   └── (阶段1: 创建任务目录 .godot-dev/feat-3/)
├── skills/design-ui/SKILL.md
│   └── (阶段2: 未触发 — 3D僵尸敌人无UI视觉设计)
├── skills/plan/SKILL.md
│   ├── references/plan-format.md
│   ├── references/godot/config.md
│   ├── references/godot/docs.md
│   ├── references/godot/design.md
│   ├── references/godot/nodes-3d.md
│   ├── references/godot/patterns.md
│   └── references/godot/coding.md
├── skills/art-resources-conductor/SKILL.md
│   └── (阶段4: 未触发 — 无新资源需求)
└── skills/exec/SKILL.md
    ├── skills/exec/references/exec-prompts.md
    ├── skills/exec/references/exec-logging.md
    ├── references/godot/config.md
    ├── references/godot/coding.md
    ├── agents/test-agent.md
    │   ├── references/godot/testing.md
    │   └── references/godot/config.md
    ├── agents/coding.md
    │   ├── references/godot/config.md
    │   ├── references/godot/coding.md
    │   ├── references/godot/style-guide.md
    │   ├── references/godot/project-organization.md
    │   ├── references/godot/docs.md
    │   └── references/godot/ui.md
    ├── skills/collect-lessons/SKILL.md
    └── skills/write-tutorial/SKILL.md
```

所有路径已通过 `bash ls` 验证存在。

### 逐步骤诊断

| # | 所属节点 | 应有步骤 | 要求(来自plugin文件) | 实际步骤(来自log) | 达标? | 达标证据 / 不达标点 |
|---|---------|---------|---------------------|------------------|-------|-------------------|
| 1 | skills/exec/SKILL.md | 步骤6b: RED — spawn game-dev:test-agent | "使用 `references/exec-prompts.md` 的 **RED prompt** 模板组装 spawn prompt"（SKILL.md:146） | 子agent meta记录显示每个AI任务都有RED spawn（如AI-1 RED: ZombieData schema tests, toolUseId: call_019f32bee78e70c2bd98fb49） | ✅ | 所有8个AI任务都有对应RED test-agent spawn记录（来自subagents/*.meta.json），说明RED spawn被正确执行 |
| 2 | skills/exec/SKILL.md | 步骤6b: 记录RED日志 | "按 exec-logging.md RED 格式追加"（SKILL.md:152），exec-logging.md 要求格式：`### Iter {iter_N} — RED (test-agent) — {timestamp}` 含 Test file、Test cases 表格、Self-correction rounds、Verdict | tdd-iterations.md 中无任何 RED 格式的条目。文件从 `## [AI-1] GREEN — Test Run #1 — 2026-07-05` 开始，之前无RED记录 | ❌ | exec-logging.md 要求exec在每轮RED后立即追加记录（"每次 agent spawn 返回后**立即追加**"），但 tdd-iterations.md 中零条 RED 记录。exec 未执行日志记录义务。 |
| 3 | skills/exec/SKILL.md | 步骤6b: 检查RED结果 | "按 references/exec-prompts.md RED 检查规则验收。不合格 → 指出具体问题，重新 spawn"（SKILL.md:148-149）。exec-prompts.md RED检查规则："测试文件已创建、RED report 中所有testcase 都失败了且原因正确、没有 mock/假代码" | tdd-iterations.md 中无任何检查记录。无法从日志中确认exec是否执行了RED结果检查 | ❌ | exec-prompts.md 定义了3条RED检查规则（测试文件已创建、失败原因正确、无mock），但 tdd-iterations.md 中没有证据显示exec执行了这些检查。exec既未记录检查结果，也未记录"合格/不合格"判定。 |
| 4 | skills/exec/SKILL.md | 步骤6c: GREEN — spawn game-dev:coding | "使用 **GREEN prompt** 模板。从 test-agent 的 RED report 提取 testsuite 名称和 testcase 名称"（SKILL.md:156） | 子agent meta记录显示每个AI任务都有GREEN spawn（如AI-1 GREEN: implement ZombieData, toolUseId: call_019f32c0c4ba7b32a449cda0） | ✅ | 所有8个AI任务都有对应GREEN coding spawn记录。coding agent自验证报告显示目标testsuite全部通过 |
| 5 | skills/exec/SKILL.md | 步骤6c: 记录GREEN日志 | "按 exec-logging.md GREEN 格式追加"（SKILL.md:162）。exec-logging.md 要求：`### Iter {iter_N} — GREEN (coding-agent) — {timestamp}` 含 Files modified、Self-verification rounds、Verdict | tdd-iterations.md 中的GREEN条目由 coding agent 自行写入（使用 agent 定义中的 GREEN 日志格式），而非exec按 exec-logging.md 格式追加。格式为：`## [AI-N] GREEN — Test Run #N — date` | ⚠️ | tdd-iterations.md 中存在 GREEN 记录，但格式来自 coding agent 的自我日志（`agents/coding.md` 第162-208行定义的格式），而非 exec-logging.md 要求的 exec 格式（`### Iter {iter_N} — GREEN (coding-agent) — {timestamp}`）。log 中有内容但格式不符合 exec-logging.md 规范。风险：如果 coding agent 自身记录不完整，exec 无独立日志补充。 |
| 6 | skills/exec/SKILL.md | 步骤6c: 检查GREEN结果 | "按 references/exec-prompts.md GREEN 检查规则验收。不合格 → 指出具体问题，重新 spawn"（SKILL.md:158-159）。exec-prompts.md GREEN检查规则："coding-agent 自验证报告显示目标 testsuite 全部通过、未修改 game/tests/ 下文件、无 pass/TODO/NotImplemented 残留" | tdd-iterations.md 中无任何 exec 检查记录。coding agent 的自我报告声称全通过，但 exec 未独立验收 | ❌ | exec-prompts.md 定义了3条GREEN检查规则，但 tdd-iterations.md 中无exec的独立检查记录。Exec依赖coding agent自我报告（"Self-verification rounds: 1/5, Verdict: ✅"），但没有exec的独立验收判定。对AI-4，coding agent的GREEN redo跨越两天（07-05→07-06），exec未记录检查。 |
| 7 | skills/exec/SKILL.md | 步骤6d: VERIFY — spawn game-dev:test-agent（实现后独立验证门） | "使用 **VERIFY prompt**"（SKILL.md:166）。exec-prompts.md VERIFY prompt："独立验证 — 跑全量测试确认当前代码状态"，检查规则："全量测试全部通过" | AI-1和AI-2的meta记录中无VERIFY spawn。AI-3到AI-7有VERIFY spawn（如AI-3 VERIFY: independent re-run） | ❌ (AI-1, AI-2) | 子agent meta记录：AI-1 只有RED+GREEN（无VERIFY），AI-2 有RED+GREEN+额外fix（无VERIFY）。exec SKILL.md 步骤6d 是强制步骤（"使用 VERIFY prompt"），无例外条款。AI-1（ZombieData Resource）和AI-2（ZombieBase AI状态机）是后续所有任务的基础，跳过独立验证门违反了TDD循环的完整性。 |
| 8 | skills/exec/SKILL.md | 步骤6d: 记录VERIFY日志 | "按 exec-logging.md VERIFY 格式追加"（SKILL.md:172）。exec-logging.md 要求：`### Iter {iter_N} — VERIFY (test-agent) — {timestamp}` 含 Verdict | tdd-iterations.md 中无任何 VERIFY 格式的条目 | ❌ | 尽管 AI-3 到 AI-7 有 VERIFY spawn（meta记录确认），但 tdd-iterations.md 中零条 VERIFY 记录。exec-logging.md 要求"每次 agent spawn 返回后**立即追加**"（exec-logging.md:36），exec 未执行此义务。 |
| 9 | skills/exec/SKILL.md | 步骤6d: 检查VERIFY结果 | "按 references/exec-prompts.md VERIFY 检查规则验收。不合格 → 回退到 GREEN（6c）再修"（SKILL.md:168-169）。exec-prompts.md VERIFY检查："全量测试全部通过 合格 / 有失败时报告是否包含具体 testcase 名称和错误行" | tdd-iterations.md 中无任何 exec 对 VERIFY 结果的检查记录 | ❌ | exec 未记录对 VERIFY 结果的检查。AI-2 的 VERIFY 被跳过意味着ZombieBase状态机（24个testcase）从未经过独立验证门验证——只有 coding agent 的自我验证。此后的 AI-3 到 AI-7 都依赖 AI-2 的实现正确性。 |
| 10 | skills/exec/SKILL.md | 步骤6e: 边界检查 — 通用检查 | "测试文件隔离：coding agent 是否修改了测试文件？空代码/假代码：是否有 pass、# TODO、NotImplemented 残留？"（SKILL.md:180-183） | tdd-iterations.md 中无边界检查记录。coding agent的自我报告中偶尔提到边界检查（如AI-5 REFACTOR提到"grep pass\|TODO\|NotImplemented\|print → 0 命中"），但这是coding agent自查，不是exec主会话检查 | ❌ | exec SKILL.md 步骤6e 明确说"exec 主会话执行"边界检查，但 tdd-iterations.md 中无任何exec执行的边界检查记录。coding agent的自查（AI-5的REFACTOR日志中提到"Boundary: pass/TODO/NotImplemented/print → 0 hits"）是agent行为，不是exec的独立检查。只有 AI-5 和 AI-6 有部分边界检查痕迹（来自REFACTOR阶段），AI-1到AI-4、AI-7 完全没有边界检查痕迹。 |
| 11 | skills/exec/SKILL.md | 步骤6e: 边界检查 — 技术栈专属(Godot) | "资源引用完整性、节点路径有效性、信号连接有效性、文件路径有效性"（SKILL.md:187-191） | tdd-iterations.md 中无任何技术栈专属边界检查记录 | ❌ | exec SKILL.md 定义了4项Godot专属边界检查（资源引用完整性、节点路径有效性、信号连接有效性、文件路径有效性），但 tdd-iterations.md 中零条记录。对AI-4（zombie.tscn场景创建），这些检查尤其关键——实际上AI-4因为UID collision导致资源解析到错误的类型（zombie_data.gd被当作zombie_basic.tres的UID目标），如果exec执行了资源引用完整性检查，可以提前发现。 |
| 12 | skills/exec/SKILL.md | 步骤6f: REFACTOR — spawn game-dev:coding | "只有 VERIFY 全部通过后才执行"（exec-prompts.md:140）。使用 REFACTOR prompt + 边界违规清单 | 只有AI-5和AI-6有REFACTOR spawn（meta记录确认）。AI-1到AI-4、AI-7无REFACTOR spawn | ❌ (AI-1,2,3,4,7) | exec-prompts.md 说REFACTOR是完整TDD循环的一部分（步骤6a-6g），但7个AI任务中只有2个（AI-5、AI-6）执行了REFACTOR。exec SKILL.md 没有"简单任务可跳过REFACTOR"的例外条款。 |
| 13 | skills/exec/SKILL.md | 步骤6f: 记录REFACTOR日志 | "按 exec-logging.md REFACTOR 格式追加"（SKILL.md:218）。exec-logging.md 要求：`### Iter {iter_N} — REFACTOR (coding-agent) — {timestamp}` | AI-5和AI-6有REFACTOR记录，但格式来自coding agent（`### Iter 1 — REFACTOR (coding-agent) — date`），不是exec-logging.md格式 | ⚠️ | REFACTOR记录存在但格式来源是coding agent自记（agents/coding.md第237-244行），而非exec-logging.md要求。风险与#5相同。 |
| 14 | skills/exec/SKILL.md | 步骤6g: VERIFY — spawn game-dev:test-agent（重构后独立验证门） | "使用 **VERIFY prompt**"（SKILL.md:222）。检查规则："全量测试全部通过" | AI-5和AI-6有post-REFACTOR VERIFY spawn（meta记录：AI-5 VERIFY(post-REFACTOR)、AI-6 VERIFY(post-REFACTOR)）。AI-1,2,3,4,7无post-REFACTOR VERIFY | ❌ (AI-1,2,3,4,7) | 只有AI-5和AI-6有post-REFACTOR VERIFY。其他5个任务没有REFACTOR也没有post-REFACTOR VERIFY。 |
| 15 | skills/exec/SKILL.md | 步骤8: 最终验证 | "从 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md` 读取 test_cmd_full 并执行。验证全部通过"（SKILL.md:240） | tool-results/brjhgjy2s.txt 包含最终测试输出：`98/98 passed, 6 scripts, 162 asserts` | ✅ | tool-results/brjhgjy2s.txt 第613-624行显示全量测试结果："Scripts 6, Tests 98, Passing Tests 98, Asserts 162, Time 0.84s, ---- All tests passed! ----"。最终全量测试全部通过。 |
| 16 | skills/exec/SKILL.md | 步骤9: 收集开发经验 | "调用 `game-dev:collect-lessons` skill"（SKILL.md:244-248） | .work/collect-lessons-summary.md 存在 | ✅ | 产物 .godot-dev/feat-3/.work/collect-lessons-summary.md 存在，说明 collect-lessons 被执行。 |
| 17 | skills/exec/SKILL.md | 步骤10: 编写教学文档 | "仅 feat 和 refactor 任务执行此步骤"（SKILL.md:252）。调用 `game-dev:write-tutorial` | 产物中未发现 TUTORIAL.md 或 write-tutorial 执行痕迹 | ⚠️ | exec SKILL.md 步骤10明确要求feat任务调用write-tutorial（"将本次开发工作编写为教学文档，追加到项目 TUTORIAL.md"），但 .work/ 目录中无 write-tutorial 相关产物。无法从log确认是否执行。 |
| 18 | skills/exec/SKILL.md | 步骤6a: 标记开始 | "更新 progress.json：状态 → in_progress。按 exec-logging.md 初始化节初始化 tdd-iterations.md。创建 coding agent 日志目录"（SKILL.md:132-142） | progress.json 显示所有任务为"done"，tdd-iterations.md 存在但初始化格式不符合 exec-logging.md | ⚠️ | tdd-iterations.md 文件头为 `# TDD Iteration Log`，但 exec-logging.md 要求的初始化格式是追加任务分隔符 `## [AI-N] {任务描述} — 开始于 YYYY-MM-DD HH:MM:SS`。实际文件中每个任务以 `## [AI-N] GREEN — Test Run #1 — date` 开始，缺少 exec-logging.md 要求的"开始于"标记。 |
| 19 | skills/plan/SKILL.md | 步骤6: 任务描述不含 class 名 | "class 名不出现在任务描述中"（来自 plan SKILL.md:165 ❌ 例1："创建角色选择界面文件，定义 CharacterSelect 类"） | AI-3任务描述含 "ZombieBasic 子类"、AI-4含 "CharacterBody3D"、"CollisionShape3D"、"AnimationPlayer"、"Zombie_Basic" | ❌ | plan.md 第78-83行任务描述包含多个 class/type 名称。plan SKILL.md 步骤6 明确规定 "class 名不出现在任务描述中"（来自 ❌ 例1），但 AI-3（"ZombieBasic 子类"）、AI-4（"CharacterBody3D 根 + CollisionShape3D 胶囊 + AnimationPlayer"）违反此规则。 |
| 20 | skills/plan/SKILL.md | 步骤6: 任务描述不含方法名 | "方法名/函数名不出现在任务描述中"（来自 plan SKILL.md:167 ❌ 例2："在脚本文件中添加 select_character 入口函数"） | AI-2含 "take_damage"、AI-3含 "_ready"、AI-5含 "_attack_timer"、AI-6含 "queue_free" | ❌ | plan.md 第78-83行多处出现方法名。plan SKILL.md 步骤6 明确规定 "方法名/函数名不出现在任务描述中"（来自 ❌ 例2），但 AI-2（"take_damage"）、AI-3（"_ready"）、AI-5（"_attack_timer"）、AI-6（"queue_free"）违反此规则。 |
| 21 | skills/plan/SKILL.md | 步骤6: 任务描述用行为语言 | "描述 = 可验证的功能行为，用户操作后能看到什么"（来自 plan SKILL.md:172 ✅ 例1） | AI-1描述 "实现僵尸数据 Resource schema：数值字段、动画表、character_scene / animation_player_path 引用字段" — 描述的是数据结构，不是玩家可感知的行为 | ❌ | plan.md AI-1 任务描述（第77行）完全由技术术语构成（Resource schema、字段列表），没有描述任何玩家可感知的行为。plan SKILL.md 步骤6 ✅ 例1 要求"可验证：打开界面后能看到排列整齐的卡片列表"，即从用户视角描述。 |
| 22 | skills/plan/SKILL.md | 步骤6: 任务描述不含文件路径 | "文件名不出现在描述中"（来自 plan SKILL.md:197 规则表）。plan-format.md 禁止内容清单 grep：`grep -nP '\[AI-\d+\].*\.(rpy|gd|tscn|tres)\b' plan.md` 零命中 | grep检查 plan.md 任务描述行：AI-4含 "Zombie_Basic glTF 实例子节点"（含类型引用但非文件后缀） | ✅ | plan.md 任务描述行中未找到 `.gd`、`.tscn`、`.tres` 文件扩展名。虽然含有引擎类型名，但 plan-format.md 的 grep 规则针对的是文件扩展名。 |
| 23 | references/plan-format.md | plan.md格式校验：不含代码级API调用 | "不含代码级 API 调用（引擎特定 API、`scope[`、`assert len(` 等）——实现细节属于 agent 自主决策"（plan-format.md:223） | plan.md 第79行含 "take_damage(amount, hit_dir) 与玩家基类签名一致"，第83行含 "health <= 0 时切 DEAD 终态、播放死亡动画、发出 died 信号并清理节点" | ❌ | plan.md 设计摘要（第31-36行）和任务描述（第77-83行）多处出现引擎API级细节。plan-format.md 第223行明确禁止。虽然plan-format.md主要作用于 plan.md 任务列表，但设计摘要中嵌入代码级细节同样会让 coding agent 形成锚定效应。 |
| 24 | agents/coding.md | 关键规则2: 不写空壳/假代码 | "绝不写空壳/假代码。不允许 pass、# TODO 或 NotImplementedError"（coding.md:280） | tdd-iterations.md AI-2 条目提到 zombie_base.gd 包含 `pass` abstract stub。AI-6 REFACTOR 边界检查确认 "zombie_base.gd:251 pass abstract stub ✅ 保留(原 GREEN 已合法)" | ⚠️ | coding.md 规则2 写的是 "不允许 pass"，没有区分 abstract stub（合法的 Godot 模式）和空实现（不合规的假代码）。tdd-iterations.md AI-2 日志中 coding agent 必须额外解释 "Godot 4.7 framework限制" 才能保留 pass abstract stub。规则未区分 abstract stub vs 空实现，可能导致 coding agent 浪费时间去"修复"合法的 abstract stub pass，也可能让 coding agent 对真正违规的 pass 视而不见。这是插件规则歧义问题（在诊断范围内）。 |
| 25 | skills/exec/SKILL.md | 步骤6: 信息隔离清单 | "从 game-dev:test-agent 到 game-dev:coding：可以传 行为级失败描述 + 具体失败 testcase 名称和错误信息、设计文档路径。禁止传 测试源码、测试文件路径"（SKILL.md:93-95） | meta记录中可以看到AI-4有RED revision spawn（"AI-4 RED revision: align tests with actual architecture"），说明test-agent收到了额外上下文 | ⚠️ | 无法从meta记录确认exec在spawn coding agent时是否严格过滤了测试源码。但exec-prompts.md GREEN模板中只传了testsuite名称和testcase名称，不传测试源码路径——模板本身合规。风险：coding agent可能通过task_dir自行读取测试文件（coding agent允许Read），违反信息隔离意图。 |
| 26 | skills/exec/SKILL.md | 步骤4: 确认测试环境 | "硬门：测试运行器必须可用。测试目录必须存在。已知坑必须处理"（SKILL.md:89） | AI-0被创建为bootstrap任务来处理缺失的test/目录。tool-results/brjhgjy2s.txt 确认 GUT 9.7.0 可用 | ✅ | tool-results/brjhgjy2s.txt 第8行显示 "GUT version: 9.7.0"。plan.md AI-0 创建了 test/ 目录和 smoke test。测试环境确认通过。 |
| 27 | skills/exec/SKILL.md | TDD循环前：一次性读取参考文件 | "在开始循环前，一次性读取以下参考文件：exec-prompts.md、exec-logging.md、config.md、coding.md"（SKILL.md:122-126） | tdd-iterations.md 和meta记录无法直接证明exec是否读取了这些文件 | ⚠️ | 无法从log中直接确认exec是否"一次性读取"了所有4个参考文件。exec在spawn agent时使用了exec-prompts.md的模板（从GREEN prompt包含testsuite/testcase名称可推断），但无法确认exec-logging.md是否被读取（因为日志格式不符合exec-logging.md）。 |

### 根因分析与解决方案

| # | 应有步骤 | 达标? | 根因 | 解决方案 | 解决方案来源 |
|---|---------|-------|------|---------|-------------|
| 2 | 步骤6b: 记录RED日志 | ❌ | **护栏缺失**：exec-logging.md 要求"每次 agent spawn 返回后**立即追加**"（exec-logging.md:36），但 exec SKILL.md 没有将此要求设为硬门（Hard Gate）。exec 的步骤 6b 列出了3个子步骤（spawn → 检查结果 → 记录日志），但没有像 agent 的"自我验证协议"那样用"先记日志再改代码"的铁律强制执行。结果：exec 执行了 spawn 和检查，但跳过了日志记录。 | 在 exec SKILL.md 步骤 6b/6c/6d/6f/6g 的每个子步骤中，将"记录日志"从步骤末尾提升到步骤开头，并加入类似 agent 的"先记日志再改代码"铁律：**"spawn 返回后第一件事：追加日志。不等检查结果。"** | `references/harness-methodology.md` 机制 #4 (Hard Gate)、机制 #11 (铁律)。coding agent 已有类似机制（coding.md:103 "先记日志，再改代码"），exec 应镜像。 |
| 3 | 步骤6b: 检查RED结果 | ❌ | **护栏缺失**：exec-prompts.md 定义了 RED/GREEN/VERIFY/REFACTOR 检查规则，但 exec SKILL.md 步骤 6b 的检查指令是"按 references/exec-prompts.md RED 检查规则验收"——这是一个引用，不是嵌入的检查清单。exec 读取了引用文件但没有将其转化为必须逐项打勾的检查表。结果：exec 可以声称"检查了"但没有任何证据。 | 将 exec-prompts.md 中的检查规则**直接嵌入** exec SKILL.md 每个步骤的正文中（不再只是引用），每条检查规则前加 `[ ]` checkbox 格式，要求 exec 输出检查结果。例如步骤 6b 嵌入：`- [ ] 测试文件已创建（路径：___） - [ ] 所有 testcase 失败且原因正确（非语法错误） - [ ] 无 mock/假代码` | `references/harness-methodology.md` 机制 #6 (内联检查清单)。对比 coding agent 的"诊断完成前自检清单"（coding.md:148-156），该清单直接嵌入 agent 定义文件，agent 无法跳过。 |
| 5 | 步骤6c: 记录GREEN日志 | ⚠️ | **双重日志源冲突**：exec-logging.md 定义了 exec 的日志格式，coding.md 定义了 coding agent 的自记格式（coding.md:162-208）。两套格式并存，但 tdd-iterations.md 只有一个文件。coding agent 的 GREEN 模式要求它"先记日志再改代码"（coding.md:103），所以 coding agent 会自行追加。exec 也"应该"追加，但 coding agent 已经写了，exec 就不再写。结果：日志只有 agent 视角，没有 exec 视角（spawn 参数、检查判定、重试决策）。 | 在 exec-logging.md 中明确**双日志机制**：exec 在主会话输出中记录 spawn/check/retry 决策（不入 tdd-iterations.md），tdd-iterations.md 只由 agent 写入（作为 agent 工作记录）。exec 的"Completion Gate"检查 tdd-iterations.md 完整性而非自己写。 | `references/skill-structure.md` §日志分离。对比 game-dev 插件架构中 agent 隔离规则（agents 不互写文件），exec 和 agent 写同一文件也违反了隔离原则。 |
| 6 | 步骤6c: 检查GREEN结果 | ❌ | **根因同 #3**：exec-prompts.md 的检查规则是引用而非嵌入。exec 可以在 spawn 返回后直接进入下一阶段而不输出检查清单。 | 同 #3 方案：将 GREEN 检查规则内联嵌入 exec SKILL.md 步骤 6c，格式化为 checkbox 清单。 | 同 #3 |
| 7 | 步骤6d: VERIFY spawn (AI-1, AI-2) | ❌ | **流程设计缺陷**：exec SKILL.md 步骤 6d 说"不合格 → 回退到 GREEN（6c）再修"，但没有说"合格 → 进入 6e"——步骤 6d 和 6e 之间的连接是隐式的（下一个步骤就是 6e）。对于 AI-1（ZombieData Resource，18 个 testcase 首跑全绿）和 AI-2（ZombieBase，coding agent 自验证全绿），exec 可能将 coding agent 的"首跑全绿"等同于"不需要独立 VERIFY"。但 exec 的核心原则之一是"exec 不做判断，只做传递"——跳过 VERIFY 就是做了判断（"首跑全绿 = 不需要独立验证"）。 | 在 exec SKILL.md 步骤 6c 和 6d 之间加入**显式硬门**："无论 GREEN 自验证结果如何，必须执行 VERIFY。GREEN 全绿不是跳过 VERIFY 的理由——VERIFY 验证的是'独立测试环境下的全量测试'，不是'coding agent 自己跑的测试'。" | `references/harness-methodology.md` 机制 #1 (Hard Gate)。对比 exec SKILL.md 已有的 Red Flags（SKILL.md:37-49），应增加一条："'首跑全绿，不需要 VERIFY 了' → STOP。VERIFY 是独立验证门，不是 GREEN 的补充。" |
| 8 | 步骤6d: 记录VERIFY日志 | ❌ | **根因同 #2**：exec 未执行日志记录义务。即使 AI-3 到 AI-7 实际 spawn 了 VERIFY agent，exec 也没有记录。 | 同 #2 方案 | 同 #2 |
| 9 | 步骤6d: 检查VERIFY结果 | ❌ | **根因同 #3**：检查规则引用而非嵌入。 | 同 #3 方案 | 同 #3 |
| 10 | 步骤6e: 边界检查(通用) | ❌ | **护栏缺失 + 流程设计**：边界检查（步骤 6e）被定位在"VERIFY 全部通过后、REFACTOR 之前"。但 AI-1 到 AI-4、AI-7 都没有 REFACTOR，所以边界检查也一起被跳过了。exec SKILL.md 的流程暗示边界检查只是 REFACTOR 的前置步骤，而非独立的质量门。实际上，边界检查应该对每个任务执行（无论是否 REFACTOR），因为它检查的是 agent 隔离违规（coding agent 是否修改了测试文件）和代码卫生（pass/TODO 残留）。 | 将步骤 6e 从 REFACTOR 前置步骤改为**独立的质量门**，放在步骤 6d（VERIFY）之后，硬性要求对每个任务执行。如果无违规则标记为 clean 进入下一阶段；如果有 REFACTOR 则写入边界违规清单。即使跳过 REFACTOR，边界检查本身不能跳过。 | `references/harness-methodology.md` 机制 #7 (独立质量门)。exec SKILL.md 的流程图（SKILL.md:18-25）应明确标注"边界检查 = 每个任务的独立门，不是 REFACTOR 的子步骤"。 |
| 11 | 步骤6e: 边界检查(Godot专属) | ❌ | **同 #10 + 实现成本**：Godot 专属的4项边界检查（资源引用完整性、节点路径有效性、信号连接有效性、文件路径有效性）需要读取 .tscn 和 .gd 文件进行交叉验证。exec 作为主会话不是专门做代码分析的——这比通用检查（grep pass/TODO）复杂得多。缺乏工具支持导致 exec 倾向于跳过。 | 将 Godot 专属边界检查实现为**独立的边界检查脚本**（skills/exec/references/check-boundary-godot.sh），exec 只需运行脚本并读取输出。脚本用 grep/sed 检查 .tscn ext_resource 引用完整性、$NodeName 路径有效性、信号连接有效性、文件路径有效性。 | `references/harness-methodology.md` 机制 #13 (自动化检查)。对比 config.md 的 test_cmd_full（一键运行），边界检查也需要一键脚本。 |
| 12 | 步骤6f: REFACTOR spawn (AI-1,2,3,4,7) | ❌ | **流程设计缺陷**：exec SKILL.md 的 TDD 循环描述为 "RED → GREEN → VERIFY → 边界检查 → REFACTOR → VERIFY"，但 exec 实际行为表明简单任务跳过了 REFACTOR。根本原因是 exec SKILL.md 没有定义"何时可以跳过 REFACTOR"的明确规则，导致 exec 自行判断。AI-1（首跑全绿）和 AI-7（只改 main.tscn 一个文件）被判定为"不需要重构"。 | 在 exec SKILL.md 步骤 6f 前增加**REFACTOR 触发规则**：① 边界检查有违规 → 必须 REFACTOR；② GREEN 阶段修改了 >1 个文件 → 必须 REFACTOR（需要检查跨文件一致性）；③ GREEN 阶段有 >1 轮自我验证 → 必须 REFACTOR（代码有迭代痕迹）；④ 以上均不满足 → REFACTOR 可选（标记为"跳过 REFACTOR：{原因}"）。 | `references/harness-methodology.md` 机制 #8 (明确触发条件)。对比 agent 的"重试上限"规则（coding.md:157-159），exec 也需要量化的 REFACTOR 触发条件而非主观判断。 |
| 13 | 步骤6f: 记录REFACTOR日志 | ⚠️ | **根因同 #5**：双重日志源冲突。 | 同 #5 方案 | 同 #5 |
| 14 | 步骤6g: post-REFACTOR VERIFY spawn | ❌ | **连锁效应**：#12 导致 #14。没有 REFACTOR 就没有 post-REFACTOR VERIFY。 | 同 #12 方案（如果 REFACTOR 被触发则 post-REFACTOR VERIFY 自然跟随） | 同 #12 |
| 17 | 步骤10: write-tutorial | ⚠️ | **Completion Gate 无强制执行**：exec SKILL.md 步骤 10 在 Completion Gate 中列出（SKILL.md:280 "game-dev:write-tutorial 已完成（feat/refactor）"），但步骤 10 正文中只是说"调用 game-dev:write-tutorial skill"，没有硬门强制。exec 可能在步骤 9（collect-lessons）之后认为"流程完成"而跳过步骤 10。 | 在步骤 10 的正文中加硬门："**硬门：** collect-lessons 和 write-tutorial 必须全部完成才能声明 Completion Gate 通过。步骤 9 完成后立即进入步骤 10，不得在步骤 9 之后输出完成报告。" | `references/harness-methodology.md` 机制 #1 (Hard Gate)。exec 的 Completion Gate（SKILL.md:273-282）列出了6个条件，但没有在步骤正文中为每个条件设置硬门。 |
| 18 | 步骤6a: 初始化格式 | ⚠️ | **根因同 #5**：tdd-iterations.md 的初始化和写入由 coding agent 而非 exec 执行。exec SKILL.md 步骤 6a 说 exec 初始化，但 coding agent 的 GREEN 模式在 Phase 1 也会追加（coding.md:167），导致 agent 覆盖了 exec 的初始化。 | 同 #5 方案（日志职责分离） | 同 #5 |
| 19 | plan步骤6: 不含class名 | ❌ | **规则执行无硬门**：plan SKILL.md 步骤 6 定义了 6 对 ❌/✅ 示例和 5 条规则，但步骤 10 的"格式自检"只检查 plan-format.md 的禁止内容清单（grep 命令），不检查任务描述中的 class 名/方法名。plan-format.md 的 grep 命令扫描的是文件扩展名和代码级表达式，不扫描 class 名模式（PascalCase 标识符）。结果：plan 通过了所有 grep 自检但仍然输出了含 class 名的任务描述。 | 在 plan-format.md 的"自检 grep 命令"中增加一条：`grep -nP '\[AI-\d+\].*\b[A-Z][a-z]+[A-Z]\w*\b' {task_dir}/plan.md` — 检测任务描述中的 PascalCase 标识符（class名）。将此 grep 加入步骤 10 "格式自检"强制执行。 | `references/plan-format.md` §禁止内容清单 — 扩展现有 grep 命令集。对比现有 grep 规则（plan-format.md:258-281），同类扫描需要扩展覆盖范围。 |
| 20 | plan步骤6: 不含方法名 | ❌ | **根因同 #19**：grep 自检不扫描 snake_case 方法名模式。 | 在 plan-format.md 的"自检 grep 命令"中增加：`grep -nP '\[AI-\d+\].*\b[a-z]+_[a-z]+\b' {task_dir}/plan.md` — 检测 snake_case 模式（可能的函数名/变量名）。 | 同 #19 |
| 21 | plan步骤6: 用行为语言 | ❌ | **规则执行无硬门**：plan SKILL.md 步骤 6 的 5 条描述写作规则（用行为语言、可独立验证、不含文件路径、不含代码符号、不含"测试"）没有对应的机械化检查。grep 可以检查"不含文件路径"和"不含代码符号"，但"用行为语言"和"可独立验证"是语义要求——只有人工审查能判断。plan 没有在步骤 10 要求"逐条人工复查 5 条规则"，导致语义违规漏过。 | 在步骤 10 格式自检中增加**人工复查步骤**："逐条阅读每个 AI 任务描述，问：① 描述了用户做什么→看到什么吗？（行为语言）② 不看其他任务能判断完成吗？（可独立验证）③ 含代码术语吗？（class名/方法名/引擎类型名）——任一条不满足则改写。" | `references/harness-methodology.md` 机制 #15 (人工复查门)。grep 能检查字符串，不能检查语义。语义规则必须有人工复查步骤。 |
| 23 | plan.md含代码级API调用 | ❌ | **plan-format.md 规则不完整**：plan-format.md 第 223 行说"不含代码级 API 调用"，但 grep 命令（plan-format.md:264）只扫描 `scope[`、`assert len(`、`assert scope` 这 3 个 Ren'Py 特定模式。对 Godot 代码级 API（如 `take_damage(amount)`、`queue_free`、`_attack_timer`），grep 无法检测。 | 在 plan-format.md 的"自检 grep 命令"中针对 Godot 增加模式：`grep -nPi '(func\s+\w+\s*\(|\.connect\(|queue_free|_ready|_process|_physics_process|@export|preload\(|load\()' {task_dir}/plan.md` | `references/plan-format.md` §禁止内容清单。grep 规则应该覆盖当前技术栈的代码级模式。 |
| 24 | coding.md "禁止pass"未区分abstract stub | ⚠️ | **规则歧义**：coding.md 规则2（coding.md:280）写的是"绝不写空壳/假代码。不允许 pass、# TODO 或 NotImplementedError"。在 Godot 中，`@abstract` 类的空方法用 `pass` 是语言要求的正确模式（`@abstract` 不允许实例化，子类必须 override）。coding agent 在 AI-2 遇到此歧义——`test_zombie_base_is_abstract` 失败，coding agent 需要额外诊断才能确认 `pass` abstract stub 是合法的。规则不加区分会导致两个方向的问题：agent 浪费时间"修复"合法 pass（churn），或 agent 对真正违规的 pass 视而不见（漏检）。 | 修改 coding.md 规则2 为："绝不写空壳/假代码。不允许 `# TODO`、`NotImplementedError`、非 abstract 方法中的 `pass`（`@abstract` 方法的 `pass` stub 除外）。" 同时在 Godot coding.md 附录增加 `@abstract pass` 的合法用例说明。 | `references/agent-structure.md` §规则清晰性。对比 coding.md 已有机制的精确性（如"自我验证协议"分为 Phase 1/2/3 三个层次），关键规则也应精确到场景级别。 |
| 25 | 信息隔离: exec → coding | ⚠️ | **设计缺陷 — spawn prompt 传递设计文档路径**：exec-prompts.md GREEN prompt 中明文告诉 coding agent 读取 `{task_dir}/plan.md` 和 `{task_dir}/.work/design.md`（exec-prompts.md:79-81）。coding agent 从这些文件中可以获得完整的实现方案（含 class 名、方法签名等），这削弱了"只传行为描述"的信息隔离意图。但 dir_path 传递是不可避免的（agent 需要定位项目）。 | 不需要修改（当前设计是有意为之）。coding agent 读设计文档是设计意图——exec SKILL.md 步骤 5 信息隔离清单只禁止传测试源码，不禁止传设计文档。GREEN prompt 中明确列出"需要读取的文件"是功能而非 bug。 | exec-prompts.md:78-85 |
| 27 | 参考文件一次性读取 | ⚠️ | **缺乏自证机制**：exec SKILL.md 步骤 6 的"一次性读取"指令（SKILL.md:122-126）要求 exec 在开始循环前读取 4 个参考文件，但没有要求 exec 回显确认（类似 orchestrator 的 Step 0b 硬门："回显确认后才能调用"）。结果：无法从 log 区分"读了但没按格式执行"和"没读所以不知道格式"。 | 在 exec SKILL.md 步骤 6 前增加**初始化确认块**，要求 exec 回显：`已读取: exec-prompts.md (RED/GREEN/VERIFY/REFACTOR 模板已加载), exec-logging.md (日志格式已加载), config.md (test_cmd_full={cmd}), coding.md (边界检查规则={N}条)`。 | `references/harness-methodology.md` 机制 #3 (回显确认)。对标 orchestrator Step 0b 的强制回显机制（orchestrator SKILL.md:79-87）。 |

### 修复状态

| # | 状态 |
|---|------|
| 2 | ✅ 已修复：exec SKILL.md 增加"日志铁律" |
| 3 | ✅ 已修复：exec SKILL.md 步骤 6b 嵌入 checkbox 检查清单 |
| 5 | ✅ 已修复：exec-logging.md 增加"日志职责分离"表 |
| 6 | ✅ 已修复：exec SKILL.md 步骤 6c 嵌入 checkbox 检查清单 |
| 7 | ✅ 已修复：exec SKILL.md 步骤 6c 增加 VERIFY 硬门 |
| 8 | ✅ 已修复：exec SKILL.md 增加"日志铁律" |
| 9 | ✅ 已修复：exec SKILL.md 步骤 6d 嵌入 checkbox 检查清单 |
| 10 | ✅ 已修复：exec SKILL.md 步骤 6e 改为独立质量门 |
| 11 | ⚠️ 部分修复：步骤 6e 增加强制声明和日志格式，但 Godot 专属自动化脚本（check-boundary-godot.sh）需要后续创建 |
| 12 | ✅ 已修复：exec SKILL.md 步骤 6f 增加 REFACTOR 触发规则表 |
| 13 | ✅ 已修复：exec-logging.md 增加"日志职责分离"表 |
| 14 | ✅ 已修复：REFACTOR 触发规则修复连锁修复 |
| 17 | ✅ 已修复：exec SKILL.md 步骤 10 增加硬门 |
| 18 | ✅ 已修复：exec SKILL.md 增加回显确认块 + exec-logging.md 日志职责分离 |
| 19 | ✅ 已修复：plan-format.md 增加 PascalCase 标识符扫描 grep |
| 20 | ✅ 已修复：plan-format.md 增加 snake_case 标识符扫描 grep |
| 21 | ⚠️ 部分修复：plan-format.md 增加"语义复查"人工步骤，但语义检查无法自动化 |
| 23 | ✅ 已修复：plan-format.md 增加 Godot API 扫描 grep |
| 24 | ✅ 已修复：coding.md 规则2 区分 @abstract stub |
| 25 | ⏭️ 不在范围 — 当前设计是有意为之 |
| 27 | ✅ 已修复：exec SKILL.md 增加回显确认块 |
