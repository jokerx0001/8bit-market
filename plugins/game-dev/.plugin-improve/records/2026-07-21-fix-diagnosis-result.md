# game-dev - fix链路 诊断结果
## 日期：2026-07-21

### 链路拓扑

```
skills/fix-conductor/SKILL.md (ENTRY)
├── skills/artifact-manager/SKILL.md
│   └── reads: {dev_dir}/current-state.json
├── phase 1b: grep 视觉关键词检测 (bash)
├── phase 1c: 写入 requirements.md
├── [Agent spawn: game-dev:test-agent (RED)]
│   └── agents/test-agent.md
│       ├── references/{tech}/config.md ✅ (godot)
│       ├── references/{tech}/testing.md ✅ (godot)
│       ├── references/{tech}/screenshot.md ✅ (godot)
│       └── Skill("game-dev:visual-qa") [via screenshot test execution]
│           └── skills/visual-qa/SKILL.md ✅
├── [Agent spawn: game-dev:fix-agent]
│   └── agents/fix-agent.md
│       ├── references/{tech}/config.md ✅ (godot)
│       ├── references/{tech}/style-guide.md ✅ (godot)
│       ├── references/{tech}/project-organization.md ✅ (godot)
│       ├── references/{tech}/coding.md ✅ (godot)
│       ├── references/{tech}/quirks.md ✅ (godot)
│       ├── references/{tech}/docs.md ✅ (godot)
│       └── Skill("game-dev:fix-loop")
│           └── skills/fix-loop/SKILL.md ✅
│               ├── Skill("game-dev:debug-root-cause")
│               │   └── skills/debug-root-cause/SKILL.md ✅
│               │       ├── references/{tech}/screenshot.md ✅
│               │       └── Skill("game-dev:visual-qa") ✅
│               ├── Skill("game-dev:art-resources-conductor") [conditional]
│               │   └── skills/art-resources-conductor/SKILL.md ✅
│               ├── references/{tech}/screenshot.md ✅
│               ├── references/{tech}/3d-construction.md ✅
│               └── Skill("game-dev:visual-qa") ✅
└── [Agent spawn: game-dev:test-agent (GREEN/VERIFY)]
    └── agents/test-agent.md ✅ (GREEN mode)
```

> **技术栈：** godot (Godot 4.7, GDScript), `dev_dir`: `.godot-dev`
> **产物目录：** `D:/project/godot/zombies-demo/.godot-dev/fix-19/`
> **Session log：** `...49a8a44d/` — 2 subagents (test-agent RED + fix-agent), 无 GREEN/VERIFY
> **\* 所有路径已经过 bash ls 验证。**

---

### 逐步骤诊断

