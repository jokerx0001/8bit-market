### 第 9 轮（2026-07-24）— feat 链路 `--auto` 编造 + grill 跳过 + VERIFY 放行 + 截图场景错误 + coding-agent Skill 缺失 + GREEN 数据传递断裂

- **节点：** agents/coding.md
- **问题：** 诊断追加 #3 — coding-agent 的 `tools` 列表缺少 `Skill`。coding.md 初始化步骤 3 定义了 `调用 Skill("game-dev:visual-qa")`（L80），规则 14 要求截图 + visual-qa 自验证（L721），但 frontmatter `tools: ["Read", "Write", "Edit", "Glob", "Bash", "Grep", "WebFetch"]` 中没有 `Skill`。coding-agent 即使知道要调 visual-qa，工具权限不允许。session f36dc99b 中 0 次 Skill 调用（对比：VERIFY test-agent 有 7 次 visual-qa）。
- **修复：** tools 列表增加 `Skill`
- **来源：** coding.md frontmatter vs L80/L721 代码分析；session log — GREEN coding-agent 0 Skill calls vs VERIFY test-agent 7 Skill calls
- **结果：** 待验证

---

- **节点：** skills/exec/references/exec-prompts.md + agents/coding.md
- **问题：** 诊断追加 #4 — GREEN spawn prompt 的数据传递断裂（日志证据确认）。RED report（L391）明确包含 `### Screenshot Testcases` 段（8 个 testcase + behavior 描述 + 文件路径），但 exec-prompts.md GREEN 模板（L69-75）只提取了 `### Testsuite` 和 `### Testcases`（实际匹配到 `### GUT Testcases`），完整丢弃了 Screenshot Testcases。结果：GREEN spawn prompt（L402）有 32 个 GUT testcase 名称，零个 screenshot testcase。coding-agent 读了 screenshot.md（在其 Read 列表中）但 spawn prompt 没告诉它存在 screenshot testcase。
- **修复：**
  1. **exec-prompts.md GREEN spawn 模板**：`### Testcases` → `### GUT Testcases`；新增 `## 目标 screenshot testcase（如有）` 段，从 RED report 的 `### Screenshot Testcases` 表格提取
  2. **coding.md Phase 1 Step 1b**：新增 screenshot 同步执行说明——spawn prompt 中有 screenshot testcase 时必须在 Phase 1 运行，失败与 GUT 同等对待进入 Phase 2
- **来源：** L391 RED report vs L402 GREEN spawn prompt 逐字段对比；exec-prompts.md L69-75
- **结果：** 待验证

---

- **节点：** skills/exec/references/exec-prompts.md + agents/coding.md
- **问题：** 诊断追加 #3 — GREEN spawn prompt 的数据传递断裂。coding-agent 的 coding.md 规则 14 和初始化步骤 3 明明定义了 screenshot + visual-qa 方法，但 session f36dc99b 中 coding-agent 从未执行 screenshot 验证。根因：exec-prompts.md GREEN spawn 模板只提取了 "### Testsuite" 和 "### Testcases"（GUT），丢弃了 RED report 中的 "### Screenshot Testcases" 表格。coding-agent 根本不知道有 screenshot testcase 存在，只跑了 GUT，全绿就报告成功。
- **修复：**
  1. **exec-prompts.md GREEN spawn prompt**：新增 `## 目标 screenshot testcase（如有）` 字段，从 RED report 的 "### Screenshot Testcases" 表格提取 testcase 名 + .question Requirement + 脚本路径
  2. **coding.md Phase 1 Step 1b**：新增 "如有 screenshot testcase 必须在 Phase 1 同步执行——截图脚本 → visual-qa → 日志落盘。screenshot 失败与 GUT 失败同等对待，进入 Phase 2 逐个诊断修复"
  3. **exec-prompts.md GREEN 检查条件**：screenshot visual-qa PASS 从泛泛的 "PASS" 改为 "所有 screenshot testcase visual-qa PASS"，增加 visual-qa 结果必须出现在自验证日志中的要求
- **来源：** session f36dc99b — coding-agent init.log 只解析了 GUT 命令；tdd-iterations.md GREEN 报告无 screenshot 内容；coding.md L79-82 + L721 规则 14 定义了方法但未被触发
- **结果：** 待验证

