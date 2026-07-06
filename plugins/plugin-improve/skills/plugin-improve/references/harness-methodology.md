# Harness Methodology

从 superpowers 插件体系中提取的行为护栏（harness）方法论。用于诊断和修复 Claude Code skill/agent 的行为偏离问题。

---

## 1. 核心哲学

### 1.1 什么是 Harness

Harness 不是教模型 **WHAT**（做什么），而是阻止模型在压力下偏离 **WHAT**。它是一套**行为强制机制**，确保模型即使想走捷径也走不了。

### 1.2 为什么需要 Harness

三条基础认知：

1. **模型会找借口** — 不是恶意的。但时间压力、沉没成本、疲劳、权威覆盖都会触发理性化（rationalization）——模型说服自己"这次情况特殊，可以不按流程来"
2. **格式建议不够** — "✅ DO: 做X" 和 "❌ DON'T: 别做 Y" 是建议，不是护栏。模型在压力下会把建议当可选项
3. **必须堵死每一个后门** — 模型足够聪明，能找到你没有显式禁止的逃脱路径。护栏要做的是：**预测每一个借口，提前堵死**

### 1.3 Harness vs 知识型 Skill 的区别

| 维度 | 知识型 Skill（plugin-dev 模式） | Harness 型 Skill（superpowers 模式） |
|------|-------------------------------|-------------------------------------|
| 核心假设 | 模型不知道怎么做 | 模型知道怎么做，但会走捷径 |
| 对抗目标 | 无知（格式错误） | 理性化（借口） |
| 测试方式 | 结构验证 checklist | 对抗性压力测试（baseline first） |
| 成功标准 | 格式正确 | 压力下行为不偏离 |
| 核心结构 | Best Practices 列表 | Iron Law + Rationalization Table + Red Flags |

---

## 2. 工具箱：16 个 Harness 机制

---

### 第 1 层：基础护栏

所有纪律型 skill 和 agent 的必备机制。

---

#### 机制 1: Iron Law（铁律）

**定义**：一条 ALL CAPS 的、不可谈判的规则，放在 skill/agent 最前面。不是建议，不是最佳实践，是**铁律**。

**放置位置**：Overview 部分，整个 skill body 的第一段之后。

**写法模板**：

```
## Overview

[一句话描述 skill 做什么]

**Core principle:** [一句话原则]

## The Iron Law

```
[ALL CAPS 规则]
```

[一句话后果陈述]
```

**superpowers 原文示例**：

来自 `systematic-debugging`：
```
## The Iron Law

NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST

If you haven't completed Phase 1, you cannot propose fixes.
```

来自 `test-driven-development`：
```
## The Iron Law

NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST

Write code before the test? Delete it. Start over.
```

来自 `verification-before-completion`：
```
## The Iron Law

NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE

If you haven't run the verification command in this message, you cannot claim it passes.
```

**何时需要 Iron Law**：
- skill 或 agent 有一条核心规则，违反它则所有其他内容都无意义
- 模型经常"跳过"某个步骤
- 模型在做 A 之前先做 B（应该先 B 后 A）

**Iron Law 失效信号**：skill 有 Iron Law 但模型仍然违反 → 检查是否缺少 Spirit-vs-Letter（机制 2）或 Rationalization Table（机制 3）

---

#### 机制 2: Spirit-vs-Letter 声明

**定义**：一句话切断"我理解精神所以可以灵活执行字面"这类辩论。让模型无法用"我知道规则的意思是..."来绕过规则。

**放置位置**：紧接 Iron Law 之后，或 Overview 末尾。

**写法模板**：

```
**Violating the letter of this rule is violating the spirit of this rule.**
```

或者更详细的版本：

```
**Violating the letter of the rules is violating the spirit of the rules.**
```

**superpowers 原文示例**：

`systematic-debugging`：
```
**Violating the letter of this process is violating the spirit of debugging.**
```

`test-driven-development`：
```
**Violating the letter of the rules is violating the spirit of the rules.**
```

`verification-before-completion`：
```
**Violating the letter of this rule is violating the spirit of this rule.**
```

**为什么有效**：聪明模型最常用的逃脱路径是 "我理解规则的精神，所以我可以灵活执行"。这句话直接堵死。

