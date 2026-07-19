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
