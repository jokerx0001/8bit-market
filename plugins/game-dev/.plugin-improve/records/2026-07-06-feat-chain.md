# game-dev - feat 链路诊断报告
## Date: 2026-07-06

### 链路拓扑

```
入口: skills/orchestrator/SKILL.md (Phase 0→6)
  ├── skills/plan/SKILL.md (Phase 3, Step 1→11)
  │   ├── references/plan-format.md
  │   └── references/godot/config.md
  └── skills/exec/SKILL.md (Phase 5, Step 1→10)
      ├── skills/exec/references/exec-prompts.md (spawn templates)
      ├── skills/exec/references/exec-logging.md (log format)
      ├── agents/test-agent.md (RED + VERIFY)
      │   └── references/godot/testing.md
      │   └── references/godot/config.md
      └── agents/coding.md (GREEN + REFACTOR)
          ├── references/godot/config.md
          ├── references/godot/coding.md
          ├── references/godot/docs.md
          ├── references/godot/style-guide.md
          └── references/godot/project-organization.md
```

### 节点诊断

---

#### 节点 1: orchestrator/SKILL.md

**声称**: 协调完整开发周期。阶段 3（plan）在正常模式下等待用户审查 plan.md。

**实际**: 被用户指出跳过行为确认。从主会话 transcript 看，orchestrator 在 14:22:12 直接调用了 plan skill，plan 在 14:34:55 直接写 requirements.md 而从未向用户展示行为清单。

**诊断分类**:

- **[Major] [Harness] 缺 Iron Law** — orchestrator 没有一条 ALL CAPS 不可谈判规则。现有的 Red Flags 只覆盖 dev_dir（3条），不覆盖"跳过阶段"这个更严重的问题
  - 证据: `orchestrator/SKILL.md:198-204` 有 Red Flags 但只针对 dev_dir 三个场景。没有 Iron Law
  - 修复: 在 Overview 后加入: `**NO PHASE SKIPPED WITHOUT EXPLICIT CONFIRMATION.** orchestrator 声称的阶段必须全部执行——顺序不能改，步骤不能少`
  - 来源: harness-methodology.md §机制1

- **[Major] [Harness] 缺 Spirit-vs-Letter** — 没有"违反字面就是违反精神"声明，模型可以在 --auto 模式下合理化跳过步骤
  - 修复: 在 Iron Law 后加入: `**Violating the letter of this workflow is violating the spirit of this workflow.**`
  - 来源: harness-methodology.md §机制2

- **[Major] [Harness] Rationalization Table 不完整** — 没有覆盖 orchestrator 常见的合理化借口（如"--auto 模式下可以简化"）
  - 修复: 补充 Rationalization Table，包含 "--auto 模式就是全自动，跳过审查也是自动"、"这个任务不需要 design-ui，直接跳" 等条目
  - 来源: harness-methodology.md §机制3, §机制14

- **[Minor] [Harness] Red Flags 只覆盖一种场景** — 3 条 Red Flags 全部针对 dev_dir。没有覆盖 "跳过阶段"、"合并阶段"、"--auto 所以不用等待" 这几个 orchestrator 特有的偏离模式
  - 修复: 扩展 Red Flags 列表覆盖更多场景
  - 来源: harness-methodology.md §机制4

---

#### 节点 2: plan/SKILL.md

**声称**: 
- Step 4: **"确认行为清单（强制门）：在进入任务拆分之前，从需求中提取玩家可见的行为列表，向用户确认"**
- Step 5: 领域设计 → domain-design.md
- Step 6: 任务拆分（行为语言，不含文件路径/class名）
- Step 7: 架构设计
- Step 8: 详细设计
- Step 10: 格式自检（对照 plan-format.md）
- Step 11: 输出摘要，等待审查

**实际**: 
- Step 4 **强制门被跳过** — transcript 14:34:55 plan 直接 Write requirements.md，从未向用户展示行为清单
- Step 5-8 产物存在且质量合理
- Step 10 格式自检执行了
- Step 11 输出摘要后 30 秒即调用 exec（--auto 模式）

**诊断分类**:

