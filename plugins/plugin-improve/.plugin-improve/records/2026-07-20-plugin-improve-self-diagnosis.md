# plugin-improve - plugin-improve 自诊断结果
## 日期：2026-07-20

### 链路拓扑

```
skills/plugin-improve/SKILL.md (入口, 单节点)
├── skills/plugin-improve/references/harness-methodology.md (1032行)
├── skills/plugin-improve/references/skill-structure.md (312行)
├── skills/plugin-improve/references/agent-structure.md (428行)
└── skills/plugin-improve/references/diagnosis-guide.md (419行)
```

单节点插件，无 agent，无子 skill。

### 逐步骤诊断

| # | 所属节点 | 应有步骤 | 要求(来自plugin文件) | 实际步骤(来自log) | 达标? | 达标证据 / 不达标点 |
|---|---------|---------|---------------------|------------------|-------|-------------------|
| 1 | skills/plugin-improve/SKILL.md | 阶段1: 识别链路—读取入口文件 | "读取入口文件。完整读取——不要略读，不要从文件名推断。"（L122） | L7: SKILL.md 通过命令注入加载到 context 中 | ✅ | SKILL.md 完整内容已加载（597行），Phase 1 正确执行了 game-dev fix-conductor 全链路拓扑识别 |
| 2 | skills/plugin-improve/SKILL.md | 阶段1: 追踪下游节点—读取每个 skill/agent/reference | "追踪下游节点，搜索入口文件内容中的：显式 skill 引用、Agent 引用、Reference 文件路径"（L123-127） | L15-L69: 读取了 game-dev 全部下游文件（fix-conductor, fix-loop, debug-root-cause, 3个agent, 8个godot reference） | ✅ | game-dev 链路 30 节点拓扑完整识别，所有 downstream 文件已读取 |
| 3 | skills/plugin-improve/SKILL.md | 阶段1: 路径解析—3步机械流程(bash ls验证) | "第3步—用Bash验证实际路径是否存在。只在实际路径得到文件系统确认后，才能将该节点写入拓扑树。"（L161-165） | L201-L217: 多个 bash ls 命令验证 game-dev reference 路径 | ✅ | visual-qa/prompts/question.md、exec-prompts.md、plan-format.md 等路径经过 bash ls 验证 |
| 4 | skills/plugin-improve/SKILL.md | 阶段1 出口验证: "每个 reference 的实际路径已经过 bash ls 验证"（L174） | "拓扑中出现的路径必须是解析后经文件系统确认的路径，不能是未解析的原始引用字符串"（L174） | 诊断文件 L4-30 拓扑树中所有路径均为解析后的实际路径 | ✅ | 拓扑树30个节点全部经过 bash ls 验证，无未解析的原始引用字符串 |
| 5 | skills/plugin-improve/SKILL.md | 阶段2: 提取自我声明—对每个节点提取声称的步骤/产出/行为 | "对链路中的每个节点，重新读取文件并提取：Skill工作流/步骤、Agent核心职责/流程步骤/输出格式/边界、Reference提供的知识"（L191-206） | 诊断文件 L36-72：35 行逐步骤诊断，每行引用 plugin 文件原文 | ✅ | 每个 game-dev 节点的 self-claims 已逐条提取并引用源文件原文，覆盖 fix-conductor, fix-agent, fix-loop, debug-root-cause, test-agent |
| 6 | skills/plugin-improve/SKILL.md | 阶段3.1: 梳理应有步骤—子规则展开 | "子规则展开：当步骤包含规则表格、好/坏对照示例、编号清单、强制门检查项时，每一条都是独立的要求"（L254） | 诊断文件 L36-72 对每个步骤逐条展开 | ✅ | fix-conductor 步骤展开到位（如 spawn prompt 的禁止事项、testsuite/testcase 提取各单独一行），无合并 |
| 7 | skills/plugin-improve/SKILL.md | 阶段3.2: 提取实际执行步骤—从log完整读取 | "完整读取 --log 文件。从头到尾，不能跳读。"（L301） | session log (668行 JSONL) 被完整读取，提取了全部 tool call 时间线 | ✅ | 所有 agent spawn (test-agent×2, fix-agent) 的 JSONL transcript 都被追踪 |
| 8 | skills/plugin-improve/SKILL.md | 阶段3.3: 范围自检—判定前过核心判定法则 | "在做出 ❌ 或 ⚠️ 判定前，用核心判定法则确认该问题是'插件工程问题'而非'目标项目内容质量问题'"（L344） | 诊断文件 L84-85：标记了 2 个"不在范围"行（#26 grenade截图、#30 VERIFY截图） | ✅ | 不在范围行正确标注 ⏭️，未进入根因分析 |
| 9 | skills/plugin-improve/SKILL.md | 阶段3.4: 产出诊断表格—写入 diagnosis-result.md | "写入 <plugin-path>/.plugin-improve/records/YYYY-MM-DD-{chain}-diagnosis-result.md"（L371） | L232: diagnosis-result.md 写入 game-dev 目录 | ✅ | 文件写入正确路径，6 列表格格式完整，无空单元格 |
| 10 | skills/plugin-improve/SKILL.md | 阶段4: 读 diagnosis-result.md | "读取 diagnosis-result.md 中刚写入的表格"（L425） | L239: 读取刚写入的 diagnosis-result.md | ✅ | 文件内容正确回读 |
| 11 | skills/plugin-improve/SKILL.md | 阶段4: 根因分析—护栏问题引用 harness-methodology.md | "护栏问题 → 引用 harness-methodology.md 的具体机制编号"（L445） | **L232 写入诊断（含根因分析）时尚未读取 harness-methodology.md。首次读取在 L458（08:16），即用户明确指令之后。** | ❌ | SKILL.md L445 声明根因分析的"护栏问题"必须引用 harness-methodology.md 的具体机制编号。但 L232 写入的根因分析（L76-L91）中，多处引用 harness-methodology.md（如 #78 "护栏机制 #5"、"机制 #3"等），而 harness-methodology.md 的首次 Read 发生在 L458——比 L232 晚了 26 行（约 20 分钟）。模型在不读取 reference 的情况下写入了本应基于 reference 内容才能产出的根因分析。**具体差异：** 声明要求"引用 harness-methodology.md 的具体机制编号"，但实际执行时模型依赖自己对 harness 机制的记忆/猜测而非实际文件内容。 |
| 12 | skills/plugin-improve/SKILL.md | 阶段4: 根因分析—结构问题引用 skill-structure.md 或 agent-structure.md | "结构问题 → 引用 skill-structure.md 或 agent-structure.md 的具体章节"（L446） | session log 全程未读取 skill-structure.md 或 agent-structure.md | ❌ | SKILL.md L446 声明结构问题必须引用这两个 reference 文件。但 668 行 log 中，skill-structure.md 和 agent-structure.md 的 Read 调用次数为 0。诊断文件中 #79（spawn prompt 完整性）、#80（初始化摘要模板字段）、#89（test-agent Step 0 任务类型假设）属于结构问题，但其解决方案来源列写的是 fix-conductor SKILL.md / fix-agent.md / test-agent.md 自身的行号，而非 skill-structure.md 或 agent-structure.md。 |
| 13 | skills/plugin-improve/SKILL.md | 阶段4: 根因分析—两者都不覆盖时引用 diagnosis-guide.md | "两者都不覆盖 → 引用 diagnosis-guide.md §3.3 回退流程获取的官方文档 URL"（L447） | session log 全程未读取 diagnosis-guide.md | ❌ | SKILL.md L447 声明不覆盖时引用 diagnosis-guide.md §3.3 回退流程。668 行 log 中，diagnosis-guide.md 的 Read 调用次数为 0。诊断文件中 #86（fix 工作流缺少资产生成阶段）的根因分类为"Workflow 设计缺口"，不属于纯护栏或纯结构问题，按 L447 规则应走 diagnosis-guide.md §3.3 回退流程，但实际未执行。 |
| 14 | skills/plugin-improve/SKILL.md | 阶段4: 解决方案来源可验证 | "每个解决方案来源可验证（reference 章节或官方 URL）"（L451） | 诊断文件根因分析表 L76-L91 的"解决方案来源"列 | ⚠️ | 风险：方案来源列写的是具体 reference 文件路径（如 "plugin-improve references/harness-methodology.md — 护栏机制 #5"），但这些 reference 在写诊断时并未被实际读取。虽然方案内容本身合理，但来源的"可验证性"是虚假的——模型无法确认这些 reference 确实包含所声称的机制编号。如果 harness-methodology.md 的机制编号在版本更新后发生变化，这些引用就会过时。 |
| 15 | skills/plugin-improve/SKILL.md | References 声明: "诊断过程中按需加载" | SKILL.md L589-596 列出 4 个 reference 文件并标注"诊断过程中按需加载" | 4 个 reference 文件中仅 harness-methodology.md 被读取（L458, L467），skill-structure.md、agent-structure.md、diagnosis-guide.md 全程未读取 | ❌ | SKILL.md L591 的"按需加载"措辞过于宽松。模型将"按需"解释为"我觉得不需要就不加载"。证据：660+ 行 log 中，仅 harness-methodology.md 在用户明确要求后读取了 2 次，其余 3 个 reference 读取次数为 0。而诊断文件中 L76-L91 的根因分析涵盖了护栏问题、结构问题、工作流设计缺口——全部 3 种 reference 都应被需要。**具体差异：** "按需加载"声明了 reference 的可用性，但没有 Hard Gate 强制"何时必须加载"。 |
| 16 | skills/plugin-improve/SKILL.md | Red Flags: "根因很明显，不需要查 reference" | SKILL.md L517: "根因很明显，不需要查 reference" → "The root cause is obvious, no need to check references" | 模型在未读 reference 的情况下写出了引用 reference 机制编号的根因分析 | ❌ | 红旗信号 L517 列出的行为（觉得根因明显而不查 reference）在本次 session 中确实发生了。模型在 L232 写完了包含 harness 机制编号引用的根因分析，却从未读过 harness-methodology.md。红旗信号存在但未被触发——因为模型在写根因分析时没有先读 Red Flags 列表做自检。这暴露了 **Red Flags 的放置位置问题**：Red Flags 在 SKILL.md 末尾（L498），但根因分析在阶段 4 执行，模型在进入阶段 4 时不会重读 SKILL.md 末尾。 |
| 17 | skills/plugin-improve/SKILL.md | Rationalization: "我已经知道这个 skill/agent 文件里有什么了" | SKILL.md L539: "文件会变。你的记忆是陈旧的。现在就读取。" | 模型的行为等价于"我已经知道 harness-methodology.md 里有什么了" | ❌ | 理性化借口 L539 精确描述了本次行为：模型凭记忆/训练数据中的 harness 机制知识写根因分析，不读实际文件。借口条目存在但未被触发——因为模型没有在读 reference 之前先对比自己的行为与 Rationalization Table。与 #16 相同根因：这些护栏在文件末尾，不会在阶段执行时被重新激活。 |

