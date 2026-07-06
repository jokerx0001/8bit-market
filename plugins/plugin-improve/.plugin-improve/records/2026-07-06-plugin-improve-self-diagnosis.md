# Plugin Improve - Self Diagnosis Report
## Date: 2026-07-06

### Chain Topology

```
skills/plugin-improve/SKILL.md (entry, single node)
  ├── references/harness-methodology.md
  ├── references/skill-structure.md
  ├── references/agent-structure.md
  └── references/diagnosis-guide.md
```

Single-node plugin. No agents, no sub-skills. All problems concentrate in SKILL.md.

### Node-by-Node Diagnosis

#### Node 1: skills/plugin-improve/SKILL.md

**Claims:**
- Phase 1: Identify the Chain — search plugin for entry point, trace downstream nodes, build topology tree
- Phase 2: Extract Self-Claims — for each node, read the file and extract what it claims to do
- Phase 3: Diagnose Actual Behavior — compare claims against log/artifact, classify each deviation
- Phase 4: Write Diagnosis Report — write structured report to `.plugin-improve/records/`
- Phase 5: Apply Fixes — read repair-log.md first, apply fixes one at a time, record each fix
- Key Rules: cite source for every finding, read repair-log before fixing, 3+ failures = question architecture

**Actual:** (from user report of execution)
- Did NOT read target plugin's artifacts
- When reminded to read, still did NOT read artifact details
- plan.md had obvious issues that were completely unexamined
- Multiple phases were skipped — the "analyze artifacts" step never actually happened
- The "compare what claims vs what actual" comparison was done from memory/assumptions, not from reading files

**Deviations:**
1. Phase 1 "Identify the Chain" → partially done (topology identified) but no deep reading of downstream nodes
2. Phase 2 "Extract Self-Claims" → SKIPPED — never read actual node files to extract claims
3. Phase 3 "Diagnose Actual Behavior" → SKIPPED — never compared claims against actual artifacts
4. Phase 4 "Write Diagnosis Report" → produced output without evidence (hallucinated diagnosis)
5. Phase 5 "Apply Fixes" → never reached because prior phases were broken

### Classification

#### [CRITICAL] Missing Iron Law (harness-methodology.md §机制1)

- **Evidence:** SKILL.md has no ALL CAPS non-negotiable rule. The Overview is a one-line description. No statement equivalent to "NO DIAGNOSIS WITHOUT READING ARTIFACTS FIRST."
- **Reference:** harness-methodology.md §机制1 — "一条 ALL CAPS 的、不可谈判的规则，放在 skill/agent 最前面"
- **Fix:** Add Iron Law: `NO DIAGNOSIS WITHOUT READING THE ACTUAL ARTIFACT FILES FIRST`. Place at top of Overview.

#### [CRITICAL] Missing Rationalization Table (harness-methodology.md §机制3)

- **Evidence:** No `| Excuse | Reality |` table exists. The user's exact complaint ("完全不读产物，提醒要读又不去读细节") matches the rationalization pattern: model convinces itself "I already know what's in the artifact" or "the summary is enough."
- **Reference:** harness-methodology.md §机制3 — 必须显式堵死每一个模型会用的借口
- **Fix:** Add Rationalization Table covering: "I already know what's there", "The summary is enough", "I can infer from the chain topology", "This is obvious, I don't need to read", "I'll read it later"

#### [CRITICAL] Missing Hard Gates between phases (harness-methodology.md §机制5)

- **Evidence:** The 5 phases are listed as `### Phase 1`, `### Phase 2` etc., but there are zero "BEFORE proceeding to Phase N" or "DO NOT proceed until" declarations. The model can flow from Phase 1 directly to Phase 4 without completing Phases 2-3.
- **Reference:** harness-methodology.md §机制5 — "DO NOT proceed until X"
- **Fix:** Add Hard Gate after each phase: "**BEFORE proceeding to Phase N+1:** verify [conditions]. If ANY condition not met: DO NOT proceed. Return to Phase N."

