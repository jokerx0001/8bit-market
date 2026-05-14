"""Tests for install/uninstall hook injection and removal logic.

These tests replicate the inline Python code from install.sh and uninstall.sh
to verify hook injection, idempotency, and clean removal.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

HOOK_CMD = "python3 /Users/test/claude-lark/claude_lark_notify.py"


# ── Hook injection (mirrors install.sh logic) ────────────────────────


def _inject_hooks(settings: dict, hook_cmd: str) -> dict:
    """Replicate install.sh hook injection logic."""
    hooks = settings.setdefault("hooks", {})
    entry = {"matcher": "", "hooks": [{"type": "command", "command": hook_cmd, "timeout": 30}]}

    for ev in ("Stop", "Notification"):
        entries = hooks.setdefault(ev, [])
        already = any(
            "claude_lark_notify" in h.get("command", "")
            for e in entries for h in e.get("hooks", [])
        )
        if not already:
            entries.append(entry)
    return settings


def _remove_hooks(settings: dict) -> dict:
    """Replicate uninstall.sh hook removal logic."""
    hooks = settings.get("hooks", {})

    for event_type in ("Stop", "Notification"):
        entries = hooks.get(event_type, [])
        filtered = []
        for entry in entries:
            hook_list = entry.get("hooks", [])
            cleaned = [h for h in hook_list if "claude_lark_notify" not in h.get("command", "")]
            if cleaned:
                entry["hooks"] = cleaned
                filtered.append(entry)
            elif hook_list != cleaned:
                continue
            else:
                filtered.append(entry)
        hooks[event_type] = filtered
        if not hooks[event_type]:
            del hooks[event_type]

    settings["hooks"] = hooks
    return settings


# ── Tests ────────────────────────────────────────────────────────────


class TestHookInjection:
    def test_inject_into_empty_settings(self):
        settings = _inject_hooks({}, HOOK_CMD)
        hooks = settings["hooks"]
        assert "Stop" in hooks
        assert "Notification" in hooks
        assert len(hooks["Stop"]) == 1
        assert hooks["Stop"][0]["hooks"][0]["command"] == HOOK_CMD

    def test_inject_into_existing_hooks(self):
        """Should add alongside existing hooks, not replace them."""
        settings = {
            "hooks": {
                "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "other.sh"}]}]
            }
        }
        result = _inject_hooks(settings, HOOK_CMD)
        # Existing hooks preserved
        assert "PreToolUse" in result["hooks"]
        assert len(result["hooks"]["PreToolUse"]) == 1
        # New hooks added
        assert "Stop" in result["hooks"]
        assert "Notification" in result["hooks"]

    def test_inject_idempotent(self):
        """Running install twice should not duplicate hooks."""
        settings = _inject_hooks({}, HOOK_CMD)
        settings = _inject_hooks(settings, HOOK_CMD)
        assert len(settings["hooks"]["Stop"]) == 1
        assert len(settings["hooks"]["Notification"]) == 1

    def test_inject_preserves_other_stop_hooks(self):
        """Other Stop hooks should not be affected."""
        settings = {
            "hooks": {
                "Stop": [{"matcher": "", "hooks": [{"type": "command", "command": "other-notify.sh"}]}]
            }
        }
        result = _inject_hooks(settings, HOOK_CMD)
        assert len(result["hooks"]["Stop"]) == 2  # original + claude-lark

    def test_inject_preserves_settings_fields(self):
        """Non-hook settings should be untouched."""
        settings = {
            "language": "Chinese",
            "permissions": {"allow": ["Bash(ls:*)"]},
            "hooks": {},
        }
        result = _inject_hooks(settings, HOOK_CMD)
        assert result["language"] == "Chinese"
        assert result["permissions"]["allow"] == ["Bash(ls:*)"]


class TestHookRemoval:
    def test_remove_from_installed(self):
        """Standard uninstall after install."""
        settings = _inject_hooks({}, HOOK_CMD)
        result = _remove_hooks(settings)
        assert "Stop" not in result["hooks"]
        assert "Notification" not in result["hooks"]

    def test_remove_preserves_other_hooks(self):
        """Uninstall should not remove hooks from other tools."""
        settings = {
            "hooks": {
                "Stop": [
                    {"matcher": "", "hooks": [{"type": "command", "command": "other-notify.sh"}]},
                    {"matcher": "", "hooks": [{"type": "command", "command": HOOK_CMD}]},
                ],
                "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "rtk.sh"}]}],
            }
        }
        result = _remove_hooks(settings)
        # other-notify.sh kept, claude-lark removed
        assert len(result["hooks"]["Stop"]) == 1
        assert "other-notify" in result["hooks"]["Stop"][0]["hooks"][0]["command"]
        # PreToolUse untouched
        assert "PreToolUse" in result["hooks"]

    def test_remove_idempotent(self):
        """Uninstalling when not installed should be safe."""
        settings = {
            "hooks": {
                "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "rtk.sh"}]}],
            }
        }
        result = _remove_hooks(settings)
        assert "PreToolUse" in result["hooks"]

    def test_remove_from_empty(self):
        """Uninstalling with no hooks should not crash."""
        result = _remove_hooks({})
        assert result.get("hooks") == {}

    def test_remove_mixed_hook_entry(self):
        """Entry with both claude-lark and other hooks: keep other, remove ours."""
        settings = {
            "hooks": {
                "Stop": [{
                    "matcher": "",
                    "hooks": [
                        {"type": "command", "command": "other.sh"},
                        {"type": "command", "command": HOOK_CMD},
                    ]
                }]
            }
        }
        result = _remove_hooks(settings)
        assert len(result["hooks"]["Stop"]) == 1
        assert len(result["hooks"]["Stop"][0]["hooks"]) == 1
        assert "other.sh" in result["hooks"]["Stop"][0]["hooks"][0]["command"]


class TestInstallUninstallRoundtrip:
    def test_full_roundtrip(self):
        """Install → verify → uninstall → verify clean."""
        original = {
            "language": "Chinese",
            "hooks": {
                "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "rtk.sh"}]}]
            },
        }

        # Install
        installed = _inject_hooks(json.loads(json.dumps(original)), HOOK_CMD)
        assert "Stop" in installed["hooks"]
        assert "Notification" in installed["hooks"]
        assert "PreToolUse" in installed["hooks"]

        # Uninstall
        cleaned = _remove_hooks(installed)
        assert "Stop" not in cleaned["hooks"]
        assert "Notification" not in cleaned["hooks"]
        assert "PreToolUse" in cleaned["hooks"]
        assert cleaned["language"] == "Chinese"

    def test_file_roundtrip(self, tmp_path):
        """Install and uninstall via file I/O."""
        settings_file = tmp_path / "settings.json"

        # Start with existing settings
        original = {"hooks": {}, "language": "Chinese"}
        settings_file.write_text(json.dumps(original))

        # Install
        settings = json.loads(settings_file.read_text())
        settings = _inject_hooks(settings, HOOK_CMD)
        settings_file.write_text(json.dumps(settings, indent=2))

        # Verify installed
        check = json.loads(settings_file.read_text())
        assert len(check["hooks"]["Stop"]) == 1

        # Uninstall
        settings = json.loads(settings_file.read_text())
        settings = _remove_hooks(settings)
        settings_file.write_text(json.dumps(settings, indent=2))

        # Verify clean
        check = json.loads(settings_file.read_text())
        assert "Stop" not in check["hooks"]
        assert check["language"] == "Chinese"