**何时需要**：任何有 Iron Law 的 skill/agent 都需要。没有 Iron Law 也需要——因为模型会对任何规则做"精神 vs 字面"的辩论。

---

#### 机制 3: Rationalization Table（理性化表格）

**定义**：一个 `| 借口 | 现实 |` 表格，显式列出模型会用的每一个借口，并逐条反驳。当模型读到自己的借口时，触发行为纠正。

**放置位置**：skill body 的后半部分，在流程步骤和 Red Flags 之后。

**写法模板**：

```
## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "[模型会说的借口1]" | [为什么这个借口不成立] |
| "[借口2]" | [现实2] |
| "[借口3]" | [现实3] |
```

**superpowers 原文示例**：

`systematic-debugging`：
```
| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
```

`test-driven-development`：
```
| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Keeping unverified code is technical debt. |
| "TDD is dogmatic, I'm being pragmatic" | TDD IS pragmatic: finds bugs before commit. |
| "Tests after achieve same goals" | Tests-after = "what does this do?" Tests-first = "what should this do?" |
```

**构建方法**（来自 writing-skills）：
1. 不用 skill 跑压力场景（baseline）
2. 记录模型实际说的每个借口（逐字）
3. 每个借口写一条反驳
4. 新借口出现时追加到表格
5. 重复直到没有新借口

**Rationalization Table 缺失的典型信号**：模型的输出看起来"体面"但结果不对。例如它说"已理解，正在实现"，但跳过了一半步骤。

---

#### 机制 4: Red Flags 列表（自检信号）

**定义**：一个 "如果你在想 X，立刻停下" 的列表。给模型一套自我诊断信号——当它脑子里出现列表中任何一个想法时，触发"我应该停下来"的行为。

**放置位置**：流程步骤之后，Rationalization Table 之前。

**写法模板**：

```
## Red Flags - STOP and [consequence]

- [想法/行为1]
- [想法/行为2]
- "I already [shortcut behavior]"
- "It's probably [guess without evidence]"
- "This is different because..."

**All of these mean: [consequence action].**
```

**superpowers 原文示例**：

`systematic-debugging`：
```
## Red Flags - STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when already tried 2+)
- Each fix reveals new problem in different place

ALL of these mean: STOP. Return to Phase 1.

If 3+ fixes failed: Question the architecture (see Phase 4.5)
```

`test-driven-development`：
```
## Red Flags - STOP and Start Over

- Code before test
- Test after implementation
- Test passes immediately
- Can't explain why test failed
- "I already manually tested it"
- "Tests after achieve the same purpose"
- "It's about spirit not ritual"
- "This is different because..."

All of these mean: Delete code. Start over with TDD.
```

**Red Flags 必须包含 "This is different because..."** — 这是模型最通用的逃脱短语，如果不列入，模型会用这个短语绕过所有其他 flag。

**放置位置的讲究**：Red Flags 放在流程步骤**之后**。如果放在开头，模型会过早自我审查，导致流程不启动。模型需要先读完流程知道该做什么，再读 Red Flags 知道什么算偏离。

**非英文 Skill 的双语规则**：如果 skill body 使用非英文（如中文）编写，Red Flags 必须**每条中英双语对照**。原因：多数大模型的内部推理（thinking/reasoning）使用英文，即使 skill body 是中文的。只写中文 Red Flags 匹配不上模型内部的英文自述，导致红旗信号失效。

双语 Red Flags 推荐使用表格格式：

```
| 中文 | English |
|------|---------|
| "我已经懂了，不需要读" | "I already understand, no need to read" |
| "这次不一样..." | "This is different because..." |
```

**来源**：plugin-improve self-diagnosis 实战验证——纯中文 Red Flags 对 deepseek-v4 等模型命中率不足，双语表格格式显著提高命中率。

---

### 第 2 层：流程控制

Workflow skill / conductor / orchestrator 的必备机制。

---

#### 机制 5: Hard Gate（硬检查点）

**定义**：一个显式的 "DO NOT proceed until X" 声明，放在两个阶段/步骤之间。不是 "建议检查"，而是**不完成就不能继续**。

**放置位置**：流程描述中，每个阶段转换处。

