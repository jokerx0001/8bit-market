# unity-dev

AI-safe Unity game development plugin for Claude Code.

## Core Idea

Unity has visual editor systems (Scene, Prefab, Animator) that AI cannot safely modify. This plugin enforces a strict separation: **AI handles C# logic, humans own visual assets**.

## Skills

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `plan` | `/unity-dev:plan <task>` or auto-activate | Analyze requirements → documented implementation plan |
| `exec` | `/unity-dev:exec` | Execute plan via TDD: write tests → subagent implements → verify |
| `scaffold-core` | `/unity-dev:scaffold-core` | Generate GameManager + StateMachine + EventBus + Log |
| `scaffold-system` | `/unity-dev:scaffold-system <name>` | Generate a System class template |
| `scaffold-entity` | `/unity-dev:scaffold-entity <name>` | Generate Controller + SO Data + Factory |
| `scaffold-event` | `/unity-dev:scaffold-event <name>` | Generate an Event type |
| `review` | `/unity-dev:review` | Audit C# code against safety principles |

## Usage

```
# Plan a feature
/unity-dev:plan 实现战斗系统

# Execute the plan
/unity-dev:exec

# Generate architecture
/unity-dev:scaffold-core

# Review for safety violations
/unity-dev:review
```

## Architecture

The plugin enforces this safe architecture:

```
/Game
  /Core      → GameManager, GameStateMachine, EventBus, Log
  /Systems   → PlayerSystem, EnemySystem, CombatSystem, etc.
  /Data      → ScriptableObjects (pure data, no logic)
  /Entities  → Controllers + Factories
  /Events    → IGameEvent types for EventBus
```

## Safety Principles

1. AI never touches Scene/Prefab/Animator
2. All logic centralized in code (not Inspector/events/Animator)
3. Single entry-point systems control everything
4. EventBus for all cross-system communication
5. ScriptableObject = data only
6. Factory + Config for entity creation
7. State in one place, other systems read/request only
8. No direct Unity component manipulation
9. Logging + observability built in
10. AI permissions strictly defined

## Installation

```bash
# Local testing
cc --plugin-dir .claude/plugins/unity-dev
```