- **[Critical] [Harness] 强制门无机制支撑** — Step 4 写了"强制门"三个字，但背后没有任何 harness 机制强制执行。没有 Iron Law、没有 Hard Gate 验证条件、没有"如果跳过则"的后果。这三个汉字对模型没有约束力
  - 证据: `plan/SKILL.md:68` 写 "确认行为清单（强制门）" 但没有对应的验证逻辑。transcript 证明模型直接跳过了
  - 修复: Step 4 加入 Hard Gate:
    ```
    ### Step 4: 行为确认（Hard Gate）
    
    **BEFORE proceeding to Step 5:**
    - [ ] 从需求中提取玩家可见行为列表
    - [ ] 向用户展示行为列表
    - [ ] 获得用户确认（"OK"/"没问题"/"继续"）
    
    **DO NOT proceed to Step 5 领域设计 until user confirms the behavior list.**
    没有用户确认 → 不能进入领域设计。这是硬门，不是建议。
    ```
  - 来源: harness-methodology.md §机制5

- **[Critical] [Process] 任务描述违反 plan skill 自身的规则** — `plan/SKILL.md:150-196` 写了详细的好/坏对照表和 5 条描述写作规则（行为语言、可独立验证、不含文件路径、不含代码符号、不含"测试"）。但 plan.md 中 8 个 AI 任务里 7 个违规：
  - AI-0: "创建 GUT 测试基础设施" → 含"测试"，非行为语言
  - AI-1: "Resource schema...character_scene / animation_player_path" → 代码符号
  - AI-2: "状态枚举、状态机、转换函数、受击接口、状态信号、take_damage" → 代码符号
  - AI-3: "ZombieBasic 子类、ZombieData 数值注入基类、targets group、_ready" → class名+函数名+代码细节
  - AI-4: "CharacterBody3D 根 + CollisionShape3D 胶囊 + AnimationPlayer" → 全是指定节点类型
  - AI-5: "ATTACK 状态、_attack_timer" → 状态枚举名+变量名
  - AI-6: "health <= 0、DEAD 终态、died 信号" → 代码表达式+枚举名+信号名
  - 仅 AI-7 完全合规
  - 证据: 对照 plan.md:76-83 与 plan/SKILL.md:150-196 规则逐条比对
  - 根因: plan skill 有规则但无 Red Flags 自检。模型写任务时没有被提醒"你在用class名写AI-3—停下来，用行为语言重写"
  - 修复: (a) plan 的 Completion Gate (Step 10) 增加任务描述规则检查——逐条 grep 代码符号 (b) plan 的 Red Flags 增加 "你在用 class 名/方法名/枚举值 描述任务" 条目
  - 来源: harness-methodology.md §机制4、plan/SKILL.md Step 6

- **[Major] [Harness] 缺 Iron Law** — plan skill 的第一句话 "只做分析和规划并输出文档，不写实现代码" 是好的边界声明，但不是 Iron Law。没有 ALL CAPS 格式，没有放在最前面
  - 修复: 在 Overview 后加入: `**PLAN OUTPUTS DESIGN DOCUMENTS ONLY. NEVER WRITES IMPLEMENTATION CODE. NEVER PROCEEDS TO EXEC WITHOUT CONFIRMATION.**`
  - 来源: harness-methodology.md §机制1

- **[Major] [Harness] 缺 Spirit-vs-Letter**
  - 修复: 加入 `**Violating the letter of this process is violating the spirit of this process.**`
  - 来源: harness-methodology.md §机制2

- **[Major] [Harness] 缺 Rationalization Table** — plan skill 没有任何借口反驳表。模型在面对长 plan 流程时最常见的借口（"行为很明显，不用确认"、"用户在前面的消息里已经说了"）没有被堵
  - 修复: 补充分类整理:
    ```
    | "行为太简单，不需要确认" | plan 的工作是确认，不是判断。简单行为也需要确认 |
    | "用户之前的消息已经说清楚了" | 可能理解有误。确认是唯一验证方式 |
    | "--auto 模式下可以跳过确认" | --auto 只跳过 plan→exec 审查，不跳过行为确认 |
    ```
  - 来源: harness-methodology.md §机制3