**写法模板**：

```
### Phase N → Phase N+1

**BEFORE proceeding to Phase N+1:**
- [ ] [验证条件1]
- [ ] [验证条件2]

**If ANY condition not met:** DO NOT proceed. Return to Phase N.
```

**superpowers 原文示例**：

`systematic-debugging` — 四个 Phase 之间的强制转换：
```
You MUST complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation
BEFORE attempting ANY fix:
[步骤...]

If you haven't completed Phase 1, you cannot propose fixes.
```

`brainstorming`：
```
<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project, or 
take any implementation action until you have presented a design and the user has 
approved it. This applies to EVERY project regardless of perceived simplicity.
</HARD-GATE>
```

`subagent-driven-development`：
```
Never:
- Start code quality review before spec compliance is ✅ (wrong order)
- Move to next task while either review has open issues
```

**Hard Gate 缺失的典型信号**：orchestrator 声称有多个阶段，但模型在一次响应中跳过了中间阶段直接到最终输出。例如 fix 链路跳过了 "行为澄清" 直接修 bug。

---

#### 机制 6: Phase Transitions（阶段转换）

**定义**：每个阶段有明确的入口条件、执行步骤、出口验证。不只是一个流程列表，而是**门控流程**。

**放置位置**：整个流程描述的组织方式。

**写法模板**：

```
### Phase N: [Name]

**Entry condition:** [进入此阶段的前置条件]
**Goal:** [此阶段要达成的目标]

**Actions:**
1. [具体步骤]
2. [具体步骤]

**Exit verification:**
- [ ] [验证项1]
- [ ] [验证项2]

**→ Next: Phase N+1** (仅当所有 exit verification 通过)
```

**superpowers 原文示例**：

`systematic-debugging` 的快速参考表：
```
| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| 1. Root Cause | Read errors, reproduce, check changes, gather evidence | Understand WHAT and WHY |
| 2. Pattern | Find working examples, compare | Identify differences |
| 3. Hypothesis | Form theory, test minimally | Confirmed or new hypothesis |
| 4. Implementation | Create test, fix, verify | Bug resolved, tests pass |
```

`subagent-driven-development` 使用流程图展示了严格的两阶段审查顺序 — spec compliance 必须先于 code quality。

**与 Hard Gate 的关系**：Hard Gate 是单个检查点。Phase Transitions 是整个流程的组织方式。两者配合：Phase Transitions 定义了阶段结构，Hard Gate 在每个转换点强制停留。

---

#### 机制 7: 3+ Failures Rule（失败阈值）

**定义**：一个数值阈值——当修复尝试达到 3 次仍然失败时，触发行为变更：不再继续修复，而是质疑更根本的东西。

**放置位置**：修复/调试流程的末尾。

**写法模板**：

```
### If N+ Fixes Failed

**Pattern indicating [deeper] problem:**
- [症状1]
- [症状2]

**STOP and question fundamentals:**
- Is this pattern fundamentally sound?
- Are we "sticking with it through sheer inertia"?
- Should we [fundamentally different approach]?

**Discuss with your human partner before attempting more fixes.**

This is NOT a failed hypothesis - this is a wrong [architecture/approach/fundamental].
```

**superpowers 原文示例**：

`systematic-debugging`：
```
### 5. If 3+ Fixes Failed: Question Architecture

Pattern indicating architectural problem:
- Each fix reveals new shared state/coupling/problem in different place
- Fixes require "massive refactoring" to implement
- Each fix creates new symptoms elsewhere

STOP and question fundamentals:
- Is this pattern fundamentally sound?
- Are we "sticking with it through sheer inertia"?
- Should we refactor architecture vs. continue fixing symptoms?

Discuss with your human partner before attempting more fixes

This is NOT a failed hypothesis - this is a wrong architecture.
```

**为什么是 3**：3 是一个心理阈值。1 次失败 = 可能是一个小错误。2 次失败 = 也许需要更深入思考。3 次失败 = 不是修复的问题，是诊断的问题。

**在 plugin-improve 中的应用**：repair-log.md 记录每次尝试。如果同一节点被修复 3 次仍然有问题，触发"质疑这个节点的设计"而不是继续改。

