---
name: unity-dev:artifact-manager
description: |
  This skill should be used to manage design documents under .unity-dev/. Trigger when the plan or exec skill needs to create task directories, save documents, update state, or query current workflow status. Not user-facing — invoked internally by other unity-dev skills via "调用 unity-dev:artifact-manager" with structured parameters.
---

# Unity Dev — Artifact Manager

Manage all design documents and state under `.unity-dev/` at the project root. Called by `unity-dev:plan` and `unity-dev:exec` skills to create task directories, save/load documents, and maintain workflow state.

## Directory Structure

```
.unity-dev/                      ← project root
├── current-state.json           ← global state (current task, phase, counters)
└── feat-{N}/                    ← task directory (auto-incrementing)
    └── plan.md                  ← implementation plan
```

## Core Operations

This skill supports the following operations, invoked with structured parameters:

| Operation | Parameters | Purpose |
|-----------|------------|---------|
| `create_task` | `kind` (always "feat") | Create `feat-{N}` directory, increment counter, write state |
| `save_document` | `task`, `doc_type`, `content` | Write a document to `.unity-dev/{task}/{doc_type}.md` |
| `update_state` | `phase` | Transition to next phase (validates phase order) |
| `get_state` | (none) | Read and return current state from `current-state.json` |
| `get_active_plan` | (none) | Return path to approved plan, or null if none approved |
| `list_tasks` | (none) | List all feat directories with their phases |

### Operation Details

### 1. create_task
```
调用 unity-dev:artifact-manager：
- 操作: create_task
- kind: feat
```

Execute:
1. Read `.unity-dev/current-state.json`; if absent, initialize with defaults:
   ```json
   {"current_task": null, "phase": null, "phases_completed": [], "counters": {"feat": 0}}
   ```
2. Increment `counters.feat` → N
3. `mkdir -p .unity-dev/feat-{N}`
4. Update state: `current_task = "feat-{N}"`, `phase = "initialized"`, touch `started_at` and `last_updated`
5. Write `current-state.json`

Output:
```
Created: .unity-dev/feat-{N}/
Phase: initialized
```

Only "feat" kind is supported. Other kinds return an error.

### 2. save_document
```
调用 unity-dev:artifact-manager：
- 操作: save_document
- task: feat-1
- doc_type: plan
- content: <document content in markdown>
```

Execute:
1. Verify `.unity-dev/{task}/` exists
2. Write content to `.unity-dev/{task}/{doc_type}.md` (overwrite if exists)
3. Update `last_updated` in state

Output:
```
Saved: .unity-dev/feat-1/plan.md
```

Supported doc_types: `plan`. Additional types may be added in future phases.

### 3. update_state
```
调用 unity-dev:artifact-manager：
- 操作: update_state
- phase: plan_approved
```

Execute:
1. Read current state
2. Validate transition:

| Current Phase | Allowed Next |
|---------------|-------------|
| `initialized` | `plan_generated` |
| `plan_generated` | `plan_approved` |
| `plan_approved` | `execution_complete` |

3. If invalid transition, reject with error listing valid next phases
4. Append completed phase to `phases_completed`, set new `phase`, update `last_updated`
5. Write state

Output:
```
Phase updated: plan_generated → plan_approved
```

The `plan_generated` → `plan_approved` transition is the approval gate. Only `unity-dev:plan` may execute this transition after user confirmation.

### 4. get_state
```
调用 unity-dev:artifact-manager：
- 操作: get_state
```

Output: Parsed `current-state.json`, or default initialized state if file does not exist.

Use `cat .unity-dev/current-state.json` and `jq` for parsing if available, otherwise read file and extract fields.

### 5. get_active_plan
```
调用 unity-dev:artifact-manager：
- 操作: get_active_plan
```

Execute:
1. Get state via `get_state`
2. If `phase == "plan_approved"` and `current_task` is set:
   - Return `.unity-dev/{current_task}/plan.md`
3. Otherwise return `null` with reason

Output (approved plan exists):
```
Active plan: .unity-dev/feat-1/plan.md
```

Output (no approved plan):
```
No approved plan. Current phase: plan_generated. Run /unity-dev:plan and approve the plan first.
```

### 6. list_tasks
```
调用 unity-dev:artifact-manager：
- 操作: list_tasks
```

Execute:
1. `ls -d .unity-dev/feat-* 2>/dev/null` or find all feat directories
2. For each, read state to get phase
3. Output formatted list

Output:
```
feat-1/  phase: plan_approved
feat-2/  phase: plan_generated
```

## State File Schema

```json
{
  "current_task": "feat-1",
  "phase": "plan_approved",
  "phases_completed": ["plan_generated"],
  "counters": {
    "feat": 1
  },
  "started_at": "2026-06-13T10:00:00Z",
  "last_updated": "2026-06-13T10:05:00Z"
}
```

**Fields:**
- `current_task`: Active task directory name (e.g., `"feat-1"`)
- `phase`: Current phase in the workflow state machine
- `phases_completed`: Ordered list of completed phase names
- `counters.feat`: Auto-increment counter for task numbering
- `started_at`: ISO 8601 timestamp of task creation
- `last_updated`: ISO 8601 timestamp of last state mutation

## Phase State Machine

```
initialized → plan_generated → plan_approved → execution_complete
```

- `initialized`: Task directory created, no documents yet
- `plan_generated`: Plan document saved, awaiting user approval
- `plan_approved`: User approved the plan, ready for execution
- `execution_complete`: All AI tasks executed

## Validation Rules

### When Reading State

If `.unity-dev/current-state.json` does not exist, return a default initialized state:
```json
{
  "current_task": null,
  "phase": null,
  "phases_completed": [],
  "counters": {"feat": 0}
}
```

### When Creating Tasks

- `counters.feat` must be a non-negative integer; initialize to 0 if absent
- New counter value must be `current + 1`
- Task directory must not already exist; if it does, increment counter again

### When Updating State

- Validate phase transition is forward-only (no skipping phases)
- If transition is invalid, reject with message listing allowed next phases
- Always append the previous phase to `phases_completed` before setting new phase

### When Saving Documents

- `kind` directory must exist (created by `create_task`)
- `doc_type` must be one of: `plan`
- Content must be non-empty; reject empty content

## Constraints

1. **Never delete documents** — preserve all generated plans for reference
2. **Single active task** — `current_task` always points to the most recently created or modified task
3. **Forward-only state** — phase transitions cannot go backward
4. **Idempotent counter** — multiple `create_task` calls create incrementing directories, never overwrite

## Usage in Other Skills

### Called by plan skill:
```
Step 7: create_task → Step 8: save_document → update_state(plan_generated)
          ↓
      User confirms
          ↓
      update_state(plan_approved)
```

### Called by exec skill:
```
Step 1: get_active_plan → load plan → execute tasks → update_state(execution_complete)
```
