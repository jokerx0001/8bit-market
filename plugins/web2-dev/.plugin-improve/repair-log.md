# Repair Log

## 第 2 轮（2026-08-19）

诊断记录：`records/2026-08-19-new-diagnosis-result.md`（new 链路，产物目录 /mnt/d/project/neonbit/goal-backend/.web2-dev/new-1，无 log 仅产物证据）

### 修复 1 — G1：Phase 2→3 硬门机械化（debug-analysis 文件强制）
- **节点：** `skills/backend-integration-test/SKILL.md`（Phase 2c + Phase 2→3 硬门）
- **问题：** 08-11 修复 4 加入的硬门是纯文字 checklist，无 bash 机械检查；措辞"调用过 debug-root-cause 的用例"是条件式，agent 自行内联诊断时条件为空、门空转。本次运行 5 个失败 case 零 debug-analysis-*.md 文件，循环未 STOP 照常进入 Phase 3
- **修复：** ① Phase 2c 改为无条件："每个失败用例必须调用 debug-root-cause——自行内联诊断不算；不产出文件 = 本轮修复无效"；② Phase 2→3 硬门新增机械检查命令模板（C=fix-attempts case 计数、A=debug-analysis 文件计数，A<C → ANALYSIS_MISSING → STOP 回 Phase 2）
- **来源：** harness-methodology.md 机制5 Hard Gate（L282-330）+ 机制6 Phase Transitions 出口验证（L333-372）；diagnosis-guide.md §2.1；对照同插件 new-orchestrator L128-131 的 test -s 先例
- **结果：** 已确认（编辑落地）

### 修复 2 — G2：mattpocock-skills 引用改裸名（引用解析）
- **节点：** `skills/new-orchestrator/SKILL.md`（L116 grilling）、`skills/exec/SKILL.md`（L154 + 总览 L46 tdd）、`agents/coding.md`（L42 + description）、`skills/fix-orchestrator/SKILL.md`（L40/117/147 tdd）、`README.md`（依赖插件节）、`CLAUDE.md`（L41/72/135）
- **问题：** 插件引用 `mattpocock-skills:grilling`/`mattpocock-skills:tdd`，但环境无该插件（installed_plugins.json 无），实际安装为 `~/.claude/skills/` 裸名 `grilling`/`tdd`——Skill 调用必然失败，agent 临场绕过（grill 记录被整理/补写违反铁律；TDD 走非声明路径）
- **修复：** 全部引用改为裸名 `grilling`/`tdd`；new-orchestrator Step 2b 增加"Skill 调用失败 → 报告阻塞，禁止临场自办采访"；README 依赖节注明两种安装方式及对应引用名
- **来源：** diagnosis-guide.md §2.4 数据传递不一致（L120-145）；skill-structure.md §7.3 引用但目标不存在（L278-285）；harness-methodology.md §3.3 Reference 准确性
- **结果：** 已确认（编辑落地）

### 修复 3 — G3：部署阶段完成验证门（阶段4 停滞无声）
- **节点：** `skills/exec/SKILL.md`（阶段 1b 新增 + 阶段 4b 新增 + 错误处理表 + 阶段完成记录）、`skills/service-ops/SKILL.md`（部署流程 6 机械自检）
- **问题：** 阶段 3-10 无完成验证步骤（L214"省略重复"抹掉进度记录），主会话信任 ops agent 报告无产物级验证；错误处理表无"部署停滞/构建状态不可确认"场景。本次运行部署 commit 已 push 但部署后 API 全部 404（非当前构建）、ops-local.md 无环境地址清单、progress.json 停在 deploy_backend 无完成记录、无失败报告
- **修复：** ① exec 新增阶段 1b（基础设施完成验证硬门）与阶段 4b（部署完成验证硬门：ops-local.md 含环境地址清单 + 健康检查 curl 200，任一失败重 spawn ops 最多 3 轮）；② 阶段 3-10 每阶段结束强制更新 progress.json（stages_completed 追加）；③ service-ops 部署流程 6 增加 ADDRLIST 机械自检（grep 外网入口/API baseURL/健康检查 ≥3），MISSING 禁止声明部署成功；④ 错误处理表增加"部署停滞/构建状态不可确认 → AskUserQuestion 报告用户"
- **来源：** harness-methodology.md 机制5（L282-330）+ 机制6（L333-372）+ 机制8（L428-473）；diagnosis-guide.md §2.2；agent-structure.md §5.2
- **结果：** 已确认（编辑落地）

### 修复 4 — #4：stack-detector auto 模式确认门分支
- **节点：** `skills/stack-detector/SKILL.md`（强制确认门）
- **问题：** "强制确认门：未收到用户 OK 确认前不落盘"（L41-53）与 new-orchestrator"不确定时向用户确认"（L89）及 auto 模式跳过人工审查点冲突——规则歧义，agent 行为不确定
- **修复：** 增加 auto 模式分支：特征单条唯一命中 → 允许落盘但 stack.json 标注 `"confirmed": "auto-unambiguous"`；特征冲突/不明确 → 即使 auto 也必须确认
- **来源：** harness-methodology.md 机制16 Flowchart for Decision Points（L796-818）
- **结果：** 已确认（编辑落地）

### 修复 5 — #30：artifact-manager 目录结构对齐实际产出
- **节点：** `skills/artifact-manager/SKILL.md`（目录结构）、`CLAUDE.md`（输出目录）
- **问题：** 声明 .work/ 含 coding/ 与 tdd-iterations.md，但链路无任何节点写入（08-09 诊断 #27 已指出未修复，本次再现）
- **修复：** 目录结构移除 coding/ 与 tdd-iterations.md，替换为实际产出的 fix-attempts.md 与 debug-analysis-*.md
- **来源：** harness-methodology.md 机制6 阶段声明 vs 实际能力一致性；diagnosis-guide.md §2.2；08-09 诊断记录 #27
- **结果：** 已确认（编辑落地）

### 修复 6 — #3/#8：模式判定产物化 + Red Flags 盲区条目
- **节点：** `skills/new-orchestrator/SKILL.md`（Step 0b 模式回显 + Red Flags）
- **问题：** 模式回显为纯交互步骤无产物化设计，无 log 时不可审计；grill 硬门（test -s + 问号）无法验证回答来自用户，auto 模式 self-directed grilling 可通过
- **修复：** ① Step 0b 回显后写入 `{task_dir}/.work/mode.md`（mode + source grep 证据）；② Red Flags 新增"auto 模式编造用户回答"条目（中英双语，含英文自述以匹配模型内部推理）
- **来源：** harness-methodology.md 机制4 Red Flags 双语规则（L261-272）+ 机制5 Hard Gate（L282-330）
- **结果：** 已确认（编辑落地）

### 未修复项
- 无。本轮 6 项修复全部落地。⚠️ 行（#3/#4/#8/#30）已并入修复 4/5/6。

---

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