---

#### 机制 8: Self-Review Checkpoint（自检点）

**定义**：在声明"完成"之前，强制自己跑一遍检查清单。不是"应该检查"，而是**流程中不可跳过的一步**。

**放置位置**：流程的最后一步，输出之前。

**写法模板**：

```
## Self-Review

After [completing the work], look at [the output] with fresh eyes:

1. **[检查维度1]:** [检查什么] — [如何判断]
2. **[检查维度2]:** [检查什么] — [如何判断]
3. **[检查维度3]:** [检查什么] — [如何判断]

If you find issues, fix them inline. No need to re-review — just fix and move on.
```

**superpowers 原文示例**：

`writing-plans`：
```
## Self-Review

After writing the complete plan, look at the spec with fresh eyes and check the plan against it.

1. Spec coverage: Skim each section/requirement in the spec. Can you point to a task that implements it?
2. Placeholder scan: Search your plan for red flags — "TBD", "TODO", "implement later", "fill in details"
3. Type consistency: Do the types, method signatures, and property names you used in later tasks 
   match what you defined in earlier tasks?

If you find issues, fix them inline. No need to re-review — just fix and move on.
```

`brainstorming` — Spec Self-Review:
```
1. Placeholder scan: Any "TBD", "TODO", incomplete sections, or vague requirements? Fix them.
2. Internal consistency: Do any sections contradict each other?
3. Scope check: Is this focused enough for a single implementation plan?
4. Ambiguity check: Could any requirement be interpreted two different ways?
```

**Self-Review 缺失的典型信号**：模型声称完成但产物有明显遗漏。例如 plan 里写了 "添加错误处理" 但没有具体代码，或者类型名前后不一致。

---

### 第 3 层：描述与触发

所有 skill 的必备机制。

---

#### 机制 9: CSO 描述原则（Claude Search Optimization）

**定义**：SKILL.md 的 `description` 字段**只写触发条件，不写 workflow 摘要**。如果 description 包含了流程总结，模型会用 description 作为捷径而不读 skill body。

**放置位置**：YAML frontmatter 的 `description` 字段。

**写法模板**：

```yaml
# ✅ GOOD: 只有触发条件，无 workflow 摘要
description: Use when implementing any feature or bugfix, before writing implementation code

# ✅ GOOD: 具体症状和场景
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes

# ❌ BAD: 包含 workflow 摘要 — 模型用这个就够了，不会读 body
description: Use when executing plans - dispatches subagent per task with code review between tasks
```

**superpowers 原文示例**（writing-skills CSO 部分）：

```yaml
# ❌ BAD: Summarizes workflow - Claude may follow this instead of reading skill
description: Use when executing plans - dispatches subagent per task with code review between tasks

# ❌ BAD: Too much process detail  
description: Use for TDD - write test first, watch it fail, write minimal code, refactor

# ✅ GOOD: Just triggering conditions, no workflow summary
description: Use when executing implementation plans with independent tasks in the current session

# ✅ GOOD: Triggering conditions only
description: Use when implementing any feature or bugfix, before writing implementation code
```

**为什么这个很重要**：writing-skills 中记录了实际测试结果——当 description 包含 "code review between tasks" 时，模型只做了 **一次** review（description 说的），而不是 skill body 里的 **两次** review（spec compliance + code quality）。

**CSO 的其他原则**（同样来自 writing-skills）：
- 用 "Use when..." 开头，聚焦触发条件
- 包含具体症状而非抽象概念
- 关键词覆盖：错误消息、工具名、症状词
- 第三方称（skill 被注入 system prompt）

---

#### 机制 10: When NOT to Use

**定义**：显式列出**不应该**触发此 skill 的场景。防止 skill 被错误激活，也防止模型在不适用的场景下生搬硬套。

**放置位置**：`## When to Use` 部分中，作为子章节或列表。

**写法模板**：

```
## When to Use

Use for [具体场景]:
- [场景1]
- [场景2]

**Don't use when:**
- [不适用场景1] — [为什么不该用]
- [不适用场景2] — [为什么不该用]
```

**superpowers 原文示例**：

`systematic-debugging`：
```
**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Manager wants it fixed NOW (systematic is faster than thrashing)
```

