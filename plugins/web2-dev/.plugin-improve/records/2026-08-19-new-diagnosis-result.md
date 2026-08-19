# web2-dev - new 链路诊断结果

## 日期：2026-08-19

> 被分析执行：`/mnt/d/project/neonbit/goal-backend/.web2-dev/new-1`（2026-08-18 13:14 → 08-19 12:25）
> 用户输入：`/web2-dev:new 根据同级目录的goal-app，完成后端。大模型调用使用springboot ai.提示词需要外部配置化方便修改调试。 --auto`
> 证据来源：产物目录（无 --log，用户确认"仅用产物目录"）——`.web2-dev/new-1/` 下 plan.md / progress.json / .work/*，项目 git 历史与部署服务器 curl 探测
> 运行时插件版本：`~/.claude/plugins/cache/8bit-market/web2-dev/0.1.8`（与 dev 工作副本逐文件 diff 一致）

### 链路拓扑

```
commands/new.md
→ skills/new-orchestrator/SKILL.md
  → skills/stack-detector/SKILL.md（阶段0c）
  → skills/artifact-manager/SKILL.md（阶段1）
  → grilling（阶段2b：引用 "mattpocock-skills:grilling"；实际安装为 ~/.claude/skills/grilling 裸名）
  → skills/requirements/SKILL.md（阶段3）
  → skills/architecture/SKILL.md（阶段4）
  → skills/design/SKILL.md（阶段5）
  → frontend-design（阶段5b 条件触发 — 本次未触发）
  → skills/plan/SKILL.md（阶段6）
  → skills/exec/SKILL.md（阶段8）
    → agents/ops.md → skills/infra-ops/SKILL.md（阶段1）+ skills/service-ops/SKILL.md（阶段4/9）
      → references/ops/ansible-patterns.md, references/ops/security.md,
        references/ops/springboot-deploy-pattern.md, references/ops/templates/springboot/,
        references/ops/jenkins-api-patterns.md
    → agents/coding.md（阶段2/3/5/6/7/10）
      → tdd（引用 "mattpocock-skills:tdd"；实际安装为 ~/.claude/skills/tdd 裸名）
      → skills/backend-integration-test/SKILL.md（阶段3/5）→ references/web/backend-testing.md → skills/debug-root-cause/SKILL.md
      → skills/frontend-e2e-test/SKILL.md（阶段7/10，未到达）→ references/web/frontend-e2e.md
      → references/rules/java/（技术栈规范）
    → skills/code-review/SKILL.md（Step 2b / 阶段8）
```

所有路径经 bash `ls` 验证存在。外部节点：`grilling`/`tdd` 为 `~/.claude/skills/` 用户级裸名 skill（symlink 08-11 创建），**无 mattpocock-skills 插件**（`installed_plugins.json` 无此插件，会话可用 skill 列表无 `mattpocock-skills:*`）。

### 逐步骤诊断

| # | 所属节点 | 应有步骤 | 要求(来自plugin文件) | 实际步骤(来自产物) | 达标? | 达标证据 / 不达标点 |
|---|---------|---------|---------------------|------------------|-------|-------------------|
| 1 | skills/new-orchestrator/SKILL.md | 阶段0a 运维配置检查硬门 | "检查项目根目录 ops-local.md 是否存在；检查文件非空（test -s ops-local.md）；任一条件不满足 → 输出 ❌ 运维配置缺失 → 终止"（L48-64） | ops-local.md 存在且非空（1059 字节，08-18 20:31） | ✅ | 产物：`/mnt/d/project/neonbit/goal-backend/ops-local.md` 存在，含 应用部署/基础设施 两节 |
| 2 | skills/new-orchestrator/SKILL.md | 阶段0b --auto 来源验证硬门 | "从 {task_dir}/.work/user-prompt.md 中 grep --auto；如果 user-prompt.md 中不含 --auto 但 mode 被判定为 auto → 报错：--auto 来源不明，回退为 normal 模式"（L70-74） | user-prompt.md L3 含 "--auto"；全链路按 auto 执行（无任何人工审查暂停痕迹） | ✅ | 产物：`new-1/.work/user-prompt.md` L3 "根据同级目录的goal-app，完成后端。大模型调用使用springboot ai.提示词需要外部配置化方便修改调试。 --auto" — 来源验证有据 |
| 3 | skills/new-orchestrator/SKILL.md | 阶段0b 模式回显确认 | "回显确认后才能进入阶段 1：## 运行模式 模式: {normal / auto}"（L75-82） | 无 log，产物无回显痕迹 | ⚠️ | 回显是纯交互显示步骤，无产物化设计——无 log 时不可验证 |
| 4 | skills/stack-detector/SKILL.md | 强制确认门 | "输出检测结果，**必须向用户确认**…**强制确认门：未收到用户 OK 确认前不落盘**"（L41-53） | stack.json 已落盘（.web2-dev/stack.json，值 java/spring-boot-ai/postgresql/nacos/minimax/flutter） | ⚠️ | 规则冲突：stack-detector"必须向用户确认"（L41-53）vs new-orchestrator 0c"不确定时向用户确认"（L89）vs auto 模式跳过人工审查点。本次 auto 运行落盘无用户 OK 痕迹——agent 在两个指令间选择了"不确定时才确认"的宽松解释。插件规则歧义导致行为不确定 |
| 5 | skills/new-orchestrator/SKILL.md | 阶段1 创建任务目录 | "artifact-manager 读取 current-state.json、递增计数器、创建 {dev_dir}/new-{N}/、写回状态。返回 task_dir"（L91-97） | current-state.json `{"current_task":"new-1","counters":{"new":1}}`；new-1/ 目录存在 | ✅ | 产物：`.web2-dev/current-state.json` 计数正确；`.web2-dev/new-1/` 含 plan.md/progress.json/.work/ |
| 6 | skills/new-orchestrator/SKILL.md | 阶段2a 保存用户原语 | "将用户的原始任务描述（触发 /web2-dev:new 的完整输入）原样写入 {task_dir}/.work/user-prompt.md"（L105-112） | user-prompt.md 存在，内容为用户原始输入 | ✅ | 产物：user-prompt.md L1-3 为原语全文（含 --auto），未加工 |
| 7 | skills/new-orchestrator/SKILL.md | 阶段2b 调用 Grilling 采访 | "Skill({skill: \"mattpocock-skills:grilling\"})"（L116）；铁律："grill-interview.md 只能由 grilling skill 的返回内容写入。orchestrator 绝不自己创建、自己整理、自己补写此文件"（L119-124） | grill-interview.md 存在但格式 ≠ grilling skill 声明的输出格式 | ❌ | 引用无法解析：环境无 mattpocock-skills 插件（installed_plugins.json 全量无此插件；会话可用 skill 仅裸名 `grilling`），`mattpocock-skills:grilling` 必然调用失败。产物格式偏差佐证：grilling skill 声明问句格式 `❓ **Q1** - **<title>**: <body>` + `➡️ <recommended answer>`（~/.claude/skills/grilling/SKILL.md L12-16），而 grill-interview.md 为 `### Q1 - ...` + `➡️ 推荐：...` + `**用户回答**: ...` + 自加的 "## 采访背景（已核实事实…）"（L6-16）与 "## 达成共识"（L45-50）节——文件被整理/补写，违反"不分类、不整理、不转化"铁律 |
| 8 | skills/new-orchestrator/SKILL.md | 阶段2b grill 产出硬门 | "test -s {task_dir}/.work/grill-interview.md…GRILL_MISSING → 报告阻塞…读回文件前 20 行，确认内容有 ? 或 ？。零问句 → 不是采访 → STOP"（L126-134） | grill-interview.md 存在且前 20 行含问句（Q1"是否完整实现 api-contract.md 全部 13 章接口？"） | ✅ | 机械门通过；但盲区：test -s + 问号检查只能验证格式，无法验证回答来自用户——auto 模式下 self-directed grilling 可通过此门（机制盲区并入 #7 根因） |
| 9 | skills/new-orchestrator/SKILL.md | 阶段3 requirements | "产出：项目级 {dev_dir}/requirements.md…per-task {task_dir}/.work/requirements.md（本次需求，含行为确认清单）"（L147-158）；行为清单格式"每条含 行为/验证描述/优先级"（L74-82） | 两文件均存在；per-task 31 条行为清单，每条有验证描述与优先级 | ✅ | 产物：`.web2-dev/requirements.md`（90 行表格，模块 1-13 需求）；`new-1/.work/requirements.md` L15-45 行为清单 31 行，如 "1 未带 token 请求业务接口 / 返回 401 + code=UNAUTHENTICATED / P0" |
| 10 | skills/new-orchestrator/SKILL.md | 阶段4 architecture | "产出：{task_dir}/.work/architecture.md — 模块划分、实体关系和领域模型、数据流、技术选型"（L160-166） | architecture.md 四节齐全 | ✅ | 产物：architecture.md 含 1.模块划分表（11 模块）/2.领域模型（实体+关系+规则）/3.数据流（4 条链路）/4.技术选型（11 项） |
| 11 | skills/new-orchestrator/SKILL.md | 阶段5 design | "产出：{task_dir}/.work/design.md — 按模块组织：数据库设计、API 接口设计、模块间交互"（L168-174） | design.md 13 模块，每模块 DB/API/交互齐全 | ✅ | 产物：design.md 每模块含 数据库设计表/API 设计表/模块交互 节（如 goal 模块 L53-102） |
| 12 | skills/new-orchestrator/SKILL.md | 阶段5b frontend-design 判定硬门 | "只要有任何一个行为描述了原来不存在的界面 → 调用 frontend-design；产出保存到 {task_dir}/.work/layouts/"（L176-189） | 用户原语"完成后端"无 UI 行为描述 → 未调用 frontend-design；layouts/ 不存在 | ✅ | 判定合理：任务为纯后端，前端（goal-app Flutter）已存在，plan.md 前端节"无前端"与之一致 |
| 13 | skills/new-orchestrator/SKILL.md | 阶段6 plan | "产出：{task_dir}/plan.md — 简洁任务清单（模块名 + 文件路径）"（L211-217）；"全部项目只有 1 个微服务 → plan.md 中只有 1 个任务"（L64） | plan.md 存在：元信息/任务列表(1 行)/前端节 | ✅ | 产物：plan.md L10-12 任务 1 行（goal-backend，含涉及路径）；L14-16 前端节"无前端"；与 1 微服务=1 任务硬约束一致 |
| 14 | skills/new-orchestrator/SKILL.md | 阶段7 审查（auto 跳过） | "全自动模式（mode=auto）：跳过 AskUserQuestion，直接进入阶段 8"（L238） | 无审查记录，直接进入 exec（progress.json 有 exec 产物） | ✅ | auto 模式合法跳过（#2 已验证 --auto 来源） |
| 15 | skills/exec/SKILL.md | Step 0b 读取 plan.md 任务列表 | "grep -E '^\\|' {task_dir}/plan.md…提取模块名列表。任务按行号顺序串行执行"（L75-78） | plan.md 可提取 1 个任务（goal-backend） | ✅ | 产物：plan.md 任务表 L10-12 仅 1 行 |
| 16 | skills/exec/SKILL.md | 阶段1 基础设施（ops） | "spawn ops agent…ops agent 返回后验证部署结果"（L93-121） | progress.json stages_completed[0] = infra_verify | ✅ | 产物：progress.json L7 "stages_completed": ["infra_verify", ...]（阶段完成记录；技能示例名 "infra_deploy" 为弱差异，不判） |
| 17 | skills/exec/SKILL.md | 阶段2a spawn coding（TDD） | "调用 Skill(\"mattpocock-skills:tdd\") 完成 RED→GREEN 循环"（L154） | 121 个单元测试产出（progress.json "121/121 unit"） | ❌ | 引用无法解析：环境无 mattpocock-skills 插件（同 #7 证据），`mattpocock-skills:tdd` 必然调用失败。TDD 行为本身发生了（src/test 下 30+ 测试文件、单测全过），说明 agent 以裸名 tdd 或自行执行绕过了声明路径——声明步骤未按字面执行 |
| 18 | skills/exec/SKILL.md | Step 2b code-review | "主 agent 执行 code-review…有不合格项 → spawn coding agent 一次性修复全部…最多 3 轮"（L167-199） | progress.json review_rounds: 2, review_passed: true | ✅ | 产物：progress.json L4-5 "review_rounds": 2, "review_passed": true — 2 轮 review 后通过，未超 3 轮上限 |
| 19 | skills/exec/SKILL.md | Step 2c 记录进度 | "将任务完成状态写入 {task_dir}/progress.json"（L202-212） | progress.json completed_tasks 含 goal-backend completed | ✅ | 产物：progress.json L4-5 `{"module":"goal-backend","status":"completed","review_passed":true,"review_rounds":2,"tests":"121/121 unit, 63/63 integration, 9/9 e2e"}` |
| 20 | skills/exec/SKILL.md | 阶段3 后端集成测试（本地） | "按 CLAUDE.md 中的方式在本地启动后端服务。对 design.md 中每个模块的 API 接口运行集成测试（成功 + 失败场景）。对 design.md 中声明的集成验证/全链路要求执行端到端验证…"（L233-235） | integration/ 脚本 8 个 + results.json ~62 用例全部 passed | ✅ | 产物：`.work/integration/results.json` 62 条 passed=true（如 case=03 POST /goals creates goal+plan+tasks、case=28 幂等回放 same=True、case=31 用户隔离 404）；server.log 显示连真实 PostgreSQL（jdbc:postgresql://dev.neonbit.if:5432/goal_backend，Flyway 9.22.3） |
| 21 | skills/backend-integration-test/SKILL.md | Phase 2a 读取 fix-attempts.md | "读取 {task_dir}/.work/fix-attempts.md 失败经验（告诉自己：不重复错误路径，必须换思路）"（L63） | fix-attempts.md 存在，5 个失败 case 分节 | ✅ | 产物：fix-attempts.md L5-51 按用例分节 "## case=POST /goals 等写接口 500 INTERNAL_ERROR 第 1 轮"、"## case=28 幂等回放失败（多次轮）第 1-3 轮" 等（08-11 修复 4 部分生效：文件本轮被创建） |
| 22 | skills/backend-integration-test/SKILL.md | Phase 2c debug-root-cause → debug-analysis-{case}.md | "调用 Skill(\"web2-dev:debug-root-cause\") 深度根因分析 → 产出 {task_dir}/.work/debug-analysis-{case}.md（逆向追踪 + 最小验证 + 证据链）"（L66-67） | .work/ 下零 debug-analysis-*.md 文件 | ❌ | find 全项目：无任何 debug-analysis-*.md。fix-attempts.md 记录 5 个失败 case 均被修复（含幂等 case 的逆向追踪与"复现实验 0/5→5/5"最小验证 L29-39）——诊断实质存在，但未产出 skill 声明的 per-case 文件 |
| 23 | skills/backend-integration-test/SKILL.md | Phase 2e 重跑 + 追加 fix-attempts.md | "重跑该用例 → 通过 → 下一个 / 失败 → 追加失败详情到 fix-attempts.md → 回到 2a"（L68） | fix-attempts.md 按用例分节且含轮次编号 | ✅ | 产物：fix-attempts.md L5 "第 1 轮"、L23 "第 1-3 轮"、L41 "第 1 轮"、L47 "第 1 轮" — 节格式与要求"## {case} 第 {N} 轮"一致 |
| 24 | skills/backend-integration-test/SKILL.md | Phase 2→3 硬门（强制） | "每轮失败修复后必须：追加失败详情到 fix-attempts.md…调用过 debug-root-cause 的用例产出 debug-analysis-{case}.md；任一缺失 → STOP。回到 Phase 2 补记录。不记录不得进入 Phase 3"（L81-88） | debug-analysis 全部缺失但循环未 STOP——进入 Phase 3 全量重跑（results.json 全过），且 progress.json 推进到 deploy_backend | ❌ | 硬门声明存在但未被执行：5 个失败 case 零 debug-analysis 文件，Phase 3 照常进入。对比 new-orchestrator grill 硬门有 `test -s` bash 命令模板（L128-131），本硬门纯文字无机械检查。且措辞为条件式（"调用过 debug-root-cause 的用例"）——agent 未调用 skill 而自行内联诊断（fix-attempts.md 的深度分析即证据）时，条件为空、门空转 |
| 25 | skills/backend-integration-test/SKILL.md | 结论硬门（强制） | "结论声明必须与验证范围一致。核心业务成功路径…未执行或环境不可验证 → 结论必须标注 BLOCKED/部分验证，禁止宣布全链路 PASS"（L136-147） | LLM 成功路径经 mock 验证（mock_llm_server.py / stub ChatClient），理由记录在 fix-attempts.md | ✅ | 产物：fix-attempts.md L59 "LLM 真实调用会花钱：集成环境不可行 → 服务端注入 stub ChatClient…集成测试只验证 402 预检/503 降级，LLM 成功路径由单测覆盖"；results.json case=19 "POST /llm/generate-plan via mock -> 200 + charge, consumed=6" — 环境受限理由有记录，成功路径经 mock 执行，无虚假 PASS 声明 |
| 26 | skills/exec/SKILL.md | 阶段4 部署后端 + 健康检查 | "按 CLAUDE.md 部署方式执行，不创建特性分支。部署完成后执行健康检查"（L257-260） | deploy 文件 commit+push（git 3 个部署 commit）；但部署后 API 不可达 | ❌ | 实测：dev.neonbit.if nginx 无路由（/api/v1/health → nginx 404 页）；192.168.1.16:8080 上运行的应用对 /health、/api/v1/health、/api/v1/goals 全部 404（Spring 错误 envelope，仅 /actuator/health UP）——部署的应用无任何 goal API 控制器映射，非当前构建。progress.json current_stage 停在 deploy_backend（无完成记录） |
| 27 | skills/service-ops/SKILL.md | 部署流程 6：产出环境地址清单 | "成功 → 产出/更新环境地址清单（见下节）→ 写入 ops-local.md"（L66） | ops-local.md 无环境地址清单节 | ❌ | 产物：ops-local.md 仅 应用部署/基础设施 两节，无 外网入口/API baseURL/前端入口/健康检查/中间件连接 清单（service-ops L69-82 声明的结构）——声明的成功产物缺失 |
| 28 | skills/service-ops/SKILL.md | 部署流程 4：健康检查 | "健康检查 → curl /health 或对应检查端点"（L64） | 无健康检查通过证据 | ❌ | 实测：部署后 /health 与 /api/v1/health 均 404（见 #26），无任何健康检查通过的产物证据；无部署失败报告（service-ops 流程 5"失败 → 输出部署失败报告"亦无） |
| 29 | agents/ops.md | 硬约束 #4 部署完必须测试 | "每个部署步骤完成后必须验证服务可用性（端口监听、API 响应、数据库连接）"（L36） | 192.168.1.16:8080 有 Spring 响应但无 goal API | ⚠️ | 与 #26-28 同源：无验证报告产物，无法确认 ops agent 是否验证过/如何归因——部署未达声明完成态 |
| 30 | skills/artifact-manager/SKILL.md | 目录结构声明 | ".work/ 中间产物：…coding/（coding agent 日志）…tdd-iterations.md（TDD 迭代记录）"（L65-82） | .work/ 仅 7 项：architecture.md design.md fix-attempts.md grill-interview.md integration/ requirements.md user-prompt.md；无 coding/、无 tdd-iterations.md | ⚠️ | 声明结构超出链路实际产出能力：全插件无任何节点写入这两个路径（exec Iron Law "log everything" L22 无落盘路径；coding.md 无日志步骤；tdd skill 不产出 tdd-iterations.md——grep 全插件+tdd skill 无写入动作）。08-09 诊断 #27 已指出同问题，未修复，本次再现 |
| 31 | agents/coding.md | 启动规则 4：调用 TDD skill | "调用 Skill(\"mattpocock-skills:tdd\") 执行 RED→GREEN 循环"（L42） | 与 #17 同：引用无法解析，TDD 行为发生但未走声明路径 | ❌ | 环境事实同 #7/#17：无 mattpocock-skills 插件，`mattpocock-skills:tdd` 无法解析；src/test 30+ 测试文件证明 TDD 效果存在——声明路径失效被临场绕过 |
| 32 | skills/exec/SKILL.md | 断点续跑：progress.json 阶段记录 | "progress.json 记录每个阶段的完成状态…exec 启动时读取 progress.json，从上次中断处继续"（L385-400） | stages_completed 只到 integration_test_local；deploy_backend 无完成记录 | ⚠️ | 阶段 3-10 的"记录进度"步骤在 skill 中被省略（L214"阶段 3-10 的 spawn prompt 模板结构…省略重复"——省略的还包括完成验证与进度记录），仅 Step 2c（L202-212）定义了 task_loop 的记录动作——部署阶段完成与否无法从进度文件确认，断点续跑只能回到 deploy_backend 重跑 |

备注：exec 阶段 5-10（部署后集成测试/前端开发/E2E）未到达——run 停在阶段 4，非本轮违规（前端按 plan.md"无前端"约束本也应跳过）。

### 根因分析与解决方案

| # | 应有步骤 | 达标? | 根因 | 解决方案 | 解决方案来源 |
|---|---------|-------|------|---------|-------------|
| 7/17/31 | grilling/tdd skill 引用解析 | ❌ | **依赖引用与安装环境不一致 + 无运行时依赖检查。** 插件 3 处引用 `mattpocock-skills:grilling`（new-orchestrator L116）、`mattpocock-skills:tdd`（exec L154、coding.md L42），README 依赖插件节声明 `mattpocock-skills`（README L40）；但环境实际安装的是 `~/.claude/skills/` 用户级裸名 `grilling`/`tdd`（08-11 symlink，无 mattpocock-skills 插件——installed_plugins.json 全量无）。Skill 工具按精确名字解析，插件前缀引用必然失败。agent 无声明回退机制，临场绕过：grill 自行采访并整理（grill-interview.md 格式 ≠ grilling skill 输出格式、含自加节，违反"grilling 返回什么就保存什么"铁律 L119-124）；TDD 以裸名/自行执行。机制层：引用解析断裂（diagnosis-guide §2.4）+ 依赖缺失无护栏 | ① 将 3 处引用改为环境可解析的裸名：`Skill({skill: "grilling"})`（new-orchestrator L116）、`Skill("tdd")`（exec L154、coding.md L42）——与已安装 skill 一致；② README 依赖插件节改为两条安装路径（mattpocock-skills 插件 或 用户级裸名），并注明两者 skill 名不同；③ new-orchestrator Step 2b 增加"Skill 调用失败 → 报告阻塞，禁止临场自办"（与铁律配套，堵死绕过路径） | harness-methodology.md §3.3 Reference 准确性/时效性（"不准确的引用直接导致 agent 做出错误行为"，L907-912）；diagnosis-guide.md §2.4 数据传递不一致（L120-145）；skill-structure.md §7.3 引用但目标不存在（L278-285） |
| 22/24 | debug-analysis-{case}.md 硬门未执行 | ❌ | **Hard Gate 无机械强制 + 条件式措辞可空转。** 08-11 修复 4 加入的 Phase 2→3 硬门（L81-88）是纯文字 checklist：无 bash 存在性检查命令模板（对比 new-orchestrator grill 硬门 L128-131 有 `test -s` 模板——同插件内部先例）；且措辞"调用过 debug-root-cause 的用例产出…"是条件式——coding agent 未调用 debug-root-cause（fix-attempts.md 的深度内联诊断即证据，L23-39 逆向追踪+最小验证）时条件为空，门空转。本次 5 个失败 case 零 debug-analysis 文件，Phase 3 照常进入并宣布全过，progress.json 推进——硬门形同虚设 | ① Phase 2→3 硬门内联机械检查命令模板：`ls {task_dir}/.work/debug-analysis-*.md 2>/dev/null | wc -l` 与 `grep -c '^## case=' {task_dir}/.work/fix-attempts.md`，任一输出为 0 → 输出 STOP 模板并回到 Phase 2；② Phase 2c 措辞改为无条件：**每个失败用例必须**产出 `{task_dir}/.work/debug-analysis-{case}.md`（删除"调用过 debug-root-cause 的"条件词）；③ Phase 3 入口（重跑全量前）内联上述 bash 检查，检查失败禁止重跑 | harness-methodology.md 机制5 Hard Gate（L282-330，对照 superpowers 示例均有可执行验证项）+ 机制6 Phase Transitions 出口验证（L333-372）；diagnosis-guide.md §2.1（"如果存在但仍跳过 → 检查强制执行动作"，L49-53）；对照同插件 new-orchestrator L126-134 的 test -s 先例 |
| 26/27/28/29/32 | 阶段4 部署未达完成态 | ❌ | **阶段 3-10 无完成验证门 + 部署停滞无报告机制。** exec 阶段 4 声明"部署完成后执行健康检查"（L260），service-ops 声明流程 4"健康检查"（L64）+ 流程 6"成功 → 产出/更新环境地址清单 → 写入 ops-local.md"（L66），但：① exec 只有 Step 2c（L202-212）定义 task_loop 的进度记录，阶段 3-10 的完成验证/进度记录被 L214"省略重复"抹掉——主会话信任 ops agent 报告，无产物级验证；② 错误处理表（L402-411）无"部署停滞/构建状态不可确认 → 报告用户"场景（08-09 诊断 #21 agent 挂起检测未修复的同类缺口）；③ 结果：部署 commit 已 push（Jenkins 触发），但部署后 API 全部 404（dev.neonbit.if 无 nginx 路由；192.168.1.16:8080 应用无 goal 控制器——非当前构建），ops-local.md 无环境地址清单，progress.json 停在 deploy_backend 无完成记录，无部署失败报告——链在无声处停滞 | ① exec 阶段 4 增加完成验证硬门：ops agent 返回后主 agent 验证 (a) ops-local.md 含环境地址清单节 (b) 健康检查端点 curl 200——任一失败 → 不进入阶段 5，重新 spawn ops；② service-ops 部署流程 6 增加机械自检：`grep -c '外网入口\|API baseURL\|健康检查' ops-local.md` 为 0 → 禁止声明部署成功；③ exec 错误处理表增加"部署停滞/构建状态不可确认"行：ops agent 无法确认 Jenkins 构建结果 → 立即 AskUserQuestion 报告用户（继续等待/中断），不无限重试；④ 阶段 3-10 每阶段完成时更新 progress.json（把 L214 的"省略重复"改为显式列出阶段完成记录模板） | harness-methodology.md 机制5 Hard Gate（L282-330）+ 机制6 Phase Transitions 出口验证（L333-372）+ 机制8 Self-Review Checkpoint（L428-473）；diagnosis-guide.md §2.2 声称完成但产物不符（L57-86）；agent-structure.md §5.2"每个流程步骤都有验证"（L197-204） |
| 4 | stack-detector 强制确认门 vs auto 模式 | ⚠️ | **插件规则歧义。** stack-detector"强制确认门：未收到用户 OK 确认前不落盘"（L41-53）与 new-orchestrator 0c"不猜测技术栈——不确定时向用户确认"（L89）是两套不同强度的指令，auto 模式又跳过人工审查点——agent 行为不确定。本次落盘正确（pom.xml → java/spring-boot-ai 无歧义）但确认门被宽松解释 | 统一规则：stack-detector 增加 auto 模式分支——技术栈特征唯一匹配（文件特征表 L21-35 单条命中）→ 允许落盘并在 stack.json 标注 `"confirmed": "auto-unambiguous"`；特征不明确 → 即使 auto 也必须确认。与 new-orchestrator 0c"不确定时确认"措辞对齐 | harness-methodology.md 机制16 Flowchart for Decision Points（L796-818，决策点需明确分支）；skill-structure.md §2.1/§4 规则无歧义 |
| 30 | artifact-manager 目录结构 vs 实际产出 | ⚠️ | **声明结构超出链路实际产出能力。** artifact-manager L65-82 声明 .work/ 含 coding/ 与 tdd-iterations.md，但链路无任何节点写入：exec Iron Law"log everything"（L22）无落盘路径，coding.md 无日志步骤，tdd skill 不产出 tdd-iterations.md。08-09 诊断 #27 已指出（修复记录 repair-log.md 第 1 轮未包含此项），本次再次缺失 | 推荐最小变更：从 artifact-manager 目录结构移除 coding/ 与 tdd-iterations.md 两行（与链路实际产出对齐）。若需保留：exec Step 2c 增加"coding agent 报告追加到 {task_dir}/.work/coding/{task}.md"、coding.md 增加"每轮 TDD 迭代追加 tdd-iterations.md" | harness-methodology.md 机制6 阶段声明 vs 实际能力一致性；diagnosis-guide.md §2.2 声明 vs 产物不符；08-09 诊断记录 #27（同根因历史） |
| 3 | 模式回显可审计性 | ⚠️ | 纯交互显示步骤无产物化设计，无 log 时不可验证 | 低优先级：阶段0b 回显后将判定结果并入 progress.json（`"mode": "auto"` 字段，与断点续跑结构合并），使 auto/normal 判定可审计 | harness-methodology.md 机制6 Phase Transitions 入口验证（L333-372） |
| 8 | grill 硬门机械盲区 | ⚠️ | 硬门（test -s + 问号检查）只能验证格式，无法验证"回答来自用户"——auto 模式下 self-directed grilling（Red Flags L280 明令禁止）可通过此门 | 与 #7 合并：修复 grilling 引用后，铁律"grill-interview.md 只能由 grilling skill 的返回内容写入"（L119-124）可恢复强制力；追加 Red Flags 条目："auto 模式下我自己编一份用户回答 → STOP"（双语：中/英） | harness-methodology.md 机制4 Red Flags（L199-273，双语规则 L261-272）+ 机制5 Hard Gate（L282-330） |

### 诊断结论摘要

- **核心问题 1（❌）**：backend-integration-test Phase 2→3 硬门（08-11 修复 4 加入）在真实运行中仍未执行——5 个失败 case 零 debug-analysis-{case}.md，循环未 STOP 照常进入 Phase 3 并推进到部署。文字级硬门无机械强制力，条件式措辞可空转。
- **核心问题 2（❌）**：`mattpocock-skills:grilling`/`mattpocock-skills:tdd` 引用在当前环境必然无法解析（插件未安装，实际为裸名用户级 skill），agent 临场绕过：grill 记录被整理/补写（违反"原样保存"铁律）、TDD 走非声明路径。依赖声明（README）与安装环境不一致且无运行时检查。
- **核心问题 3（❌）**：部署阶段（exec 阶段4 / service-ops）未达声明完成态——部署后 API 全部 404（非当前构建）、ops-local.md 无环境地址清单、progress.json 停在 deploy_backend 无完成记录、无失败报告。阶段 3-10 缺完成验证门（"省略重复"抹掉了进度记录与验证），部署停滞无报告机制（08-09 #21 同类缺口）。
- **次要问题（⚠️）**：stack-detector 确认门 vs auto 模式规则歧义；artifact-manager 目录结构声明超实际产出（08-09 #27 未修复再现）；grill 硬门机械盲区（auto 模式无法防 self-directed grilling）；模式回显不可审计。
- **符合声明**：#1、#2、#5、#6、#8-16、#18-21、#23、#25 —— orchestrator 各阶段产物齐全且格式合规，集成测试真实中间件全过且结论硬门合规（LLM 环境受限理由有记录、成功路径经 mock 验证），code-review 2 轮通过。执行纪律总体良好，问题集中在硬门强制力、外部引用解析、部署完成验证三处。

### 修复优先级

1. ❌ #22/#24（debug-analysis 硬门机械化）— 同插件已有 test -s 先例，改动小、收益直接
2. ❌ #7/#17/#31（skill 引用改裸名 + 依赖安装说明）— 3 处引用替换，消除"铁律被绕过"的源头
3. ❌ #26-29/#32（exec 阶段4 完成验证门 + service-ops 机械自检 + 错误处理表补部署停滞行）
4. ⚠️ #4（stack-detector auto 分支）、#30（目录结构对齐）、#3/#8（低优先级）

### 修复状态（第 2 轮，2026-08-19）

- #22/#24：已修复 ✅ — backend-integration-test Phase 2c 无条件化 + Phase 2→3 硬门内联 bash 机械检查（C/A 计数，A<C → STOP）
- #7/#17/#31：已修复 ✅ — new-orchestrator/exec/coding.md/fix-orchestrator 全部 `mattpocock-skills:*` 引用改裸名 `grilling`/`tdd`；README 依赖节注明两种安装方式；Step 2b 增加"Skill 调用失败 → 报告阻塞"；CLAUDE.md 同步
- #26-29/#32：已修复 ✅ — exec 新增阶段 1b/4b 完成验证硬门 + 阶段 3-10 每阶段强制更新 progress.json + 错误处理表补"部署停滞"行；service-ops 部署流程 6 增加 ADDRLIST 机械自检
- #4：已修复 ✅ — stack-detector 增加 auto 模式确认门分支（单条唯一命中可落盘并标注 `confirmed: auto-unambiguous`；特征冲突仍必须确认）
- #30：已修复 ✅ — artifact-manager/CLAUDE.md 目录结构移除 coding/ 与 tdd-iterations.md，替换为实际产出的 fix-attempts.md 与 debug-analysis-*.md
- #3/#8：已修复 ✅ — Step 0b 增加 mode.md 产物化；Red Flags 新增"编造用户回答"双语条目

详见 `.plugin-improve/repair-log.md` 第 2 轮。
