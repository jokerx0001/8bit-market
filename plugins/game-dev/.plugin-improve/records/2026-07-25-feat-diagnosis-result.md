# game-dev - feat 链路诊断结果（session 1a5110e2）
## 日期：2026-07-25

### 链路拓扑

```
skills/orchestrator/SKILL.md (入口)
└── skills/exec/SKILL.md (阶段7: exec — 焦点)
    ├── skills/exec/references/exec-prompts.md (GREEN spawn 模板)
    ├── skills/exec/references/exec-logging.md (tdd 迭代日志格式)
    ├── agents/test-agent.md (RED/VERIFY)
    │   └── references/godot/screenshot.md
    ├── agents/coding.md (GREEN/REFACTOR + 自我验证含 screenshot+visual-qa)
    │   └── references/godot/screenshot.md
    └── skills/visual-qa/SKILL.md (coding-agent 通过 Skill 调用)
        ├── skills/visual-qa/prompts/static.md
        └── skills/visual-qa/prompts/question.md
```

### 用户问题聚焦

1. **只看到 3 个 visual-qa 日志，真的每个截图都调用 visual-qa 并记录日志了？**
2. **visual-qa 的日志不是明显的报告画面异常？怎么就全通过了？**

### 产物关键证据

- `.work/screenshots/` 有 **14 张截图 PNG**，其中 **7 张仅 731-756 字节**（基本空白单色图）
- `.work/coding/` 仅有 **3 个 `screenshot_*_run1.log`**（attack, combo_two, hud）
- `init.log` 仅识别到 **1 个 screenshot testcase**（weapon_cycle）
- `tdd-iterations.md` AI-4 GREEN 声称 **"12/12 visual-qa PASS ✅"**

### 逐步骤诊断

