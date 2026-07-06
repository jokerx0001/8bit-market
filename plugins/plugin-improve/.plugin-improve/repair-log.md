# Plugin Improve — Repair Log

### Round 1 (2026-07-06)

- **Node:** `skills/plugin-improve/SKILL.md`
- **Problems:** 
  - [CRITICAL] Missing Iron Law — no non-negotiable rule preventing diagnosis without reading artifacts
  - [CRITICAL] Missing Rationalization Table — model's excuses for skipping file reads not preemptively blocked
  - [CRITICAL] Missing Hard Gates — phases had no forced checkpoints, allowing phase skipping
  - [CRITICAL] Missing Phase Transitions — phases lacked entry conditions, goals, exit verification
  - [MAJOR] Missing Red Flags — no self-diagnosis signals for step-skipping behavior
  - [MAJOR] Missing Self-Review Checkpoint — no verification before claiming completion
  - [MAJOR] Missing Checklist with Consequences — no enforcement mechanism for completion criteria
  - [MAJOR] Missing Spirit-vs-Letter declaration — escape path for "I understand the spirit" rationalization
  - [MAJOR] CSO violation — description contained workflow summary ("tracing its behavior chain, comparing...")
  - [MINOR] Missing When NOT to Use section
  - [MINOR] Missing Pressure Awareness coverage in rationalization table
- **Fix:** Complete restructure of SKILL.md:
  - Added Iron Law: "NO DIAGNOSIS WITHOUT READING THE ACTUAL ARTIFACT FILES FIRST"
  - Added Spirit-vs-Letter declaration
  - Rewrote description to CSO-compliant trigger-conditions-only format
  - Added When to Use / When NOT to Use section
  - Restructured all 5 phases with Entry condition, Goal, Actions, Exit verification, Hard Gate, and Next transition
  - Added Red Flags section with 9 self-diagnosis signals
  - Added Common Rationalizations table with 10 entries covering all pressure dimensions
  - Added Verification Checklist with consequence statement
  - Added Self-Review step within Phase 4
  - Retained Key Rules and References sections
- **Source:** harness-methodology.md §机制1,2,3,4,5,6,8,9,10,13,14; diagnosis-guide.md §2.1,2.2,2.3
- **Result:** pending verification

### Round 3 (2026-07-06)

- **Node:** `skills/plugin-improve/SKILL.md` 阶段3 + 阶段4
- **Problem:** [CRITICAL] 阶段3"诊断实际行为"是一条模糊的5步指令，模型可以"读过log→打勾→分类→写报告"，无法强制逐步骤、逐内容对照。阶段4"撰写诊断报告"是一个自由格式模板，没有强制表格结构。
- **Fix:** 
  - 阶段3拆分为4个强制顺序执行的子步骤（3.1→3.2→3.3→3.4），每个子步骤有独立硬检查点：
    - 3.1 梳理应有步骤和要求 — 从plugin文件提取每步+引用原文
    - 3.2 提取实际执行步骤 — 从log完整提取+与3.1建立映射
    - 3.3 逐步骤对比 — 每步判断✅/❌，达标必须引用产物证据
    - 3.4 产出诊断表格 — 强制6列表格写入 `diagnosis-result.md`
  - 阶段4重新定义为"分析根因并出具解决方案" — 读取诊断表格 → 对每个❌行追加根因+方案+来源三列
  - 关键约束:
    - ✅行必须有证据引用（不只有"✅"符号），否则整行无效
    - ❌行必须有具体要求vs实际的差异描述
    - 根因必须追溯到机制/结构层面（不能只说"模型没做"）
    - 每个方案来源可验证（reference章节或官方URL）
  - 更新红旗信号（+3条覆盖子步骤偷懒）、理性化借口（+2条）、验证清单（+6条）
- **Source:** 用户需求设计
- **Result:** pending verification

### Round 4 (2026-07-06)

- **Node:** `skills/plugin-improve/SKILL.md` 阶段1 步骤6（路径解析）
- **Problem:** [CRITICAL] reference 路径解析不执行——模型看到 skill 文件中的 `references/xxx.md` 后直接当作插件根目录路径，不执行"以源文件目录为基准解析"的规则。game-dev 诊断中 `skills/exec/SKILL.md` 引用的 `references/exec-prompts.md` 被解析为 `<plugin-root>/references/exec-prompts.md`（标记为❌），而文件实际存在于 `skills/exec/references/exec-prompts.md`。导致 5 行 ❌ 假阳性诊断和错误根因分析。
- **Evidence:** 诊断产物 `2026-07-06-feat-diagnosis-result.md` 拓扑树第24-25行显示 `references/exec-prompts.md ← ❌ 文件不存在`，但 `ls skills/exec/references/exec-prompts.md` 确认文件存在。game-dev exec/SKILL.md 第123行引用 `references/exec-prompts.md`，按路径解析规则应解析为 `skills/exec/references/exec-prompts.md`。
- **Fix:** 
  - 阶段1 步骤6 从模糊的"按路径解析规则计算实际路径"改为**强制3步机械流程**（确定源目录→拼接实际路径→bash ls验证）
  - 增加约束："只在实际路径得到文件系统确认后，才能将该节点写入拓扑树"
  - 出口验证增加 bash ls 验证要求
  - 红旗信号+理性化借口各增加1条路径解析相关条目
