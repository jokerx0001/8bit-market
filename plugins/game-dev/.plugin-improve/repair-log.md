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

### 第 5b 轮（2026-07-20）— 遗漏问题补充修复（harness 正确方案）

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