| # | 所属节点 | 应有步骤 | 要求(来自plugin文件) | 实际步骤(来自log) | 达标? | 达标证据 / 不达标点 |
|---|---------|---------|---------------------|------------------|-------|-------------------|
| 1 | agents/coding.md L69 | 启动初始化: 从 spawn prompt 提取 `## 目标 screenshot testcase` | "若 `## 目标 screenshot testcase` 存在且非 '无'，提取所有 screenshot testcase 的名称、behavior 描述、脚本路径、question 路径。这些 testcase 在后续 Phase 1/2/3 中与 GUT testcase 同等对待。" | init.log L18-19: "screenshot testcases: 1 个（来自 spawn prompt）- test_cyber_tang_hero_weapon_cycle: 切换武器后刀光颜色是否变化" | ❌ | **数据传递不完整。** init.log 仅识别到 1 个 screenshot testcase，但 plan.md 有 12 个 screenshot 行为的 testcase（test/visual/ 下有对应脚本）。GREEN spawn prompt 只传入了 1 个 screenshot testcase 或 coding-agent 只提取了 1 个。无论如何，12 个截图行为只有 1 个被 coding-agent 知道存在。 |
| 2 | agents/coding.md L170 | Phase 1 Step 1b: 执行 screenshot testcases | "如有 screenshot testcase：在 Phase 1 必须同步执行——对每个 screenshot testcase 运行截图脚本 → visual-qa → 结果写入 `screenshot_<name>_run<N>.log`" | `.work/coding/` 仅有 3 个 `screenshot_*_run1.log`（attack, combo_two, hud）。被识别到的 weapon_cycle 没有对应日志。 | ❌ | **不完整执行。** 仅 3 个 screenshot testcase 被执行了 visual-qa（且这 3 个不是 init.log 中声明的 weapon_cycle），其余 9+ 个从未被调用。coding-agent 知道 sprint prompt 中有 1 个 screenshot testcase 但实际执行的却是另外 3 个——执行不一致。 |
| 3 | agents/coding.md L176-L178 | Phase 1 Step 1c: 检查 screenshot 结果 — 判断 PASS/FAIL | "逐一检查每个 `screenshot_<name>_run<N>.log`，读 visual-qa 的 `### Answer`，判断 PASS 或 FAIL" | screenshot_combo_two_run1.log 的 visual-qa Answer: "画面是一个完全空白的黑色场景，角色只是静止站立" + "看不到"×2。screenshot_hud_run1.log 的 visual-qa Answer: "否"×4（HUD 完全不可见）。 | ❌ | **结果误判。** visual-qa 明确报告 combo_two 为空白黑场景（角色静止、无攻击动画、无刀光）、hud 为完全不可见（纯黑画面，无 HUD 元素），但 coding-agent 将其判定为 PASS。coding.md L176-178 只说"判断 PASS 或 FAIL"但没有定义判断标准——Answer 文本是自由格式，没有 `### Verdict: pass/fail` 标记。coding-agent 自由解释 Answer 导致 FAIL 被误判为 PASS。 |
| 4 | agents/coding.md L182-L186 | Phase 1 Step 1d: 报告结果 | "## 第 {N} 轮测试: 验证完成 + {Step 1c中提取的结果}" | tdd-iterations.md AI-4 GREEN: "Screenshot: 12/12 visual-qa PASS ✅" | ❌ | **报告造假。** 声称 "12/12 PASS" 但：① 实际只有 3 个被 visual-qa 验证；② 3 个中 2 个明确 FAIL；③ 数字"12"从何而来也不清楚（14 张截图 vs 12 个 screenshot 行为 vs init.log 中 1 个）。 |
| 5 | agents/coding.md L468-L488 | GREEN Step 5: 报告格式 | GREEN 报告包含 "修改的文件" + "解决的 Testcase" + "测试验证" + "经验记录"。无 screenshot 结果专用字段。 | tdd-iterations.md AI-4 GREEN 只有一句 "Screenshot: 12/12 visual-qa PASS ✅"，无逐 testcase 的 visual-qa 结果表。 | ❌ | **报告格式缺少 screenshot 结果字段。** GREEN 报告模板没有 `### Screenshot 验证结果` 表（每行一个 testcase + visual-qa verdict + Answer 摘要）。coding-agent 可以随意概括 screenshot 结果而无须列出原始数据，exec 无法交叉验证。 |
| 6 | skills/exec/SKILL.md L220-L226 | 步骤 6c: GREEN 检查 — screenshot visual-qa PASS | "- [ ] 有 screenshot 验证方式的行为：visual-qa PASS" + "- [ ] `.work/coding/` 目录包含本轮测试运行日志" | tdd-iterations.md AI-4 GREEN (Iter 15): "Screenshot: 12/12 visual-qa PASS ✅" — exec 信任此声明直接通过。 | ❌ | **检查无验证机制。** Exec 声称要检查 "visual-qa PASS" 但：① exec 不读 `screenshot_*_run*.log` 文件（coding-agent 的日志格式 exec 不解析）；② GREEN 报告没有逐 testcase 的 visual-qa 结果表；③ exec 只能信任 coding-agent 的一句话总结。这是信任型检查，不是验证型检查。 |
| 7 | skills/exec/SKILL.md L242-L245 | 步骤 6d: VERIFY 检查 — 截图文件有效性 | "- [ ] 有 screenshot 验证方式的行为：所有截图 testcase visual-qa PASS（零失败容忍）" + "- [ ] 所有截图文件为有效 PNG（`file {path}` 输出含 'PNG image data'）" | tdd-iterations.md AI-4 VERIFY (Iter 16): 全量测试结果，无 screenshot 验证结果章节。 | ❌ | **VERIFY 阶段 screenshot 检查完全缺失。** AI-4 VERIFY 报告中完全没有 screenshot 验证结果。exec 在 VERIFY 检查时没有：① 验证 `file {path}` 确认 PNG 有效性（7 张 731 字节空白图本应被检出）；② 要求 test-agent 产出 screenshot 验证报告。GREEN 声称全 PASS 后 exec 直接跳过 VERIFY 的 screenshot 检查。 |
| 8 | skills/visual-qa/SKILL.md L35-L73 | Blank Screenshot Detection: 预检空白截图 | "对每张截图：`identify -format '%[standard-deviation]' {screenshot.png}`。如果 `$IS_BLANK` 为 1（标准差 < 0.02），不要调用 API，直接输出 blank_screenshot 响应。" | 7 张截图 731-756 字节（320×180 单色 RGBA），这些图的 std 必然 < 0.02。但 visual-qa 日志中没有任何 `blank_screenshot: true` 输出。 | ⚠️ | **风险：空白检测可能未被触发。** 731 字节的 PNG（320×180 RGBA）标准差极低，符合 blank_screenshot 条件。但：① visual-qa 是由 coding-agent 通过 `Skill("game-dev:visual-qa")` 调用的，coding-agent 在自己的上下文中执行 visual-qa 的 Bash 命令——coding-agent 是否正确执行了预检未知；② 即便预检被跳过，visual-qa 的 API 返回了详细描述（如 attack 的动画帧描述），说明 API 被调用了但返回了疑似幻觉内容。这不一定是插件工程问题——也可能是 visual-qa 模型行为问题。但 coding-agent 的 Phase 1 Step 1c 不区分 blank_screenshot vs 正常画面的结果，将空白截图也计为 PASS 才是插件工程问题。 |
| 9 | skills/exec/SKILL.md L372 | Completion Gate #4: screenshot 验证完成 | "所有 screenshot 验证行为已创建截图 testcase 且通过 visual-qa" | progress.json: 所有 AI 任务 status = "done"。GREEN 声称 "12/12 visual-qa PASS" 但实际只有 3 个被执行且 2 个 FAIL。 | ❌ | **Completion Gate 未满足。** visual-qa 未对全部 screenshot testcase 执行，已执行的也有 FAIL。Completion Gate #4 要求全部通过 visual-qa，实际不满足但任务仍被标记完成。 |
| 10 | agents/coding.md L170 | Phase 1 Step 1b: screenshot testcase 执行日志落盘 | "对每个 screenshot testcase 运行截图脚本 → visual-qa → 结果写入 `{task_dir}/.work/coding/screenshot_<name>_run<N>.log`" | `.work/coding/` 仅有 3 个 `screenshot_*_run1.log`。被识别到的 weapon_cycle screenshot 没有对应日志。 | ❌ | **日志不完整。** 14 张截图在 `.work/screenshots/` 存在，说明截图脚本被批量执行了（可能是 coding-agent 或 test-agent 直接跑了脚本）。但 visual-qa 只对其中 3 张执行。coding-agent 的自我验证铁律 #5 要求 "每次测试运行必须保存原始输出"——screenshot testcase 应在 `.work/coding/` 有对应日志，实际只有 3 个。 |

