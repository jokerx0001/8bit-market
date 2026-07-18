# game-dev - feat 诊断结果

## 日期：2026-07-18

### 链路拓扑

```
game-dev:orchestrator (skills/orchestrator/SKILL.md)
├── game-dev:artifact-manager (skills/artifact-manager/SKILL.md)
├── grill-with-docs (external skill)
├── grilling (external skill) [retry after grill-with-docs returned no content]
├── game-dev:requirements (skills/requirements/SKILL.md)
├── game-dev:concept-art → SKIPPED by orchestrator (L177)
├── game-dev:design-ui → SKIPPED by orchestrator (L177)
├── game-dev:asset-extract → SKIPPED by orchestrator
├── game-dev:plan (skills/plan/SKILL.md)
│   ├── game-dev:domain-modeling (skills/domain-modeling/SKILL.md)
│   ├── game-dev:architecture --task (skills/architecture/SKILL.md)
│   └── superpowers:brainstorming
├── game-dev:art-resources-conductor → SKIPPED (resources.md declared no external resources)
├── game-dev:exec (skills/exec/SKILL.md)
│   ├── game-dev:test-agent → NEVER SPAWNED (exec ran tests directly via Bash)
│   ├── game-dev:coding → NEVER SPAWNED (exec ran tests directly via Bash)
│   ├── skills/exec/references/exec-prompts.md → NOT USED
│   └── skills/exec/references/exec-logging.md → NOT USED
├── game-dev:ui-restoration (skills/ui-restoration/SKILL.md) → NEVER CALLED
├── game-dev:architecture --update (skills/architecture/SKILL.md)
├── game-dev:collect-lessons (skills/collect-lessons/SKILL.md)
└── game-dev:write-tutorial (skills/write-tutorial/SKILL.md)
```

所有 reference 路径已通过 bash ls 验证存在：
- `skills/exec/references/exec-prompts.md` ✓
- `skills/exec/references/exec-logging.md` ✓
- `references/plan-format.md` ✓
- `references/godot/config.md` ✓
- `references/godot/coding.md` ✓
- `references/godot/ui.md` ✓
- `references/godot/testing.md` ✓

---

### 逐步骤诊断