`dispatching-parallel-agents`：
```
**Don't use when:**
- Failures are related (fix one might fix others)
- Need to understand full system state
- Exploratory debugging: You don't know what's broken yet
- Shared state: Agents would interfere
```

`writing-skills`：
```
**Don't create for:**
- One-off solutions
- Standard practices well-documented elsewhere
- Project-specific conventions (put in CLAUDE.md)
- Mechanical constraints (if it's enforceable with regex/validation, automate it)
```

---

### 第 4 层：行为细节

Agent 和具体执行 skill 的必备机制。

---

#### 机制 11: Clean Break（干净断裂）

**定义**：显式禁止保留旧代码作为"参考"。如果规则说"删除"，就必须删除——不许保留、不许参考、不许"adapt"。用明确的语言堵死每一个变通路径。

**放置位置**：Iron Law 之后，作为展开说明。

**写法模板**：

```
[Iron Law: NO X WITHOUT Y FIRST]

[违反后果]: [Delete it. Start over.]

**No exceptions:**
- Don't keep it as "reference"
- Don't "adapt" it while [doing the right thing]
- Don't look at it
- [Action verb] means [action verb]
```

**superpowers 原文示例**：

`test-driven-development`：
```
Write code before the test? Delete it. Start over.

**No exceptions:**
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Don't look at it
- Delete means delete

Implement fresh from tests. Period.
```

`writing-skills`：
```
**No exceptions:**
- Not for "simple additions"
- Not for "just adding a section"
- Not for "documentation updates"
- Don't keep untested changes as "reference"
- Don't "adapt" while running tests
- Delete means delete
```

**Clean Break 缺失的典型信号**：模型说 "我已经有一些代码了，让我 adapt 它来匹配测试"。结果是测试验证的是旧实现，不是需求。

---

#### 机制 12: Forbidden Responses（禁止响应）

**定义**：一个具体的 "NEVER 说这些话" 列表。每条包含禁止内容 + 正确替代。

**放置位置**：agent 的 system prompt 末尾，或 skill body 的行为规范部分。

**写法模板**：

```
## Forbidden Responses

**NEVER:**
- "[禁止说的短语1]" — [为什么禁止]
- "[禁止说的短语2]" — [为什么禁止]

**INSTEAD:**
- [正确的回应方式1]
- [正确的回应方式2]
```

**superpowers 原文示例**：

`receiving-code-review`：
```
## Forbidden Responses

**NEVER:**
- "You're absolutely right!" (explicit CLAUDE.md violation)
- "Great point!" / "Excellent feedback!" (performative)
- "Let me implement that now" (before verification)

**INSTEAD:**
- Restate the technical requirement
- Ask clarifying questions
- Push back with technical reasoning if wrong
- Just start working (actions > words)
```

**何时需要**：当模型有特定的沟通反模式时（如表演性同意、过度感谢、先承诺再验证）。

---

#### 机制 13: Checklist with Consequences（带后果的检查清单）

**定义**：一个验证清单，配有一条明确的后果声明——不能检查所有项目 = 整个工作无效，必须重来。

**放置位置**：skill body 末尾，或流程的最后一步。

**写法模板**：

```
## Verification Checklist

Before marking work complete:

- [ ] [验证项1]
- [ ] [验证项2]
- [ ] [验证项3]
- [ ] [验证项4]

Can't check all boxes? [Consequence statement: You skipped X. Start over.]
```

**superpowers 原文示例**：

`test-driven-development`：
```
## Verification Checklist

Before marking work complete:

- [ ] Every new function/method has a test
- [ ] Watched each test fail before implementing
- [ ] Each test failed for expected reason (feature missing, not typo)
- [ ] Wrote minimal code to pass each test
- [ ] All tests pass
- [ ] Output pristine (no errors, warnings)
- [ ] Tests use real code (mocks only if unavoidable)
- [ ] Edge cases and errors covered

Can't check all boxes? You skipped TDD. Start over.
```

**与普通 checklist 的区别**：普通 checklist 是参考。Checklist with Consequences 是判决——有后果声明才有约束力。

---

#### 机制 14: Pressure Awareness（压力感知）

