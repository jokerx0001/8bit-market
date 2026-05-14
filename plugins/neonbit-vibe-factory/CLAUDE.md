# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **Claude Code plugin** (`neonbit-vibe-factory`) that orchestrates the complete development lifecycle from requirements to E2E testing using a multi-agent TDD approach.

## Plugin Commands

- `/neonbit-vibe-start <task>` — Start a new feature development workflow (full: requirements → architecture → design → TDD)
- `/neonbit-vibe-refactor <target> [constraints]` — Start a refactoring/modification workflow (lightweight: analyze → impact → plan → TDD refactor)
- `/neonbit-vibe-tdd <module> <target>` — Direct TDD entry point (skip all design phases)

## Rules Injection

每个命令入口在创建任务目录后会调用 `stack-detector` skill 检测语言/框架，写入 `<task_dir>/stack.json` 和 `<task_dir>/routing-table.md`。conductor 派发 agent 时把对应 rule 的绝对路径注入 prompt 的"必读编程规范"段。详见 `README.md#Rules 注入机制`。

## Architecture

### Multi-Agent TDD Flow

```
新功能 (/neonbit-vibe-start → orchestrator → tdd-conductor)
    ├── spawn test agent ──→ RED (写失败测试)
    ├── spawn coding agent ──→ GREEN (实现功能)
    └── 主会话 ──→ REFACTOR (审查)

重构改造 (/neonbit-vibe-refactor → refactor-conductor)
    ├── 分析现有代码 → 影响评估 → 变更计划(审批)
    ├── spawn test agent ──→ RED (写验证目标行为的测试)
    ├── spawn coding agent ──→ GREEN (修改现有代码)
    └── 主会话 ──→ REFACTOR (审查)
```

### Key Components

| Component | Type | Location | Purpose |
|-----------|------|----------|---------|
| `orchestrator` | skill | `skills/orchestrator/` | Workflow state machine - manages phases from requirements to E2E |
| `tdd-conductor` | skill | `skills/tdd-conductor/` | TDD coordinator - orchestrates RED→GREEN→REFACTOR for new features |
| `refactor-conductor` | skill | `skills/refactor-conductor/` | Refactor coordinator - analyze→impact→plan→TDD refactor for existing code |
| `test` | agent | `agents/test/` | Writes failing tests (RED phase) |
| `coding` | agent | `agents/coding/` | Implements features (GREEN phase) |
| `e2e-test` | agent | `agents/e2e-test/` | Playwright E2E tests |

### Workflow Phases

New feature (`/neonbit-vibe-start`):
```
requirements → architecture → detailed_design → api_design →
plan_approved → backend_development (TDD) → frontend_development → e2e_testing → completed
```

Refactoring (`/neonbit-vibe-refactor`):
```
analyze → impact_assessment → change_plan (approval) → TDD refactor loop → completed
```

## TDD Workflow

### RED phase (test agent)
1. Write failing unit test (Mockito) or integration test (@SpringBootTest + MockMvc)
2. Tests must fail because feature is not implemented

### GREEN phase (coding agent)
1. Implement minimal code to make tests pass
2. **Never modify test code**

### REFACTOR phase (main session)
1. Review code quality against design documents
2. Ensure no stub code or fake implementations

## Artifact Storage

All design documents stored in `.neonbit-vibe-factory/<kind>-{N}/` where `<kind>` is one of `feat`/`refactor`/`tdd`. Each kind's counter is independent.
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