| # | 所属节点 | 应有步骤 | 要求(来自plugin文件) | 实际步骤(来自log) | 达标? | 达标证据 / 不达标点 |
|---|---------|---------|---------------------|------------------|-------|-------------------|
| 1 | skills/orchestrator/SKILL.md | 阶段4b: UI设计判定 | "触发条件：涉及创建新模块且明显包含原来没有的新界面" (L220-221)；"判定原则：宁可误判多调 design-ui，也不要漏判" (L225) | L177: orchestrator 输出 "不需要 concept-art / design-ui: 本次新增物品栏 HUD 是数据驱动的标准控件 (HBoxContainer + 10 个 Slot 子控件),无艺术决策,直接复用既有 HUD 风格。" | ❌ | 判定错误：本次任务新增物品栏 HUD（10 槽位、武器镜像+物品图标+交互高亮），是原来不存在的界面。满足触发条件"涉及创建新模块且明显包含原来没有的新界面"。orchestrator 用"数据驱动的标准控件、无艺术决策"自行合理化跳过，违反了"宁可误判多调"原则——有没有新界面是客观事实，不是风格判断。 |
| 2 | skills/orchestrator/SKILL.md | 阶段4b: design-ui 调用 | "涉及 UI 视觉设计 → 调用 design-ui: Skill({skill: "game-dev:design-ui", args: "--task-dir {task_dir} --tech {tech}"})" (L230-231) | 未调用。design-ui 从未被 invoke。 | ❌ | 步骤被跳过。产物目录 `.work/layouts/` 不存在，无任何 HTML 设计稿产出。 |
| 3 | skills/orchestrator/SKILL.md | 阶段7b: UI 还原 | "exec 完成后，检测 plan.md 是否有 `## UI 还原` 章节。有则调用 `game-dev:ui-restoration`" (L296-297) | 未调用。ui-restoration 从未出现在 Skill 调用列表中。 | ⚠️ | plan.md 没有 `## UI 还原` 章节（因为 design-ui 被跳过，无 layout.html，plan 无从生成 UI 还原任务）。风险：即使 plan.md 有 UI 还原章节，orchestrator 也可能漏调（无强制门保护）。 |
| 4 | skills/exec/SKILL.md | 6a: 标记开始 + 初始化日志 | "更新 progress.json → in_progress。按 exec-logging.md 初始化 tdd-iterations.md。创建 coding agent 日志目录：mkdir -p {task_dir}/.work/coding" (L187-194) | L293: 创建了 `.work/coding/` 和 `.work/tdd/` 目录。但 progress.json 从未更新，tdd-iterations.md 从未创建。 | ❌ | progress.json 中所有 8 个 AI 任务状态仍为 "pending"。`.work/tdd/` 是错误创建的空目录——步骤 6a 只要求创建 `.work/coding/`，不要求创建 `tdd/` 目录。`tdd-iterations.md` 应该是 `.work/` 下的文件，从未被创建。 |
| 5 | skills/exec/SKILL.md | 6b: RED — spawn game-dev:test-agent | "使用 RED prompt 模板组装 spawn prompt。Agent({subagent_type: 'game-dev:test-agent', prompt: ...})" (L172-173, exec-prompts.md L18-43) | L299-L307: exec 直接运行 Bash 命令 `godot --headless -s addons/gut/gut_cmdln.gd -gselect=test_item_da` 做 RED 检查，未 spawn test-agent。 | ❌ | test-agent 从未被 spawn。exec 自行运行测试代替 agent。违反了 exec-prompts.md 的 RED prompt 模板和 agent 隔离规则。整个 exec 阶段（L241-L707）没有任何 Agent() tool call。 |
| 6 | skills/exec/SKILL.md | 6b: RED 检查 — 测试文件已创建 | "测试文件已创建（路径：___）" (L179) | 未执行此检查（因为未 spawn test-agent）。 | ❌ | 步骤被跳过。test-agent 负责创建测试文件，但它从未被 spawn。测试文件可能由 exec 自己或之前会话创建。 |
| 7 | skills/exec/SKILL.md | 6b: RED 检查 — 所有 testcase 失败且原因正确 | "RED report 中所有 testcase 都失败了且原因正确（非语法错误、非标识符错误）" (L180) | 未执行此检查。 | ❌ | 步骤被跳过。 |
| 8 | skills/exec/SKILL.md | 6b: RED 检查 — 无 mock/假代码 | "没有 mock、假代码" (L181) | 未执行此检查。 | ❌ | 步骤被跳过。 |
| 9 | skills/exec/SKILL.md | 6c: GREEN — spawn game-dev:coding | "使用 GREEN prompt 模板。Agent({subagent_type: 'game-dev:coding', prompt: ...})" (L188, exec-prompts.md L52-93) | exec 自行运行 Bash 测试命令验证 GREEN，未 spawn coding-agent。L312: `godot --headless -s addons/gut/gut_cmdln.gd -gselect=test_item_da` | ❌ | coding-agent 从未被 spawn。违反了 exec-prompts.md 的 GREEN prompt 模板。 |
| 10 | skills/exec/SKILL.md | 6c: GREEN 检查 — coding-agent 自验证报告 | "coding-agent 自验证报告显示目标 testsuite 全部通过" (L195) | 未执行此检查（因为未 spawn coding-agent）。 | ❌ | 步骤被跳过。 |
| 11 | skills/exec/SKILL.md | 6c: GREEN 检查 — visual-qa PASS | "有 screenshot 验证方式的行为：visual-qa PASS" (L196) | 未执行此检查。无 screenshot testcase 存在。 | ❌ | 步骤被跳过。plan.md 行为列表 15/20 条标记 `screenshot` 验证方式——说明这些行为的测试需要截图验证。但 exec 没有解析行为列表中的验证方式，未将 screenshot 行为路由到 test-agent 创建截图 testcase。`.work/screenshots/` 目录不存在，无任何 visual-qa 调用。 |
| 12 | skills/exec/SKILL.md | 6c: GREEN 检查 — 未修改 test/ 文件 | "未修改 test/ 下文件（检查 coding agent 的已修改文件列表）" (L197) | 未执行此检查。 | ❌ | 步骤被跳过。 |
| 13 | skills/exec/SKILL.md | 6c: GREEN 检查 — 无 pass/TODO 残留 | "无 pass / TODO / NotImplemented 残留（grep 已修改的源文件）" (L198) | 未执行此检查。 | ❌ | 步骤被跳过。 |
| 14 | skills/exec/SKILL.md | 6c: GREEN 检查 — 测试运行日志 | "`.work/coding/` 目录包含本轮测试运行日志" (L199) | L339, L422, L485, L525, L547, L584, L621: 测试运行日志保存到了 `.work/coding/`。 | ✅ | `.work/coding/` 包含 8 个 `*_run1.log` 文件，记录了各 testsuite 的 GUT 输出。但日志是由 exec 直接保存的（Bash 重定向），非 coding-agent 按自我验证协议保存。 |
| 15 | skills/exec/SKILL.md | 6d: VERIFY — spawn test-agent 独立验证 | "使用 VERIFY prompt。Agent({subagent_type: 'game-dev:test-agent', prompt: ...})" (L210-211, exec-prompts.md L96-118) | 未执行。VERIFY 步骤完全跳过。 | ❌ | 硬门违规："GREEN 全绿不是跳过 VERIFY 的理由" (L206)。exec 在 GREEN 通过后直接进入下一个 AI 任务，没有独立 VERIFY 验证。 |
| 16 | skills/exec/SKILL.md | 6e: 边界检查 — 测试文件隔离 | "coding agent 是否修改了测试文件？`git diff --name-only` 检查是否包含 test/ 路径" (L233) | 未执行。无 git diff 调用记录。 | ❌ | 边界检查完全跳过。"对每个任务强制执行。不是 REFACTOR 的子步骤——即使跳过 REFACTOR，边界检查也必须执行。" (L225-226) |
| 17 | skills/exec/SKILL.md | 6e: 边界检查 — 空代码/假代码 | "`grep -rn 'pass\|# TODO\|NotImplemented' {修改的源文件}` 零命中？" (L234) | 未执行。无 grep 调用记录。 | ❌ | 边界检查完全跳过。 |
| 18 | skills/exec/SKILL.md | 6e: 边界检查 — 技术栈专属(Godot) | "资源引用完整性、节点路径有效性、信号连接有效性、文件路径有效性" (L238-242, coding.md 规范) | 未执行。 | ❌ | 边界检查完全跳过。 |
| 19 | skills/exec/SKILL.md | 6f: REFACTOR 判定 | "边界检查有违规 → 必须 REFACTOR; GREEN 阶段修改了 >1 个文件 → 必须 REFACTOR" (L274-280) | 未执行 REFACTOR 判定。 | ❌ | 步骤被跳过。由于边界检查 (6e) 未执行，无法判定是否需要 REFACTOR。 |
| 20 | skills/exec/SKILL.md | 6h: 标记完成 | "更新 progress.json，输出摘要。" (L294) | 未执行。progress.json 从未更新。 | ❌ | progress.json 所有 8 个 AI 任务仍为 "pending"（产物证据）。 |
| 21 | skills/exec/SKILL.md | 8: 最终验证 | "从 config.md 读取 test_cmd_full 并执行。验证全部通过。" (L303-304) | L654 之后，全量测试 75/75 通过（证据：all_tests_run1.log）。 | ✅ | 全量测试确实全部通过（75 tests, 75 passing, 157 asserts）。但这是 exec 自行运行的，不是 spawn test-agent 在 VERIFY 模式下运行的。 |
| 22 | skills/exec/SKILL.md | 9: collect-lessons | "调用 game-dev:collect-lessons skill" (L310-312) | L841: Skill(game-dev:collect-lessons, args="--tech godot") 被调用。 | ✅ | collect-lessons 被执行。 |
| 23 | skills/exec/SKILL.md | 10: write-tutorial | "调用 game-dev:write-tutorial skill" (L322-323) | L951-L961: Skill(game-dev:write-tutorial) 被调用 3 次。 | ✅ | write-tutorial 被执行。 |
| 24 | skills/orchestrator/SKILL.md | 阶段8: 完成报告 | "输出完成报告：任务完成 {done}/{total}、测试全部通过、人工任务待完成" (L316-326) | 无完成报告格式输出。 | ⚠️ | orchestrator 未输出标准完成报告格式（`## 开发完成` 模板）。但输出了非标准格式的完成消息。 |