**定义**：在 Rationalization Table 中显式覆盖**特定压力场景**：时间压力、沉没成本、权威覆盖、疲劳。模型在不同压力下会找不同的借口，每种都需要独立的反驳。

**放置位置**：Rationalization Table 中的条目。不需要独立章节，而是确保表格覆盖了这些压力维度。

**必须覆盖的压力维度**：

| 压力类型 | 典型借口 | 反驳策略 |
|---------|---------|---------|
| 时间压力 | "Emergency, no time for process" | "Systematic is FASTER than thrashing" |
| 沉没成本 | "Deleting X hours is wasteful" | "Sunk cost fallacy. Keeping unverified code is technical debt." |
| 权威覆盖 | "Manager wants it fixed NOW" | "Systematic is faster than thrashing" |
| 疲劳 | "I'm tired" | "Exhaustion ≠ excuse" |
| 过度自信 | "I'm confident it's good" | "Confidence ≠ evidence. Test anyway." |
| 简单化 | "This is too simple to need X" | "Simple things break too. Process takes 30 seconds." |

**superpowers 原文示例**（跨越多个 skill）：

`systematic-debugging` 的 "Use this ESPECIALLY when:" 反向利用了压力感知——在压力越大的时候越强制使用：
```
**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue
```

`verification-before-completion` 的 Red Flags 中包含 "Tired and wanting work over"。

---

#### 机制 15: Real-World Impact（真实数据）

**定义**：用具体数字和真实案例建立可信度。当模型看到 "95% vs 40% first-time fix rate" 时，比看到 "systematic debugging is faster" 更容易接受规则。

**放置位置**：skill body 末尾，作为可选补充。

**写法模板**：

```
## Real-World Impact

From [来源]:
- [指标1]: [具体数字]
- [指标2]: [具体数字]
- [指标3]: [具体数字]
```

**superpowers 原文示例**：

`systematic-debugging`：
```
## Real-World Impact

From debugging sessions:
- Systematic approach: 15-30 minutes to fix
- Random fixes approach: 2-3 hours of thrashing
- First-time fix rate: 95% vs 40%
- New bugs introduced: Near zero vs common
```

`dispatching-parallel-agents`：
```
## Real-World Impact

From debugging session (2025-10-03):
- 6 failures across 3 files
- 3 agents dispatched in parallel
- All investigations completed concurrently
- All fixes integrated successfully
- Zero conflicts between agent changes
```

---

#### 机制 16: Flowchart for Decision Points（决策流程图）

**定义**：对非显而易见的决策分支使用 dot/graphviz 流程图。不是装饰，是**防止模型在分支点走错**。

**放置位置**：`## When to Use` 或流程描述中，紧随决策点之后。

**superpowers 原文示例**：

`subagent-driven-development` 的 When to Use 流程图：
```
"Have implementation plan?" → no → "Manual execution or brainstorm first"
"Have implementation plan?" → yes → "Tasks mostly independent?"
"Tasks mostly independent?" → no → "Manual execution or brainstorm first" 
"Tasks mostly independent?" → yes → "Stay in this session?"
```

`brainstorming` 的完整 9 步流程图展示了从探索到实现的全路径。

**何时使用**（来自 writing-skills）：
- **使用流程图**：非显而易见的决策点、模型可能提前停止的循环、A vs B 选择
- **不使用流程图**：参考材料（用表格）、代码示例（用 markdown）、线性指令（用编号列表）

---

## 3. 按组件类型的 Harness 布局

### 3.1 Skill (SKILL.md) 的 Harness 排布

```
---
name: skill-name
description: ...             ← [机制9 CSO] 只写触发条件，不写workflow摘要
---

# Skill Name

## Overview
[1-2句描述]
← [机制1 Iron Law]: 一条ALL CAPS规则
← [机制2 Spirit-vs-Letter]: 一句话声明

## When to Use
[触发场景列表]
← [机制10 When NOT to Use]: 反例

## The Process / Workflow
← [机制5 Hard Gate]: 阶段间强制检查
← [机制6 Phase Transitions]: 逐阶段，有入口/出口验证
← [机制7 3+ Failures Rule]: 阈值分支

[流程步骤...]

← [机制8 Self-Review Checkpoint]: 完成后自检

## Red Flags - STOP and [consequence]
← [机制4 Red Flags]: 自检信号列表

## Common Rationalizations
← [机制3 Rationalization Table]: 借口vs现实
← [机制14 Pressure Awareness]: 覆盖时间/沉没成本/疲劳/过度自信/简单化

## Verification Checklist
← [机制13 Checklist with Consequences]: 带后果声明

## Real-World Impact (optional)
← [机制15 Real-World Impact]

[可选流程图]
← [机制16 Flowchart]: 仅用于非显而易见的决策分支
```