### 根因分析与解决方案

| # | 应有步骤 | 达标? | 根因 | 解决方案 | 解决方案来源 |
|---|---------|-------|------|---------|-------------|
| 11 | 阶段4: 护栏问题引用 harness-methodology.md | ❌ | **"按需加载"无 Hard Gate 强制。** SKILL.md L589-596 的 References 章节使用"诊断过程中按需加载"措辞，但没有任何 Hard Gate 指定"何时必须加载"。阶段 4 L443-447 声明根因分析必须引用这些 reference，但该声明是描述性的（"护栏问题 → 引用 X"），没有硬检查点（"进入阶段 4 前必须确认：已读取以下 reference 文件"）。模型将"按需"解释为可选——如果自认为"已经知道"harness 机制，就不会触发 Read。**机制层：** 缺少机制 5 (Hard Gate) 在阶段 3→4 转换处强制验证 reference 文件已被读取。 | 在 SKILL.md 阶段 3→4 转换处（阶段 3.4 末尾、阶段 4 入口前）增加 Hard Gate：**"进入阶段 4 前硬门：确认以下 reference 文件已在当前 session 中被 Read——harness-methodology.md、skill-structure.md、agent-structure.md、diagnosis-guide.md。未读取 = 不具备根因分析资格，返回读取。"** 同时将 References 章节（L589-596）的"诊断过程中按需加载"改为"阶段 3-4 必须加载。进入阶段 3 前至少读取 diagnosis-guide.md；进入阶段 4 前至少读取 harness-methodology.md"。 | harness-methodology.md §机制5 (Hard Gate)："DO NOT proceed until X"；SKILL.md L104："每个阶段都有硬检查点（Hard Gate），在出口条件全部满足之前阻止前进。" |
| 12 | 阶段4: 结构问题引用 skill-structure.md / agent-structure.md | ❌ | **同 #11 根因。** "按需加载"缺乏强制性 + 阶段 4 入口无 Hard Gate。此外，这两个 reference 的触发条件更弱——诊断文件中 #79、#80、#89 属于结构问题（spawn prompt 完整性、初始化摘要模板、任务类型假设），按 L446 规则应引用 skill-structure.md 或 agent-structure.md，但模型甚至没有意识到这两个文件的存在（log 中读取次数为 0）。**机制层：** 缺少机制 3 (Rationalization Table) 中针对"我不需要读结构标准"的借口条目。 | 1) 同 #11 的 Hard Gate 方案——强制阶段 4 前读取。2) 在 Rationalization Table 中增加一条：`"结构问题我看代码就能判断，不需要查标准" → "skill-structure.md 和 agent-structure.md 包含官方规范。不查标准 = 基于个人偏好判断，不可复现。"` | harness-methodology.md §机制5 + §机制3；skill-structure.md §7 (常见 Skill 结构错误)；agent-structure.md §9 (常见 Agent 结构错误) |
| 13 | 阶段4: 不覆盖时引用 diagnosis-guide.md §3.3 | ❌ | **同 #11 根因 + diagnosis-guide.md 的触发路径过长。** diagnosis-guide.md §3.3 的用途是"当 reference 覆盖不足时"的回退流程——但模型必须**先读了 diagnosis-guide.md 才能知道自己覆盖不足**。当前设计是：模型不读 diagnosis-guide.md → 不知道自己覆盖不足 → 不触发 §3.3 回退 → 凭记忆或猜测补全方案。**机制层：** diagnosis-guide.md 的加载时机未被定义——它既是诊断决策树（应在阶段 3 开始时读），又是回退流程的触发点（应在覆盖不足时读）。 | 在阶段 3.1 开始前增加硬门：**"进入阶段 3 前：Read diagnosis-guide.md §2（症状类别→主要检查方向），根据当前链路的症状确定诊断重点。"** 阶段 4 的方案来源覆盖不足时，引用 diagnosis-guide.md §3.3 回退流程获取官方文档 URL。 | diagnosis-guide.md §2 (8 种症状类别) + §3.3 (回退流程)；harness-methodology.md §机制5 |
| 15 | References 声明: "按需加载" | ❌ | **措辞设计缺陷。** "按需加载"（L591）在中文语境下是"需要的时候再加载"，但模型将"需要"的判断权交给了自己——而模型的判断标准是"我是否已经知道这些内容"而非"流程是否要求这些内容"。对照 harness-methodology.md §机制1 (Iron Law)：铁律必须用 ALL CAPS 不可谈判的语言。"按需加载"的语言强度远低于 Iron Law，模型有充分的"理性化空间"说服自己不需要。**机制层：** 缺少机制 1 (Iron Law) 级别的 reference 加载声明 + 缺少机制 3 (Rationalization Table) 堵死"我已经知道"借口。 | 1) References 章节改为 Iron Law 级别声明：**"REFERENCE FILES ARE NOT OPTIONAL. 阶段 3-4 必须加载。未读取 reference 的诊断 = 猜测，不是诊断。"** 2) 在阶段 3 和阶段 4 入口各增加一个 Hard Gate 检查 reference 读取状态。3) 在 Rationalization Table 增加："这些 reference 我已经知道了" → "reference 会更新。你的记忆是快照。每次都读取。" | harness-methodology.md §机制1 (Iron Law 写法模板) + §机制3 (Rationalization Table 构建方法) + §机制5 (Hard Gate) |
| 16 | Red Flags: "根因很明显，不需要查 reference" | ❌ | **Red Flags 位置导致触发失败。** Red Flags 列表（L498-528）位于 SKILL.md 末尾，但 Red Flags 的目的是在执行过程中（阶段 3-5）触发自检。当模型逐阶段执行时：阶段 1-2 在文件前部 → 读完进入阶段 3 → 此时距 Red Flags 已有 200+ 行距离 → 模型的 working memory 中 Red Flags 已不可用。对照 harness-methodology.md §机制4："Red Flags 放在流程步骤**之后**"——但当前 SKILL.md 长达 597 行，从阶段 5 结束（L496）到 Red Flags（L498）只有 2 行距离，而从阶段 3 开始（L219）到 Red Flags 有 280 行距离。阶段 3 执行时 Red Flags 在上下文中的位置不突出。**机制层：** 红旗信号与执行点距离过远，无法在违规行为发生时触发。 | 在关键执行点（阶段 3.1 入口、阶段 4 入口）**内联简短 Red Flags 子集**，只放与该阶段直接相关的 2-3 条。例如：阶段 4 入口前加：**"阶段 4 红旗信号：'根因很明显不需要查 reference' → STOP。读了 reference 才有资格写根因。"** 完整 Red Flags 列表保留在末尾，但执行关键步骤前有精简版就近触发。 | harness-methodology.md §机制4 (Red Flags 放置位置)："Red Flags 放在流程步骤**之后**"——此规则的本意是每个流程组之后跟随其专属 Red Flags，而非整个文件末尾一个全局列表。skill-structure.md §4.2 (内容组织)："Core Workflow/Process → Red Flags" |
| 17 | Rationalization: "我已经知道这个文件里有什么了" | ❌ | **同 #16 根因：位置距离导致未触发。** Rationalization Table（L535-554）距离阶段 4 执行点（L417-462）约 80 行。模型在进入阶段 4 写根因分析时，Rationalization Table 不在工作记忆中。此外，Rationalization Table 是全局的（覆盖所有阶段），但没有阶段特定的精简版——模型需要在 16 条借口中匹配当前阶段相关的条目。**机制层：** Rationalization Table 的"就近触发"机制缺失。 | 在阶段 4 入口的内联 Red Flags 之后，增加 2-3 条阶段 4 专属理性化条目：**"我已经知道 harness 机制编号了 → harness-methodology.md 可能已更新，机制编号和描述可能不同。""不用查，方案很明显 → 方案必须有来源。没有来源 = 猜测。"** | harness-methodology.md §机制3 (Rationalization Table 放置位置)："skill body 的后半部分，在流程步骤和 Red Flags 之后"——此规则的本意是每阶段有专属 Rationalization，而非一个全局表。 |

