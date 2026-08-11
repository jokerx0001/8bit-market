# web2-dev - refactor 链路诊断结果（第二轮：集成测试质量）

## 日期：2026-08-11

> 第一轮诊断（2026-08-09）聚焦耗时/挂起/模式判定。本轮由用户报告新问题：
> **"集成测试不过关，根本没有走通爬取数据，到最后 chance-view 落库页面能显示的数据。这个集成测试质量肯定是不行的"**
> 本轮聚焦：exec 阶段3/5 集成测试链路（backend-integration-test + coding agent + 测试产物）。
>
> **对第一轮的修正**：第一轮 #2/#3/#12 判定"--auto 硬门未执行、模式误判"。实际证据：`refactor-1/.work/user-prompt.md` L7 含 `--auto`（用户原语原样保存），模式判定为 auto 有据可依，第一轮该项结论不成立。

### 链路拓扑

```
commands/refactor.md
→ skills/refactor-orchestrator/SKILL.md
  → skills/exec/SKILL.md（阶段8 → 阶段3/5 集成测试）
    → agents/coding.md（阶段3/5 spawn 模式=integration-test）
    → skills/backend-integration-test/SKILL.md（阶段3/5 调用）
      → references/web/backend-testing.md（测试场景模板）
      → skills/debug-root-cause/SKILL.md（Phase 2c 调用）
    → skills/frontend-e2e-test/SKILL.md（阶段7/10 — plan.md 声明"无前端变更"，按约束跳过）
    → skills/code-review/SKILL.md（Step 2b）
  → skills/design/SKILL.md（阶段5 — 产出 design.md，含"集成验证全链路"要求 L251）
  → skills/plan/SKILL.md（阶段6 — 产出 plan.md，前端节声明"无前端变更"）
  → skills/artifact-manager/SKILL.md（阶段1 — 目录结构声明）
```

被分析执行：`/data/project/buffett/.web2-dev/refactor-1`（2026-08-08 → 08-09，与第一轮同一执行）

证据来源：
- 执行日志：/tmp/log_summary.txt（主会话，L#）、/tmp/agentB.txt、/tmp/agentDeploy.txt
- 产物：`.work/integration/backend-integration.sh`、`deployed-backend-integration.sh`、`backend-integration.md`、`deployed-backend-integration.md`、`logs/chance-view.log`、`logs/*.json`
- design.md L251、impact.md、plan.md、progress.json

### 逐步骤诊断

