# Repair Log

## 第 1 轮（2026-08-11）

诊断记录：`records/2026-08-11-refactor-diagnosis-result.md`（第二轮，聚焦集成测试质量）

### 修复 1 — G1/G3：端到端数据流验证纳入测试范围
- **节点：** `skills/backend-integration-test/SKILL.md`（测试范围节）
- **问题：** 测试范围表只有 4 类单接口场景，design.md 声明的"集成验证：跑通全链路"无执行归属；页面数据源查询接口从未验证返回测试数据
- **修复：** 测试范围表新增"端到端数据流"场景行 + "端到端数据流硬门"（链路必须完整走通，最后一环 = 页面数据源查询接口返回该批次数据；环境无法产生真实新数据时允许等价种子数据但消费→落库→查询可见必须走通；成功路径未执行标 BLOCKED）
- **来源：** harness-methodology.md 机制5 Hard Gate（L282-330）+ 机制6 Phase Transitions（L333-372）；diagnosis-guide.md §2.4
- **结果：** 已确认（编辑落地）

### 修复 2 — G1：exec spawn prompt 传递全链路要求
- **节点：** `skills/exec/SKILL.md`（阶段3/5 spawn prompt）
- **问题：** 阶段3/5 prompt 只要求"对 design.md 中每个模块的 API 接口运行集成测试"，未把 design.md 的集成验证/全链路要求传给 coding agent
- **修复：** 两处 prompt 均增加"对 design.md 中声明的集成验证/全链路要求执行端到端验证——不限于单接口，最后一环是页面数据源查询接口返回该批次数据"
- **来源：** harness-methodology.md 机制5（传递边界验证 "spawn prompt 是否包含所有信息"）；diagnosis-guide.md §2.4
- **结果：** 已确认（编辑落地）

### 修复 3 — G2：结论硬门（成功路径不可验证 → BLOCKED）
- **节点：** `skills/backend-integration-test/SKILL.md`（输出格式节）
- **问题：** 无"结论与验证范围一致"机制——精炼成功路径从未执行（LLM 占位 key），报告却宣布"全链路通过 30/30 PASS"；脚本把"精炼失败，跳过"和 refined=0 断言为 expected PASS
- **修复：** 新增"结论硬门（强制）"：核心业务成功路径未执行/不可验证 → 结论必须标 BLOCKED/部分验证；降级路径断言不能替代成功路径验证；报告完成前 3 项自检（Checklist with Consequences）
- **来源：** harness-methodology.md 机制8 Self-Review Checkpoint（L428-473）+ 机制13 Checklist with Consequences（L675-717）；diagnosis-guide.md §2.2
- **结果：** 已确认（编辑落地）

### 修复 4 — #9-12：失败记录机制硬门
- **节点：** `skills/backend-integration-test/SKILL.md`（自修复循环 Phase 2→3）
- **问题：** 声明了"读取 fix-attempts.md / 产出 debug-analysis-{case}.md / 每轮失败追加"，但 3 次真实修复（P1/P2/P3）零记录——无出口硬门
- **修复：** 新增"Phase 2 → Phase 3 硬门（强制）"：每轮失败修复后必须追加 fix-attempts.md（按用例分节）；调用过 debug-root-cause 的用例必须产出 debug-analysis-{case}.md；任一缺失 STOP 回 Phase 2
- **来源：** harness-methodology.md 机制5 Hard Gate（L282-330）+ 机制6 Phase Transitions 出口验证（L333-372）；agent-structure.md §5.2
- **结果：** 已确认（编辑落地）

### 修复 5 — G2 配套：Red Flags 新增降级路径借口
- **节点：** `skills/backend-integration-test/SKILL.md`（Red Flags 节）
- **问题：** 无"LLM key 占位 → 成功路径测不了算 PASS"和"查询接口 200 = 数据可见"两条逃脱借口
- **修复：** Red Flags 增加 2 条："LLM key 是占位符…算预期行为 PASS → STOP"、"查询接口 200 就说明数据可见了 → STOP"
- **来源：** harness-methodology.md 机制4 Red Flags（L199-273）
- **结果：** 已确认（编辑落地）

### 修复 6 — G1 配套：backend-testing.md 覆盖清单
- **节点：** `references/web/backend-testing.md`（测试场景覆盖清单）
- **问题：** 模板清单只有单接口场景，无端到端数据流项
- **修复：** 覆盖清单新增"端到端数据流"项（跨服务链路：真实触发/等价数据 → 中间件 → 落库 → 查询接口返回该数据；成功路径未走通 → BLOCKED）
- **来源：** 与修复 1 同源（G1 的模板配套）
- **结果：** 已确认（编辑落地）

### 未修复项
- 无。本轮全部 6 项修复已落地；⚠️ #14（输出格式偏离）已并入修复 3 的结论硬门，无需单独修复。
