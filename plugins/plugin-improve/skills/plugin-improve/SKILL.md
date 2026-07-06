---
name: plugin-improve
description: Diagnose and improve Claude Code plugins. Use when the user provides a plugin path and wants to find why its skills/agents aren't behaving correctly, or when the user has execution logs and incorrect outputs from a plugin.
disable-model-invocation: true
argument-hint: <plugin-path> [--chain <chain-name>] [--entry <skill-or-agent-path>] [--log <log-path>] [--artifact <artifact-path>]
allowed-tools: Read, Write, Grep, Glob, Bash, WebFetch
---

# Plugin Improve

Diagnose a plugin by tracing its behavior chain, comparing what each node claims to do against what it actually does, and producing an evidence-based improvement plan.

## Parameters

- `<plugin-path>` (required): Path to the plugin directory
- `--chain <name>`: Name of the chain to analyze (e.g. `fix`, `feat`, `refactor`)
- `--entry <path>`: Entry point within the plugin. If omitted, ask the user
- `--log <path>`: Execution log file showing the plugin's actual behavior
- `--artifact <path>`: Incorrect output the user received

## Workflow

### Phase 1: Identify the Chain

1. If `--entry` is provided, use it as the starting node
2. If only `--chain` is provided, search the plugin for the likely entry:
   - `skills/<chain>-conductor/SKILL.md`
   - `commands/<chain>.md`
   - `skills/<chain>/SKILL.md`
3. If neither is provided, list the plugin's top-level skills and commands, and ask the user which chain/entry to analyze

**Trace downstream nodes** by searching the entry file's content for:
- Explicit skill names (e.g. `skills/xxx/SKILL.md`, `/xxx` references)
- Agent names (e.g. `agents/xxx.md`, `game-dev:xxx`)
- Reference file paths (e.g. `references/xxx.md`)

Build the chain topology as a tree: `entry → skill → skill → agent → reference`.

### Phase 2: Extract Self-Claims

For each node in the chain, extract what it **claims** to do:

**Skill (SKILL.md):**
- What workflow/steps does it describe?
- What outputs does it promise?
- What behavior does its description claim?

**Agent (agents/*.md):**
- What does "Core Responsibilities" say?
- What process steps are defined?
- What output format is specified?
- What boundaries are declared?

**Reference (references/*.md):**
- What knowledge does it claim to provide?
- Is the information verifiable against reality?

### Phase 3: Diagnose Actual Behavior

If `--log` is provided, compare claimed behavior against logged behavior. If `--artifact` is provided, compare claimed outputs against actual outputs.

For each deviation found, classify the problem type and consult the corresponding reference:

- **Harness missing** → `references/harness-methodology.md`
- **Skill structure wrong** → `references/skill-structure.md`
- **Agent structure wrong** → `references/agent-structure.md`
- **Symptom unclear** → `references/diagnosis-guide.md`
- **Reference doesn't cover it** → `references/diagnosis-guide.md` §3.3 for the official docs fallback procedure

For each problem, state:
1. The evidence (what the node claims vs what actually happened)
2. The classification (Harness / Structure / Trigger / Unknown)
3. The specific reference section that defines the correct behavior
4. If no reference covers it, follow the fallback procedure in diagnosis-guide.md §3.3

### Phase 4: Write Diagnosis Report

Write the diagnosis to the target plugin's `.plugin-improve/records/YYYY-MM-DD-<chain>-diagnosis.md`:

```markdown
# [Plugin] - [Chain] Diagnosis Report
## Date: YYYY-MM-DD

### Chain Topology
[Tree from entry to all downstream nodes]

### Node-by-Node Diagnosis

#### Node N: [path/to/file.md]
**Claims:** [what this node says it does]
**Actual:** [what the log/artifact shows]
**Deviations:**
1. [Specific deviation with evidence]

**Classification:**
- [#] [Type] [Severity] — [Description]
  - Evidence: [quote from self-claim vs quote from log/artifact]
  - Reference: [specific section in specific reference file]
  - Fix: [concrete change needed]

### Summary
- Critical: [count]
- Major: [count]
- Minor: [count]
```

### Phase 5: Apply Fixes

1. Read `.plugin-improve/repair-log.md` in the target plugin to understand prior fix attempts
2. Present the fix plan from the diagnosis report
3. Apply fixes one at a time, following these rules:
   - Each fix references its source authority (reference file or official doc URL)
   - After each fix, record what was changed in `repair-log.md`:
     ```markdown
     ### Round N (YYYY-MM-DD)
     - **Node:** [path]
     - **Problem:** [from diagnosis]
     - **Fix:** [what was changed]
     - **Source:** [reference section or URL]
     - **Result:** [pending verification / confirmed / reverted because...]
     ```
   - If a fix fails, do NOT retry more than 3 times on the same node. After 3 attempts, flag it as architectural and escalate
4. After all fixes, update the diagnosis report with a "Fixed: ✅" marker on each resolved item

## Key Rules

- Each diagnosis item MUST cite its source. No "I think this is wrong" — every finding must reference a specific section of a reference file or an official doc URL
- When a reference doesn't cover the issue, fetch the official docs URL. Do not guess at standards
- Read repair-log.md before fixing to avoid repeating failed approaches
- Fix one node completely before moving to the next. Do not batch unrelated fixes
- If 3+ fix attempts on the same node fail, stop and question whether the node's architecture is wrong

## References

Load these as needed during diagnosis:

- **`references/harness-methodology.md`** — 16 harness mechanisms
- **`references/skill-structure.md`** — Skill file structure standards
- **`references/agent-structure.md`** — Agent file structure standards  
- **`references/diagnosis-guide.md`** — Symptom-to-root-cause decision tree + official docs fallback (§3.3)

