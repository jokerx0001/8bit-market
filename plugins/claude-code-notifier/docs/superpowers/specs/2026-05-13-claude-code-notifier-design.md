# Claude Code Notifier Plugin - Design Spec

**Date**: 2026-05-13
**Author**: Claude Code + User
**Status**: Draft

## 1. Overview

**Purpose**: Notify user via Feishu when Claude Code stops waiting for input, and allow user to reply directly from Feishu to continue the conversation.

**Core Flow**:
```
Claude Code stops → Hook detects → Send Feishu notification (card format)
                                 → Start Feishu WebSocket listener for replies
                                 → User replies in Feishu
                                 → Message received via WebSocket
                                 → Write to named pipe → Claude Code reads pipe
```

## 2. Architecture

### 2.1 Components

| Component | Responsibility |
|-----------|---------------|
| `hooks/stop.py` | Hook entry point - detects Claude Code stop events |
| `feishu_sender.py` | Sends notification cards to Feishu via Webhook |
| `feishu_ws_client.py` | Maintains WebSocket connection to Feishu, receives user replies |
| `pipe_writer.py` | Writes user replies to named pipe for Claude Code |
| `config.js` | User configuration (App ID, App Secret, Webhook URL, notification rules) |

### 2.2 File Structure

```
8bit-market/plugins/claude-code-notifier/
├── .claude-plugin/
│   └── plugin.json
├── hooks/
│   └── stop.py              # Stop hook - main entry point
├── lib/
│   ├── feishu_sender.py      # Feishu Webhook notifications
│   ├── feishu_ws_client.py   # Feishu WebSocket client for receiving messages
│   ├── pipe_writer.py       # Named pipe writer
│   └── config_loader.py     # Loads config.js
├── config.js                # USER CONFIGURATION FILE (edit here)
├── README.md
└── LICENSE
```

### 2.3 Configuration Schema (config.js)

```javascript
module.exports = {
  feishu: {
    // Required for both sending notifications and receiving replies
    appId: 'cli_xxxxxxxxxx',           // Replace with your Feishu App ID
    appSecret: 'xxxxxxxxxxxxxxxx',       // Replace with your Feishu App Secret
    webhookUrl: 'https://open.feishu.cn/...',  // Webhook URL for notifications

    // Optional: Custom notification channel
    chatId: '',  // Specific chat ID to send notifications to (empty = bot DM)
  },

  notification: {
    // What events trigger notifications
    onAskUserQuestion: true,     // Claude asks user a question
    onPermissionRequest: true,   // Permission confirmations (delete, git push --force, etc.)
    onTaskComplete: false,       // Task completion (usually not needed)
    onTaskFail: true,            // Task failures
  },

  // Advanced
  pipePath: '/tmp/claude-code-notifier/pipe',  // Named pipe location
}
```

## 3. Feishu Integration Details

### 3.1 Sending Notifications (Webhook)

- Use Feishu Webhook API to send Interactive Cards
- Card format varies by event type (color-coded borders)

### 3.2 Receiving Replies (WebSocket Long Connection)

- Use Feishu's **长连接 (Long Connection)** mode - no public server needed
- Subscribe to `im.message.receive_v1` event
- Receive user messages via the persistent WebSocket connection
- OpenClaw has proven this approach works (see AlexAnys/openclaw-feishu)

### 3.3 Card Templates

**Permission Request (Red border)**:
```
┌─────────────────────────────────────┐
│ 🔴 Permission Required              │
│                                     │
│ Claude Code wants to:               │
│ • Delete 3 files                    │
│ • Force push to main                │
│                                     │
│ Reply with: y/n or your answer     │
└─────────────────────────────────────┘
```

**Question (Blue border)**:
```
┌─────────────────────────────────────┐
│ 🔵 Claude Code needs your input     │
│                                     │
│ What file should I modify?          │
│                                     │
│ Reply with your answer              │
└─────────────────────────────────────┘
```

**Task Fail (Orange border)**:
```
┌─────────────────────────────────────┐
│ 🟠 Task Failed                      │
│                                     │
│ Error: Cannot connect to database   │
│                                     │
│ Reply with: retry / skip / cancel   │
└─────────────────────────────────────┘
```

## 4. Named Pipe Communication

### 4.1 Pipe Setup

- Create named pipe at `config.pipePath` (default: `/tmp/claude-code-notifier/pipe`)
- Claude Code reads from pipe to get user replies

### 4.2 Input Format

User's Feishu reply is written to pipe as plain text followed by newline:
```
{your reply}
```

### 4.3 Claude Code Integration

Claude Code would need to be configured to read from this pipe when waiting for input. This is the main uncertainty that needs verification during implementation.

## 5. Hook Implementation

### 5.1 Stop Hook Behavior

The Stop hook receives input when Claude Code wants to stop and wait for user. It should:

1. Parse the stop reason (AskUserQuestion, permission request, etc.)
2. Determine if notification should be sent based on `notification.*` config
3. Send Feishu notification with appropriate card format
4. Start WebSocket listener if not already running
5. Return control to Claude Code (non-blocking)

### 5.2 JSON Input Format (from Claude Code)

```json
{
  "reason": "AskUserQuestion",
  "message": "Which file should I modify?",
  "options": ["a.txt", "b.txt", "c.txt"],
  "sessionId": "..."
}
```

### 5.3 JSON Output Format (to Claude Code)

```json
{
  "systemMessage": "Notification sent to Feishu"
}
```

## 6. Verification Plan

### Phase 1: Quick Feasibility Test
1. Write a simple Python script to send Feishu Webhook notification
2. Verify Webhook cards arrive correctly
3. Test Feishu WebSocket long connection receiving messages

### Phase 2: Hook Integration
1. Create the Stop hook that triggers on Claude Code stop
2. Connect to Feishu WebSocket and listen for replies
3. Write replies to named pipe

### Phase 3: End-to-End Test
1. Simulate Claude Code stop event
2. Verify Feishu notification arrives
3. Reply from Feishu
4. Verify reply appears in Claude Code

## 7. Technical Notes

- **No public server needed**: Feishu long connection is outbound from client to Feishu servers
- **WSL compatible**: Works on WSL since connection is outbound
- **Language**: Python 3 (for hook scripts) - same as existing hookify plugin
- **Dependencies**: Standard library + `websocket-client` package for Feishu WebSocket

## 8. Open Questions

1. **Claude Code pipe input**: Does Claude Code support reading from named pipe for user input?
   - If not, may need alternative approach (e.g., background process that injects via terminal input)

2. **Session management**: How to route replies to correct Claude Code session if multiple sessions running?

3. **Security**: Should there be authentication for Feishu → Claude Code communication?