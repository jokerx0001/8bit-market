# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **Claude Code plugin** (`neonbit-vibe-factory`) that orchestrates the complete development lifecycle from requirements to E2E testing using a multi-agent TDD approach.

## Plugin Commands

- `/neonbit-vibe-start <task>` — Start a new development workflow (e.g., `/neonbit-vibe-start 开发一个用户管理模块`)

## Architecture

### Multi-Agent TDD Flow

```
conductor (主协调器)
    ├── test agent ──→ RED (写失败测试)
    ├── coding agent ──→ GREEN (实现功能)
    └── conductor ──→ REFACTOR (审查)
```

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `orchestrator` skill | `skills/orchestrator/` | Workflow state machine - manages phases from requirements to E2E |
| `conductor` agent | `agents/conductor/` | TDD导演 - coordinates RED→GREEN→REFACTOR cycles |
| `test` agent | `agents/test/` | Writes failing tests (RED phase) |
| `coding` agent | `agents/coding/` | Implements features (GREEN phase) |
| `e2e-test` agent | `agents/e2e-test/` | Playwright E2E tests |

### Workflow Phases

```
requirements → architecture → detailed_design → api_design →
plan_approved → backend_development (TDD) → frontend_development → e2e_testing → completed
```

## TDD Workflow

### RED phase (test agent)
1. Write failing unit test (Mockito) or integration test (@SpringBootTest + MockMvc)
2. Tests must fail because feature is not implemented

### GREEN phase (coding agent)
1. Implement minimal code to make tests pass
2. **Never modify test code**

### REFACTOR phase (conductor)
1. Review code quality against design documents
2. Ensure no stub code or fake implementations

## Artifact Storage

All design documents stored in `.neonbit-vibe-factory/feat-{N}/`:
- `requirements.md` — Requirements summary
- `architecture.md` — Architecture design (Mermaid diagrams)
- `design.md` — Detailed design
- `database.sql` — Database design
- `openapi.yaml` — API documentation (OpenAPI 3.0.3)
- `plan.md` — Execution plan (requires user approval before development)

## Key Constraints

- **Test-first**: No production code without a failing test
- **No test modification**: coding agent must not modify tests
- **Design documents are source of truth**: Ignore prior discussions if they conflict with documents
- **No stub/fake code**: All implementations must have actual logic paths