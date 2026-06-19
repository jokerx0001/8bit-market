# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Claude Code plugin (`renpy-dev`) that provides an autonomous Plan → Exec → Review development workflow for Ren'Py visual novel projects. It orchestrates design, TDD implementation, and compliance review through a state-machine architecture.

## Commands

```bash
# No build step — this is a Claude Code plugin (YAML frontmatter + markdown skills/agents/commands)
# Validate plugin structure
ls .claude-plugin/plugin.json && echo "valid"

# Run tests for a Ren'Py project that has installed this plugin's test infra:
python tools/test.py                    # all three layers
python tools/test.py structure          # lint + AST checks (< 5s)
python tools/test.py behavior           # headless SDK test_b_* labels (~30s)
python tools/test.py visual             # headless SDK test_v_* labels, screenshot diff (~60s)
python tools/test.py scaffold           # generate test_v_<screen> skeletons
python tools/test.py --update-baselines # regenerate baseline images
python tools/test.py --filter <name>    # filter by test name
```

`RENPY_SDK` env var must point to the Ren'Py SDK executable (defaults checked: Windows/Unix common paths).

## Architecture

The plugin has **two workflow state machines** for different task types:

### New Feature: `orchestrator` → `plan` → `exec` → `review`

```
idle → plan → [human_review] → exec → review → completed
```

### Refactoring: `refactor-conductor` → analyze → `plan` → `exec` → `review`

The refactor workflow has one additional step: **analyze existing code and write `impact.md`** before calling `plan`. The plan skill reads impact.md as hard constraints on scope, exclusions, and existing test protection.

```
analyze → write impact.md → plan (reads impact constraints) → [review] → exec → review
```

- `/renpy-dev:start <task> [--auto]` — new feature entry point
- `/renpy-dev:refactor <target> [--auto]` — refactoring entry point
- `--auto` skips human review checkpoints

### TDD Loop (exec phase)

Each `[AI-N]` task follows a strict RED→GREEN→REFACTOR cycle:

1. **RED**: spawn `renpy-dev:test-agent` to write failing tests
2. **GREEN**: spawn `renpy-dev:coding` to write minimal implementation
3. **VERIFY**: run `python tools/test.py` and read `.last_results.json` — **must use actual runtime output**, never infer "should pass" from code reading
4. **REFACTOR**: main session runs `renpy-dev:review` compliance check

### Agent Isolation Rules

| Agent | Writes to | Must never touch |
|-------|-----------|-----------------|
| `renpy-dev:test-agent` | `game/tests/` | any source code |
| `renpy-dev:coding` | `game/` (not `tests/`) | `game/tests/`, `game/libs/`, `game/tl/` |

### Progress & Resume

`progress.json` tracks each task's status (`pending` → `in_progress` → `done`). On restart, exec skips completed tasks and resumes from the first non-done task.

## Key Design Rules (from the plugin's internal contracts)

- **plan.md is self-contained**: exec reads ONLY plan.md, never `.work/` intermediate files. plan.md must absorb all key design decisions — no cross-references like "see design.md".
- **Impact analysis is the refactor differentiator**: refactor-conductor writes `impact.md` before calling plan; plan reads it as hard constraints (modification scope, exclusions, existing test protection, risk handling).
- **Test baseline discipline**: never commit baseline updates in the same commit as source changes. At minimum: `feat: ...` then `chore: baseline update`.
- **OWN_MANIFEST.json** is the single source of truth for what code we own — the test runner only scans what's listed there.
- **New screens must have widget `id` attributes** on interactive elements — this is required for Layer 3 visual tests.
- **`config.test=True`** gates all test code from release builds (via `_guard.rpy` at init offset=-100).

## File Organization

```
commands/           # Slash command entry points (thin wrappers that invoke skills)
skills/             # Core skill definitions (orchestrator, plan, exec, review, test, refactor-conductor)
agents/             # Subagent definitions (coding, test-agent)
references/         # Format contracts read by skills at runtime
  plan-format.md    #   plan.md → exec parsing contract
  impact-format.md  #   impact.md → plan constraints contract
  renpy-docs.md     #   Ren'Py doc URLs and query conventions
assets/test-infra/  # Three-layer test framework installed into Ren'Py projects
.claude-plugin/     # Plugin manifest (plugin.json)
```

## Output Directory

All design documents and progress tracking go under `.renpy-dev/`:

```
.renpy-dev/{kind}-{N}/
├── plan.md           # Self-contained design doc (the only file exec reads)
├── progress.json     # Task progress for resume support
└── .work/            # Intermediate artifacts (not read by exec; for traceability)
    ├── requirements.md
    ├── architecture.md
    ├── design.md
    └── (refactor-only: impact.md)
```

State tracking across sessions is in `.renpy-dev/current-state.json`.