#### [CRITICAL] Missing Phase Transitions (harness-methodology.md §机制6)

- **Evidence:** Each phase has no Entry condition, no Goal, no Exit verification. Phase 4's template even has placeholders like "[Tree from entry to all downstream nodes]" showing it was never fully specified.
- **Reference:** harness-methodology.md §机制6 — 每个阶段需要入口条件、执行步骤、出口验证
- **Fix:** Restructure each phase with Entry condition, Goal, Actions, Exit verification, → Next transition.

#### [MAJOR] Missing Red Flags list (harness-methodology.md §机制4)

- **Evidence:** No "Red Flags - STOP" section. Model cannot self-detect when it's skipping steps.
- **Reference:** harness-methodology.md §机制4 — Red Flags 列表 + 必须包含 "This is different because..."
- **Fix:** Add Red Flags section with entries like: "I already understand the plugin structure", "This is obvious, no need to read every file", "I'll check the details later", "The summary from the user is enough"

#### [MAJOR] Missing Self-Review Checkpoint (harness-methodology.md §机制8)

- **Evidence:** No "Before marking work complete" review step. Model can claim "diagnosis complete" without verifying it actually read the artifacts.
- **Reference:** harness-methodology.md §机制8 — 流程最后一步的自检点
- **Fix:** Add Self-Review step before writing diagnosis: verify each claim is backed by a file read, verify each deviation cites a specific line/section from the artifact.

#### [MAJOR] Missing Checklist with Consequences (harness-methodology.md §机制13)

- **Evidence:** No verification checklist. "Key Rules" section has rules but no consequence for violating them.
- **Reference:** harness-methodology.md §机制13 — 带后果声明的检查清单
- **Fix:** Add "Verification Checklist" with consequence: "Can't check all boxes? You skipped diagnosis. Start over from Phase 1."

#### [MAJOR] Missing Spirit-vs-Letter declaration (harness-methodology.md §机制2)

- **Evidence:** No statement cutting off the "I understand the spirit so I can be flexible" escape.
- **Reference:** harness-methodology.md §机制2
- **Fix:** Add: "**Violating the letter of any phase is violating the spirit of plugin improvement.**"

#### [MAJOR] CSO violation in description (harness-methodology.md §机制9)

- **Evidence:** Description contains: "tracing its behavior chain, comparing what each node claims to do against what it actually does, and producing an evidence-based improvement plan" — this is a workflow summary, not just trigger conditions.
- **Reference:** harness-methodology.md §机制9 — description 只写触发条件，不写 workflow 摘要
- **Fix:** Rewrite description to trigger conditions only: "Use when the user asks to improve, diagnose, or fix a Claude Code plugin. Also use when plugin behavior is incorrect, a skill/agent produces wrong output, or the user provides plugin execution logs and artifacts for analysis."

#### [MINOR] Missing When NOT to Use (harness-methodology.md §机制10)

- **Evidence:** No explicit exclusion criteria.
- **Reference:** harness-methodology.md §机制10
- **Fix:** Add "When NOT to Use" section: don't use for creating new plugins, don't use for general code review.

#### [MINOR] Missing Pressure Awareness (harness-methodology.md §机制14)

- **Evidence:** Rationalization Table (when added) should cover all pressure dimensions: time pressure, sunk cost, overconfidence, simplicity bias.
- **Reference:** harness-methodology.md §机制14
- **Fix:** Ensure Rationalization Table covers: "Emergency/urgent", "I've already spent time on this", "This is simple", "I'm confident I know the answer"

### Summary

- **Critical:** 4 (Iron Law, Rationalization Table, Hard Gates, Phase Transitions) — Fixed: ✅
- **Major:** 5 (Red Flags, Self-Review, Checklist w/ Consequences, Spirit-vs-Letter, CSO violation) — Fixed: ✅
- **Minor:** 2 (When NOT to Use, Pressure Awareness) — Fixed: ✅

### Fix Applied: 2026-07-06 Round 1

Complete restructure of SKILL.md with all 11 missing harness mechanisms. See repair-log.md for details.