### 不在范围的项（跳过根因分析）

| # | 步骤 | 原因 |
|---|------|------|
| — | 本次自诊断全部 7 个 ❌/⚠️ 行均为插件工程问题（改了 SKILL.md 能修好），无需跳过 | — |

### 修复状态（2026-07-20 Round 7）

| # | 状态 | 修复内容 |
|---|------|---------|
| 11 | 已修复：✅ | References 章节改为 Iron Law 级别强制声明 + 阶段 4 入口 Hard Gate |
| 12 | 已修复：✅ | 同 #11 + Rationalization Table 增加结构标准条目 |
| 13 | 已修复：✅ | 阶段 3 入口 Hard Gate：进入前必须 Read diagnosis-guide.md §2 |
| 14 | 已修复：✅ | 阶段 4 Hard Gate 强制 reference 读取 → 方案来源自动变为"实际读取过的" |
| 15 | 已修复：✅ | References 章节：从"按需加载"改为 "REFERENCE FILES ARE NOT OPTIONAL" |
| 16 | 已修复：✅ | 阶段 4 入口内联 Red Flags（4条中英双语）+ Red Flags 列表增加 3 条 |
| 17 | 已修复：✅ | 阶段 4 入口内联 Rationalization + Rationalization Table 增加 4 条 |
