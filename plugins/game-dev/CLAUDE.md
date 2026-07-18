# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Claude Code plugin (`game-dev`) that provides autonomous Plan → Exec development workflows for game projects. Supports Ren'Py and Godot through automatic tech-stack detection. Three task types (feat, refactor, fix) through mode-aware state machines, TDD implementation, and boundary checking.

Each workflow uses a different analysis methodology:
- **feat**: brainstorming → design → [resources]
- **refactor**: code analysis → impact assessment → constrained design
- **fix**: behavior clarification → BUG reproduction test → backward tracing → fix plan

## Commands

```bash
# No build step — this is a Claude Code plugin (YAML frontmatter + markdown skills/agents/commands)
ls .claude-plugin/plugin.json && echo "valid"
```

- `/game-dev:start <task> [--auto]` — new feature entry point
- `/game-dev:refactor <target> [--auto]` — refactoring entry point
- `/game-dev:fix <bug description> [--auto]` — bug fix entry point
- `--auto` skips human review checkpoints

## Architecture

The plugin auto-detects the project tech stack by reading CLAUDE.md. Tech-specific configs live in `references/{tech}/`.

### New Feature: `orchestrator`

```
detect tech → create dir → [UI检测] → design-ui → plan → [资源检测] → design-resources → [review] → exec → completed
```

### Refactoring: `refactor-conductor`

```
detect tech → create dir → [UI检测] → design-ui → analyze → impact.md → plan → [review] → exec → completed
```

### Bug Fix: `fix-conductor`

```
detect tech → behavior clarification → test agent BUG test → fix-agent (fix-loop + debug-root-cause) → VERIFY → completed
```

### TDD Loop (exec phase)

Each `[AI-N]` task: RED → GREEN → VERIFY → **boundary check** → REFACTOR → VERIFY

Boundary checks are embedded before REFACTOR (not as a separate review phase). Violations become REFACTOR input.

### Agent Isolation Rules

| Agent | Writes to | Must never touch |
|-------|-----------|-----------------|
| `game-dev:test-agent` | test directory | any source code |
| `game-dev:coding` | source code (not tests) | test files, third-party code |

## File Organization

```
commands/           # Slash command entry points (thin wrappers)
skills/             # Core skill definitions
  orchestrator/     #   Feat workflow state machine (+tech detection)
  refactor-conductor/
  fix-conductor/
  debug-root-cause/ #   Root cause analysis (backward tracing)
  design-ui/        #   UI design phase (tech-aware)
  design-resources/ #   Resource generation (Godot-specific)
  plan/             #   Design phase (tech-aware)
  fix-loop/         #   Fix repair loop
  exec/             #   TDD implementation (tech-agnostic)
  artifact-manager/ #   Shared directory management
  collect-lessons/  #   Experience collection
agents/             # Subagent definitions (test-agent, coding, fix-agent)
references/         # Format contracts + tech-specific knowledge
  renpy/            #   Ren'Py tech stack config + references
    config.md       #     Project detection, test commands, paths
    testing.md      #     testcase/testsuite API reference
    coding.md       #     Ren'Py coding conventions
    ui.md           #     UI principles + HTML translation
    docs.md         #     Doc URLs and query conventions
    html-to-renpy.md
  godot/            #   Godot tech stack config + references
    config.md       #     Project detection, 2D/3D, test commands
    testing.md      #     GUT API reference
    coding.md       #     GDScript + .tscn + .tres conventions
    ui.md           #     Godot Theme/Control principles
    docs.md         #     Godot doc URLs
    design-resources-2d.md
    design-resources-3d.md
    nodes-2d.md     #     2D core node reference
    nodes-3d.md     #     3D core node reference
  plan-format.md    #   plan.md → exec parsing contract
  impact-format.md  #   impact.md → plan constraints contract
  exec-prompts.md   #   Agent spawn prompt templates
  exec-logging.md   #   TDD iteration log format
  lessons-format.md #   Lessons file format
.claude-plugin/     # Plugin manifest (plugin.json)
```

## Output Directory

All design documents and progress tracking go under the tech-specific directory:

```
{dev_dir}/{kind}-{N}/
├── plan.md              # Self-contained design doc (the only file exec reads)
├── progress.json        # Task progress for resume support
├── impact.md            # (refactor only) Modification scope constraints
└── .work/               # Intermediate artifacts
    ├── requirements.md
    ├── architecture.md
    ├── design.md
    ├── tdd-iterations.md
    └── debug-analysis.md  # (fix only) Root cause analysis
```

State tracking is in `{dev_dir}/current-state.json` with independent counters per kind.