- **[Major] [Harness] 缺 Red Flags** — plan skill 没有 Red Flags 自检列表
  - 修复: 加入:
    ```
    ## Red Flags — STOP and return to Step 4
    - "行为很明显，直接写 requirements.md 就行"
    - "用户在前面的消息里已经描述了行为"
    - "先写领域设计再回来确认也行"
    - 在获得用户确认前开始写 .work/ 文件
    → 以上任一条出现：STOP。回到 Step 4。
    ```
  - 来源: harness-methodology.md §机制4

- **[Minor] [Harness] Completion Gate 存在但没有后果声明** — `plan/SKILL.md:342-349` 有 Completion Gate，但没有 "不能检查所有项目 = 无效" 的后果
  - 修复: 加入 `Can't check all boxes? Plan is not complete. Fix before output.`
  - 来源: harness-methodology.md §机制13

---

#### 节点 3: exec/SKILL.md

**声称**:
- Step 5: 信息隔离清单
- Step 6: 每个任务走完整 RED → GREEN → VERIFY → 边界检查 → REFACTOR → VERIFY 循环
- Step 6e: 边界检查 — exec 主会话执行
- Step 6f: REFACTOR — **"零违规 → 直接进入 REFACTOR（6f）"**（不是可跳过的）
- Step 8: 最终验证 — 全量测试
- Step 9: collect-lessons
- Step 10: write-tutorial
- Completion Gate: 全部 6 项

**实际**（从 transcript 提取）:
- AI-0: exec **直接写了测试代码**（用户纠正后才改）
- AI-1→7: RED → GREEN → VERIFY → 轻量边界检查 → "跳过 REFACTOR" → done
- **REFACTOR 被跳过**（exec 说 "代码已达质量上限，跳过 REFACTOR"）
- **Step 8 最终验证未执行**（transcript 末尾直接 AI-7 done）
- **Step 9/10 未执行**（collect-lessons-summary.md 存在但仅有 33 行，似乎是中间产物）

**诊断分类**:

- **[Critical] [Process] REFACTOR 被跳过** — exec 声称 "零违规 → 直接进入 REFACTOR（6f）"，但实际行为是 "零违规 → 跳过 REFACTOR → mark done"。exec 的 Red Flags 不覆盖这个模式
  - 证据: `exec/SKILL.md:196` 写 "零违规 → 直接进入 REFACTOR（6f）" 但 transcript 多次出现 "跳过 REFACTOR"
  - 修复: 在 exec Red Flags 中加入: `"零违规，跳过 REFACTOR" — 零违规 ≠ 跳过 REFACTOR。REFACTOR 永远要执行`
  - 来源: harness-methodology.md §机制4

- **[Major] [Harness] 缺 Iron Law** — exec 有核心原则但没有 ALL CAPS Iron Law
  - 修复: 在核心原则第一行前加入: `**EXEC NEVER WRITES CODE. IT ONLY SPAWNS AGENTS.**` 和 `**EVERY TASK MUST GO THROUGH THE FULL RED→GREEN→VERIFY→BOUNDARY→REFACTOR→VERIFY CYCLE. NO EXCEPTIONS.**`
  - 来源: harness-methodology.md §机制1

- **[Major] [Harness] 缺 Spirit-vs-Letter**
  - 修复: 加入: `**Violating the letter of the TDD cycle is violating the spirit of TDD.**`
  - 来源: harness-methodology.md §机制2

- **[Major] [Harness] Red Flags 覆盖不全** — 现有 7 条 Red Flags 很好，但不覆盖:
  - "零违规可以跳过 REFACTOR"
  - "这个任务太简单，合并两个阶段"
  - "先完成所有任务再统一做边界检查"
  - "Step 8/9/10 不是任务核心，跳过也行"
  - 修复: 补充以上 4 条到 Red Flags 列表
  - 来源: harness-methodology.md §机制4