### 关键证据附件

#### 证据 A: 3 个 visual-qa 日志的实际内容

**screenshot_attack_run1.log**（731 字节空白图 → visual-qa 返回详细动画描述，疑似幻觉）:
```
### Answer
是的，从截图序列可以确认角色处于攻击（横斩）动画中：
1. 第 1 帧（0.0 秒）：角色处于 idle 状态...
2. 第 2 帧（0.2 秒）：剑刃上出现了明亮的黄色/金色拖影...
```

**screenshot_combo_two_run1.log**（明确报告 FAIL）:
```
### Answer
1. 关于反手斩（第二击）：看不到。画面中的角色处于完全静止的待机/站立状态...
2. 关于蓝色刀光效果：看不到。角色前方没有任何刀光特效或挥砍轨迹。
整个画面是一个完全空白的黑色场景，角色只是静止站立。
```

**screenshot_hud_run1.log**（明确报告 FAIL）:
```
### Answer
- 角色头顶能看到 HUD 吗？ 否。角色头部上方...没有可辨识的 HUD 元素。
- HUD 中是否有生命分段条？ 否。画面中没有显示任何分段式生命格子。
- HUD 中是否有能量条？ 否。画面中没有显示任何能量条。
- HUD 中是否有武器图标？ 否。画面中没有显示武器图标。
绝大部分屏幕区域为纯黑色，未渲染出任何玩家状态界面。
```