---

- **节点：** agents/test-agent.md
- **问题：** 诊断追加 #2（已纠正）— 最初误判为 test-agent 未调 visual-qa。经查证 log L453，VERIFY 的 test-agent（agentId: a91380c9296f2440e）**确实调了 visual-qa**，运行了全部 8 张截图，产出详细报告：1 PASS (jump_fall), 7 FAIL。真正的问题是 **exec 的 VERIFY 门** 拿到这个 7/8 FAIL 的结果后只看了 GUT 全绿就放行了。test-agent 的行为是正确的。
- **修复（已回退）：** 最初对 test-agent.md screenshot测试执行方法 增加了 Iron Law + 硬门 + qa.log 保存，现已全部还原。正确修复在 exec SKILL.md §6d（见下方 exec 条目）
- **来源：** session f36dc99b log L453 — VERIFY test-agent 完整 visual-qa 报告
- **结果：** 已回退 ✅（保留 Screenshot Iron Law + 场景选择规则 + Red Flags 关于 isolated .tscn 的部分）
- **修复：**
  1. Screenshot Iron Law 增加：禁止加载 isolated component .tscn；截图必须捕获行为在游戏关卡/HUD/菜单中的实际表现
  2. Screenshot Red Flags 增加 2 条中英双语：禁止"加载角色的 tscn 就行"和"加载独立的 tscn 就能看到角色外观"
  3. Step W2 新增"场景选择规则"表格：角色外观→加载关卡场景；UI界面→加载游戏场景含UI；战斗→加载关卡含敌人；主菜单→加载菜单场景。附带判定原则"玩家在哪里看到就加载哪个场景"
- **来源：** 用户反馈 — 截图针对 isolated .tscn 无意义，行为验证要求截图反映实际 gameplay
- **结果：** 待验证

---

### 第 9 轮（2026-07-24）— feat 链路 orchestrator `--auto` 编造 + grill 跳过 + VERIFY screenshot 放行

- **节点：** commands/start.md
- **问题：** 诊断 #1 — start.md 指令 "Pass `--auto` for fully autonomous mode" 被模型误解为始终添加 `--auto`，导致用户未传 `--auto` 时也被强制全自动模式
- **修复：** 将指令改为明确的条件规则：检查用户原始输入是否含 `--auto` → 含则透传，不含则不添加。增加 "NEVER fabricate `--auto`" 绝对化禁止语言
- **来源：** diagnosis-result.md 2026-07-24 #1; harness-methodology.md §机制10 (When NOT to Use)
- **结果：** 待验证

---

- **节点：** skills/orchestrator/SKILL.md
- **问题：** 诊断 #4, #5 — grill 铁律 "grill-interview.md 只能由 grilling 返回写入" 在 auto 模式下被绕过，orchestrator 自行编写 "Auto-mode self-interview"。硬门未检查文件内容是否为对话格式
- **修复：**
  1. 铁律增加 "Auto 模式也不例外" 声明
  2. 硬门 GRILL_MISSING 增加 "Auto 模式下同样报告阻塞"
  3. GRILL_OK 后增加问句检测：grep `?` / `？`，零问句 → 不是采访 → STOP 重新 grill
- **来源：** diagnosis-result.md 2026-07-24 #4, #5; harness-methodology.md §机制1 (Iron Law) + §机制5 (Hard Gate)
- **结果：** 待验证

---

- **节点：** skills/orchestrator/SKILL.md
- **问题：** 诊断 #2, #3 — orchestrator 缺少阻止 "auto 模式下可以自己 grill" 和 "新角色不需要 design-ui" 两个核心借口的 Red Flags
- **修复：** Red Flags 新增 2 条：
  1. "'--auto 模式下我可以自己完成 grill 采访（self-directed grilling），不需要真向用户提问' → STOP"
  2. "'新角色不需要 UI 设计，只是换个 sprite 外观' → STOP"
- **来源：** diagnosis-result.md 2026-07-24 #2, #3; harness-methodology.md §机制3 (Rationalization Table)
- **结果：** 待验证

---