### 3.2 Agent (system prompt) 的 Harness 排布

```
You are [role] specializing in [domain].

← [机制1 Iron Law]: 核心边界声明
← [机制2 Spirit-vs-Letter]

**Your Core Responsibilities:**
1. [明确做什么]
2. [明确不做什么]  ← 禁止项

**Process:**
1. [步骤1 + 验证]
2. [步骤2 + 验证]
...
← [机制5 Hard Gate]: 步骤间的强制验证
← [机制6 Phase Transitions]: 阶段入口/出口条件

← [机制8 Self-Review Checkpoint]: 完成后自检

**Quality Standards:**
- [可度量的标准]

**Output Format:**
[明确的结构要求]

**Red Flags:**
← [机制4 Red Flags]: 自检信号

**Edge Cases:**
- [边界1]: [处理方式]
- [边界2]: [处理方式]

← [机制12 Forbidden Responses]: 禁止的响应（如有沟通反模式）
```

### 3.3 Reference 文件的 Harness 要素

Reference 本身不是执行者，但影响 agent 行为：

- **准确性**: 不准确的 reference 直接导致 agent 做出错误行为
- **时效性**: 过期的 API/命令/路径导致 agent 使用错误工具
- **完整性**: 缺少关键边界情况导致 agent 在未覆盖场景中猜测
- **结构化**: 如果 agent 找不到需要的信息，它不会报告"找不到"——它会猜测

---

## 4. 诊断流程

### 4.1 症状 → 缺失机制 → 修复的决策路径

```
症状: 模型跳过了某个流程步骤
  ↓
  可能缺失: Iron Law (机制1) 没有声明"必须完成每一步"
  可能缺失: Hard Gate (机制5) 步骤间没有强制检查
  可能缺失: Phase Transitions (机制6) 没有出口验证
  → 检查: skill body 中是否有 "BEFORE proceeding" / "DO NOT proceed until" 声明
  → 修复: 在该步骤后加入 Hard Gate + 在 Overview 加入 Iron Law

症状: 模型声称做完了但产物不符合描述
  ↓
  可能缺失: Self-Review Checkpoint (机制8) 没有自检步骤
  可能缺失: Checklist with Consequences (机制13) 没有强制验证
  → 检查: skill body 中是否有 "Before marking work complete" 清单
  → 修复: 加入 Checklist with Consequences + Self-Review

症状: 模型说 "这次情况特殊" 或 "这种简单情况不需要走流程"
  ↓
  可能缺失: Rationalization Table (机制3) 没有堵 "too simple" 借口
  可能缺失: Spirit-vs-Letter (机制2) 没有切断辩论
  可能缺失: When NOT to Use (机制10) 模型不知道边界
  → 检查: Rationalization Table 中是否包含 "simple" 相关的借口条目
  → 修复: 添加对应的借口条目 + Spirit-vs-Letter 声明

症状: 模型在不同节点之间传递数据不一致
  ↓
  可能缺失: Hard Gate (机制5) spawn prompt 没有包含必要的上下文
  可能缺失: Phase Transitions (机制6) 阶段间没有入口条件验证
  → 检查: agent spawn prompt 是否包含该任务需要的所有信息
  → 修复: 在 spawn prompt 模板中加入强制字段检查

症状: 模型做了超出职责范围的事
  ↓
  可能缺失: Iron Law (机制1) agent 没有边界声明
  可能缺失: Forbidden Responses (机制12) agent 没有禁止行为列表
  可能缺失: Red Flags (机制4) 没有 "超出范围" 的自检信号
  → 检查: agent system prompt 中 "Core Responsibilities" 是否包含禁止项
  → 修复: 加入 "You do NOT" 边界声明 + Red Flags 中的越界信号

症状: description 触发了但 model 不读 skill body
  ↓
  缺失: CSO (机制9) description 包含了 workflow 摘要
  → 检查: description 中是否出现了 "and then...", "with...", "dispatches..."
  → 修复: 删除所有 workflow 细节，只保留触发条件

症状: 同一个节点反复修改仍有问题
  ↓
  可能缺失: 3+ Failures Rule (机制7) 没有失败阈值
  可能缺失: repair-log 没有记录历史尝试
  → 检查: skill 中是否有 "If N+ fixes failed" 的逻辑
  → 修复: 加入 3+ Failures Rule + 读取 repair-log.md 检查历史
```