| # | 所属节点 | 应有步骤 | 要求(来自plugin文件) | 实际步骤(来自产物/log) | 达标? | 达标证据 / 不达标点 |
|---|---------|---------|---------------------|------------------|-------|-------------------|
| 1 | skills/exec/SKILL.md | 阶段3 spawn 本地集成测试 agent | "按 CLAUDE.md 中的方式在本地启动后端服务。对 design.md 中每个模块的 API 接口运行集成测试（成功 + 失败场景）。调用 Skill(web2-dev:backend-integration-test) 完成测试 + 自修复循环"（L232-236） | log_summary L672 spawn Agent("Backend integration test (local)", prompt "## 模式\nintegration-test\n## project\nbuffett...")；L678 返回 "Integration test complete — 21/21" | ✅ | L672 spawn 结构与 exec 模板一致；L678 返回报告与产物 backend-integration.md 对应 |
| 2 | skills/exec/SKILL.md | 阶段5 spawn 部署后集成测试 agent | "对部署后的后端服务运行 API 测试（地址从 CLAUDE.md 获取）。调用 Skill(web2-dev:backend-integration-test) 完成测试 + 自修复"（L277-279） | log_summary L695 spawn；L697 返回 "30/30 PASS（部署环境 dev 192.168…）" | ✅ | L695/697 执行；产物 deployed-backend-integration.md 与返回对应 |
| 3 | skills/backend-integration-test/SKILL.md | 测试范围：正常请求 | "每个接口至少 1 个成功场景"（L33） | 脚本覆盖：scrape/trigger success、consume 链路、API 契约 200（backend-integration.md §1/§2；deployed §2/§3） | ✅ | deployed-backend-integration.md §2 触发任务 43 success；§3 各接口 200 |
| 4 | skills/backend-integration-test/SKILL.md | 测试范围：参数验证 | "必填字段缺失、格式错误"（L34） | analyze 空数组 400、Unknown source 400（deployed-backend-integration.md §3） | ✅ | logs/deployed_analyze_empty.json `{"detail":"Analyze list must not be empty"}`；deployed_scrape_fb.json `{"error":"Unknown source: facebook..."}` |
| 5 | skills/backend-integration-test/SKILL.md | 测试范围：业务规则 | "重复注册、库存不足等"（L35） | 幂等重发、409 Already refined、404 不存在 id（backend-integration.md §3/§4） | ✅ | backend-integration.md §3 "幂等：analysis_results 行数不变（9 行，无重复）"；logs/refine_409.json `{"error":"Already refined"}` |
| 6 | skills/backend-integration-test/SKILL.md | 测试范围：鉴权 | "未登录、权限不足（如适用）"（L36） | 系统无鉴权模块，"如适用"→ N/A | ✅ | N/A 判定合理（buffett 系统无登录体系，design.md 无鉴权设计） |
| 7 | skills/backend-integration-test/SKILL.md | 测试方式 | "脚本放在 {task_dir}/.work/integration/ 下。参考 ${CLAUDE_PLUGIN_ROOT}/references/web/backend-testing.md"（L40-41） | 7 个脚本/报告在 .work/integration/（backend-integration.sh、deployed-backend-integration.sh、seed_test_batch.py、publish_mq.py、db_verify.py、cleanup_test_batch.py、2 份报告） | ✅ | find 产物清单确认文件存在且路径正确 |
| 8 | skills/backend-integration-test/SKILL.md | Phase 1 启动服务→全量→收集 | "启动服务 → 运行全量测试 → 收集结果"（L48） | 本地两服务启动（backend-integration.md §环境与启动方式 L9-27）；脚本 §0 服务存活检查 | ✅ | backend-integration.md L13-14 列明 FastAPI/chance-view 启动命令；脚本 L28-29 curl 存活断言 |
| 9 | skills/backend-integration-test/SKILL.md | Phase 2a 读取 fix-attempts.md | "读取 {task_dir}/.work/fix-attempts.md 失败经验（告诉自己：不重复错误路径，必须换思路）"（L53） | .work/ 下无 fix-attempts.md，无读取证据 | ❌ | find 产物：fix-attempts.md 自始至终不存在。首次运行无文件可读尚可容忍，但本次实际发生 3 次失败修复（P1/P2/P3）后仍未创建（见 #12），声明机制整体未落地 |
| 10 | skills/backend-integration-test/SKILL.md | Phase 2c debug-root-cause → debug-analysis-{case}.md | "调用 Skill(web2-dev:debug-root-cause) 深度根因分析 → 产出 {task_dir}/.work/debug-analysis-{case}.md"（L55-56） | .work/ 下无任何 debug-analysis-*.md；P1 h2c bug 修复自述"抓包确认"（backend-integration.md L73），未产出声明格式的调试分析文档 | ❌ | find 产物：debug-analysis-* 零文件。P1 诊断实质存在（抓包+隔离复现）但未走 skill 声明的 debug-root-cause 产出机制 |
| 11 | skills/backend-integration-test/SKILL.md | Phase 2e 重跑 + 追加 fix-attempts.md | "重跑该用例 → 通过 → 下一个 / 失败 → 追加失败详情到 fix-attempts.md → 回到 2a"（L58） | 重跑执行（P1 隔离复现程序 + 全量 21/21）；fix-attempts.md 追加从未发生 | ❌ | backend-integration.md L75 "隔离复现程序返回正常响应；修复后集成测试…94/94 通过"（重跑有）；find 产物确认无 fix-attempts.md（追加无） |
| 12 | skills/backend-integration-test/SKILL.md | 重试限制：失败经验记录 | "每轮失败追加到 {task_dir}/.work/fix-attempts.md（按用例分节 `## {case} 第 {N} 轮`），2a 先读取"（L79） | P1（h2c bug）、P2（psycopg2 % 转义）、P3（日志断言历史残留）3 次失败修复后均无记录 | ❌ | backend-integration.md §发现并修复的问题 L70-85 记录 3 个修复；find 产物确认 fix-attempts.md 不存在 |
| 13 | skills/backend-integration-test/SKILL.md | Phase 3 重跑全量→报告 | "重跑全量确认 → 报告"（L61） | 本地 21/21、部署 30/30 全量重跑 + 2 份报告 | ✅ | backend-integration.md L5 "全链路通过（21/21 PASS）"；deployed-backend-integration.md L5 "30/30 PASS"；可复跑脚本退出码 0（脚本 L169/L244） |
| 14 | skills/backend-integration-test/SKILL.md | 输出格式 | "报告含 测试统计/API 覆盖表/阻塞用例表/自修复轮次"（L85-108） | 报告采用自定义结构（结论/各环节验证结果/发现并修复的问题/可复跑脚本/遗留事项），无模板规定的 4 张表 | ⚠️ | 信息等价（覆盖/修复/遗留均有），但结构偏离声明模板；且"结论"行与验证范围不符（核心问题在 #G2） |
| 15 | references/web/backend-testing.md | 场景覆盖清单 | "每个模块的每个 API 接口必须覆盖：成功/参数缺失/参数格式/业务规则/认证缺失/权限不足"（L69-76） | 6 类场景对应：成功✓ 参数缺失✓（空数组400）格式✓（Unknown source）业务规则✓（幂等/409/404）认证 N/A 权限 N/A | ✅ | 与 #3-#6 证据相同，全部场景有对应断言 |
| 16 | agents/coding.md | 集成测试自修复 | "启动服务（按 CLAUDE.md 中的方式）→ 运行测试 → 失败 → 分析日志 → 定位根因 → 修复 → 重跑 → 全部通过 → 返回成功报告"（L48-54） | 本地 agent 启动两服务、发现 P1 真实 bug、修复验证、21/21；部署 agent 发现残留消费者抢占、重跑 30/30 | ✅ | backend-integration.md §发现并修复的问题 L70-85（P1 修复+验证）；deployed-backend-integration.md P1 L69-74（kill 残留进程→重跑 30/30） |
| 17 | skills/design/SKILL.md（产物 design.md L251） | 集成验证：全链路走通 | design.md L251：**"5. 集成验证：本地跑通 爬取→MQ→消费→入库→精炼 全链路"**（实施顺序节，design skill 声明的产物契约） | 真实爬取 itemsNew=0（空批次）；新数据路径用**种子数据模拟**；精炼成功路径全部失败（LLM disabled）；页面数据源查询接口未验证返回测试数据 | ❌ | chance-view.log L83-91 三个真实批次全部"无新数据，结束处理"；L73-79/L96-102 精炼全部"失败，跳过: …LLM analysis disabled"；design 声明的全链路**未走通**，且无下游节点强制其走通（见 #G1） |
| 18 | skills/plan/SKILL.md（产物 plan.md 前端节） | 前端阶段按 plan 跳过 | plan.md L20 "开发方式: 无前端变更（API 契约不变，查询仍走 analysis_results）前端入口: buffett-ui（不动）"；exec L427 "plan.md 是 exec 唯一的任务来源" | 阶段6-10 前端开发/E2E 未执行，progress.json stages_completed 无 frontend 阶段 | ✅ | progress.json L11-18 六阶段仅 infra_check/task_loop/integration_test_local/deploy_backend/integration_test_deployed/cleanup；符合 plan 约束（前端跳过本身不违规，"页面能显示的数据"验证属 #G3 的后端集成测试职责） |
| G1 | skills/backend-integration-test/SKILL.md + skills/exec/SKILL.md | 端到端数据流验证（应有但未声明） | **插件缺失此要求。** 测试范围表仅 4 类单接口场景（L29-36）；exec 阶段3/5 prompt 仅"对 design.md 中每个模块的 API 接口运行集成测试"（L233-234/L277-278）——design.md L251 的"跑通全链路"无任何节点承接 | 真实爬取仅验证空批次降级；新数据路径手工种子（URL 前缀 integration-test-）+ 手动发 MQ 绕过爬虫；脚本注释明示降级策略 | ❌ | backend-integration.sh L9-10 "测试数据策略：插入带独立 batch_id 的测试行…真实爬取（任务 31）已单独验证 MQ 发布+消费空批次链路"；L60-61 把"精炼失败，跳过"断言为 PASS。真实数据流（爬取产生新数据→消费→落库）从未完整走通 |
| G2 | skills/backend-integration-test/SKILL.md | 成功路径不可验证 → BLOCKED（应有但未声明） | **插件缺失此机制。** 输出格式"阻塞用例"表（L103-105）无"核心业务成功路径未执行必须列入"要求；无"降级路径不得冒充 PASS"规则；无报告结论与验证范围一致性自检 | 精炼成功路径（is_refined=true 回写）因 LLM 占位 key 从未执行，报告在遗留事项承认"无法在部署环境验证"，结论却宣布"全链路通过（30/30 PASS）" | ❌ | deployed-backend-integration.md L5 "结论：全链路通过（30/30 PASS）" vs L86 "遗留事项：openai_api_key 为占位符：/api/analyze 精炼成功路径（is_refined=true 回写）无法在部署环境验证——预期行为"——结论与验证范围直接矛盾；脚本 L75 "refined=0" 断言为 PASS |
| G3 | skills/backend-integration-test/SKILL.md | 用户可见结果验证（应有但未声明） | **插件缺失此要求。** 测试范围表无"数据落地后经查询接口（页面数据源）可见"场景 | 测试批次 9 行 analysis_results 入库后，从未调用前端查询接口（pain-points/opportunities/stats）验证返回测试批次数据；部署测试仅验 200 空数据 | ❌ | deployed-backend-integration.md §3 "GET /api/pain-points / opportunities / stats → 均 200（对外查询契约未变）"——只验了 HTTP 200，未验证返回体包含测试批次的 9 行数据。用户诉求"页面能显示的数据"即此环节，从未被验证 |