- **节点：** skills/orchestrator/SKILL.md
- **问题：** 诊断 #1 (连锁修复) — Step 0e 缺少 `--auto` 来源验证。如果 start command 错误添加了 `--auto`，orchestrator 无法检测
- **修复：** Step 0e 新增 "硬门 — `--auto` 来源验证"：从 user-prompt.md grep `--auto`，不含但 mode=auto → 报错回退为 normal 模式
- **来源：** diagnosis-result.md 2026-07-24 #1; harness-methodology.md §机制5 (Hard Gate)
- **结果：** 待验证

---

- **节点：** skills/exec/SKILL.md
- **问题：** 诊断 #13, #16 — VERIFY 步骤 7/8 screenshot 失败但仍判定通过，Completion Gate §4 "所有 screenshot 通过 visual-qa" 是人工检查清单而非自动化硬门
- **修复：** §6d VERIFY 检查结果：
  1. screenshot 行改为 "零失败容忍" 
  2. 新增截图文件 PNG 有效性检查（`file {path}` 含 "PNG image data"）
  3. 失败条件从 "有失败" 扩展为 "GUT 失败 或 screenshot FAIL 或截图文件无效"
- **来源：** diagnosis-result.md 2026-07-24 #13, #16; harness-methodology.md §机制5 (Hard Gate)
- **结果：** 待验证

---

- **节点：** skills/exec/SKILL.md
- **问题：** 诊断 #12 — GREEN 阶段截图文件无效（base64 解码错误，非 PNG）未被检测
- **修复：** §6c GREEN 检查新增：截图文件必须为有效 PNG（`file {path}` 含 "PNG image data"），非图片文件 → screenshot 脚本执行失败，GREEN 不通过
- **来源：** diagnosis-result.md 2026-07-24 #12, #14; harness-methodology.md §机制5 (Hard Gate)
- **结果：** 待验证

---

### 第 8 轮（2026-07-23）— feat 链路 screenshot 执行方法分离

- **节点：** agents/coding.md
- **问题：** 诊断 #2, #3 — coding.md 步骤3 把 GUT 和 screenshot 两种完全不同的测试体系强行套用同一套"全量执行/单case执行"命名框架。screenshot 没有批量 CLI 命令（GUT 有 `test_cmd_suite`），agent 在 init.log 中尝试为 screenshot 解析"全量执行"等价物时失败，标为 `godot CLI (unavailable)`。同时初始化摘要模板中 GUT 和 screenshot 的执行方法共用字段名，导致 agent 无法正确表达。
- **修复：**
  1. 步骤3 screenshot 方法定义: "全量执行/单case执行" → "截图执行"（去掉不存在的批量概念，Phase 1 vs Phase 2 仅 scope 不同，方法相同）
  2. 初始化摘要模板: `全量执行`/`单case执行` → `全量执行 (GUT)`/`单case执行 (GUT)`/`截图执行`，各自独立字段
  3. 结果提取也分开: `结果提取 (GUT)` + `结果提取 (截图)`
- **来源：** diagnosis-result.md 2026-07-23; coding.md L79-82 原方法定义分析; init.log "godot CLI (unavailable)" 证据
- **结果：** 待验证

---

### 第 4 轮（2026-07-19）— fix 链路修复

- **节点：** skills/fix-conductor/SKILL.md
- **问题：** 诊断 #5-8, #9-11, #12-13, #15, #19, E1-E4 + 数据流断裂 — 行为澄清跳过、视觉检测跳过、spawn prompt 含预判根因、conductor 自行调试源代码、requirements.md 未写入导致 test-agent 无法获取行为清单
- **修复：**
  1. 增加 Iron Law + Spirit-vs-Letter（CONDUCTOR DOES NOT DEBUG）
  2. 阶段 1 末尾增加硬门检查点 5 项 checklist
  3. 阶段 1b 视觉检测改为强制执行 grep
  4. **阶段 1c 新增：用户确认行为后写入 requirements.md 到 .work/，含 BUG 描述 + 预期行为（含验证方式）**
  5. 硬门检查表增加第 5 项：requirements.md 已写入且非空
  6. 阶段 2 spawn prompt 增加必需字段，删除根因分析
  7. 阶段 3 spawn prompt 增加禁止事项
  8. Red Flags + 自我合理化表格
