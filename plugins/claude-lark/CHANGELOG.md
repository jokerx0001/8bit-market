# Changelog

## v1.0.0 (2026-03-15)

Initial release.

### Features

- Zero-dependency hook script (Python stdlib only)
- Rich Lark interactive cards with project, device, stats
- Checkpoint-based turn-level statistics (tokens, tools, duration)
- Sub-agent tracking and display
- Git info: branch, last commit, dirty status
- Markdown → Lark-compatible conversion (headings, tables, code blocks, lists)
- Sub-agent detection via worktree path
- Token caching (2h TTL)
- Event filtering via config
- Interactive installer with phone/email Open ID lookup
- Uninstaller

### Notification Types

- **Stop** (turquoise) — task completion
- **Notification** (orange/yellow/blue) — permission prompt, idle, auth
- **Sub-agent** (blue) — worktree/swarm agent completion
