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
