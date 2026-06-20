# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Claude Code plugin (`renpy-dev`) that provides autonomous Plan → Exec → Review development workflows for Ren'Py visual novel projects. It supports three task types (feat, refactor, fix) through mode-aware state machines, TDD implementation, and compliance review.

Each workflow uses a different analysis methodology:
- **feat**: brainstorming → design
- **refactor**: code analysis → impact assessment → constrained design
- **fix**: systematic-debugging → root cause verification → fix plan

## Commands

```bash
# No build step — this is a Claude Code plugin (YAML frontmatter + markdown skills/agents/commands)
# Validate plugin structure
ls .claude-plugin/plugin.json && echo "valid"

# Run tests for a Ren'Py project:
renpy.sh <project> test                  # all tests in global suite
renpy.sh <project> test <testcase_name>  # single testcase
renpy.sh <project> test --report-detailed  # detailed output
```

`RENPY_SDK` env var must point to the Ren'Py SDK executable.

## Architecture

The plugin has **three workflow state machines** for different task types:

### New Feature: `orchestrator` → `plan` → `exec --mode feat` → `review`

```
idle → plan → [human_review] → exec → review → completed
```

### Refactoring: `refactor-conductor` → analyze → `plan` → `exec --mode refactor` → `review`

The refactor workflow has one additional step: **analyze existing code and write `impact.md`** before calling `plan`. The plan skill reads impact.md as hard constraints on scope, exclusions, and existing test protection.

```
analyze → write impact.md → plan (reads impact constraints) → [review] → exec → review
```

### Bug Fix: `fix-conductor` → systematic-debugging → debug-analysis.md → `plan` → `exec --mode fix` → `review`

The fix workflow uses `superpowers:systematic-debugging` instead of brainstorming. Includes a verification gate (up to 3 rounds) to confirm root cause before writing plan.md.

```
systematic-debugging → verify root cause → debug-analysis.md → plan → [review] → exec → review
```

- `/renpy-dev:start <task> [--auto]` — new feature entry point
- `/renpy-dev:refactor <target> [--auto]` — refactoring entry point
- `/renpy-dev:fix <bug description> [--auto]` — bug fix entry point
- `--auto` skips human review checkpoints

### Mode System

Exec accepts `--mode` and `--task-dir` parameters. Conductors pass these explicitly. Manual invocation also supported:

```
/renpy-dev:exec --mode feat --task-dir .renpy-dev/feat-1
/renpy-dev:exec --mode fix --task-dir .renpy-dev/fix-3
```

Exec uses mode to determine which documents subagents should read:

| mode | Documents |
|------|----------|
| feat | plan.md, .work/design.md |
| refactor | plan.md, .work/design.md, impact.md |
| fix | plan.md, .work/debug-analysis.md |

Subagents no longer hardcode document paths — they read the concrete paths from exec's spawn prompt.

### TDD Loop (exec phase)

Each `[AI-N]` task follows a strict RED→GREEN→REFACTOR cycle:

1. **RED**: spawn `renpy-dev:test-agent` to write failing tests using Ren'Py's native `testcase`/`testsuite` framework
2. **GREEN**: spawn `renpy-dev:coding` to write minimal implementation
3. **VERIFY**: run `renpy.sh project test` — **must use actual runtime output**, never infer "should pass" from code reading
4. **REFACTOR**: main session runs `renpy-dev:review` compliance check

### Agent Isolation Rules

| Agent | Writes to | Must never touch |
|-------|-----------|-----------------|
| `renpy-dev:test-agent` | `game/tests/` | any source code in `game/` |
| `renpy-dev:coding` | `game/` (not `tests/`) | `game/tests/`, `game/libs/`, `game/tl/` |

### Progress & Resume

`progress.json` tracks each task's status (`pending` → `in_progress` → `done`). On restart, exec skips completed tasks and resumes from the first non-done task.

## Key Design Rules (from the plugin's internal contracts)

- **plan.md is self-contained**: exec reads ONLY plan.md, never `.work/` intermediate files. plan.md must absorb all key design decisions — no cross-references like "see design.md".
- **Impact analysis is the refactor differentiator**: refactor-conductor writes `impact.md` before calling plan; plan reads it as hard constraints (modification scope, exclusions, existing test protection, risk handling).
- **Test baseline discipline**: never commit screenshot baseline updates in the same commit as source changes. At minimum: `feat: ...` then `chore: baseline update`.
- **New screens must have widget `id` attributes** on interactive elements — this is required for `click id "..."` and `assert id "..."` in tests.
- **Ren'Py SDK** (`RENPY_SDK` env var) is required for running `renpy.sh project test`.

## File Organization

```
commands/           # Slash command entry points (thin wrappers that invoke skills)
skills/             # Core skill definitions (orchestrator, plan, exec, review, refactor-conductor, fix-conductor)
agents/             # Subagent definitions (coding, test-agent)
references/         # Format contracts read by skills at runtime
  plan-format.md    #   plan.md → exec parsing contract
  impact-format.md  #   impact.md → plan constraints contract
  renpy-docs.md     #   Ren'Py doc URLs and query conventions
  renpy-testing.md  #   Ren'Py native testcase/testsuite complete reference
.claude-plugin/     # Plugin manifest (plugin.json)
```

## Output Directory

All design documents and progress tracking go under `.renpy-dev/`:

```
.renpy-dev/{kind}-{N}/
├── plan.md              # Self-contained design doc (the only file exec reads)
├── progress.json        # Task progress for resume support
├── impact.md            # (refactor only) Modification scope constraints
└── .work/               # Intermediate artifacts (not read by exec; for traceability)
    ├── requirements.md
    ├── architecture.md
    ├── design.md
    └── debug-analysis.md  # (fix only) Root cause analysis
```

State tracking across sessions is in `.renpy-dev/current-state.json` with independent counters per kind.
