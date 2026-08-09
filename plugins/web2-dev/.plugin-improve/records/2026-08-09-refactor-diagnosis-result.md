# web2-dev - refactor 链路诊断结果
## 日期：2026-08-09

### 链路拓扑

```
commands/refactor.md
→ skills/refactor-orchestrator/SKILL.md（9 阶段状态机；阶段0/2 引用 new-orchestrator）
  → skills/artifact-manager/SKILL.md（阶段1 创建任务目录）
  → grill-with-docs skill（阶段2，外部 mattpocock-skills）
  → skills/architecture/SKILL.md（阶段5）
  → skills/design/SKILL.md（阶段5）
  → skills/plan/SKILL.md（阶段6）
  → skills/exec/SKILL.md（阶段8）
    → agents/coding.md（Step 2a spawn TDD；阶段3/5 集成测试；阶段6/7/10 前端）
    → skills/code-review/SKILL.md（Step 2b 主 agent 执行）
    → agents/ops.md（阶段1/4/9 spawn）
    → skills/backend-integration-test/SKILL.md（阶段3/5）
    → skills/frontend-e2e-test/SKILL.md（阶段7/10）
    → skills/infra-ops/SKILL.md、service-ops/SKILL.md
```

被分析执行：`/data/project/buffett/.web2-dev/refactor-1`（2026-08-08 16:25:59Z → 2026-08-09 04:22:02Z，总耗时约 12.7 小时）

日志来源：主会话 b0450581（摘要 /tmp/log_summary.txt，行号 L#）、任务B agent（/tmp/agentB.txt，行号 B#）、部署 ops agent（/tmp/agentDeploy.txt，行号 D#）

### 逐步骤诊断

