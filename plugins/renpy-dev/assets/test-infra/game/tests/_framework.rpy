# _framework.rpy — Test helper API for Ren'Py behavior and visual tests
# Provides assert_*, inject_*, screenshot_*, and result-reporting utilities.
# All tests receive this framework via _guard.rpy.

init -50 python:
    import json
    import os
    from collections import OrderedDict

    class TestFramework(object):
        """Singleton test helper injected into all test labels."""

        def __init__(self):
            self._results = OrderedDict()
            self._log_lines = []
            self._last_screenshot = None

        # ── Assertions ──────────────────────────────────────────

        def assert_screen_var(self, screen_name, key, expected):
            """Assert a screen-local variable equals expected value."""
            actual = getattr(renpy.get_screen(screen_name).scope.get(key, None), "__self__", None)
            if actual is None:
                actual = renpy.get_screen(screen_name).scope.get(key)
            result = actual == expected
            label = "assert_screen_var({}, {}, {})".format(screen_name, key, repr(expected))
            self._record(label, result, expected=expected, actual=actual)
            return result

        def assert_log_contains(self, marker):
            """Assert a substring appears in captured log output."""
            log_text = "\n".join(self._log_lines)
            result = marker in log_text
            label = "assert_log_contains({})".format(repr(marker))
            self._record(label, result, expected=marker, actual="(present)" if result else "(missing)")
            return result

        def assert_visual(self, screen_name, widget_id, baseline_name, threshold=0.02):
            """Full visual diff pipeline: screenshot → crop widget → diff baseline.

            threshold: fraction of pixels (0.0-1.0) whose per-channel max abs delta exceeds 8/255.
            Default 0.02 = 2% of pixels may differ slightly (anti-aliasing tolerance).
            """
            import io
            test_dir = os.path.join(config.gamedir, "tests")
            baseline_path = os.path.join(test_dir, "baselines", baseline_name + ".png")
            artifact_dir = os.path.join(test_dir, "artifacts")
            os.makedirs(artifact_dir, exist_ok=True)

            need_update = os.environ.get("RENPY_UPDATE_BASELINES", "0") == "1"

            # 1. Screenshot
            screenshot = renpy.screenshot()
            if screenshot is None:
                self._record("assert_visual({}, {})".format(screen_name, widget_id),
                             False, expected=baseline_name, actual="screenshot failed")
                return False

            # 2. Crop to widget bbox
            widget = renpy.get_widget(screen_name, widget_id)
            if widget is None:
                self._record("assert_visual({}, {})".format(screen_name, widget_id),
                             False, expected=baseline_name,
                             actual="widget '{}' not found".format(widget_id))
                return False

            x, y, w, h = widget.get_placement()
            # Clamp to image bounds
            img_w, img_h = screenshot.get_size()
            x = max(0, min(x, img_w))
            y = max(0, min(y, img_h))
            w = max(1, min(w, img_w - x))
            h = max(1, min(h, img_h - y))
            cropped = screenshot.subsurface((x, y, w, h))

            # 3. Bootstrap: no baseline → save as baseline, pass
            if need_update or not os.path.exists(baseline_path):
                cropped.save(baseline_path)
                label = "assert_visual({}, {})".format(screen_name, widget_id)
                self._record(label, True,
                             expected=baseline_name,
                             actual="baseline {} (first run)".format(
                                 "updated" if need_update else "created"))
                return True

            # 4. Diff against baseline
            try:
                from PIL import Image
                import numpy as np

                baseline = Image.open(baseline_path)
                # Ensure same size
                if (w, h) != baseline.size:
                    baseline = baseline.resize((w, h), Image.LANCZOS)

                current_arr = np.array(cropped)
                baseline_arr = np.array(baseline)

                # Per-channel max abs delta > 8/255
                diff = np.max(np.abs(current_arr.astype(np.int16) -
                                     baseline_arr.astype(np.int16)), axis=2)
                changed_pixels = np.sum(diff > 8)
                total_pixels = diff.size
                fraction = changed_pixels / total_pixels if total_pixels > 0 else 0

                label = "assert_visual({}, {})".format(screen_name, widget_id)
                if fraction > threshold:
                    artifact_path = os.path.join(
                        artifact_dir, baseline_name + "_actual.png")
                    cropped.save(artifact_path)
                    self._record(label, False,
                                 expected="diff <= {:.1%}".format(threshold),
                                 actual="diff = {:.1%} ({} changed pixels). Artifact at {}".format(
                                     fraction, changed_pixels, artifact_path))
                    return False
                else:
                    self._record(label, True,
                                 expected="diff <= {:.1%}".format(threshold),
                                 actual="diff = {:.1%}".format(fraction))
                    return True

            except ImportError:
                self._record("assert_visual({}, {})".format(screen_name, widget_id),
                             False, expected=baseline_name,
                             actual="PIL/NumPy not available for pixel diff")
                return False

        # ── Input Injection ─────────────────────────────────────

        def inject_swipe(self, direction, distance=500):
            """Synthesize mouse-down/move/up sequence."""
            import pygame
            sw = config.screen_width
            sh = config.screen_height
            cx, cy = sw // 2, sh // 2
            dx, dy = 0, 0
            if direction == "up":    dy = -distance
            elif direction == "down":  dy = distance
            elif direction == "left":  dx = -distance
            elif direction == "right": dx = distance

            ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(cx, cy), button=1)
            pygame.event.post(ev)
            renpy.pause(0.02)
            ev = pygame.event.Event(pygame.MOUSEMOTION, pos=(cx + dx, cy + dy))
            pygame.event.post(ev)
            renpy.pause(0.02)
            ev = pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(cx + dx, cy + dy), button=1)
            pygame.event.post(ev)
            renpy.pause(0.1)

        def inject_click(self, x, y):
            """Inject a mouse click at (x, y)."""
            import pygame
            ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(x, y), button=1)
            pygame.event.post(ev)
            renpy.pause(0.02)
            ev = pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(x, y), button=1)
            pygame.event.post(ev)
            renpy.pause(0.1)

        def inject_key(self, key_name):
            """Inject a keyboard event."""
            import pygame
            key_const = getattr(pygame, key_name, None)
            if key_const is None:
                return
            ev = pygame.event.Event(pygame.KEYDOWN, key=key_const)
            pygame.event.post(ev)
            renpy.pause(0.02)
            ev = pygame.event.Event(pygame.KEYUP, key=key_const)
            pygame.event.post(ev)
            renpy.pause(0.1)

        # ── Waiting ─────────────────────────────────────────────

        def wait_for_screen(self, name, timeout=2.0):
            """Block until named screen is the topmost, or timeout."""
            elapsed = 0.0
            tick = 0.05
            while elapsed < timeout:
                if renpy.get_screen(name) is not None:
                    return True
                renpy.pause(tick)
                elapsed += tick
            return False

        # ── Log Capture ─────────────────────────────────────────

        def log(self, msg):
            """Append a line to the captured log."""
            self._log_lines.append(str(msg))

        def read_log(self):
            """Return captured log as a single string."""
            return "\n".join(self._log_lines)

        # ── Internal ────────────────────────────────────────────

        def _record(self, label, passed, expected=None, actual=None):
            entry = {"label": label, "passed": passed}
            if expected is not None:
                entry["expected"] = str(expected)
            if actual is not None:
                entry["actual"] = str(actual)
            self._results[label] = entry

        def _flush_results(self):
            """Write all accumulated results to .last_results.json."""
            test_dir = os.path.join(config.gamedir, "tests")
            results_path = os.path.join(test_dir, ".last_results.json")
            passed = []
            failed = []
            errors = []
            for entry in self._results.values():
                if entry["passed"]:
                    passed.append(entry)
                else:
                    failed.append(entry)
            with open(results_path, "w") as f:
                json.dump({
                    "passed": [p["label"] for p in passed],
                    "failed": [f["label"] for f in failed],
                    "errors": [e["label"] for e in errors],
                    "details": list(self._results.values())
                }, f, indent=2)