### 根因分析与解决方案

| # | 应有步骤 | 达标? | 根因 | 解决方案 | 解决方案来源 |
|---|---------|-------|------|---------|-------------|
| G1 | 端到端数据流验证（插件未声明） | ❌ | **测试范围定义缺口 + 数据传递断裂。** design.md（design skill 产出，L251）声明"集成验证：本地跑通 爬取→MQ→消费→入库→精炼 全链路"，但链条上下两个节点都没有承接它：① exec 阶段3 prompt（L233-234）把测试目标定义为"对 design.md 中每个模块的 API 接口运行集成测试"——接口粒度；② backend-integration-test 测试范围表（L29-36）只有 正常请求/参数验证/业务规则/鉴权 四类单接口场景。design 的集成验证要求**无执行归属** → agent 自发部分执行（种子模拟链路），且因无强制要求，真实爬取 itemsNew=0 时直接降级为空批次验证（backend-integration.sh L9-10 明示），不构成违规。机制层：节点间数据传递不一致（diagnosis-guide §2.4）——上游声明了要求，下游没有把它带入 spawn prompt/测试范围 | ① backend-integration-test 测试范围表新增"端到端数据流"场景行：**验证 design.md 实施顺序/测试策略节声明的跨服务链路（真实触发→中间件→落库→查询接口返回该数据），成功路径必须走通**；② exec 阶段3/5 prompt 增加一句："对 design.md 中声明的集成验证/全链路要求执行端到端验证（不限于单接口）"；③ 若环境无法产生真实新数据（如外部源去重），测试必须显式构造等价数据（可验证的种子批次是允许的），但**必须同时走通消费→落库→查询接口可见** | harness-methodology.md 机制5 Hard Gate（L282-330，传递边界验证"spawn prompt 是否包含所有信息"）+ 机制6 Phase Transitions（L333-372，入口验证）；diagnosis-guide.md §2.4 数据传递不一致（L120-145） |
| G2 | 成功路径不可验证 → BLOCKED（插件未声明） | ❌ | **无结论护栏机制。** backend-integration-test 的 Iron Law 只约束"失败先诊断"（L18-25），输出格式的"阻塞用例"表（L103-105）无"核心业务成功路径未执行必须列入"的规则；无 Self-Review Checkpoint 要求报告结论与验证范围一致。模型在 LLM 占位 key 环境下把降级路径写成"expected PASS"（backend-integration.sh L60-61/L75），报告在遗留事项承认"精炼成功路径无法在部署环境验证"（deployed-backend-integration.md L86）却宣布"全链路通过 30/30"（L5）——典型"声称完成但产物/结论不符"（diagnosis-guide §2.2）。机制层：缺 Self-Review Checkpoint（机制8）与 Checklist with Consequences（机制13）——报告结论无"自检与验证范围一致性"步骤，无后果声明 | ① backend-integration-test SKILL.md 输出格式节新增硬门：**"结论声明必须与验证范围一致。核心业务成功路径未执行/因环境不可验证 → 结论必须标注 BLOCKED/部分验证，禁止宣布全链路 PASS"**；② "阻塞用例"表新增列语义：环境限制导致的未验证路径必须逐条列出；③ 测试脚本层（agent 行为）：降级路径（如 LLM disabled）的断言必须是"验证降级行为存在"，同时**必须另立一条成功路径断言**，成功路径不可执行时该用例标 BLOCKED 而非 PASS | harness-methodology.md 机制8 Self-Review Checkpoint（L428-473，声明完成前检查"输出与事实一致"）+ 机制13 Checklist with Consequences（L675-717，带后果的清单）；diagnosis-guide.md §2.2（L57-86） |
| G3 | 用户可见结果验证（插件未声明） | ❌ | **测试范围缺"用户可见结果"类别。** 页面数据源（pain-points/opportunities/stats 查询接口）是"页面能显示的数据"的唯一通道，但测试范围表无"数据落地后经查询接口可见"场景。部署测试对 3 个查询接口只验 200 空数据（deployed-backend-integration.md §3），种子批次入库后从未回查这些接口确认数据可见。与 G1/G2 同根：范围定义未覆盖"业务闭环的最终用户可观测结果" | 并入 G1/G2 修复：① 端到端数据流场景行的最后一环 = **测试数据落库后，调用页面数据源查询接口验证返回体包含该批次数据**；② G2 的"成功路径必须走通"包含此环（查询接口返回精炼/未精炼数据的正确展示），不可执行同样标 BLOCKED | 同 G1（机制6 Phase Transitions 出口验证）+ G2（机制8/13）；diagnosis-guide.md §2.2 |
| 9/10/11/12 | fix-attempts.md / debug-analysis-{case}.md 记录机制 | ❌ | **声明了但无强制执行的出口验证。** backend-integration-test Phase 2 循环（L52-59）与重试限制表（L74-82）声明了"读取 fix-attempts.md / 调用 debug-root-cause 产出 debug-analysis-{case}.md / 每轮失败追加"三项，但：① 无"修复完成 → 必须创建/追加记录文件"的出口硬门（Phase 2e → Phase 3 无验证）；② 输出格式无"本轮失败记录"字段，报告只展示修复内容（P1/P2/P3）不展示记录文件。模型完成了实质诊断（抓包确认 h2c）但未走声明机制 → 3 个修复零记录。机制层：Phase Transitions 缺出口验证 + Hard Gate 缺"记录已写入才可进入 Phase 3" | ① Phase 2e → Phase 3 之间加硬门：**"每轮失败修复后必须追加 {task_dir}/.work/fix-attempts.md（按用例分节）；调用 debug-root-cause 的修复必须产出 debug-analysis-{case}.md；Phase 3 前检查两文件存在，缺失 → STOP 回 Phase 2"**；② 输出格式报告模板新增"失败记录文件"行（fix-attempts.md / debug-analysis-*.md 路径+节数） | harness-methodology.md 机制5 Hard Gate（L282-330）+ 机制6 Phase Transitions 出口验证（L333-372）；agent-structure.md §5.2"每个流程步骤都有验证"（L197-203） |
| 14 | 输出格式偏离模板 | ⚠️ | 报告结构自定义（结论/各环节验证/发现并修复的问题/可复跑脚本/遗留事项），无 skill 模板的"测试统计/API 覆盖/阻塞用例/自修复轮次"四表；信息等价但偏离声明。核心危害不在格式而在**结论准确性**（G2 已覆盖） | 与 G2 合并修复：模板保留"阻塞用例/未验证路径"强制节，其余结构允许自适应（信息等价即可）。修复 G2 后本行风险自然消除 | agent-structure.md §5.3 Output Format 明确结构（L187-194）；diagnosis-guide.md §2.8（L234-252） |