- **来源：** diagnosis-result.md 2026-07-18; harness-methodology.md; test-agent.md Step 0-1 数据流分析
- **结果：** 待验证

---

- **节点：** agents/fix-agent.md
- **问题：** 诊断 #21-22, #24-27 — fix-agent 跳过 fix-loop、跳过规范文件读取
- **修复：** Iron Law (NO FIX WITHOUT FIX-LOOP)、spec_files_read 强制表格、Hard Gate、Red Flags
- **来源：** diagnosis-result.md 2026-07-18; harness-methodology.md
- **结果：** 待验证

---

- **节点：** agents/test-agent.md
- **问题：** 诊断 #16 — Step 0 缺少 requirements.md 不存在的 Hard Gate
- **修复：** Step 0 增加 Hard Gate + 缺失报告模板
- **来源：** diagnosis-result.md 2026-07-18; harness-methodology.md
- **结果：** 待验证

---

### 第 5 轮（2026-07-20）— fix 链路细化修复

- **节点：** skills/fix-conductor/SKILL.md
- **问题：** 诊断 #11, #15 — fix-conductor spawn prompt 缺少 testsuite/testcase 字段，导致 fix-agent 无法精确获取测试目标
- **修复：** 在阶段 2→3 之间增加 spawn prompt 完整性验证硬门（6 字段 checklist），特别是 testsuite 名和 testcase 列表必须非空
- **来源：** diagnosis-result.md 2026-07-20; harness-methodology.md 护栏机制 #9 "Spawn Prompt Validation"
- **结果：** 已确认 ✅

- **节点：** skills/fix-conductor/SKILL.md
- **问题：** 诊断 #6 — 视觉关键词 grep 是否执行无法验证
- **修复：** grep 结果追加写入 requirements.md 底部（`VISUAL_CHECK_RESULT:`），提供可验证的执行证据
- **来源：** diagnosis-result.md 2026-07-20; harness-methodology.md 护栏机制 #5 "Hard Gate Evidence"
- **结果：** 已确认 ✅

---
  
- **节点：** skills/debug-root-cause/SKILL.md
- **问题：** 诊断 #18, #33 — 跳过步骤 1（跑测试确认 BUG），直接读源代码分析
- **修复：** 步骤 1 末尾增加硬门检查表（3 项）：GUT 测试已执行并捕获输出、screenshot 已执行或标注环境限制、证据链 §1 已写入测试输出
- **来源：** diagnosis-result.md 2026-07-20; harness-methodology.md 护栏机制 #1
- **结果：** 已确认 ✅

- **节点：** skills/debug-root-cause/SKILL.md
- **问题：** 诊断 #20 — 跳过步骤 4（最小验证），直接用代码分析写入 debug-analysis.md
- **修复：** 步骤 4 末尾增加硬门检查表（3 项）：临时修改已记录、验证测试已执行、修改已撤销且工作区干净
- **来源：** diagnosis-result.md 2026-07-20; harness-methodology.md 护栏机制 #1
- **结果：** 已确认 ✅

---
  
- **节点：** agents/test-agent.md
- **问题：** 诊断 #31, #32 — test-agent Step 0 无条件要求读 design.md，但 fix 工作流不产出 design.md
- **修复：** 修改 Step 0 文件列表：design.md 改为条件读取（不存在则跳过），并说明 fix 工作流不需要 design.md
- **来源：** diagnosis-result.md 2026-07-20; fix-conductor 工作流分析
- **结果：** 已确认 ✅

---
  
- **节点：** agents/fix-agent.md
- **问题：** 诊断 #14 — 初始化摘要中 `screenshot 命令` 字段标注来源为 config.md，但 config.md 无此单一配置项
- **修复：** 字段名改为 `screenshot 方法`，来源标注改为 `screenshot.md`，添加注释说明差异
- **来源：** diagnosis-result.md 2026-07-20; screenshot.md CLI 模板
- **结果：** 已确认 ✅

---

### 第 6 轮（2026-07-21）— fix 链路 screenshot 验证 + 完成步骤 + VERIFY 硬门

