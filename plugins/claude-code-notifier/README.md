# Claude Code Notifier

Send Feishu notifications when Claude Code stops waiting for input, and reply directly from Feishu to continue the conversation.

## Features

- Feishu card notifications for permission requests, user questions, and task failures
- Color-coded cards (red = permission, blue = question, orange = failure)
- Reply directly from Feishu — replies are routed back to Claude Code via named pipe
- No public server needed — uses Feishu's WebSocket long connection (outbound only)
- WSL compatible

## Prerequisites

- Python 3.6+
- Node.js (for config loading)
- Feishu Bot with:
  - App ID and App Secret
  - A webhook URL (incoming webhook bot)
  - `im:message:receive_v1` event subscription enabled

Install Python dependency:
```bash
pip install websocket-client
```

## Installation

Install from plugin marketplace or via local path. After installation, configure your Feishu credentials (see below).

## Configuration

**IMPORTANT**: Do NOT edit the plugin's own `config.js` — it would be overwritten on plugin update.

Create your config file at one of these locations (priority order):

1. **Global** (recommended): `~/.claude/claude-code-notifier/config.js`
2. **Project**: `./.claude/claude-code-notifier/config.js`

Copy the template from the plugin's `config.js` and fill in your credentials:

```bash
mkdir -p ~/.claude/claude-code-notifier
cp /path/to/plugin/config.js ~/.claude/claude-code-notifier/config.js
# Then edit ~/.claude/claude-code-notifier/config.js
```

Config template:

| Field | Description |
|-------|-------------|
| `feishu.appId` | Your Feishu app ID (required for replies) |
| `feishu.appSecret` | Your Feishu app secret (required for replies) |
| `feishu.webhookUrl` | Incoming webhook URL for sending notifications |
| `feishu.chatId` | Specific chat ID (empty = webhook default) |
| `notification.onAskUserQuestion` | Notify when Claude asks a question |
| `notification.onPermissionRequest` | Notify when Claude needs permission |
| `notification.onTaskComplete` | Notify on task completion |
| `notification.onTaskFail` | Notify on task failure |
| `pipePath` | Named pipe path for IPC |

## How It Works

```
Claude Code stops → Stop Hook fires → Send Feishu card notification
                                     → Start WebSocket listener daemon
                                     → User replies in Feishu
                                     → WebSocket receives reply
                                     → Reply written to named pipe
                                     → Claude Code reads from pipe
```

## Getting Feishu Credentials

1. Go to [Feishu Open Platform](https://open.feishu.cn/app)
2. Create a new app or use an existing one
3. Under "Credentials & Basic Info", copy App ID and App Secret
4. Add an "Incoming Webhook" bot to get a webhook URL
5. Enable `im:message:receive_v1` event subscription for receiving replies

## Limitations

- Named pipe input to Claude Code requires verification (see design doc)
- Session routing for multiple concurrent Claude Code sessions is not yet implemented
- WebSocket long connection requires `websocket-client` Python package

## License

MIT