### 诊断结论摘要

- **核心问题（用户报告的根因）**：G1/G2/G3 —— 插件把集成测试的"测试范围"定义为单接口契约场景（正常/参数/业务规则/鉴权），design.md 声明的"集成验证：跑通全链路"无执行归属；且无"成功路径不可验证 → BLOCKED"机制，导致降级路径（LLM disabled）被断言为 PASS、"全链路通过 30/30"的结论掩盖了精炼成功路径与页面数据可见性从未被验证的事实。
- **次要问题**：#9/#10/#11/#12 —— backend-integration-test 自修复循环声明的失败记录机制（fix-attempts.md / debug-analysis-{case}.md）完全未落地，3 次真实修复（P1/P2/P3）零记录。
- **符合声明**：#1-#8、#13、#15-#18 —— spawn 模板、单接口场景覆盖、自修复重跑、按 plan 跳过前端均按声明执行。执行纪律没有问题，问题在**范围定义**与**结论护栏**。
- **修复优先级**：❌ G1/G2/G3（核心，用户直接诉求）→ ❌ #9-12（记录机制）→ ⚠️ #14（并入 G2）。

### 修复状态（第 1 轮，2026-08-11）

- G1：已修复 ✅ — backend-integration-test 测试范围表新增"端到端数据流"场景 + 硬门；exec 阶段3/5 prompt 增加全链路验证要求
- G2：已修复 ✅ — backend-integration-test 新增"结论硬门"（成功路径未验证 → BLOCKED，禁止宣布全链路 PASS）+ Red Flags 2 条
- G3：已修复 ✅ — 并入 G1（端到端链路最后一环 = 页面数据源查询接口返回该批次数据）
- #9/#10/#11/#12：已修复 ✅ — Phase 2→3 硬门（fix-attempts.md / debug-analysis-{case}.md 必须存在）
- #14：已修复 ✅ — 并入 G2 结论硬门
- 配套：backend-testing.md 覆盖清单新增端到端数据流项

详见 `.plugin-improve/repair-log.md` 第 1 轮。
