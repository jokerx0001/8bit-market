#!/usr/bin/env python3
"""Claude Code Notifier - Stop Hook Entry Point.

This script is invoked by Claude Code's Stop hook. It receives JSON on stdin
describing why Claude Code is stopping, sends a Feishu notification if
configured, and ensures the WebSocket reply listener is running.

Input (stdin):
    {
      "reason": "AskUserQuestion | PermissionRequest | TaskComplete | TaskFail",
      "message": "...",
      "options": ["opt1", "opt2"],  // optional
      "sessionId": "..."
    }

Output (stdout):
    {
      "systemMessage": "Notification sent to Feishu"
    }
"""

import json
import os
import sys


def _setup_path():
    """Add lib/ to sys.path for imports."""
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if not plugin_root:
        plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lib_dir = os.path.join(plugin_root, "lib")
    if lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)


def _is_ws_client_running(pipe_path):
    """Check if the WebSocket client daemon is already running."""
    pid_file = os.path.join(os.path.dirname(pipe_path), "ws_client.pid")
    if not os.path.isfile(pid_file):
        return False
    try:
        with open(pid_file, "r") as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)  # Signal 0 checks if process exists
        return True
    except (OSError, ValueError):
        return False


def main():
    _setup_path()

    # Read input from stdin
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            # No input, nothing to do
            print(json.dumps({"systemMessage": ""}))
            return
        hook_input = json.loads(raw_input)
    except json.JSONDecodeError:
        print(json.dumps({"systemMessage": ""}))
        return

    reason = hook_input.get("reason", "")
    message = hook_input.get("message", "")
    options = hook_input.get("options", [])
    session_id = hook_input.get("sessionId", "")

    # Load configuration
    from config_loader import load_config, validate_config
    config = load_config()

    if config is None:
        print(json.dumps({"systemMessage": "Feishu notifier: config not found or invalid"}))
        return

    # Check if this event type should trigger a notification
    notification_config = config.get("notification", {})
    event_key = {
        "AskUserQuestion": "onAskUserQuestion",
        "PermissionRequest": "onPermissionRequest",
        "TaskComplete": "onTaskComplete",
        "TaskFail": "onTaskFail",
    }.get(reason, "")

    if not event_key or not notification_config.get(event_key):
        # This event type is not configured for notification
        print(json.dumps({"systemMessage": ""}))
        return

    # Validate config
    missing = validate_config(config)
    if missing:
        msg = f"Feishu notifier: config incomplete - missing {', '.join(missing)}"
        print(json.dumps({"systemMessage": msg}))
        return

    feishu_config = config["feishu"]
    webhook_url = feishu_config["webhookUrl"]

    # Send notification
    from feishu_sender import send_notification
    success = send_notification(webhook_url, reason, message, options, session_id)

    # Start WebSocket listener daemon if not already running (only for
    # interactive events where user might reply)
    if reason in ("AskUserQuestion", "PermissionRequest", "TaskFail"):
        pipe_path = config.get("pipePath", "/tmp/claude-code-notifier/pipe")
        if not _is_ws_client_running(pipe_path):
            app_id = feishu_config["appId"]
            app_secret = feishu_config["appSecret"]
            from feishu_ws_client import start_ws_client_daemon
            start_ws_client_daemon(app_id, app_secret, pipe_path)

    if success:
        print(json.dumps({"systemMessage": "Notification sent to Feishu"}))
    else:
        print(json.dumps({"systemMessage": "Feishu notification failed to send"}))


if __name__ == "__main__":
    main()