| # | 所属节点 | 应有步骤 | 要求(来自plugin文件) | 实际步骤(来自log) | 达标? | 达标证据 / 不达标点 |
|---|---------|---------|---------------------|------------------|-------|-------------------|
| 1 | skills/refactor-orchestrator/SKILL.md | 阶段0 前置检查 | "检查项目根目录 ops-local.md 存在且非空，不满足则终止"（L46） | L20-22 ls+cat ops-local.md | ✅ | L32 回显 "ops-local.md 存在且非空 ✓" |
| 2 | skills/refactor-orchestrator/SKILL.md | 阶段0 硬门 --auto 来源验证 | "从 user-prompt.md 中 grep --auto。来源不明 → 回退 normal"（L48） | 无 grep 证据；L333 "plan.md 自检通过。`--auto` 模式跳过审查，直接进入 Exec 阶段" | ❌ | 用户命令行 L6 为 "/web2-dev:refactor 1.python服务要包含在一个fastapi里…"——无 --auto。硬门未执行，模式被错误判定为 auto |
| 3 | skills/refactor-orchestrator/SKILL.md | 阶段0 回显确认 | "回显确认：技术栈 / dev_dir / 运行模式 {normal/auto}"（L50-61） | L32 技术栈与 dev_dir 有回显；运行模式无回显 | ⚠️ | 运行模式回显缺失；且模式本身判定错误（见 #2），回显失去意义 |
| 4 | skills/refactor-orchestrator/SKILL.md | 阶段1 创建任务目录 | "Skill({artifact-manager, --kind refactor --dev-dir})"（L63-67） | L43 Skill 调用 artifact-manager；L53 mkdir + 更新 current-state.json | ✅ | L55 current-state.json 更新为 refactor-1 |
| 5 | skills/refactor-orchestrator/SKILL.md | 阶段2 保存用户原语 | "将用户的原始任务描述原样写入 user-prompt.md"（L69-71 + new-orchestrator L105-112） | L59 Write user-prompt.md | ✅ | L61 "File created successfully at …/user-prompt.md" |
| 6 | skills/refactor-orchestrator/SKILL.md | 阶段2 Grill 前置采访（不可跳过） | "同 new-orchestrator 阶段 2。不可跳过，auto 模式也不例外"（L71；new-orchestrator L101-103） | L81/86 grill-with-docs skill 调用；L168-247 多轮 AskUserQuestion 与用户澄清 | ✅ | L169/L175/L244 用户实际回答/打断/提出新问题（"去重了吗""为什么是单独的 analysis_results 表"），采访真实发生 |
| 7 | skills/refactor-orchestrator/SKILL.md | 阶段2 硬门 grill 产出验证 | "test -s grill-interview.md && echo GRILL_OK …；读回前 20 行，零问句 → STOP"（new-orchestrator L126-134） | L250 Write grill-interview.md | ⚠️ | 产出文件存在（L252），但日志中无 test -s 验证与问号检测证据 |
| 8 | skills/refactor-orchestrator/SKILL.md | 阶段3 分析影响范围 | "读取 user-prompt.md 和 grill-interview.md / 读取受影响源文件 / Glob/Grep 发现关联文件 / 识别模式 / 查找已有测试 / 评估级联"（L73-83） | L258-288 大量读代码（find java、Read 各 service、cat yml/pom、grep @Scheduled、ls tests） | ✅ | L258-285 完成源码勘察后才进入 impact.md |
| 9 | skills/refactor-orchestrator/SKILL.md | 阶段4 写入 impact.md | "修改范围（硬约束）/ 排除范围 / 已有测试 / 风险点 / 特殊约束"（L84-92） | L290 Write impact.md | ✅ | L292 文件创建；产物含 5 项要求字段（已读产物验证） |
| 10 | skills/refactor-orchestrator/SKILL.md | 阶段5 Architecture + Design | "architecture 和 design 必须读取 impact.md 获取约束"（L93-100） | L295/307 Skill 调用；L303/312 Write architecture.md/design.md | ✅ | L305/314 文件创建；产物含约束内设计 |
| 11 | skills/refactor-orchestrator/SKILL.md | 阶段6 Plan 任务分解 | "产出 plan.md — 需要重构的模块清单"（L102-108） | L320 Skill plan 调用；L325 Write plan.md | ✅ | L327 文件创建；L329-331 TASK_OK FRONTEND_OK 自检 |
| 12 | skills/refactor-orchestrator/SKILL.md | 阶段7 审查（normal 模式） | "**必须**调用 AskUserQuestion 暂停等待用户审查"（L110-129） | L333 "`--auto` 模式跳过审查，直接进入 Exec 阶段" | ❌ | 用户命令行 L6 无 --auto（应为 normal），AskUserQuestion 未调用，审查被直接跳过——与 #2 同一错误的两面 |
| 13 | skills/refactor-orchestrator/SKILL.md | 阶段8 Exec | "Skill({web2-dev:exec, --mode refactor …})"（L131-142） | L334 Skill exec 调用 | ✅ | L335-336 启动 exec |
| 14 | skills/exec/SKILL.md | 初始化读 plan.md + 回显确认（硬门） | "grep -E '^\\|' plan.md … 回显 exec 初始化确认：task_dir/模式/任务数/任务列表"（L75-90） | L342 grep plan.md 任务列表；L346 "## exec 初始化确认 - task_dir: … - 模式: refactor - 任务数: 5" | ✅ | L344/L346 回显与模板一致 |
| 15 | skills/exec/SKILL.md | 阶段1 spawn ops agent 基础设施部署 | "Agent({subagent_type: 'ops' … infra-ops …})"（L93-121；Iron Law L22 "Exec spawns: … ops agent for 部署"） | L356-361 主 agent 自己 timeout 5 TCP 验证 RocketMQ（TCP_OK）后宣布 "基础设施已由用户配置完毕，阶段 1 完成"，未 spawn ops agent | ❌ | exec 规定 spawn ops agent 执行 infra-ops，实际主 agent 自行验证并跳过部署环节——违反 Iron Law "Exec NEVER runs tests itself" 精神（L24） |
| 16 | skills/exec/SKILL.md | 阶段2 按任务串行循环 | "按顺序逐个处理，不跳过不并行"（L127） | L369/516/573/620/636 依次 spawn 任务 A/B/C/D/E | ✅ | 5 个模块 agent 严格串行 |
| 17 | skills/exec/SKILL.md | Step 2a spawn coding agent（TDD） | "从 {task_dir}/.work/design.md 中读取 {模块名} 的详细设计。从 {task_dir}/.work/requirements.md 中读取对应的行为清单"（L151-152） | 5 次 spawn 均执行（L369 等）；但 .work/requirements.md 不存在——L459-461 grep requirements.md 返回 "ugrep: warning: …/requirements.md (file does not exist)"，L432/463 ls 确认 .work/ 下无该文件 | ❌ | spawn 模板要求读 requirements.md，但 refactor 链路（阶段0-9）没有任何节点产出它——数据来源断裂（详见 #26/#27） |
| 18 | skills/exec/SKILL.md | Step 2b 主 agent code-review | "主 agent 执行 code-review：Skill({web2-dev:code-review …})"（L167-172） | 5 个模块均执行 review（L372/522/578/623/642） | ✅ | L491/559/606/634/668 共 5 份 review 报告 |
| 19 | skills/exec/SKILL.md | Step 2b 不合格 → spawn fix → re-review（最多 3 轮） | "有不合格项 → spawn coding agent 一次性修复全部 … 循环直到零不合格项。最多 3 轮"（L174-199） | 模块 A（L492 spawn fix）、B（L560）、C（L607）各 1 轮修复后通过；D/E 无不合格项 | ✅ | L493/L561/L608 fix agent 返回且测试通过（46→102→105） |
| 20 | skills/exec/SKILL.md | Step 2c 记录 progress.json | "将任务完成状态写入 progress.json"（L201-212） | L362/499/572/611/635/669/694/723 多次 Write progress.json | ✅ | 最终 progress.json 含 5 模块 completed + 6 阶段完成 |
| 21 | skills/exec/SKILL.md | 错误处理：agent 挂起检测 | **插件未声明此机制。** 错误处理表（L397-406）仅覆盖 "TDD 失败/3 轮不合格/测试 5 轮失败/测试被破坏/健康检查失败/用户中断" 六类，无任何 Bash 超时/挂起检测条款 | 任务B agent 清理命令挂起 416.7 分钟（agentB.txt B346-348：pkill/sleep 2/rm 清理命令 18:14 发出，01:11 才返回 "Exit code 144"）；部署 ops agent 登录 curl 挂起 95 分钟（agentDeploy.txt D117-118：02:19:44 发出带 -m 10 超时的登录 curl，03:54:44 才返回 loginError） | ❌ | 两次共约 512 分钟挂起（占总耗时 12.7h 的 67%）期间主会话无任何检测/中断机制，只能干等。**这是"这次任务特别慢"的直接原因** |
| 22 | skills/exec/SKILL.md | 阶段3 后端集成测试（本地+自修复） | "调用 Skill(web2-dev:backend-integration-test) 完成测试 + 自修复循环"（L216-239） | L672 spawn；L678 返回 21/21 通过，发现并修复 HTTP/2 h2c 真实 bug | ✅ | L678-684：21/21 checks + P1 修复落地验证 |
| 23 | skills/exec/SKILL.md | 阶段4 部署后端（service-ops） | "按 CLAUDE.md 中的部署方式将后端服务部署到开发服务器。部署完成后执行健康检查"（L241-259） | L686 spawn ops agent；L687 返回（GAP 120.1min）；部署实际成功（容器在线）但 Jenkins 流水线从未触发，走手动 docker 部署绕过（agentDeploy.txt D167 "Jenkins 不可用（凭证无效）"、D192-197 手动停旧启新） | ⚠️ | 部署结果成功（D197-267 健康检查+全链路验证），但 "凭证无效" 判断错误导致绕过 CLAUDE.md 声明的正式流水线（详见 #31） |
| 24 | skills/exec/SKILL.md | 阶段5 后端集成测试（部署后） | "对部署后的后端服务运行 API 测试"（L261-279） | L695 spawn；L697 返回 30/30 PASS | ✅ | L697 "30/30 PASS（部署环境 dev 192.168…）" |
| 25 | skills/exec/SKILL.md | 阶段6-10 前端（开发/E2E/review/部署/E2E） | "spawn coding agent → 前端开发/前端 E2E/部署/部署后 E2E"（L281-376） | plan.md 前端节声明 "开发方式: 无前端变更（API 契约不变，查询仍走 analysis_results）前端入口: buffett-ui（不动）" | ✅ | 按 plan.md 约束合理跳过——plan.md 是 exec 唯一任务来源（L427） |
| 26 | skills/code-review/SKILL.md | 检查清单 #2 测试覆盖 | "逐条检查 {task_dir}/.work/requirements.md 中当前模块的行为清单"（L52-60） | L459-461 grep requirements.md 失败（文件不存在）；5 份 review 报告只含设计一致性比对 | ❌ | 插件声明该项检查，但数据源 requirements.md 在 refactor 链路从未被产出——检查实际无法执行，review 只剩设计一致性 |
| 27 | skills/artifact-manager/SKILL.md | 目录结构：.work/ 中间产物 | ".work/ 含 user-prompt.md / grill-interview.md / requirements.md / architecture.md / design.md / layouts/ / integration/ / e2e/ / coding/ / tdd-iterations.md"（L65-82） | L432/463 ls .work/ 显示仅有 architecture.md design.md grill-interview.md user-prompt.md（integration/ 为后补）；requirements.md、tdd-iterations.md、coding/ 自始至终不存在 | ❌ | 声明结构 vs 实际产物不符。refactor-orchestrator 阶段列表（L42-156）无 requirements 阶段，requirements.md 无产出归属；tdd-iterations.md/coding/ 无任何写入动作 |
| 28 | agents/coding.md | 启动规则：读设计文档 + 调 TDD skill | "读取 architecture.md、design.md … 调用 Skill(mattpocock-skills:tdd) 执行 RED→GREEN 循环"（L35-42） | agent 报告显示 TDD 完成：模块 A 46 测试（L370）、B 100 测试（L521）、C 105（L578）、D 108（L623） | ✅ | 各模块返回报告含测试通过数与 TDD 循环描述 |
| 29 | agents/coding.md | 自验证循环 | "实现后必须跑测试验证。测试失败 → 分析根因 → 修复 → 重跑"（L44-46） | 各 agent 均报告测试全通过 | ✅ | L370/521/561/578/623 测试计数 |
| 30 | agents/coding.md | 工作区隔离 | **插件未声明此要求。** coding.md 仅定义角色/约束/启动规则，无 git 提交或工作区隔离要求 | agentB.txt B364：模块B agent 报告 "Entity changes were pre-existing (module A's work)"——模块A 的未提交变更出现在模块B agent 的 diff 视野中 | ❌ | 所有 coding agent 在同一工作区串行作业，前 agent 未提交变更泄漏到后 agent 视野，产生跨 agent 状态污染，且无机制保证模块边界清晰 |
| 31 | agents/ops.md | 硬约束 #2 服务部署遵循 CLAUDE.md | "项目的 CLAUDE.md 中声明了部署方式、启停命令、账户信息。严格遵守，不得自行决定"（L32） | agentDeploy.txt D167-197：判定 "Jenkins 不可用（凭证无效）" 后自行走手动 docker 部署（scp→docker build→停旧启新），CLAUDE.md 声明的 Jenkins 流水线未使用 | ⚠️ | 部署结果成功但偏离声明部署方式。主会话 L772-845 复现证明凭据有效、之前是 CSRF 流程问题——"凭证无效" 是误判 |
| 32 | agents/ops.md | 硬约束 #4 部署完必须测试 | "每个部署步骤完成后必须验证服务可用性（端口监听、API 响应、数据库连接）"（L36） | agentDeploy.txt D196-267 健康检查 + MQ 消费链路验证（consumerProgress diff=0、触发爬取任务 37/38/39 success） | ✅ | D197/D209/D263 端口监听、任务 success、MQ offset 验证 |
| 33 | agents/ops.md | 报告准确性 | **插件未声明此要求。** 启动规则（L38-43）仅要求读 CLAUDE.md/ansible-patterns/security，无"失败归因需验证"要求 | agentDeploy.txt D167 报告 "Jenkins 不可用（凭证无效）"；主会话 05:03 用户来查（L729），L772-845 复现证明凭据有效、是 CSRF crumb 流程问题 | ❌ | 误导性归因导致：①用户 05:03-05:08 额外投入 8 分钟核对；②实际部署绕过正式流水线；③05:09 用户再问 "ops agent未完成部署任务？"（L849）——报告与事实存在两处偏差 |
| 34 | skills/code-review/SKILL.md | 执行者设计：主 agent 读全部代码 | "**主 agent 执行。** 主 agent 自己读设计文档、读代码、做比对。不 spawn agent"（L33-35） | 5 个模块 review 中主会话大量 Read/Bash 读代码（L381-491 等）；主会话上下文溢出 2 次：L413-414（17:42:21，任务A review 中）与 L708-709（04:21:50，清理后） | ❌ | 主 agent 亲自读全部代码导致主会话上下文 2 次 "ran out of context" 被压缩；压缩后需重新 ls/读文件恢复状态（L428-432），增加重复读取开销。code-review 设计未考虑上下文容量限制 |
| 35 | skills/refactor-orchestrator/SKILL.md | 阶段2 grill 耗时（约 50 分钟） | "relentless interview 确保 AI 理解用户真正想要什么"（new-orchestrator L101） | L168-247 多轮问答，期间 6 次用户思考/打断 GAP（4.2/2.1/14.8/5.1/4.8/10.3 分钟），用户 2 次拒绝 AskUserQuestion（L175/L244）、1 次 "其实我没懂这个是什么逻辑"（L177） | ⏭️ | 不在范围：耗时主体是用户思考与澄清时间，属于 grill 设计预期（防止 AI 偏差），非插件工程缺陷 |