- **Source:** harness-methodology.md §机制5(Hard Gate) — 3步机械流程是不可跳过的检查点；harness-methodology.md §机制3(Rationalization Table) — 堵死"一看就是插件根路径"的借口
- **Result:** pending verification

- **Node:** `skills/plugin-improve/SKILL.md` 阶段3.1（子规则展开）
- **Problem:** [CRITICAL] 子规则展开不执行——虽然 SKILL.md 第173行已有"子规则展开"规则，但模型仍然将多条规则合并。game-dev 诊断中 plan/SKILL.md 步骤6含 6对 ❌/✅ 示例+多条独立原则，但只产出2行（应有至少8行）。
- **Evidence:** 诊断产物第21-22行 plan/SKILL.md 步骤6 只展开为2行，而源文件步骤6 含6对好/坏对照+"拆分原则"+"核心规则"等至少8条独立约束。
- **Fix:**
  - 增加**子规则展开示例**：展示"错误做法（合并1行）" vs "正确做法（展开为N行）"的对照
  - 出口验证增加**计数硬检查**："源文件 N 条独立规则 → 3.1 产出至少 N 行"
  - 红旗信号+理性化借口各增加1条规则合并相关条目
- **Source:** harness-methodology.md §机制5(Hard Gate) — 计数检查是不可跳过的硬门；harness-methodology.md §机制13(Checklist with Consequences) — 计数不匹配=工作无效
- **Result:** pending verification

### Round 5 (2026-07-06)

- **Node:** `skills/plugin-improve/SKILL.md` — 诊断范围边界缺失
- **Problem:** [CRITICAL] 诊断结果严重偏离核心目标。plugin-improve 应诊断"插件 skill/agent 是否按声明步骤执行、产物格式是否符合要求"，但实际产出的 `2026-07-06-feat-diagnosis-result.md` 根因分析部分（5个❌/⚠️行中的4个）聚焦在：
  - config.md 已知坑列表是否完整（reference 内容维护问题）
  - GUT engine error 处理机制（framework 限制）
  - 测试 fixture 写法质量（目标项目代码质量）
  - coding.md pass 规则覆盖不完整（reference 内容完善问题）
  
  这些全是 game-dev 具体开发效果问题，不是插件工程问题。用户反馈："结果最后列出的问题怎么都是game-dev具体开发的效果问题？那不是我们关心的，偏离的太离谱了"。
- **Evidence:** `game-dev/.plugin-improve/records/2026-07-06-feat-diagnosis-result.md` 根因分析第14、16、18、20、30行。其中第14行建议"在 config.md 增加已知坑"、第18行建议"增加 framework limitation 豁免"——这些修改的是 reference 内容，不会改变插件自身行为。
- **Root cause:** SKILL.md 缺少"诊断范围边界"约束。阶段3.1 无差别提取 plugin 文件中的所有要求（包括 reference 中的业务内容规范），阶段3.3 无差别评价所有要求的达标情况，阶段4 对所有不达标行进行根因分析。没有机制区分"插件工程问题"和"目标项目内容质量问题"。
- **Fix:**
  - 新增"诊断范围边界"章节（在"适用场景"之后、"参数"之前），包含：
    - 核心判定法则："改了这个问题会让插件自身更可靠地按声明步骤执行吗？"
    - 在范围内/不在范围内的明确列表
    - 边界区分示例表（6个场景对照）
    - 区分标准（改插件文件 vs 改 reference 内容 vs 改目标项目代码）
  - 阶段3.1 新增"范围过滤"规则：提取要求后逐条过核心判定法则，丢弃业务内容要求
  - 阶段3.3 新增"范围自检"判断标准 + 4个具体示例
  - 阶段4 新增步骤3："跳过不在范围的项"
  - 红旗信号新增4条范围偏离条目（中英双语）
  - 理性化借口新增2条范围偏离条目
  - 验证清单新增3条范围检查项
- **Source:** 用户反馈 + 诊断范围边界设计；harness-methodology.md §机制1(Iron Law) — 范围边界本质上是诊断流程的 Iron Law
- **Result:** pending verification

### Round 6 (2026-07-06) — 精简版

- **Node:** `skills/plugin-improve/SKILL.md`"决定 plugin 路径"
- **Problem:** Round 5 的修改被写入了 cache 目录而非源目录。
- **精确诱因:** 系统注入了两个不同的目录锚点——`Base directory for this skill` 指向 cache，`Primary working directory` 指向源目录。而 SKILL.md 的"决定 plugin 路径"只写了"当前目录"三个字，模型在歧义下选错了。
- **Fix（精准打击）:** 将"决定 plugin 路径"从模糊的"当前目录"改为：
  > `<plugin-path> = 当前工作目录（Primary working directory）。如果当前目录是 market 根目录，则是 plugins/<plugin-name>。`
  > 注意：系统注入的 `Base directory for this skill` 指向 cache（路径含 `plugins/cache`），这是 skill 自身的存储位置，不是你要诊断的目标插件路径。
- **去掉了:** Iron Law 加 cache 条款、阶段 5 步骤 0 hard gate、阶段 3.4 cache 写入检查、cache 相关 Red Flags(2条)、cache 相关理性化借口(1条)——所有这些对于防止一个路径歧义而言都是过度布防。
- **Source:** 系统提示中 `Base directory for this skill` vs `Primary working directory` 的双锚点分析
- **Result:** pending verification