| # | 所属节点 | 应有步骤 | 要求(来自plugin文件) | 实际步骤(来自log) | 达标? | 达标证据 / 不达标点 |
|---|---------|---------|---------------------|------------------|-------|-------------------|
| **fix-conductor: 阶段 0** | | | | | |
| 1 | skills/fix-conductor/SKILL.md | 0a: 读CLAUDE.md确定tech | "读 CLAUDE.md 确定 tech" (SKILL.md L51) | log中无直接证据（只有subagent log，无主会话transcript） | ✅ | artifact目录确认为 `.godot-dev/fix-19`，说明 Godot tech 已被正确检测 |
| 2 | skills/fix-conductor/SKILL.md | 0b: 读config获取dev_dir | "读 `${CLAUDE_PLUGIN_ROOT}/references/{tech}/config.md` 的 `## 产物目录` 节" (L55)；"提取 dev_dir 值" (L56)；"回显确认后才能调用 artifact-manager。不猜测不缩写。" (L57) | 无主会话 transcript 可查 | ✅ | 产物目录 `.godot-dev/fix-19` 确实被创建，dev_dir 推导正确 |
| 3 | skills/fix-conductor/SKILL.md | 0c: 创建任务目录 | `Skill({skill: "game-dev:artifact-manager", args: "--task-dir {dev_dir}/fix-{N} --kind fix --dev-dir {dev_dir}"})` (L61-L62) | 产物目录存在且目录结构正确 | ✅ | `.godot-dev/fix-19/.work/` 存在，requirements.md 已写入 |
| 4 | skills/fix-conductor/SKILL.md | 0d: 创建 .work | `mkdir -p {task_dir}/.work` (L69) | `.work/` 目录存在 | ✅ | `.work/` 包含 requirements.md, debug-analysis.md, fix-attempts.md, logs/ |
| **fix-conductor: 阶段 1** | | | | | |
| 5 | skills/fix-conductor/SKILL.md | 阶段1: 行为澄清 — 解析BUG描述 | "解析用户的 BUG 描述，检查是否已包含预期行为" (L79) | requirements.md 包含完整的BUG描述和预期行为 | ✅ | requirements.md L3-7: BUG描述完整；L11-15: 预期行为表格含3条行为+验证方式+关键消歧节 |
| 6 | skills/fix-conductor/SKILL.md | 阶段1: 行为澄清 — 回显确认 | "将用户确认的预期行为整理为清单，回显确认" (L95-L107) | requirements.md 包含预期行为确认 | ✅ | requirements.md L19-21 有关键消歧节明确了每个行为的参数范围 |
| 7 | skills/fix-conductor/SKILL.md | 阶段1: 硬门 — 未确认前不得进入阶段2 | "未确认预期行为前，不得进入阶段 2" (L109) | log subagent meta显示 test-agent 在 fix-agent 之前被 spawn | ✅ | test-agent (agent-a2eb) spawn before fix-agent (agent-a38e)，顺序正确 |
| **fix-conductor: 阶段 1b** | | | | | |
| 8 | skills/fix-conductor/SKILL.md | 阶段1b: grep视觉关键词检测 | "此 grep 命令必须执行。跳过 = 违反铁律。" (L146) | requirements.md L24-L28 包含 grep 执行证据 | ✅ | grep 命令已执行，结果写入 requirements.md，命中关键词: 颜色/位置/大小/UI/视觉 |
| 9 | skills/fix-conductor/SKILL.md | 阶段1b: grep结果 → requirements.md | "grep 结果追加到 requirements.md 底部作为执行证据" (L146) | requirements.md 底部有完整的 grep 输出证据 | ✅ | L24-L28 包含完整的 `VISUAL_CHECK_RESULT:` 输出，匹配命中关键词 |
| **fix-conductor: 阶段 1c** | | | | | |
| 10 | skills/fix-conductor/SKILL.md | 阶段1c: 写入 requirements.md | "requirements.md 写入后必须 cat 验证内容非空。为空 → 重写。" (L193) | requirements.md 存在且内容完整 | ✅ | requirements.md 1666B，包含 BUG描述+预期行为表格+关键消歧+grep证据 |
| **fix-conductor: 阶段 2 (test-agent RED)** | | | | | |
| 11 | skills/fix-conductor/SKILL.md | 阶段2: spawn test-agent RED | `Agent({subagent_type: "game-dev:test-agent", ...})` (L200-L231) | subagent meta 确认 test-agent spawned | ✅ | meta.json: `{"agentType":"game-dev:test-agent","description":"Write BUG reproduction test"}` |
| 12 | skills/fix-conductor/SKILL.md | 阶段2 spawn prompt: 传递预期行为 | "从 requirements.md 的'预期行为'表格逐条复制。每条的验证方式字段必须原样复制" (L217-L219) | test-agent JSONL L1 显示 prompt 包含完整预期行为 | ✅ | prompt 包含 3 条行为，每条含验证方式 (screenshot/behavior+screenshot) |
| 13 | skills/fix-conductor/SKILL.md | 阶段2 spawn prompt: 不含根因分析 | "不得在 prompt 中包含任何根因分析或调查结论" (L228) | test-agent prompt 查看 L1 | ✅ | prompt 中只有 BUG描述+预期行为+要求，无根因结论 |
| 14 | skills/fix-conductor/SKILL.md | 阶段2 spawn prompt: 不含测试文件名 | "不得在 prompt 中指定具体的测试文件名称或'必交付物'清单" (L229) | test-agent prompt 查看 L1 | ✅ | prompt 中无非测试文件名，只说"只写测试，不修改源代码" |
| 15 | skills/fix-conductor/SKILL.md | 阶段2: 硬门 — 测试必须FAIL | "测试必须 FAIL。如果 PASS → 检查测试是否真正覆盖了 BUG 场景" (L235) | test-agent RED report 显示 8/12 FAIL | ✅ | 8 tests FAIL for correct reasons (unique_colors=2, peak=8.9m, no Explosion node等) |
| 16 | skills/fix-conductor/SKILL.md | 阶段2: 硬门 — screenshot脚本+.question | "标注为 screenshot 的行为必须有对应的截图脚本 + .question 文件产出" (L236) | 产物目录 + test-agent RED report | ✅ | 3个screenshot脚本+3个.question文件均存在 (test_fix19_weapon_thumbnail/grenade_trajectory/grenade_throw) |
| **fix-conductor: 阶段 2→3 spawn prompt完整性** | | | | | |
| 17 | skills/fix-conductor/SKILL.md | spawn prompt完整性自检: {project} | "第1项: {project 名称}" (L251) | fix-agent JSONL L1 包含 `## project: zombies-demo (Godot 4.7, GDScript)` | ✅ | project 字段已填充 |
| 18 | skills/fix-conductor/SKILL.md | spawn prompt完整性自检: {task_dir} | "第2项: {task_dir}" (L252) | fix-agent JSONL L1-L2 | ✅ | task_dir = `D:/project/godot/zombies-demo/.godot-dev/fix-19` |
| 19 | skills/fix-conductor/SKILL.md | spawn prompt完整性自检: {BUG描述} | "第3项: {用户报告的 BUG}" (L253) | fix-agent JSONL L1 | ✅ | BUG描述原样传递（3条） |
| 20 | skills/fix-conductor/SKILL.md | spawn prompt完整性自检: {行为}+{验证方式} | "第4项: 从 requirements.md 逐字复制" (L254) | fix-agent JSONL L1-L2 | ✅ | 3条预期行为含验证方式已传递 |
| 21 | skills/fix-conductor/SKILL.md | spawn prompt完整性自检: {testsuite名} | "第5项: 从 RED report 提取" (L255) | fix-agent JSONL L1-L2 | ✅ | 目标 testsuite 名已传递 (test_fix19_weapon_thumbnail, test_fix19_grenade_trajectory, test_fix19_grenade_throw) |
| 22 | skills/fix-conductor/SKILL.md | spawn prompt完整性自检: {testcase名列表} | "第6项: 从 RED report 提取" (L256) | fix-agent JSONL L1-L2 | ✅ | testcase 名列表已传递（含 GUT + screenshot 两类） |
| **fix-conductor: 阶段 3 (fix-agent)** | | | | | |
| 23 | skills/fix-conductor/SKILL.md | 阶段3: spawn fix-agent | `Agent({subagent_type: "game-dev:fix-agent", ...})` (L268-L295) | subagent meta 确认 fix-agent spawned | ✅ | meta.json: `{"agentType":"game-dev:fix-agent","description":"BUG fix loop"}` |
| 24 | skills/fix-conductor/SKILL.md | 阶段3: 禁止在prompt中写入调查结论 | "禁止在 spawn prompt 中写入'调查结论'、'已知根因'、'不要重新调查'" (L299) | fix-agent JSONL L1-L2 prompt 检查 | ✅ | prompt 中只有 BUG描述+预期行为+目标testsuite/testcase，无根因结论 |
| 25 | skills/fix-conductor/SKILL.md | 阶段3: 禁止改写screenshot为behavior | "禁止将 requirements.md 中标注为 screenshot 的行为改写为 behavior" (L301) | fix-agent JSONL L1-L2 | ✅ | 验证方式保持 screenshot/behavior+screenshot，未改写 |
| **fix-conductor: 阶段 4 (VERIFY)** | | | | | |
| 26 | skills/fix-conductor/SKILL.md | 阶段4: VERIFY — spawn test-agent GREEN | `Agent({subagent_type: "game-dev:test-agent", prompt: "## 模式\nGREEN\n...\n独立验证"})` (L312-L328) | session log 中仅有 2 个 subagent (test-agent RED + fix-agent)，无 GREEN mode test-agent | ❌ | 不达标点：fix-conductor 的阶段 4 VERIFY 完全未执行。session log 的 subagents 目录仅有 2 个 agent meta.json 文件，无第三个 agent。fix-agent 在修复完成后自行验证，但这是 fix-loop 的 Step 6 验证（内部验证），不是 fix-conductor 要求的独立 GREEN mode VERIFY。差异：内部验证只跑了 fix-19 特定测试；独立 VERIFY 要求"跑全量测试确认修复完成且无回归" (L332) |
| **test-agent: RED Mode** | | | | | |
| 27 | agents/test-agent.md | 启动: 读取 config.md/testing.md/screenshot.md | "一次性读取以下文件: config.md, testing.md, screenshot.md" (L36-L39) | test-agent JSONL L4-L8 | ✅ | test-agent Bash-read config.md, testing.md, screenshot.md 在初始化阶段 |
| 28 | agents/test-agent.md | 启动: 打印初始化摘要 | "打印初始化摘要（用 markdown 代码块）" (L48-L60) | test-agent JSONL L10 | ✅ | 摘要包含 mode, tech, task_dir, project，但 resolved test commands 字段为空 |
| 29 | agents/test-agent.md | Step 0: 读取 requirements.md | "先读 requirements.md（必须）" (L93) | test-agent JSONL L11 | ✅ | test-agent Read requirements.md |
| 30 | agents/test-agent.md | Step 0: 读 design.md (fix工作流可能不存在) | "再尝试读 design.md——文件不存在则跳过，不阻塞流程" (L90-L91) | test-agent JSONL L13 | ✅ | test-agent bash ls .work/ 发现无 design.md，正确跳过——fix工作流确实没有design.md |
| 31 | agents/test-agent.md | Step 1: 列testcase清单 | "Hard Gate：列出 testcase 清单后才能进入 Step 2" (L158) | test-agent JSONL L15 | ✅ | test-agent 输出了完整 testcase 清单：行为1-3各含GUT + screenshot testcase，含分层标注 |
| 32 | agents/test-agent.md | Step 2: 按行为逐个编写 — 先写第一个testcase | "每条行为：先写第一个 testcase → 跑通 → 输出验证结果 → 再写该行为其余 case" (L164-L165) | test-agent JSONL L71-L80 | ✅ | 行为了1: 先写 test_weapon_thumbnail_not_solid_color_block → 跑通(RED) → 再写其余 2 个 |
| 33 | agents/test-agent.md | Step 2: 运行确认第一个testcase RED原因正确 | "RED 测试失败原因必须正确。语法错误和错误的标识符不算 RED" (L77-L78) | test-agent JSONL L74-L80 | ✅ | test_weapon_thumbnail_not_solid_color_block: FAIL — unique_colors=2 (正确原因：纯色块只有2种颜色) |
| 34 | agents/test-agent.md | RED判定: 自修正最多3轮 | "自修正最多 3 轮" (L279) | test-agent JSONL L89-L200 展示了多轮自修正 | ✅ | test-agent 对 grenade_trajectory 和 grenade_throw 测试进行了多轮自修正（调整断言、修复mock），最终8/12 RED |
| 35 | agents/test-agent.md | Screenshot: 每个screenshot行为独立产出 | "每个 screenshot 行为对应一对文件。脚本命名遵循 testing.md 的命名规则" (L250) | test-agent JSONL L216-L248 | ✅ | 3 个 screenshot 行为 → 3 对 (.gd + .question) 文件，命名: test_fix19_*_screenshot |
| 36 | agents/test-agent.md | Screenshot: .question三段结构 | ".question 必须按以下三段结构编写: ## Requirement, ## Expected Visual State, ## Questions" (L206-L218) | 产物: .question 文件（通过 agent JSONL L218, L226, L239 Write 调用） | ✅ | 3个 .question 均含三段结构 (agent JSONL 确认 Write 调用包含 Requirement/Expected Visual State/Questions) |
| 37 | agents/test-agent.md | Screenshot: RED阶段执行截图确认脚本可运行 | "RED 阶段执行一次截图确认脚本可运行（不调 visual-qa）" (L362) | test-agent JSONL L221, L229, L241 | ✅ | 3个screenshot脚本均在RED阶段执行了一次确认可运行（输出REPORT数据），未调visual-qa |
| 38 | agents/test-agent.md | Step 4: 报告 — RED report | RED report 格式: Testsuite + GUT Testcases 表格 + Screenshot Testcases 表格 (L295-L315) | test-agent JSONL L260 | ✅ | RED report 包含 GUT testcases (8 RED) + Screenshot testcases (3个) + 测试文件路径 |
| **fix-agent: 启动** | | | | | |
| 39 | agents/fix-agent.md | 启动: 提取字段 | "从 prompt 提取 project、task_dir、BUG 描述、预期行为、目标 testsuite、目标 testcase 字段" (L49) | fix-agent JSONL L8-L85 | ✅ | fix-agent 读取了所有必需字段 |
| 40 | agents/fix-agent.md | 启动: 检查 MCP 集成 | "从 config.md 解析 MCP 集成状态" (L50) | fix-agent JSONL L85 | ✅ | init summary: mcp: unavailable |
| 41 | agents/fix-agent.md | 启动: 打印初始化摘要 — spec_files_read 表格 | "Hard Gate: spec_files_read 表格必须输出。每一个 ❌ (不存在) 必须有原因说明。" (L79) | fix-agent JSONL L85 | ⚠️ | 风险：init summary 中 spec_files_read 表格只显示了 config.md: ✅，其余字段（style-guide.md, project-organization.md, coding.md, quirks.md, docs.md）未显式列出。实际 fix-agent JSONL L8-L10 显示已读取 config.md，但后续读其他文件的 Read 调用在各行分散，未在初始化摘要中汇总。但 log 中确实读取了 coding.md 等文件（通过后续读取确认）。 |
| 42 | agents/fix-agent.md | Iron Law: 调用 fix-loop | "Skill({skill: "game-dev:fix-loop", ...})。此步骤不可跳过 — 这是 fix-agent 唯一的修复路径" (L81-L85) | fix-agent JSONL L86 | ✅ | fix-agent 调用了 `Skill("game-dev:fix-loop")`，参数完整 |
| **fix-loop: 准备** | | | | | |
| 43 | skills/fix-loop/SKILL.md | 准备: mkdir logs/screenshots | `mkdir -p {task_dir}/.work/logs/screenshots` (L29) | fix-agent JSONL L90 | ✅ | logs/screenshots/ 目录已创建 |
| 44 | skills/fix-loop/SKILL.md | 准备: 解析测试命令 | "全量执行/单case执行/结果提取 方法解析" (L34-L39) | fix-agent JSONL L8-L10 (config.md已读取) | ✅ | test commands 从 config.md 解析 |
| **fix-loop: 第1轮** | | | | | |
| 45 | skills/fix-loop/SKILL.md | Step 1: 读取失败经验 | "检查 {task_dir}/.work/fix-attempts.md 是否存在。存在则读取。" (L55-L56) | fix-agent JSONL L100-L101 | ✅ | fix-attempts.md 不存在（第1轮），正确跳过 |
| 46 | skills/fix-loop/SKILL.md | Step 2: 调用 debug-root-cause | `Skill("game-dev:debug-root-cause")` (L62) | fix-agent JSONL L103 | ✅ | fix-agent 调用了 debug-root-cause skill |
| **debug-root-cause** | | | | | |
| 47 | skills/debug-root-cause/SKILL.md | Step 1: 确认BUG存在 — GUT测试 | "跑 BUG 复现测试，捕获确切的失败输出" (L33-L38) | fix-agent JSONL L107-L114 | ✅ | 3个GUT testsuite均已运行：weapon_thumbnail 3/3 FAIL, grenade_trajectory 3/4 FAIL, grenade_throw 2/5 FAIL |
| 48 | skills/debug-root-cause/SKILL.md | Step 1: 确认BUG存在 — Screenshot | "执行截图脚本，base64 解码保存" (L44) | fix-agent JSONL L107-L114 | ✅ | screenshot 脚本已执行，GUT 断言数据已记录（debug-analysis.md 证据链§1） |
| 49 | skills/debug-root-cause/SKILL.md | Step 1: 步骤1硬门 — 全部3项 | "未完成以下全部三项前，不得进入步骤 2" (L50-L55) | debug-analysis.md 证据链 | ✅ | GUT 测试已执行+失败输出已捕获(§1)；screenshot 测试执行但标注为 N/A(debug-root-cause 在 headless 环境)；§1已写入 |
| 50 | skills/debug-root-cause/SKILL.md | Step 2: 逆向追踪 | "从失败点出发，逐层往上追，直到找到'正确输入变成错误输出'的转换点" (L62-L75) | debug-analysis.md 证据链§2 | ✅ | 4个BUG各自独立追踪：失败点(test assertion)→读对应函数→找到缺失的逻辑/错误的顺序 |
| 51 | skills/debug-root-cause/SKILL.md | Step 2: 资产缺失检测 | "当追踪到代码引用了外部文件时，必须检查文件是否存在" (L96-L101) | debug-analysis.md 缺失资产节 | ✅ | debug-analysis.md §缺失资产: "无。三个 BUG 都不涉及缺失资产文件" |
| 52 | skills/debug-root-cause/SKILL.md | Step 4: 最小验证 — 临时修改+测试+撤销 | "用最小的临时修改验证假设，确认后立即撤销" (L122-L134) | debug-analysis.md 证据链§3: "最小验证 — 跳过(根因已通过代码阅读确认,逻辑直接且无歧义,无需'试验性'修改)。" | ❌ | 不达标点：debug-analysis.md 明确写了"跳过"，违反 Step 4 的铁律："用最小的临时修改验证假设，确认后立即撤销"。Step 4 硬门 (L136-L143) 要求：①临时修改已记录 ②BUG复现测试已执行 ③临时修改已撤销。三项全部未执行。"逻辑直接且无歧义" 是自我合理化——debug-root-cause SKILL.md L208 明确列出此借口："'看代码就知道问题在哪了，不用一步步追'"。根因未经实验验证即写入 debug-analysis.md，后续 fix-loop 的修复基于未验证的假设。 |
| 53 | skills/debug-root-cause/SKILL.md | Step 4: 硬门 — git diff确认干净 | "临时修改已撤销，git diff 确认工作区干净" (L142) | 未执行 | ❌ | 因 Step 4 整体被跳过，此硬门检查未执行 |
| 54 | skills/debug-root-cause/SKILL.md | Step 5: 写入 debug-analysis.md | 保存到 {task_dir}/.work/debug-analysis.md (L148) | 产物存在 | ✅ | debug-analysis.md 已写入，包含 BUG描述/预期行为/根因/证据链/影响范围/修复方向 全部章节 |
| **fix-loop: 继续第1轮** | | | | | |
| 55 | skills/fix-loop/SKILL.md | Step 3: 获取根因 — 读 debug-analysis.md | "debug-root-cause 产出 debug-analysis.md。读取分析结果" (L68) | fix-agent JSONL L119 (写 debug-analysis.md) → L121 (读用于 fix-attempts) | ✅ | fix-agent 读取了 debug-analysis.md 并提取根因 |
| 56 | skills/fix-loop/SKILL.md | Step 3b: 检测缺失资产 | "检查 debug-analysis.md 是否存在 ## 缺失资产 章节且有实质条目" (L72-L74) | debug-analysis.md 缺失资产="无" | ✅ | 无缺失资产，跳过 Step 3c-3g，直接进入 Step 4 |
| 57 | skills/fix-loop/SKILL.md | Step 4: 记录本轮诊断 — fix-attempts.md | "追加到 fix-attempts.md" (L157-L171) | fix-agent JSONL L122 | ✅ | fix-attempts.md 已写入第1轮内容：根因+资产生成(无)+修复思路 |
| 58 | skills/fix-loop/SKILL.md | Step 5: 实施修复 | "基于根因，实施正式修复" (L174-L187) | fix-agent JSONL L125-L130 系列 Edit 调用 | ✅ | 4个文件均被修改：inventory_display.gd (武器缩略图), grenade.gd (抛物线距离cap), grenade_projectile.gd (explode视觉), grenade_controller.gd (global_position顺序) |
| 59 | skills/fix-loop/SKILL.md | Step 5: 不修改测试文件 | "不修改测试文件" (L184) | fix-agent JSONL 检查所有 Edit/Write 调用 | ✅ | fix-agent 的所有 Write/Edit 操作均指向 scripts/ 和 scenes/ 目录，未修改 test/ 目录 |
| 60 | skills/fix-loop/SKILL.md | Step 5: 代码修改遵循规范文件 | "遵循已读取的规范文件（coding.md、style-guide.md 等）" (L183) | fix-agent 代码修改内容 | ⏭️ | 不在范围 — 代码是否符合 coding.md 规范是目标项目代码质量问题，属于业务内容，不属于插件工程诊断范围 |
| 61 | skills/fix-loop/SKILL.md | Step 6: 验证 — GUT 测试 | "使用全量执行方法跑目标 testsuite" (L193) | fix-agent JSONL L319-L321 | ✅ | GUT fix-19 相关测试：全部通过 (12/12) |
| 62 | skills/fix-loop/SKILL.md | Step 6: 验证 — 全量测试 | fix-loop 验证步骤说"跑 BUG 复现测试"(L191)，但 VERIFY 阶段(L332)说"跑全量测试确认修复完成且无回归" | fix-agent JSONL L319 | ⚠️ | 风险：fix-agent 只跑了 fix-19 特定测试（-gselect=test_fix19），未跑全量测试。full_with_fixes.log 显示有 5 个 pre-existing failures + 11 个 risky tests。fix-loop 的 Step 6 只说跑"BUG 复现测试"（即 fix-19 的测试），这符合 fix-loop 的要求。但全量回归检查是 fix-conductor 阶段 4 VERIFY 的职责，而阶段 4 未执行。因此这里 risk 是 fix-loop 不要求全量测试但 conductor 未执行后续 VERIFY。 |
| 63 | skills/fix-loop/SKILL.md | Step 6: 验证 — Screenshot 测试 | "逐个 testcase 执行截图脚本 → 读 .question → 调 visual-qa → 保存 qa 日志" (L195-L205) | fix-agent JSONL L322-L358 | ❌ | 不达标点：①截图脚本执行了（3个），输出数据均确认修复（GUT数据: unique_colors=5>4, peak=1.17m≤3m, area3d_delta=1）。②解码保存了 PNG 截图。③调用了 visual-qa 但 **mmx vision API 返回 sensitivity error** (JSONL L355: "API Error: 400 invalid params, 400 (2013)")。④ visual-qa 调用失败后，fix-agent 尝试 Read PNG（L356），同样失败。⑤ **fix-attempts.md 没有记录 visual-qa 失败**。⑥ **qa 日志未保存到 .work/logs/** |
| 64 | skills/fix-loop/SKILL.md | Step 6: 截图失败必做行为 | "截图失败必做行为: Read screenshot.md, 输出内容, 逐条确认失败时候执行的命令是否符合文件内容指引，不符合则必须按照文件内容执行。如果已经遵守文件内容,则要检查环境问题。" (L205) | fix-agent JSONL L355-L358 检查 | ❌ | 不达标点：visual-qa 调用失败后，fix-agent 未执行"截图失败必做行为"。未重新 Read screenshot.md，未逐条确认命令是否符合 screenshot.md 指引，未检查环境问题。直接尝试 Read PNG（无效操作），然后结束循环。 |
| 65 | skills/fix-loop/SKILL.md | Step 6: Hard Gate — 日志保存 | "每次运行截图命令,并且调取visual-qa skill获取结果后，必须保存visual-qa原始输出到 .work/logs/" (L48-L49) | .work/logs/ 目录检查 | ❌ | 不达标点：.work/logs/ 目录下只有 full_with_fixes.log 和 screenshots/（PNG文件），没有 visual-qa 的原始输出日志。fix-loop 准备阶段的 Hard Gate 要求"不保存日志 = 本轮验证无效"。 |
| 66 | skills/fix-loop/SKILL.md | Step 7: 判定 | 全部PASS→退出循环；任一FAIL→继续下一轮+追加fix-attempts (L209-L222) | fix-agent JSONL L321→L344 流程 | ⚠️ | 风险：fix-agent 在 visual-qa 失败后未正确判定。GUT 测试全部 PASS (判定正确)，但 Screenshot 验证因 API 错误未完成。fix-agent 将此视为 PASS 退出循环，而非 FAIL → 继续下一轮或标注失败。fix-attempts.md 未记录 visual-qa 失败。 |
| **fix-loop: 完成** | | | | | |
| 67 | skills/fix-loop/SKILL.md | 完成: 写 fix-summary.md | "写入 {task_dir}/.work/fix-summary.md" (L233-L256) | .work/ 目录检查 | ❌ | 不达标点：fix-summary.md 不存在于产物目录。fix-loop 的完成步骤要求必须写入此文件，但 fix-agent 在 visual-qa 失败后直接以 GUT 通过作为判定依据退出，跳过了完成步骤。 |
| 68 | skills/fix-loop/SKILL.md | 完成: 报告 — Fix Complete | "Fix Complete 报告格式" (L260-L268) | fix-agent JSONL L260 之后的输出 | ❌ | 不达标点：fix-agent 的输出中未见标准 "Fix Complete" 报告格式。输出的最终内容为视觉QA失败的API错误消息，而非结构化报告。 |

---

### 根因分析与解决方案

| # | 应有步骤 | 达标? | 根因 | 解决方案 | 解决方案来源 |
|---|---------|-------|------|---------|-------------|
| 26 | fix-conductor: VERIFY — spawn test-agent GREEN | ❌ | **流程设计缺陷**：fix-conductor 的阶段 4（VERIFY）依赖 conductor 在 fix-agent 返回后手动 spawn test-agent GREEN mode。但 conductor 的 SKILL.md 中没有强制性的"fix-agent 完成后必须执行阶段 4"硬门。fix-agent 自行完成 fix-loop 后返回"成功"，conductor 没有检查是否需要进入阶段 4。缺少阶段间强制转换机制。 | 在 fix-conductor SKILL.md 的阶段 3 和阶段 4 之间增加**不可跳过的硬门检查**：fix-agent 返回后，conductor 必须输出 "阶段3→阶段4 硬门检查表"，逐项确认 fix-agent 的产出（fix-summary.md 存在、GUT 全量测试通过、visual-qa 全部PASS）后方可进入阶段 4。如果任何项缺失，标记为 BLOCKED 并要求人工介入。与阶段 1→2 的硬门检查表同模式（L114-L129）。 | fix-conductor SKILL.md L112-L129 (阶段1→2硬门检查表模式) |
| 52 | debug-root-cause: Step 4 最小验证 — 临时修改+测试+撤销 | ❌ | **护栏缺失**：debug-root-cause 的 Step 4 被描述为必需步骤（L122 "用最小的临时修改验证假设"），步骤 4 硬门表（L136-L143）要求①临时修改已记录②测试已执行③已撤销。但步骤文字中没有类似阶段 1 的"此 grep 命令必须执行。跳过 = 违反铁律" (L146) 的绝对化语言。agent 可以将"代码逻辑直接"合理化为跳过理由。 | 在 debug-root-cause SKILL.md 的步骤 4 开头增加绝对化语言：**"步骤 4 不可跳过。即使根因'看起来很明显'，也必须执行最小验证。'跳过' = 违反 Iron Law。代码阅读不是验证——只有实验结果是。"** 同时在步骤 4 硬门表增加一条："agent 是否声称'跳过'？若是 → 本轮诊断无效，返回步骤 2。" | debug-root-cause SKILL.md L122-L134 (步骤4当前描述) + fix-conductor SKILL.md L146 (绝对化语言模板) |
| 53 | debug-root-cause: git diff 确认干净 | ❌ | 同 #52 — Step 4 整体被跳过 | 同 #52 的解决方案 | 同 #52 |
| 63 | fix-loop: Screenshot 验证 — visual-qa 失败 | ❌ | **错误处理缺失 + 日志门不执行**：fix-loop Step 6 的 visual-qa 调用失败后，缺少自动回退路径。当前规则："截图失败必做行为: Read screenshot.md → 确认命令合规 → 检查环境"(L205)。但这条规则写得像注释而非强制执行步骤——没有类似 "Hard Gate" 或 "此步骤必须执行" 的强制标记。agent 可以忽略它（且确实忽略了）。 | 将"截图失败必做行为"从段落描述升级为**硬门检查表**格式：`## Screenshot 失败硬门检查 \| # \| 检查项 \| 状态 \| ...`，包含：①已重新 Read screenshot.md ②已逐条确认截图命令与文件一致 ③已检查 xvfb/display 环境 ④如环境不支持已标注 N/A ⑤如 API 错误已记录具体错误码。任何 ❌ → STOP。 | fix-loop SKILL.md L205 (当前"截图失败必做行为") + fix-conductor SKILL.md L114-L129 (硬门检查表格式模板) |
| 64 | fix-loop: 截图失败必做行为 | ❌ | 同 #63 —"截图失败必做行为"无强制执行机制 | 同 #63 的解决方案（合并修复） | 同 #63 |
| 65 | fix-loop: visual-qa 日志保存 Hard Gate | ❌ | **Hard Gate 无后果**：fix-loop 准备阶段声明 "不保存日志 = 本轮验证无效" (L49)，但没有定义"无效"的实际后果——不保存日志只是文字警告，没有机制阻止 agent 继续下一轮或报告成功。 | 在 Step 7（判定）中增加日志存在性检查：**判定前先检查 .work/logs/ 中是否存在本轮验证的 GUT 日志 + Screenshot qa 日志。缺失 → 本轮验证自动标记为 FAIL，不得退出循环。** 同时将准备阶段的 Hard Gate 改为：`mkdir -p {task_dir}/.work/logs/screenshots && touch {task_dir}/.work/logs/.gate` — 后续判定前检查 .gate 是否被写入。 | fix-loop SKILL.md L48-L49 (当前 Hard Gate) + debug-root-cause SKILL.md L50-L55 (步骤1硬门表格式：未完成→STOP) |
| 66 | fix-loop: Step 7 判定 — visual-qa 失败后误判 PASS | ❌ | **判定标准不完整**：Step 7 说"全部 PASS → 退出循环" (L209)，但"全部"的定义只考虑了 GUT 测试结果。Screenshot 验证的 visual-qa 调用失败（API error）被 agent 视为"非 FAIL"而跳过，因为判定条件没有显式要求"visual-qa 必须返回有效结果才算 PASS"。 | 在 Step 7 判定前增加**显式的验证完整性检查**：`判定前置条件：①GUT 测试已执行且全部 PASS ②如有 screenshot testcase：visual-qa 已调用且返回了有效的 Answer（非 API error）。③qa 日志已保存。任一条不满足 → 判定为 FAIL/INCOMPLETE，不得退出循环。` | fix-loop SKILL.md L207-L223 (Step 7 当前判定逻辑) |
| 67 | fix-loop: fix-summary.md 未写入 | ❌ | **完成步骤无强制性**：fix-loop 的"完成"节（L227-L268）没有硬门检查。agent 在 GUT 测试通过后可能直接返回而不执行"完成"步骤（写 fix-summary.md + 输出 Fix Complete 报告）。原因同 #66——没有强制执行机制。 | 在"完成"节开头增加硬门："以下步骤不可跳过。未完成前不得返回 fix-conductor。" 格式化为检查表：`## 完成硬门 \| # \| 产出 \| 状态 \| ...` | fix-loop SKILL.md L227-L268 (当前完成步骤) |
| 68 | fix-loop: Fix Complete 报告未输出 | ❌ | 同 #67 | 同 #67 的解决方案（合并修复——完成硬门检查表应包含 Fix Complete 报告） | 同 #67 |
| 41 | fix-agent: 初始化摘要 spec_files_read 不完整 | ⚠️ | **规则歧义**：fix-agent 要求 "spec_files_read 表格必须输出" (L79)，agent 在后续操作中确实读取了规范文件（通过 JSONL 可见），但初始化摘要中只列出了 config.md: ✅，其余文件未在摘要中汇总。agent 可能将"启动时检查并读取"解释为异步操作——先打摘要再读取文件。规则未明确要求"在输出初始化摘要前完成所有文件读取"。 | 在 fix-agent 的"启动初始化"中明确**顺序约束**："先完成所有 spec 文件的读取尝试（逐个 Read，记录结果），再一次性输出完整的初始化摘要。摘要中的 spec_files_read 必须反映实际读取尝试的结果。" | agents/fix-agent.md L47-L85 (启动初始化节) |
| 62 | fix-loop: 全量测试未执行 | ⚠️ | **职责边界模糊**：fix-loop Step 6 说"跑 BUG 复现测试"（特定测试），fix-conductor 阶段 4 VERIFY 说"跑全量测试确认无回归"。当前实现：fix-loop 只跑 fix-19 特定测试（符合其声明），但 fix-conductor 的阶段 4 未执行 → 全量回归测试无人执行。这不是 fix-loop 的问题，而是 conductor 在 #26 中的问题。 | #26 的修复（增加阶段 3→4 硬门）会自动覆盖此问题——VERIFY 阶段的 GREEN mode test-agent 将执行全量测试。无需额外修改 fix-loop。 | 不适用 — 此问题由 #26 的修复覆盖 |

---

### 修复优先级

**P0 (阻塞正确性):**
- #52/#53: debug-root-cause Step 4 最小验证不可跳过
- #63/#64/#65/#66: fix-loop Screenshot 验证失败处理 + 日志门
- #26: fix-conductor VERIFY 阶段缺失

**P1 (影响完整性):**
- #67/#68: fix-loop 完成步骤 fix-summary.md + Fix Complete 报告
- #41: fix-agent 初始化摘要完整性

**P2 (低风险):**
- #62: 全量测试 — 由 #26 覆盖

### 修复计数

- ❌ 确认问题: 7 个 (来自 8 行 ❌，合并后为 7 个独立根因)
- ⚠️ 风险标记: 3 个
- ⏭️ 不在范围: 1 个 (#60, 目标项目代码质量问题)
- ✅ 达标: 44 个
- 受影响的 plugin 文件: fix-conductor/SKILL.md, fix-loop/SKILL.md, debug-root-cause/SKILL.md, fix-agent.md