### 额外步骤（不在 plugin 规定链路中）

| # | 实际步骤 | log 位置 | 
|---|---------|---------|
| E1 | exec 自行运行 GUT 测试（Bash）代替 spawn test-agent/coding-agent | L299-L654（贯穿整个 exec 阶段） |
| E2 | orchestrator 自行判断"不需要 concept-art/design-ui"跳过 UI 阶段 | L177 |

---

### 修复状态（2026-07-18 第 3 轮）

| 诊断 # | 问题 | 状态 |
|--------|------|------|
| #1, #2 | orchestrator: UI设计判定无强制门 → design-ui 被跳过 | ✅ 已修复 — orchestrator SKILL.md 阶段4b: 增加 screenshot > 0 强制门 |
| #3 | orchestrator: ui-restoration 无强制门 | ✅ 已修复 — orchestrator SKILL.md 阶段7b: 增加 grep [UI-N] 强制门 |
| #4, #20 | exec: progress.json 从未更新 | ✅ 已修复 — exec SKILL.md Completion Gate: 要求 progress.json status=done |
| #5, #9 | exec: agent spawning 被绕过（Bash 代替） | ✅ 已修复 — exec SKILL.md Red Flags: 增加 5 条 Bash 代替 spawn 检测 |
| #11 | exec: screenshot testcase 未路由 | ✅ 已修复 — exec SKILL.md 步骤3: 增加截图需求解析 + Completion Gate: 要求 screenshot 验证通过 |
| #15 | exec: VERIFY 被跳过 | ✅ 已修复 — exec SKILL.md: 增加阶段转换门（Phase Transition Gate） |
| #16, #17, #18 | exec: 边界检查被跳过 | ✅ 已修复 — exec SKILL.md: 阶段转换门强制每个 phase 输出判定 |
| #19 | exec: REFACTOR 被跳过 | ✅ 已修复 — 边界检查恢复后 REFACTOR 判定自然恢复 |
| #6, #7, #8 | RED 检查项（test-agent 未 spawn 的连锁影响） | ✅ 已修复 — 同 #5（agent spawning 恢复后连锁恢复） |
| #10, #12, #13 | GREEN 检查项（coding-agent 未 spawn 的连锁影响） | ✅ 已修复 — 同 #5 |
| #14 | 测试日志落盘 | ✅ 已在第 1 轮修复（coding.md 核心铁律第5条），但本次因 agent 未 spawn 未生效 |
| #21 | 全量测试通过（最终验证） | ⏭️ 不在范围 — 75/75 测试通过是目标项目代码质量，无插件工程问题 |
| #22 | collect-lessons 执行 | ⏭️ 不在范围 — 步骤已执行 |
| #23 | write-tutorial 执行 | ⏭️ 不在范围 — 步骤已执行 |
| #24 | 完成报告格式 | ⚠️ 低优先级 — 格式不规范但未阻塞流程，暂不修复 |