- **节点：** skills/debug-root-cause/SKILL.md
- **问题：** 诊断 #52, #53 — Step 4 最小验证在第 5 轮已添加硬门检查表，但 agent 仍能在 session 中跳过（写"跳过(根因已通过代码阅读确认,逻辑直接且无歧义)"）。硬门表缺少"跳过声明检测"和绝对化禁止语言。
- **修复：**
  1. 步骤 4 开头增加绝对化语言：**"此步骤不可跳过。跳过 = 违反 Iron Law。代码阅读不是验证——只有实验结果是验证。"**
  2. 硬门检查表新增第 0 项：检查 agent 是否在 debug-analysis.md 中写了"跳过"或"无需"——若是则本轮诊断无效
- **来源：** diagnosis-result.md 2026-07-21; fix-conductor SKILL.md L146 绝对化语言模板 ("此 grep 命令必须执行。跳过 = 违反铁律")
- **结果：** 待验证

---

- **节点：** skills/fix-loop/SKILL.md
- **问题：** 诊断 #63, #64, #65, #66 — Screenshot 验证失败处理无强制机制。visual-qa 返回 API 错误后 agent 未执行"截图失败必做行为"，qa 日志未保存，agent 将 INCOMPLETE 视为 PASS 退出循环。
- **修复：**
  1. Screenshot 验证增加硬门检查表（3 项）：qa.log 存在、含 ### Answer、Answer 判定通过
  2. "截图失败必做行为"从段落升级为硬门检查表（4 项）：重读 screenshot.md → 逐条对照命令 → 检查环境 → 标注不支持
  3. Step 7 判定前增加前置条件检查表（2 项）：GUT 日志已保存、如有 screenshot 则 qa.log 完整
  4. "任一 FAIL 或 INCOMPLETE → 继续下一轮"（原为"任一 FAIL → 继续"）
- **来源：** diagnosis-result.md 2026-07-21; fix-conductor SKILL.md L114-L129 (硬门检查表格式模板)
- **结果：** 待验证

---

- **节点：** skills/fix-loop/SKILL.md
- **问题：** 诊断 #67, #68 — fix-loop 完成步骤（fix-summary.md + Fix Complete 报告）无强制性，agent 可自行跳过
- **修复：** "完成"节开头增加硬门检查表（3 项）：fix-summary.md 已写入、Fix Complete 报告已输出、fix-attempts 最后一轮验证 PASS。任何 ❌ → 返回补全
- **来源：** diagnosis-result.md 2026-07-21; fix-conductor SKILL.md L114-L129
- **结果：** 待验证

---

- **节点：** skills/fix-conductor/SKILL.md
- **问题：** 诊断 #26 — fix-conductor 阶段 4 VERIFY 完全未执行。session 中仅有 2 个 subagent（test-agent RED + fix-agent），无 GREEN mode VERIFY。全量回归测试未执行。
- **修复：** 阶段 3→4 之间增加硬门检查表（5 项）：fix-summary.md 存在、fix-attempts 最后验证 PASS、screenshot visual-qa 结果记录、logs/ 中有验证日志、轮次 ≤ 5。任何 ❌ → STOP 不得进入阶段 4。
- **来源：** diagnosis-result.md 2026-07-21; fix-conductor SKILL.md L114-L129 (阶段1→2硬门检查表模式)
- **结果：** 待验证

---

- **节点：** agents/fix-agent.md
- **问题：** 诊断 #41 — 初始化摘要 spec_files_read 不完整。agent 在摘要中将文件读取标记为后续操作，导致摘要中只显示 config.md: ✅，其余文件未在摘要中汇总。
- **修复：** 启动步骤 3 改为"按顺序逐个尝试读取规范文件（先读后记，不可批量）"，每读一个立即记录结果。强调"不得全部读完后凭记忆写摘要"。初始化摘要输出从步骤 4 移至步骤 5（确保步骤 1-4 全部完成后再输出）。
- **来源：** diagnosis-result.md 2026-07-21; fix-agent.md L47-L85 当前初始化流程
- **结果：** 待验证

---

### 第 7 轮（2026-07-21）— fix 链路 screenshot 伪截图防护