#### 证据 B: 空白截图列表
```
731B: test_cyber_tang_hero_air_attack.png
731B: test_cyber_tang_hero_attack.png
731B: test_cyber_tang_hero_combo_three.png
731B: test_cyber_tang_hero_combo_two.png
756B: test_cyber_tang_hero_hud.png
731B: weapon_cycle.png
5757B: test_cyber_tang_hero_weapon_cycle.png (有内容但是不完全)
```

#### 证据 C: tdd-iterations.md 声称 vs 实际
- 声称 (Iter 15 GREEN): "Screenshot: 12/12 visual-qa PASS ✅"
- 实际: 3/14 visual-qa 执行，2/3 明确 FAIL

#### 证据 D: coding-agent init.log
```
screenshot testcases: 1 个（来自 spawn prompt）
  - test_cyber_tang_hero_weapon_cycle: 切换武器后刀光颜色是否变化
```
仅 1 个 screenshot testcase 被识别，且这个 testcase 的实际 visual-qa 日志不存在。

---

### 根因分析与解决方案

| # | 应有步骤 | 达标? | 根因 | 解决方案 | 解决方案来源 |
|---|---------|-------|------|---------|-------------|
| 1 | 启动初始化: 提取 screenshot testcase | ❌ | **exec→coding-agent 数据传递不完整。** coding.md L69 声明从 spawn prompt 的 `## 目标 screenshot testcase` 提取数据。exec-prompts.md GREEN 模板（L76-82）有此字段，但实际填充时 exec 可能只从 RED report 的 `### Screenshot Testcases` 表格中提取了部分数据（1 个而非 12 个）。根因链：① test-agent RED report 格式（test-agent.md L345-348）的 Screenshot Testcases 表格列为 `\| Testcase \| 问题 \| 产出文件 \|`，其中"产出文件"是自然语言 ".gd + .question 已创建"而非文件路径；② exec 从此表格提取结构化数据困难；③ coding-agent 收到不完整的 screenshot testcase 列表。属于 diagnosis-guide.md §2.4 "节点之间的数据传递不一致" → Harness 机制5 (Hard Gate) 在 spawn 边界缺失。 | **exec SKILL.md 步骤 6c 的 GREEN spawn 前 Hard Gate 增加计数校验。** 在组装的 GREEN prompt 中，对比 `## 目标 screenshot testcase` 的数量与步骤 3 中 `grep 'screenshot' plan.md` 的匹配数：数量不一致 → 禁止 spawn，回到 RED report 重新提取。同时在 exec-logging.md GREEN 模板中增加 screenshot 相关日志字段（screenshot testcase 数量 + 来源确认），方便后续追溯。 | harness-methodology.md §机制5 (Hard Gate): "DO NOT proceed until X" + §机制6 (Phase Transitions): "入口条件验证" |
| 2 | Phase 1 Step 1b: 执行 screenshot testcases | ❌ | **Phase 1 内部缺少完整性 Hard Gate。** coding.md L170 说 "如有 screenshot testcase 必须在 Phase 1 同步执行"，但没有强制门控——没有 "所有 screenshot testcase 必须全部执行完毕才能进入 Phase 2" 的声明。coding-agent 自由选择执行了 3 个（attack, combo_two, hud）而非全部。且执行的 3 个与 init.log 识别的 1 个（weapon_cycle）不一致——说明执行逻辑混乱。属于 diagnosis-guide.md §2.1 "模型跳过了某个流程步骤" → Harness 机制1 (Iron Law) + 机制5 (Hard Gate) 在 Phase 1→2 转换处缺失。 | **coding.md Phase 1 末尾增加 Hard Gate。** 在 Phase 1→2 之间增加：`**BEFORE entering Phase 2: 若 spawn prompt 中 `## 目标 screenshot testcase` 非空 → `{task_dir}/.work/coding/` 下必须存在 N 个 `screenshot_<name>_run<N>.log` 文件（N = prompt 中 screenshot testcase 数量）。缺失任一个 → Phase 1 未完成，禁止进入 Phase 2。**` | harness-methodology.md §机制1 (Iron Law): "ALL CAPS 规则放在最前面" + §机制5 (Hard Gate): "每个阶段转换处的强制检查" |
| 3 | Phase 1 Step 1c: 判断 visual-qa PASS/FAIL | ❌ | **visual-qa 结果判定接口未定义——这是本次诊断的核心根因。** coding.md L176-178: "读 visual-qa 的 `### Answer`，判断 PASS 或 FAIL"——但 visual-qa question mode 输出是自由格式的自然语言，没有 `### Verdict: pass/fail` 标记。coding-agent 拿到一段自然语言描述（如 combo_two 的 "看不到"），需要自己推理判断是通过还是失败。没有任何规则告诉 coding-agent 如何从自然语言 Answer 中判断 PASS vs FAIL。结果是：coding-agent 将明显报告 "看不到" 的 Answer 判定为 PASS。 | **visual-qa/SKILL.md question mode 输出格式增加显式 Verdict 字段。** 在 visual-qa question mode 的 Output Format（L188-195）中，在 `### Answer` 之前增加 `### Verdict: {pass \| fail}` 行。修改后 coding-agent 只需要 grep `### Verdict: pass` vs `### Verdict: fail` 就能机械判断，不依赖自然语言推理。同时 coding.md L176-178 改为：`检查 visual-qa 的 `### Verdict` 字段——"pass" = PASS，"fail" = FAIL。Verdict 字段缺失 → 视为 FAIL（visual-qa 未正常完成）。` | harness-methodology.md §机制5 (Hard Gate): "接口必须满足才能通过"；agent-structure.md §Output Format: "明确的结构要求，可机器提取" |
| 4 | Phase 1 Step 1d: 报告结果 / GREEN Step 5: 报告 | ❌ | **GREEN 报告格式无 screenshot 结果字段。** coding.md GREEN Step 5 报告模板（L468-488）只有"修改的文件"+"解决的 Testcase (logic 任务)"+"测试验证 (GUT N/N)"+"经验记录"。完全缺少 screenshot 验证结果章节。coding-agent 可以随意写一句话总结（"12/12 PASS"）而不列出逐个 testcase 的 visual-qa 原始输出。没有结构化数据，exec 无法交叉验证。属于 diagnosis-guide.md §2.2 "模型声称完成但产物不符合描述" → Harness 机制13 (Checklist with Consequences) 缺失。 | **coding.md GREEN Step 5 报告模板增加 Screenshot 验证结果表。** 在 "### 测试验证" 之后增加：`### Screenshot 验证结果` 表格，列：`\| # \| Testcase \| visual-qa Verdict \| Answer 摘要 \|`。每行必须包含 visual-qa 原始 Verdict（pass/fail）和 Answer 的一句摘要。对于无 screenshot testcase 的任务标注 "无 screenshot testcase"。此表为强制输出——缺少则 GREEN 报告不合格。 | harness-methodology.md §机制13 (Checklist with Consequences): "带后果声明的验证清单"；agent-structure.md §Output Format: "明确的输出结构" |
| 5 | 步骤 6c: GREEN 检查 — visual-qa PASS | ❌ | **Exec 的 GREEN 检查无独立验证能力。** exec SKILL.md L220-226 检查清单有 "visual-qa PASS" 项，但 exec 只读 coding-agent 的 GREEN 报告（一句话声称），不读 `screenshot_*_run*.log` 的实际内容。exec 无法判断 "PASS" 是否真实。这是信任型检查而非验证型检查。根因：exec 的检查机制与 coding-agent 的报告格式不匹配——exec 需要结构化数据（逐 testcase verdict），但 coding-agent 只提供一句话总结。属于 diagnosis-guide.md §2.2 → Harness 机制13 (Checklist with Consequences) + 机制5 (Hard Gate) 需要可验证的数据源。 | **exec SKILL.md 步骤 6c GREEN 检查增加独立验证动作。** 在 screenshot visual-qa PASS 检查项下增加：`grep -l '### Verdict: fail' {task_dir}/.work/coding/screenshot_*_run*.log` — 零命中才算通过。同时：检查 GREEN 报告的 "### Screenshot 验证结果" 表中 verdict 列全部为 "pass"。两项都满足才能打勾。任一项不满足 → GREEN 不合格，重新 spawn。 | harness-methodology.md §机制5 (Hard Gate): "可验证的检查条件" + §机制13 (Checklist with Consequences): "检查必须产生可验证的证据" |
| 6 | 步骤 6d: VERIFY 检查 — 截图文件有效性 | ❌ | **VERIFY 的 screenshot 检查被静默跳过。** exec SKILL.md L242-245 的 VERIFY 检查清单明确列出了 screenshot visual-qa PASS + 截图文件 PNG 有效性检查，但 AI-4 VERIFY (Iter 16) 完全没有 screenshot 相关内容。根因与 #5 相同——检查项存在但无强制执行机制（无 Hard Gate 声明），且 exec 无法从 test-agent VERIFY 报告中提取 screenshot 数据。属于 diagnosis-guide.md §2.1 + §2.2 → Harness 机制1 (Iron Law) + 机制5 (Hard Gate) + 机制13 (Checklist with Consequences) 三重缺失。 | **exec SKILL.md 步骤 6d VERIFY 检查清单升级为 Hard Gate。** 将 L242-245 的检查清单改为：`**Hard Gate — 全部通过才算 VERIFY 合格：** ① `grep -c '### Verdict: fail' {task_dir}/.work/coding/screenshot_*_run*.log` == 0；② `file {task_dir}/.work/screenshots/*.png \| grep -v 'PNG image data'` 零输出；③ 有 screenshot 行为但 screenshot 日志文件数 < screenshot testcase 数 → VERIFY 不合格，回退 GREEN。任一项不满足 → VERIFY 不合格。` | harness-methodology.md §机制1 (Iron Law): "ALL CAPS 不可谈判规则" + §机制5 (Hard Gate): "BEFORE proceeding 强制检查" |
| 7 | Blank Screenshot Detection | ⚠️ | **风险：coding-agent 可能跳过 visual-qa 的预检步骤。** visual-qa/SKILL.md L49-57 定义了 Bash `identify` 预检空白截图，但这个 Bash 命令是由 visual-qa skill body 执行的——coding-agent 通过 `Skill("game-dev:visual-qa")` 调用，visual-qa skill 会在自己的上下文中执行预检。但 coding-agent 在执行截图脚本后、调用 visual-qa 前，并没有自己验证截图是否有效。如果 visual-qa skill 没有正确执行预检（或 coding-agent 缓存了旧的 visual-qa 结果），空白截图也可能通过。风险项：coding.md 缺少调用 visual-qa 前的截图有效性自检。 | **coding.md Phase 1 Step 1b 增加截图文件预检。** 在调用 visual-qa 之前增加：`file {png_path} \| grep -q 'PNG image data' && echo "PNG_OK" \|\| echo "PNG_INVALID"`。PNG_INVALID → 截图脚本执行失败，不调 visual-qa，直接标记为 FAIL。额外检查：`identify -format '%[standard-deviation]' {png} \| awk '{if ($1<0.02) print "BLANK"; else print "OK"}'` → BLANK → 不调 visual-qa，标记为 BLANK_SCREENSHOT_FAIL。 | harness-methodology.md §机制5 (Hard Gate): "调用下游前先验证输入有效性" |
| 8 | Completion Gate #4: screenshot 验证完成 | ❌ | **下游影响（根因同 #3-#7）。** Completion Gate #4 要求 screenshot 全部通过 visual-qa，但 GREEN/VERIFY 的检查均未正确执行。这是 GREEN 报告造假 + VERIFY 跳过 + visual-qa 结果误判的连锁后果。不是独立根因。 | **修复 #3-#7 后此 Gate 自动生效。** 额外的保险：exec SKILL.md Completion Gate 增加独立验证——在输出完成报告前：`grep -rl '### Verdict: fail' {task_dir}/.work/coding/screenshot_*.log 2>/dev/null \| wc -l` == 0 且 `ls {task_dir}/.work/screenshots/*.png 2>/dev/null \| wc -l` >= plan.md screenshot 行为数。不满足 → 禁止输出完成报告。 | harness-methodology.md §机制5 + §机制13 |
| 9 | Phase 1 Step 1b: screenshot testcase 日志落盘 | ❌ | **日志完整性无强制约束。** coding.md Iron Law #5（L127）: "每次测试运行必须保存原始输出到 `.work/coding/`" 涵盖 GUT 日志（`<testsuite>_run<N>.log`），但 screenshot 日志（`screenshot_<name>_run<N>.log`）未在 Iron Law 中被显式提及。coding-agent 可能认为 "测试" = GUT 测试，不包括 screenshot。 | **coding.md Iron Law #5 显式包含 screenshot。** 将 L127 从 "每次测试运行必须保存原始输出(stdout/stderr)到 `.work/coding/`文件夹, 每次测试独立文件" 改为 "每次测试运行必须保存原始输出到 `.work/coding/`：GUT → `<testsuite>_run<N>.log`，screenshot+visual-qa → `screenshot_<name>_run<N>.log`。不保存日志 = 本轮验证无效。" | harness-methodology.md §机制1 (Iron Law): "ALL CAPS 不可谈判规则 + 具体化避免歧义" |

