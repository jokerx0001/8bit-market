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