- **节点：** agents/test-agent.md
- **问题：** 诊断 #4, #5, #6 — test-agent 第一个 spawn 写了 4 个程序化伪截图脚本（Image.create/fill/set_pixel 绘图），未加载真实场景，未抓 viewport。缺失 Iron Law + Red Flags 阻止 agent 用绘图替代截图
- **修复：**
  1. Screenshot 测试编写方法前增加 Screenshot Iron Law：`SCREENSHOT MEANS VIEWPORT CAPTURE. NOT PROGRAMMATIC DRAWING.` 禁止 Image.create/fill/set_pixel 和 Fake 对象
  2. 增加 Screenshot Red Flags 表格（4 条中英双语）："不加载主场景"、"Image.create 在脚本中"、"Fake/Mock 对象"、"无法到达场景但仍在写脚本"
  3. tools 字段增加 `Skill`（body 要求调用 visual-qa skill 但 tools 缺少 Skill 工具权限）
- **来源：** diagnosis 2026-07-21-fix-screenshots; harness-methodology.md §机制1 (Iron Law), §机制4 (Red Flags); agent-structure.md §6.1 (最小权限)
- **结果：** 待验证

---

- **节点：** skills/fix-conductor/SKILL.md
- **问题：** 诊断 #3, #7, #8, #9 — 阶段 2 硬门仅检查 screenshot 文件存在性，未检查内容质量；spawn prompt 构建后无内容一致性自检，导致 requirements.md 的"从 PNG 加载的图像"被改写为"真实武器模型的视觉"
- **修复：**
  1. 阶段 2 硬门增加 screenshot 脚本内容质量验证（3 条 grep 检查：必须有 change_scene_to_file/get_viewport().get_texture()；禁止 Image.create/fill/set_pixel）
  2. spawn prompt 构建后增加"内容一致性自检"步骤——逐条对比 prompt 与 requirements.md 的核心动作/对象短语
- **来源：** diagnosis 2026-07-21-fix-screenshots; harness-methodology.md §机制5 (Hard Gate), §机制8 (Self-Review Checkpoint)
- **结果：** 待验证

---

- **节点：** skills/fix-loop/SKILL.md
- **问题：** 诊断 #10 — screenshot 输出路径不一致：fix-loop 用 `.work/logs/screenshots/`，debug-root-cause/test-agent 用 `.work/screenshots/`
- **修复：** 准备阶段 mkdir 和 Step 6 output_path 统一为 `.work/screenshots/`
- **来源：** diagnosis 2026-07-21-fix-screenshots; harness-methodology.md §机制6 (Phase Transitions 出口验证)
- **结果：** 待验证

---

- **节点：** agents/fix-agent.md
- **问题：** 诊断 #24a — 声明的 `> {log_path}` 未执行，12 次 GUT 全部用管道丢弃输出
- **修复：** 测试执行方法声明后增加 Hard Gate（机制 5）：每次测试执行后确认 `{log_path}` 已替换为实际路径且输出已保存（非管道丢弃）。日志文件不存在 = 验证无效
- **来源：** harness-methodology.md 机制 5 (Hard Gate) §4.1 "症状: 模型跳过了流程步骤 → Hard Gate"
- **结果：** 已确认 ✅

- **节点：** agents/fix-agent.md
- **问题：** 诊断 #26 — screenshot.md 启动时批量预载，到执行时约束已不在工作记忆，导致用了 `--headless` 黑屏
- **修复：** screenshot.md 从启动批量列表移除，改为执行截图前 Hard Gate 即时 Read，读完立即对照约束写命令。同步处理 3d-construction.md（同样改为用到时再读）。移除初始化摘要中的 screenshot 行
- **来源：** harness-methodology.md §3.3 (Reference 的渐进式披露) + 机制 5 (Hard Gate)
- **结果：** 已确认 ✅

- **节点：** skills/fix-conductor/SKILL.md
- **问题：** 诊断 #23a — 武器缩略图为纯色方块。fix 工作流缺少资产生成阶段
- **修复：** 待定（用户重新考量如何加入，非 harness 问题）
- **来源：** —
- **结果：** ⏭️ 暂缓