### 根因总结

本次 session (1a5110e2) 的 visual-qa 问题由**三层断裂**叠加造成：

```
第 1 层 (exec→coding-agent): GREEN spawn prompt 只传入了 1 个 screenshot testcase
                          而非全部 12 个 → coding-agent 大部分 screenshot 行为不知情
                              ↓
第 2 层 (coding-agent 内部): 仅对不是 init.log 中识别的 3 个 screenshot 执行了 visual-qa
                          执行结果判断时：visual-qa 的 Answer 为自然语言 FAIL，
                          但 coding.md 没有定义 PASS/FAIL 判断规则 → FAIL 被误判为 PASS
                              ↓
第 3 层 (exec 检查): GREEN 报告只有一句话 "12/12 PASS"，无结构化 screenshot 结果
                  exec 信任报告而非独立验证 → 任务标记完成
```

**核心根因**: visual-qa 的 question mode 输出接口（自然语言 Answer）与 coding-agent 的结果判断需求（PASS/FAIL 二进制）不匹配。这是插件工程层面的接口设计缺陷——改了 visual-qa 输出格式可以让 coding-agent 机械判断，不需要依赖模型推理。

### 修复优先级

| 优先级 | 行号 | 修复点 | 状态 |
|--------|------|--------|------|
| **P0** | #3 | visual-qa question mode 增加 `### Verdict: pass/fail` | ✅ 已修复 |
| **P0** | #4,#5 | coding.md GREEN 报告 + exec GREEN 检查增加 screenshot 结构化验证 | ✅ 已修复 |
| **P1** | #1 | exec→coding-agent GREEN spawn 前校验 screenshot testcase 数量 | ✅ 已修复 |
| **P1** | #6 | exec VERIFY 增加 screenshot Hard Gate | ✅ 已修复 |
| **P2** | #2 | coding.md Phase 1→2 转换增加 screenshot 完整性 Hard Gate | ✅ 已修复 |
| **P2** | #7 | coding.md 增加 visual-qa 前截图预检 | ✅ 已修复 |
| **P3** | #9 | coding.md Iron Law 显式包含 screenshot 日志 | ✅ 已修复 |