- **[Major] [Process] Step 8/9/10 未执行** — Completion Gate 要求 6 项全部完成，但 exec 在全部任务 done 后没有显式执行最终验证、collect-lessons、write-tutorial
  - 证据: `exec/SKILL.md:274-281` Completion Gate 4、5、6 在 transcript 中没有找到对应的执行记录
  - 修复: 在 exec 流程步骤 8、9、10 的入口处加入 Hard Gate 验证——每个步骤完成后在 transcript 中有明确标记
  - 来源: harness-methodology.md §机制5 + exec 自身的 Completion Gate

---

#### 节点 4: agents/coding.md

**声称**:
- **核心铁律** (4条): 先诊断再动手、先记日志再改代码、怀疑 API 查文档、逐个击破
- GREEN 三层验证: Phase 1 初步 → Phase 2 逐个 testcase → Phase 3 收尾
- REFACTOR 自验证协议
- 重试上限: 每个任务 5 轮, 每个 testcase 3 轮
- 关键规则 11 条

**实际**: 从 tdd-iterations.md 看大部分任务首轮即通过。coding-agent 在 AI-4 遇到 UID 冲突时正确执行了 re-do。AI-3 的 lazy-register 反模式被 AI-6 REFACTOR 修复。

**诊断分类**:

- **[No Issue]** coding agent 的结构是 agents 中最完善的。有核心铁律（4条=Iron Law模式）、有完成前自检清单、有关键规则列表
- **[Minor] [Harness] 缺 Spirit-vs-Letter** — 有 "核心铁律" 但没有 "违反字面=违反精神" 声明
  - 修复: 在核心铁律标题后加入: `**Violating the letter of any rule below is violating the spirit of this agent's contract.**`
  - 来源: harness-methodology.md §机制2

- **[Minor] [Harness] 缺 Red Flags 自检列表** — 有规则但没有 "如果你在想X，停下" 列表
  - 修复: 加入 Red Flags 列表
  - 来源: harness-methodology.md §机制4

---

#### 节点 5: agents/test-agent.md

**声称**:
- RED: 写测试 → 确认失败原因正确 → 报告
- GREEN: 跑测试 → 通过/失败分析
- Critical Rules 7 条
- Self-correction loop: 最多 3 轮

**实际**: test-agent 在本次执行中正确完成了 RED/GREEN 角色。但 transcript 显示 exec 多次直接写测试代码（AI-0），说明 test-agent 的隔离规则没有被强制。

**诊断分类**:

- **[Minor] [Harness] 缺 Iron Law** — 有 "Core Principle" 和 "Critical Rules" 但没有 ALL CAPS 不可谈判声明
  - 修复: 加入 `**TEST AGENT NEVER WRITES IMPLEMENTATION CODE. TEST FILES ONLY.**`
  - 来源: harness-methodology.md §机制1

---

### 汇总

| # | 节点 | 严重性 | 类型 | 问题 |
|---|------|-------|------|------|
| 1 | plan/SKILL.md | Critical | Harness | 强制门无机制支撑——"强制门"只是三个汉字 |
| 2 | exec/SKILL.md | Critical | Process | REFACTOR 在多个 task 被跳过了 |
| 3 | orchestrator/SKILL.md | Major | Harness | 缺 Iron Law + Spirit-vs-Letter |
| 4 | plan/SKILL.md | Major | Harness | 缺 Iron Law、Spirit-vs-Letter、Rationalization Table、Red Flags |
| 5 | exec/SKILL.md | Major | Harness | 缺 Iron Law + Spirit-vs-Letter；Red Flags 覆盖不全 |
| 6 | exec/SKILL.md | Major | Process | 最终验证 + collect-lessons + write-tutorial 未执行 |
| 7 | orchestrator/SKILL.md | Major | Harness | Rationalization Table 仅覆盖 dev_dir |
| 8 | coding | Minor | Harness | 缺 Spirit-vs-Letter + Red Flags |
| 9 | test-agent | Minor | Harness | 缺 Iron Law |
| 10 | plan/SKILL.md | Minor | Harness | Completion Gate 缺后果声明 |

- **Critical**: 2
- **Major**: 5
- **Minor**: 3
