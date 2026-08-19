# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Overview

This is a Claude Code plugin (`web2-dev`) that orchestrates the complete web service development lifecycle — from requirements to deployment with TDD, integration tests, and infrastructure management.

## Commands

| Command | Purpose |
|---------|---------|
| `/web2-dev:new` | New project — project-level requirements + architecture |
| `/web2-dev:feat` | New feature — module-level requirements + architecture |
| `/web2-dev:refactor` | Refactoring — analyze → impact → change plan → TDD refactor |
| `/web2-dev:fix` | Bug fix — behavior clarification → reproduction test → fix → verify |

All commands support `--auto` to skip human review checkpoints.

## Architecture

### Design Philosophy

- **Environment as first-class**: Infrastructure + dev server managed by professional ops skills
- **Security-first**: All operations use limited-privilege accounts. Super-admin commands output-only.
- **TDD rebuilt**: No useless tests — only test methods with real logic. Compliance checks validate test quality.
- **Integration tests mandatory**: Backend API tests + Frontend Playwright E2E
- **Minimal agents**: Agents only define role + tools + constraints. All process logic lives in skills.

### Agent Isolation

| Agent | Spawned by | Can touch | Must never touch |
|-------|-----------|-----------|-----------------|
| `coding` | exec, orchestrator | source code, integration test scripts | N/A |
| `ops` | exec | infrastructure (via Ansible), service deployment | N/A (super-admin commands output-only) |

### Key Differences from game-dev

web2-dev is NOT game-dev adapted for web. It's a ground-up redesign:

- No separate test-agent — coding agent calls tdd skill for both test writing and implementation
- No concept-art / asset-extract / ui-restoration — web doesn't need these
- No multi-engine tech detection — web is web
- plan.md is task decomposition, not design doc
- exec contains ALL implementation steps (TDD → integration test → deploy → E2E)
- code-review is mandatory after each task (design consistency + test coverage)

### Workflow

```
new/feat:
  stack-detect → grill → requirements → architecture(merged domain model)
  → design(by module) → [frontend-design] → [设计审查] → plan(task decomposition)
  → [review] → exec

refactor:
  stack-detect → grill → analyze → impact.md → architecture + design
  → plan → [review] → exec

fix:
  stack-detect → behavior clarification → requirements.md
  → spawn coding agent (reproduce + fix) → code-review
```

### Exec Structure

```
exec:
  spawn ops agent → infrastructure (infra-ops)

  For each task in plan.md (serial):
    spawn coding agent (TDD via tdd skill)
    → main agent code-review (design consistency + test coverage)
    → fail? spawn coding agent fix all → re-review

  After all tasks:
    spawn coding agent → backend integration test (local + self-repair)
    spawn ops agent → deploy backend (service-ops)
    spawn coding agent → backend integration test (deployed + self-repair)
    spawn coding agent → frontend development (logic TDD + UI coding)
    spawn coding agent → frontend E2E (self-repair)
    main agent code-review (frontend)
    spawn ops agent → deploy frontend (service-ops)
    spawn coding agent → frontend E2E (deployed + self-repair)
```

## File Organization

```
commands/               # Entry points (thin wrappers)
skills/                 # Core process logic
  new-orchestrator/     #   New project state machine
  feat-orchestrator/    #   Feature state machine
  refactor-orchestrator/#   Refactoring state machine
  fix-orchestrator/     #   Bug fix state machine
  plan/                 #   Task decomposition
  requirements/         #   Requirements management
  architecture/         #   Architecture design (merged domain model)
  design/               #   Detailed design (by module: DB + API + interactions)
  exec/                 #   Implementation (TDD → test → deploy → E2E)
  code-review/          #   Design consistency + test coverage check
  infra-ops/            #   Infrastructure ops (Ansible)
  service-ops/          #   Service deployment
  backend-integration-test/  #   API integration test + self-repair
  frontend-e2e-test/    #   Playwright E2E + self-repair
  artifact-manager/     #   Directory management
  stack-detector/       #   Tech stack detection
agents/                 # Minimal agent definitions
references/             # Tech stack rules + ops patterns
  rules/                #   Language-specific rules (inherited from neonbit-vibe-factory)
  ops/                  #   Ansible patterns, security specs
  web/                  #   Testing patterns, plan format
  config.md             #   dev_dir and project structure
```

## Output Directory

```
{dev_dir}/{kind}-{N}/
├── plan.md              # Task list (the only file exec reads)
├── progress.json        # Exec progress for resume
└── .work/               # Intermediate artifacts
    ├── requirements.md
    ├── architecture.md
    ├── design.md
    ├── layouts/         # Frontend design mockups
    ├── integration/     # Backend integration test scripts
    ├── e2e/             # Frontend E2E test scripts
    └── fix-attempts.md  # Integration/E2E failure experience (per-case sections)
```

## Key Constraints

- **No production code without TDD** — coding agent calls tdd skill for RED→GREEN
- **No test-only agent** — coding agent owns both test writing and implementation
- **Plan.md is task decomposition** — not a design document
- **Code review is mandatory** — design consistency + test coverage for every module
- **Integration tests are mandatory** — backend API + frontend E2E, both with self-repair
- **Ops is Ansible-first** — no bare commands for infrastructure
- **Super-admin commands output-only** — AI outputs, human executes, AI continues