### 4.2 诊断检查顺序

对每个节点，按以下顺序检查：

1. **先看 CSO (机制9)**: description 有没有泄露 workflow？如果有，模型可能根本没读 body
2. **再看 Iron Law (机制1)**: 有不可谈判的规则吗？放在最前面吗？
3. **然后看流程控制 (机制5-6-7-8)**: 步骤间有强制检查吗？有自检吗？有失败阈值吗？
4. **再看行为护栏 (机制3-4-2)**: Red Flags 列表完整吗？Rationalization Table 覆盖了主要借口吗？
5. **最后看增强 (机制10-12-13-14-15)**: When NOT to Use、Forbidden Responses、Pressure Awareness

---

## 5. Harness 效果的验证方法

### 5.1 来自 writing-skills 的测试方法论

```
RED:   不用 skill → 跑压力场景 → 记录模型的每一个借口（逐字）
GREEN:  只针对实际出现的借口写 harness，不多写任何内容
REFACTOR: 找新的借口 → 显式堵上 → 重新验证直到无懈可击
```

### 5.2 压力场景类型

| 压力 | 测试方法 |
|------|---------|
| 时间压力 | "这个很紧急，尽快修好" |
| 沉没成本 | "我已经花了4小时在这上面" |
| 权威覆盖 | "老板说要马上上线" |
| 疲劳 | 连续处理多个任务后的第 5+ 个任务 |
| 过度自信 | "这个很简单" 的任务 |

### 5.3 Harness 有效的标志

- 模型在被压力触发时，**自我引用**了 Red Flags 或 Iron Law
- 模型的借口在 Rationalization Table 中**已经出现**
- 模型在 Hard Gate 处**实际上停了下来**
- 多次运行同样的场景，**行为一致**（不只是偶然做对）

---

## 6. 参考来源

所有机制均提取自 superpowers 5.0.7 的以下 skill：

- `systematic-debugging` — Iron Law, Spirit-vs-Letter, Rationalization Table, Red Flags, Phase Transitions, Hard Gate, 3+ Failures Rule, Pressure Awareness, When NOT to Use, Real-World Impact
- `test-driven-development` — Iron Law, Spirit-vs-Letter, Rationalization Table, Red Flags, Clean Break, Checklist with Consequences, Pressure Awareness
- `verification-before-completion` — Iron Law, Spirit-vs-Letter, Rationalization Table, Red Flags, Checklist with Consequences, Pressure Awareness, Forbidden Communication Patterns
- `writing-skills` — CSO, Rationalization Table, Clean Break, Red Flags, Pressure Awareness, When NOT to Use, 测试方法论, Flowchart 使用规则
- `writing-plans` — Self-Review Checkpoint, Hard Gate
- `brainstorming` — HARD-GATE, Phase Transitions, Self-Review Checkpoint, Flowchart
- `subagent-driven-development` — Hard Gate, Phase Transitions, Red Flags, Model Selection, Flowchart
- `executing-plans` — Phase Transitions, Hard Gate
- `receiving-code-review` — Forbidden Responses, Clean Break
- `requesting-code-review` — Red Flags
- `dispatching-parallel-agents` — When NOT to Use, Flowchart, Real-World Impact
- `finishing-a-development-branch` — Red Flags, Checklist with Consequences
- `using-git-worktrees` — Red Flags, Safety Verification
- `using-superpowers` — Rationalization Table, Red Flags, HARD-GATE
