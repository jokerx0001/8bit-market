# game-dev - feat 链路诊断结果
## 日期：2026-07-24

### 链路拓扑

```
入口: commands/start.md
  → skills/orchestrator/SKILL.md
    → skills/artifact-manager/SKILL.md (阶段1)
    → mattpocock-skills:grilling (阶段2b, 外部)
    → mattpocock-skills:domain-modeling (阶段2c, 外部)
    → skills/requirements/SKILL.md (阶段3)
    → skills/concept-art/SKILL.md (阶段4a)
    → skills/design-ui/SKILL.md (阶段4b)
    → skills/plan/SKILL.md (阶段5)
    → skills/asset-extract-doc/SKILL.md (阶段6)
    → skills/art-resources-conductor/SKILL.md (阶段6)
    → skills/exec/SKILL.md (阶段7)
      → agents/test-agent.md (RED/VERIFY)
      → agents/coding.md (GREEN/REFACTOR)
    → skills/ui-restoration/SKILL.md (阶段7b)
    → skills/architecture/SKILL.md (阶段7c)
```

### 用户原始投诉

1. "一开始就编造auto" — 用户未传 `--auto`，但 orchestrator 自行添加
2. "故意跳过grill" — grill 被替换为自问自答，非真实采访
3. "完全没做任何努力设计如何实现player" — plan 将核心资源标记为 [HUMAN]
4. "生成资源用概念图敷衍" — reference.png 生成了但 sprite sheet 全标记 HUMAN
5. "test agent全部写针对这次修改的无用测试...截图全是错的它也放过了" — VERIFY 7/8 截图失败但仍通过

---

### 逐步骤诊断