# Singleton instance
define test_framework = TestFramework()


# ── Test Runner Labels ──────────────────────────────────────────
# The external test.py sets RENPY_TEST_MODE and RENPY_TEST_FILTER
# to control which labels run.

label __test_runner_behavior__:
    python:
        import os
        mode = os.environ.get("RENPY_TEST_MODE", "behavior")
        test_filter = os.environ.get("RENPY_TEST_FILTER", "")
        # Find and run all test_b_* labels
        all_labels = sorted(renpy.get_all_labels())
        for lbl in all_labels:
            if not lbl.startswith("test_b_"):
                continue
            if test_filter and test_filter not in lbl:
                continue
            try:
                renpy.jump(lbl)
            except Exception as e:
                test_framework._record(lbl, False,
                                       expected="test passes",
                                       actual=str(e))
        test_framework._flush_results()
    return


label __test_runner_visual__:
    python:
        import os
        mode = os.environ.get("RENPY_TEST_MODE", "visual")
        test_filter = os.environ.get("RENPY_TEST_FILTER", "")
        all_labels = sorted(renpy.get_all_labels())
        for lbl in all_labels:
            if not lbl.startswith("test_v_"):
                continue
            if test_filter and test_filter not in lbl:
                continue
            try:
                renpy.jump(lbl)
            except Exception as e:
                test_framework._record(lbl, False,
                                       expected="test passes",
                                       actual=str(e))
        test_framework._flush_results()
    return