---

### 根因分析与解决方案

| # | 应有步骤 | 达标? | 根因 | 解决方案 | 解决方案来源 |
|---|---------|-------|------|---------|-------------|
| 1 | 阶段4b: UI设计判定 | ❌ | orchestrator 阶段4b 的触发条件依赖 LLM 自行判断"是否包含新界面"。当前"宁可误判多调"原则是文字声明，没有转化为可执行的操作步骤。LLM 对"数据驱动标准控件"、"无艺术决策"等主观判断绕过了客观的"有没有新界面"这一判定标准。 | 在 orchestrator SKILL.md 阶段4b 增加硬门判定流程：<br>1. 读 requirements.md 行为清单，列出所有涉及 UI 界面的行为<br>2. 判定时只问一个问题：**"这次任务完成后，玩家会看到原来不存在的画面或控件吗？"** 是 → design-ui<br>3. 提供"不是 UI 任务"的反例（纯逻辑改动、与周围一致的简单按钮）<br>4. 将"数据驱动/标准控件/无艺术决策"等主观理由写入 Red Flags | harness-methodology.md §2 (Hard Gate): "硬门 = 可自动验证的条件，不依赖 LLM 判断" |
| 2 | 阶段4b: design-ui 调用 | ❌ | 同 #1——design-ui 未调用的直接原因是 orchestrator 用主观理由自行合理化跳过。 | 同 #1 | 同 #1 |
| 3 | 阶段7b: UI 还原 | ⚠️ | plan.md 没有 `## UI 还原` 章节是 design-ui 被跳过的连锁反应——没有 layout.html，plan 无从生成 UI 还原任务。风险：即使有 UI 还原章节，orchestrator 也可能漏调（无 grep 强制门）。 | 在 orchestrator SKILL.md 阶段7b 增加硬门：<br>1. `grep '\[UI-\d+\]' plan.md`<br>2. 有匹配 → 强制调用 ui-restoration<br>3. 无匹配 → 输出 "无 UI 还原任务" 并记录 | harness-methodology.md §4 (Chain Integrity) |
| 4 | 6a: 标记开始 + 初始化日志 | ❌ | 两个问题：① exec 错误创建了 `.work/tdd/` 目录——步骤 6a 只要求创建 `.work/coding/`，`tdd-iterations.md` 是 `.work/` 下的一个文件不是目录；② progress.json 从未更新，`tdd-iterations.md` 从未创建。根因：初始化步骤缺少原子化 checklist。 | 在 exec SKILL.md 步骤6a 增加：<br>1. 明确标注 `tdd-iterations.md` 是文件不是目录<br>2. 明确只创建 `.work/coding/` 一个子目录<br>3. checklist：progress.json 更新 → tdd-iterations.md 初始化 → `.work/coding/` 创建<br>4. 每步 `test -f` 验证后才能进入 6b | exec-logging.md "初始化"节 |
| 5 | 6b: RED — spawn test-agent | ❌ | **核心根因：exec 的 Red Flags 列表未覆盖"自己跑 Bash 测试代替 spawn agent"这一违规模式。** exec SKILL.md Red Flags 列出了 11 条但都是关于"简化流程"的心理借口（如"--auto 模式下可以简化"），没有针对"我用 Bash 直接跑测试也达到了同样效果"这一自我合理化的检测。当 LLM 认为"直接跑测试更高效"时，没有任何护栏阻止它。 | 在 exec SKILL.md Red Flags 列表增加以下条目：<br>- "我先跑个测试看看状态" → STOP。那是 test-agent 的职责。<br>- "直接 Bash 跑测试和 spawn test-agent 效果一样" → STOP。spawn 的目的不是跑测试，是实现 agent 隔离。<br>- "这个任务测试已经存在了，直接跑就行" → STOP。RED 不是跑已有测试，是创建新测试。<br><br>同时在步骤 6b 增加**前置硬门**：进入 6b 前必须确认 `Agent()` tool 被调用（而非 Bash 测试命令）。 | harness-methodology.md §1 (Agent Isolation): "agent 隔离是 TDD 的基础——破坏隔离 = 破坏 RED/GREEN 独立性" |
| 6 | 6b: RED 检查 — 测试文件已创建 | ❌ | 同 #5——test-agent 未被 spawn 导致所有子检查跳过。 | 同 #5 | 同 #5 |
| 7 | 6b: RED 检查 — testcase 失败原因正确 | ❌ | 同 #5。 | 同 #5 | 同 #5 |
| 8 | 6b: RED 检查 — 无 mock/假代码 | ❌ | 同 #5。 | 同 #5 | 同 #5 |
| 9 | 6c: GREEN — spawn coding-agent | ❌ | 同 #5 的根因——Red Flags 未覆盖。此外：exec 步骤 6c 的设计是"从 test-agent 的 RED report 提取 testsuite/testcase 名称"（L188-189），但因为没有 RED report（test-agent 未 spawn），exec 无法按设计流程推进，于是自行接管了实现和验证。这是**流程断裂后的退化行为**——当上游产出缺失时，exec 没有"阻塞并报告"的机制，而是退化为自行完成。 | 在 exec SKILL.md 步骤 6c 增加**前置硬门**：<br>1. 进入 6c 前必须检查 RED report 存在（从 test-agent spawn 返回中提取）<br>2. RED report 缺失 → **阻塞**，输出"RED report 不存在，无法进入 GREEN。请检查 test-agent spawn 是否成功。"<br>3. 不允许在没有 RED report 的情况下进入 GREEN | exec-prompts.md GREEN 模板：明确要求从 RED report 提取 testsuite/testcase 名称 |
| 10 | 6c: GREEN 检查 | ❌ | 同 #5 + #9。coding-agent 未被 spawn。 | 同 #5 + #9 | 同 #5 + #9 |
| 11 | 6c: visual-qa PASS | ❌ | plan.md 行为列表中多条行为标记 `screenshot` 验证方式——说明这些行为的测试需要截图验证（screenshot 是测试验证手段，不代表需要 UI 设计）。但 exec 没有解析行为列表的验证方式列，plan-format.md §exec 解析规则 第5条要求"提取验证方式列，screenshot 行为 → 截图脚本 + .question 文件"。exec 跳过了这一步，screenshot 验证需求从 plan 到 exec 的数据传递链路断裂。 | 在 exec SKILL.md 步骤3 增加：<br>1. 解析 plan.md 行为列表的验证方式列<br>2. `screenshot: {问题}` → 生成 screenshot testcase 需求列表<br>3. RED spawn prompt 中传入 screenshot 验证需求<br>4. GREEN/VERIFY check 中增加 visual-qa 验证 | plan-format.md §exec 解析规则 L184 |
| 12 | 6c: GREEN 检查 — 未修改 test/ | ❌ | 同 #9。 | 同 #9 | 同 #9 |
| 13 | 6c: GREEN 检查 — 无 pass/TODO | ❌ | 同 #9。 | 同 #9 | 同 #9 |
| 15 | 6d: VERIFY | ❌ | **根因：exec 的硬门"GREEN 全绿不是跳过 VERIFY 的理由"（L206）是文字声明，没有转化为可执行的检查点。** exec 在跑完 GREEN 后直接输出下一个 AI 任务的标题，VERIFY 被静默跳过。缺少"每个 phase 完成后必须显式输出判定结果才能进入下一 phase"的流程锁。 | 在 exec SKILL.md 增加**阶段转换门**：<br>1. 每个 phase (RED/GREEN/VERIFY/边界检查/REFACTOR) 完成后必须输出 `## Phase {N} 判定: {✅/❌}` <br>2. 只有输出 `✅` 判定后才能进入下一 phase<br>3. 将"未输出判定直接进入下一 phase"写入 Red Flags<br>4. Completion Gate 增加"所有 5 个 phase 的判定记录存在于 tdd-iterations.md" | harness-methodology.md §3 (Checkpoint): "阶段转换必须有显式判定记录，否则视为未执行" |
| 16 | 6e: 边界检查 — 测试文件隔离 | ❌ | 同 #15——边界检查被静默跳过。exec 在完成所有 8 个 AI 任务的 GREEN 后直接进入步骤 9 (collect-lessons)，没有执行边界检查。根因：#15 的流程锁缺失+边界检查的"即使跳过 REFACTOR 也必须执行"是文字声明没有执行保障。 | 同 #15 + 在步骤 6e 增加：<br>1. 边界检查的 4 项（通用2项 + 技术栈专属）必须逐项输出结果<br>2. 结果写入 tdd-iterations.md（BOUNDARY-CHECK 格式）<br>3. 全部完成后输出 `## 边界检查判定: {✅/❌ {N} 项违规}` | exec SKILL.md L244-252: 已定义边界检查日志格式，但未被遵守 |
| 17 | 6e: 边界检查 — 空代码/假代码 | ❌ | 同 #15 + #16。 | 同 #15 + #16 | 同 #15 + #16 |
| 18 | 6e: 边界检查 — 技术栈专属 | ❌ | 同 #15 + #16。 | 同 #15 + #16 | 同 #15 + #16 |
| 19 | 6f: REFACTOR | ❌ | 边界检查(6e)被跳过的连锁效应——没有违规清单就无法触发 REFACTOR 判定。 | 同 #15 + #16（修复边界检查后 REFACTOR 判定自然恢复） | exec SKILL.md L274-280: REFACTOR 触发规则 |
| 20 | 6h: 标记完成 | ❌ | **根因：exec 的步骤 6h 和 Completion Gate 之间有 gap。** exec 在完成所有任务后调用了 collect-lessons 和 write-tutorial（步骤 9-10），但从未回到步骤 6h 更新 progress.json。步骤 6h 是 per-task 的操作，但在批量处理 8 个任务时，这个 per-task 的操作被"批量完成"的思维模式覆盖了。 | 在 exec SKILL.md 增加：<br>1. 每个 AI 任务完成（GREEN→VERIFY→边界检查→REFACTOR 全通过）后**立即**更新 progress.json 中该任务状态为 done<br>2. 不等到所有任务完成再批量更新<br>3. Completion Gate 增加"progress.json 中所有 AI 任务 status=done" | progress.json 格式：已定义 status 字段但 exec 从未写入 |

---