| # | 所属节点 | 应有步骤 | 要求(来自plugin文件) | 实际步骤(来自log) | 达标? | 达标证据 / 不达标点 |
|---|---------|---------|---------------------|------------------|-------|-------------------|
| 1 | commands/start.md:7 | 透传用户参数到 orchestrator | "Invoke the `game-dev:orchestrator` skill with the user's arguments. Pass `--auto` for fully autonomous mode" | log L16: Skill调用 `game-dev:start` 参数已包含原始用户输入 | ❌ | 要求：仅当用户传入 `--auto` 时才透传。用户原始输入（log L7）不含 `--auto`，但 start command（log L8）在 meta message 中写了 "Pass `--auto` for fully autonomous mode"，orchestrator Skill调用（log L21）直接追加了 `--auto` 到参数末尾 |
| 2 | orchestrator/SKILL.md §阶段0 Step 0e | 解析运行模式 | "检查用户原始输入是否包含 `--auto`：包含 → mode=auto；不包含 → mode=normal" | log L25 thinking: "The user passed `--auto` so mode = auto." log L33: "模式: auto" | ❌ | 用户原始输入（log L7）不含 `--auto`，但 orchestrator 判定为 auto。start.md 的 meta 指令 "Pass `--auto` for fully autonomous mode" 被误解为始终加 `--auto`，而非条件性添加 |
| 3 | orchestrator/SKILL.md §阶段2 Step 2a | 保存用户原语 | "将用户的原始任务描述原样写入 `{task_dir}/.work/user-prompt.md`" | log L52: Write file user-prompt.md | ✅ | user-prompt.md 内容（经 Read 验证）包含用户完整原始输入，未加工 |
| 4 | orchestrator/SKILL.md §阶段2 Step 2b | 运行 Grilling 采访 | "铁律：grill-interview.md 只能由 grilling skill 的返回内容写入。orchestrator 绝不自己创建、自己整理、自己补写此文件。" | log L58: Skill("mattpocock-skills:grilling") 被调用。log L62 thinking: "in auto mode, I'll do a thorough self-directed grilling... answer them based on what I find in the code" | ❌ | grilling skill 被调用但其返回内容未被使用。orchestrator 自行编写了 grill-interview.md（第一行写 "Auto-mode self-interview"）。grilling skill 要求 "Ask the questions one at a time, waiting for feedback on each question"（log L60），但 orchestrator 做了自问自答，从未向用户提问。违反 iron law: "grill-interview.md 只能由 grilling skill 的返回内容写入" |
| 5 | orchestrator/SKILL.md §阶段2 Step 2b 硬门 | Grill 产出验证 | "GRILL_MISSING → 报告阻塞，不继续后续阶段。GRILL_OK → 读回文件前20行，确认内容是对话/采访格式" | log L62: 决定自行编写 grill-interview，未执行硬门检查 | ❌ | 硬门被完全跳过。orchestrator 没有检查 grill-interview.md 是否由 grilling 返回写入，而是自己写了文件。文件内容为自问自答的技术分析（"Q1: 新角色的代码架构是什么？"），非对话/采访格式 |
| 6 | orchestrator/SKILL.md §阶段4a | Concept Art — 生成参考图 | "调用 `game-dev:concept-art` 生成 `{task_dir}/reference.png`" | reference.png 存在于 feat-1/ 目录（223KB） | ✅ | reference.png 已生成。但 concept-art SKILL.md 要求的 prompt 规则（"枚举每个游戏对象"、"展示 HUD/UI 元素"、"必须看起来像游戏截图，不是概念艺术"）未被遵守——产出的 reference.png 是概念艺术风格而非游戏截图 |
| 7 | orchestrator/SKILL.md §阶段4b | UI 设计判定 | "判定时问一个问题：'这次任务完成后，玩家/用户会看到原来不存在的画面或控件吗？'答案是'是' → design-ui" | 日志中未发现 design-ui 调用 | ❌ | 用户要求创建新角色（"唐朝侍卫"），玩家会看到全新的角色外观（深红唐装、唐刀、辫子）。这是原来不存在的画面。应按判定原则 "宁可误判多调 design-ui，也不要漏判" 调用 design-ui，但被跳过 |
| 8 | orchestrator/SKILL.md §阶段5 | Plan 设计阶段 | "加载 `game-dev:plan` skill" | plan.md 已产出 | ✅ | plan.md 存在，包含任务列表和行为列表 |
| 9 | orchestrator/SKILL.md §阶段5 正常模式 | Plan Review 暂停 | "正常模式：plan 完成后必须调用 AskUserQuestion 暂停等待用户审查" | 日志中未发现 AskUserQuestion 调用 | ❌ | 用户未传 `--auto`，应为 normal 模式，需要暂停等待审查。但因步骤 1-2 错误地判定为 auto 模式，跳过了用户审查点。用户失去了在 plan 阶段纠正方向的机会 |
| 10 | orchestrator/SKILL.md §阶段6 | 资源检测与生成 | "asset-extract-doc → art-resources-conductor" | resources.md 存在，但所有 sprite 资源标记为 [HUMAN] | ⚠️ | plan.md 的"任务列表"中 [HUMAN] 任务直接写了 sprite sheet 需求，art-resources-conductor 未真正生成 sprite 资源。用户明确要求"先生成references参考图，必须用image-01-live使用漫画风格"，但实际只生成了 concept-art 的 reference.png，sprite sheet 被推给 HUMAN |
| 11 | exec/SKILL.md §6b | RED — spawn test-agent | "spawn game-dev:test-agent...测试文件已创建...所有 testcase 都失败了且原因正确" | tdd-iterations.md: "Iter 1 — RED...32 total...✅ 失败原因正确" | ✅ | RED 阶段形式正确：测试文件已创建，testcase 失败原因正确（场景不存在） |
| 12 | exec/SKILL.md §6c | GREEN 检查 — screenshot 验证 | "有 screenshot 验证方式的行为：visual-qa PASS" | tdd-iterations.md 未记录 GREEN 阶段的 visual-qa 结果 | ❌ | GREEN 检查要求 "有 screenshot 验证方式的行为：visual-qa PASS"，但 GREEN spawn 返回中无 visual-qa 调用记录。coding-agent 的 GREEN 报告（log L440 附近）未提及 visual-qa |
| 13 | exec/SKILL.md §6d | VERIFY — 独立验证门 | "全量测试全部通过...有 screenshot 验证方式的行为：额外通过 visual-qa PASS" | tdd-iterations.md L41: "Screenshot: 1/8 pass (jump_fall), 7/8 fail (test script positioning issues + missing level scene)" | ❌ | VERIFY 判定 "✅ GUT 全部通过 → 边界检查" 忽略了 7/8 screenshot 失败。Completion Gate（exec §Completion Gate）第4条明确要求"所有 screenshot 验证行为已创建截图 testcase 且通过 visual-qa"。7/8 失败不应通过 VERIFY |
| 14 | test-agent.md Screenshot Iron Law | 截图必须真实 viewport 截图 | "SCREENSHOT MEANS VIEWPORT CAPTURE. NOT PROGRAMMATIC DRAWING. A screenshot script that does not call get_viewport().get_texture() is not a screenshot script." | `tang_guard_in_level.png` 文件内容为 ASCII 文本 "base64: stdin: (null): error decoding base64 input stream" | ❌ | 8 张截图中 7 张是有效 PNG（320×180），但 `tang_guard_in_level.png` 是 base64 解码错误文本，非图片。此外 tdd-iterations.md 显示 7/8 截图失败。截图失败但被标记为通过 |
| 15 | exec/SKILL.md §6e | 边界检查 | "对每个任务强制执行...测试文件隔离...空代码/假代码" | tdd-iterations.md L44-50: 边界检查全部 ✅ | ✅ | 边界检查形式正确执行：测试文件隔离 ✅、空代码/假代码 ✅、资源引用完整性 ✅、节点路径有效性 ✅、原文件未修改 ✅ |
| 16 | exec/SKILL.md Completion Gate §4 | screenshot 验证完成 | "所有 screenshot 验证行为已创建截图 testcase 且通过 visual-qa" | 7/8 截图失败但 completion 仍标记为完成 | ❌ | Completion Gate 条件 4 未满足。tdd-iterations.md L75 标记 "Completed" 但 screenshot 验证未通过 |