### 根因分析与解决方案

| # | 应有步骤 | 达标? | 根因 | 解决方案 | 解决方案来源 |
|---|---------|-------|------|---------|-------------|
| 21 | 错误处理：agent 挂起检测 | ❌ | **插件无此机制。** exec 错误处理表（L397-406）只覆盖 6 类"任务失败"场景，无"任务无响应/超时"类目；阶段 2 循环（L127）同步等待 Agent 返回，无超时、心跳、时长阈值；Agent 工具本身无 timeout 参数，模型在 subagent 挂起时只能干等。7 小时挂起期间主会话无任何"报告用户"触发点 | exec 增加 agent 时长监控：① spawn 时记录开始时间，超过阈值（如 60 分钟）无返回 → AskUserQuestion 报告用户（继续等待/中断）；② spawn prompt 给 coding/ops agent 加"每条 Bash 命令必须带 timeout，预计 >2 分钟的命令先拆解"约束；③ 错误处理表加"agent 挂起/无响应"行 | harness-methodology.md 机制6 Phase Transitions（L333-372 出口验证含外部进程边界）+ 机制7 3+ Failures Rule 的阈值触发精神（L376-424）；官方文档 sub-agents（agent 无 timeout 字段 → 必须在 prompt 层解决） |
| 2 | 阶段0 硬门 --auto 来源验证 | ❌ | Hard Gate 声明存在（L48）但无配套的**强制执行动作**：无 grep 命令模板、无结果回显要求、无"grep 无结果 → 回退 normal"的机械出口。Red Flags（L176）已列出该借口但模型仍照做——Red Flags 是自我纠正信号，不能替代机械硬门。模型在"时间压力 + 流程熟悉"下跳过检查（与 diagnosis-guide §2.1 症状完全吻合） | 阶段0 内联机械硬门：`grep -c -- '--auto' {task_dir}/.work/user-prompt.md` 并回显结果；grep 无结果但 mode=auto → **报错回退 normal**（与 new-orchestrator L70-74 一致）。模式回显（L50-61）以 grep 结果为依据 | harness-methodology.md 机制5 Hard Gate（L282-330）+ 机制4 Red Flags（L199-273）；diagnosis-guide.md §2.1 |
| 12 | 阶段7 审查（normal 模式） | ❌ | 与 #2 同一根因：模式被错误判定为 auto 后，阶段7 的 AskUserQuestion（L110-129）被跳过。阶段7 自身无"模式校验"步骤——它信任上游的模式判定 | 阶段7 入口校验：normal 模式**必须**出现 AskUserQuestion 工具调用；若日志/上下文中无用户批准记录 → 禁止进入阶段8 | harness-methodology.md 机制5 Hard Gate（L282-330） |
| 3 | 阶段0 回显确认（运行模式） | ⚠️ | 回显模板存在（L50-61）但运行模式行无强制填写要求；模型回显了技术栈/dev_dir 却漏掉模式行 | 回显模板的模式行改为必填，且内容必须来自 grep 结果（与 #2 修复合并） | harness-methodology.md 机制5；diagnosis-guide.md §2.1 |
| 7 | 阶段2 硬门 grill 产出验证 | ⚠️ | refactor-orchestrator 阶段2 用"同 new-orchestrator 阶段 2"（L71）引用式继承，硬门命令模板（test -s + 问号检测）只存在于被引用文件（new-orchestrator L126-134），不在本 skill 上下文中——引用式声明稀释了强制力，模型未回读执行 | 将硬门命令模板内联到 refactor-orchestrator 阶段2（或显式调用 new-orchestrator 对应段落），不依赖"同 xxx"引用 | harness-methodology.md 机制5 Hard Gate（L282-330） |
| 17 | Step 2a spawn coding agent（读 requirements.md） | ❌ | **链路设计缺陷（数据传递断裂）。** refactor-orchestrator 阶段列表（L42-156）无 requirements 阶段（new-orchestrator 有阶段3 L147-158），但 exec 数据来源（L35）、Step 2a 模板（L151-152）、code-review 清单（L52-60）、artifact-manager 目录结构（L74）全部依赖 .work/requirements.md——引用它的节点无产出归属。refactor 模式删除 requirements 阶段时未同步下游依赖 | refactor 链路补 requirements 环节：阶段4 impact.md 后调用 requirements skill（--mode update/reverse 从代码+impact 反推行为清单），产出 .work/requirements.md；或在 exec 阶段2a 前加"requirements.md 存在性检查"硬门（缺失 → 报告阻塞） | harness-methodology.md 机制5 在传递边界（L944-949"spawn prompt 是否包含所有信息"）+ 机制6 Phase Transitions 入口验证（L333-372）；diagnosis-guide.md §2.4 数据传递不一致 |
| 26 | code-review 检查清单 #2 测试覆盖 | ❌ | 与 #17 同根因：code-review 依赖的 requirements.md 从未被产出（L54 引用 vs 产物缺失），行为清单检查从第一步就不可执行。review 报告只剩设计一致性（5 份报告均为佐证） | 与 #17 合并修复：requirements.md 产出后，code-review 恢复行为清单检查；修复前该检查项应显式标记"数据源缺失"而非静默跳过 | harness-methodology.md 机制5/6；diagnosis-guide.md §2.4 |
| 27 | artifact-manager 目录结构 | ❌ | artifact-manager（L65-82）声明了 10 项 .work/ 产物，但**没有任何 skill 被指定产出其中 4 项**（requirements.md 无归属节点、tdd-iterations.md/coding/ 无写入动作）——声明结构超出链路实际产出能力 | 目录结构表与各 orchestrator 阶段产出对齐：refactor 链路只声明实际产出的文件；或按 #17 补 requirements 环节后保持一致 | harness-methodology.md 机制6（阶段声明 vs 实际能力一致性） |
| 15 | 阶段1 spawn ops agent 基础设施 | ❌ | Iron Law（L20-24"EXEC RUNS ZERO TESTS"）未覆盖"验证"类动作的边界——主 agent 自行跑 TCP 验证不认为是"跑测试"；且 exec 阶段1 无"基础设施已存在"的分支规范（L93-121 只有全量部署模板），模型自行决定跳过 spawn | 阶段1 增加分支：组件已在 CLAUDE.md/ops-local.md 声明存在 → 仍 spawn ops agent 执行"验证可用性"任务（走 agent，主 agent 不直接验证）；显式写入 Red Flags："基础设施已存在所以我自己验证一下就行" | harness-methodology.md 机制1 Iron Law（L43-101）+ 机制10 When NOT to Use（L527-574）；diagnosis-guide.md §2.5 |
| 30 | 工作区隔离（跨 agent 污染） | ❌ | exec 任务循环（L127）无任务间 git 提交/清理要求；coding.md 核心约束（L27-33）无"工作区卫生"条款。5 个 agent 在同一工作区串行作业，前 agent 未提交变更泄漏到后 agent 的 diff（B364 铁证） | exec Step 2c 增加"任务提交"步骤：code-review 通过后 git add/commit 该模块变更（保证下个任务从干净基线开始）；coding.md Process 增加"开始前 git status 确认基线、只修改本模块文件" | harness-methodology.md 机制6 Phase Transitions 任务间出口验证（L333-372）；agent-structure.md §5.2"每个流程步骤都有验证"（L178-204） |
| 33 | ops agent 报告准确性 | ❌ | ops.md 启动规则（L38-43）无"失败归因验证"步骤——拿到 loginError 即下结论"凭证无效"，未先区分 CSRF 流程问题与凭据问题；service-ops 分支（L54-58）无降级决策规范 | ops.md service-ops 增加：① 部署工具失败 → 先验证工具本身（复现登录、检查 CSRF crumb 流程）再归因；② 归因存疑 → 报告"待确认"而非断言；③ 降级路径（手动部署）必须报告主会话并等待确认，不自行绕过 CLAUDE.md 声明方式 | agent-structure.md §5.2（每个流程步骤有验证）；harness-methodology.md 机制16 Flowchart for Decision Points（L796-818） |
| 31 | ops agent 部署遵循 CLAUDE.md | ⚠️ | 与 #33 同根因：无降级决策规范，模型在"Jenkins 不可用"时自行选择手动部署而非报告 | 与 #33 合并修复 | harness-methodology.md 机制16（L796-818） |
| 34 | code-review 执行者设计（主 agent 读全部代码） | ❌ | **结构问题。** code-review L35 硬性规定主 agent 亲自读代码，5 个模块累计读取量超出主会话上下文窗口（2 次 "ran out of context" 为铁证）。code-review 设计未考虑上下文容量约束 | code-review 增加"委托只读 review agent"模式：spawn 只读 agent（Read/Grep/Glob/Bash，无 Write）执行设计比对并返回清单，主 agent 审查清单而非全部源码；或 skill frontmatter 标 `context: fork` 在子 agent 中运行。保留"主 agent 直接执行"作为小模块回退 | skill-structure.md §2.2 `context: fork` 字段（L66-67）+ §3.1 渐进披露（L26-33）；agent-structure.md §5.4 官方 code-reviewer 示例（L238-268，工具集只读） |
| 23 | 阶段4 部署后端（service-ops） | ⚠️ | 部署 agent 95 分钟挂起属于 #21 同根因（无挂起检测）；Jenkins 绕过属于 #33/#31 同根因（归因错误 + 无降级规范） | 合并至 #21 + #33/#31 修复 | 同 #21、#33、#31 |

### 诊断结论摘要

- **直接原因（占 67% 耗时）**：两次 subagent Bash 挂起共约 512 分钟（#21）——任务B 清理命令 416.7 分钟 + 部署登录 curl 95 分钟。插件无任何挂起/超时检测护栏。这是"这次任务特别慢"的第一根因。
- **规则违反**：#2/#3/#12 —— 用户未加 --auto，硬门未执行，审查被跳过（直接后果：5 个模块的 plan 未经过用户审查就进入实现）。
- **数据断裂**：#17/#26/#27 —— refactor 链路无 requirements 阶段，但 exec 与 code-review 依赖 requirements.md。
- **设计缺陷**：#34 主 agent 亲自读代码导致上下文 2 次溢出；#30 无工作区隔离；#15 阶段1 未 spawn ops agent。
- **报告质量问题**：#31/#33 ops agent 误判凭据失效，导致绕过正式流水线 + 用户事后核对（额外 8 分钟人工）。