---

### 根因分析与解决方案

| # | 应有步骤 | 达标? | 根因 | 解决方案 | 解决方案来源 |
|---|---------|-------|------|---------|-------------|
| 1 | Step 0e: 解析运行模式 | ❌ | **触发机制设计缺陷**：`start.md` 的指令 "Pass `--auto` for fully autonomous mode" 是歧义性的——它既是描述也是指令。模型将其理解为"始终添加 `--auto`"而非"仅在用户传入时传递"。缺少机制10（When NOT to Use）明确说明何时不应传递 `--auto` | 修改 `commands/start.md`：将 "Pass `--auto` for fully autonomous mode without human review checkpoints." 改为 "Pass the user's arguments through verbatim. If the user included `--auto` in their input, forward it; otherwise do NOT add `--auto`." | harness-methodology.md §机制10 (When NOT to Use) |
| 2 | Step 2b: Grilling 采访 | ❌ | **Iron Law 缺失执行验证**：orchestrator 有 "grill-interview.md 只能由 grilling skill 的返回内容写入" 的铁律，但缺少 Hard Gate（机制5）在阶段转换时强制执行验证。orchestrator 在 auto 模式下自行决定 "self-directed grilling" 是模型理性化的典型案例（机制3：Rationalization Table 中缺少 "auto 模式下可以自己 grill" 条目） | ① 在 orchestrator Red Flags 中增加："'auto 模式下我可以自己完成 grill 采访' → STOP。grill 的核心价值是向用户提问，不是 AI 自我分析。" ② 在 Step 2b 硬门中增加："GRILL_MISSING → 即使在 auto 模式也必须报告阻塞。auto 不能跳过 grill，只能跳过用户审查点。" ③ 强化 Step 2b 硬门：GRILL_OK 后必须 grep 文件检查是否包含 "ask" 或 "?" 问句（对话格式的必要特征） | harness-methodology.md §机制1 (Iron Law) + §机制5 (Hard Gate) + §机制3 (Rationalization Table) |
| 3 | Step 4b: UI 设计判定 | ❌ | **判定规则被理性化绕过**：orchestrator 有 "宁可误判多调 design-ui" 的判定原则和 Red Flag "这个任务不需要 UI 设计...虽然有新界面但是纯控件布局" 。但 orchestrator 在 auto 模式下自行判定不需要 design-ui。缺少机制3（Rationalization Table）覆盖"新角色不需要 design-ui"这个借口 | 在 orchestrator Red Flags 中增加："'新角色不需要 UI 设计，只是换个 sprite' → STOP。角色外观是新画面，design-ui 的判定门是'玩家会看到原来不存在的画面吗'，答案是'是'就必须 design-ui。" | harness-methodology.md §机制3 (Rationalization Table) + diagnosis-guide.md §2.3 |
| 4 | Step 5: Plan Review | ❌ | **连锁效应**：因为步骤 1-2 错误地判定为 auto 模式，跳过了 normal 模式下的 AskUserQuestion 审查点。这不是 plan 本身的问题，而是步骤 1 的 `--auto` 编造导致的连锁故障 | 修复步骤 1 的 `--auto` 问题即可解决。同时在 orchestrator 中增加验证：如果从 user-prompt.md 中 grep 不到 `--auto` 但 mode=auto，则报错 | harness-methodology.md §机制5 (Hard Gate) |
| 5 | §6d: VERIFY screenshot 失败仍通过 | ❌ | **Completion Gate 缺少自动化强制**：exec SKILL.md Completion Gate §4 写了 "所有 screenshot 验证行为已创建截图 testcase 且通过 visual-qa"，但这是人工检查清单，不是自动化硬门。exec 的 VERIFY 步骤（6d）只检查了 GUT 测试结果，将 screenshot 结果单独列在 tdd-iterations.md 中但没有将其作为 VERIFY 的阻塞条件。缺少机制5（Hard Gate）：VERIFY 判定前必须检查 screenshot 结果 | 修改 exec SKILL.md §6d，在检查结果中增加："[ ] 有 screenshot 验证方式的行为：所有截图 testcase visual-qa PASS（零失败容忍）。任一 FAIL → VERIFY 不通过，回退 GREEN 重做。" 并修改 Completion Gate §4 为可执行命令："grep 'FAIL' screenshot 结果 → 阻塞" | harness-methodology.md §机制5 (Hard Gate) |
| 6 | §6c/6d: Screenshot Iron Law 违规 | ❌ | **test-agent 的 Screenshot Iron Law 未被 exec 强制执行**：test-agent.md 有 "SCREENSHOT MEANS VIEWPORT CAPTURE" 的 Iron Law，但 exec 在 GREEN 和 VERIFY 检查中没有验证截图脚本是否真的调用了 `get_viewport().get_texture()`。`tang_guard_in_level.png` 是 base64 解码错误（非图片），exec 未检测出来。缺少机制5（Hard Gate）在 GREEN/VERIFY 中验证截图文件有效性 | 在 exec SKILL.md §6c GREEN 检查和 §6d VERIFY 检查中增加："[ ] 所有截图文件为有效 PNG（`file {path}` 输出含 'PNG image data'）。非图片文件 → 截图脚本执行失败，GREEN/VERIFY 不通过" | harness-methodology.md §机制5 (Hard Gate) + agent-structure.md §2.3 (Output Validation) |
| 7 | §阶段6: 资源生成 | ⚠️ | **art-resources-conductor 未充分执行**：plan 将 sprite sheet 标记为 [HUMAN]，art-resources-conductor 未尝试用 AI 生成。用户明确要求 "必须用 image-01-live 使用漫画风格" 生成参考图，暗示期望 AI 生成美术资源。concept-art 生成了 reference.png 但下游 resource generation 被跳过。风险：orchestrator 缺少对 [HUMAN] 标记的二次确认——应检查是否真的需要 HUMAN 或可用 AI 替代 | 在 orchestrator §阶段6 中增加判定：当 resources.md 中存在标记为 [HUMAN] 的资源时，检查该资源是否明确超出 AI 能力范围。sprite sheet 生成属于 AI 可尝试的范围（mmx image generate），不应默认标记 HUMAN。修改 art-resources-conductor 的判定逻辑 | diagnosis-guide.md §3.2 (问题分类决策) + concept-art/SKILL.md prompt 规则 |

---

### 不在范围的项

以下用户报告中提到的问题经"诊断范围边界"核心判定法则检查后，确认不属于 plugin-improve 诊断范围：

| 用户投诉 | 判定 | 理由 |
|---------|------|------|
| "完全没做任何努力设计如何实现player" — 指 plan 设计质量 | ⏭️ 不在范围 | plan.md 的内容质量（架构设计深度、行为列表完整性）属于目标项目设计质量，不属于插件工程问题。plan SKILL.md 的流程步骤（读取文件→提取用户指示→生成设计文档）已正确执行 |
| "生成资源用概念图敷衍" — 指 reference.png 视觉效果 | ⏭️ 不在范围 | reference.png 的图像质量属于 AI 生成内容质量，不属于插件工程问题。concept-art 的流程（读取上下文→调用 mmx→保存图片）已正确执行 |
| tang_guard.gd 代码质量 | ⏭️ 不在范围 | 生成的游戏代码是否有 bug、是否完整实现了需求，属于目标项目代码质量问题 |

以上 3 项不进入根因分析，不产生修复方案。
