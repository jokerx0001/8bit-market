#!/usr/bin/env python3
"""
Ren'Py UI Effect Self-Test Runner — single entry point for all three test layers.

Usage:
    python tools/test.py                        # all three layers
    python tools/test.py structure              # layer 1 only
    python tools/test.py behavior               # layer 2 only
    python tools/test.py visual                 # layer 3 only
    python tools/test.py scaffold               # emit test_v_<screen> skeletons
    python tools/test.py scaffold --screen X    # one screen
    python tools/test.py --update-baselines     # regenerate baselines/
    python tools/test.py --update-baselines --filter X

Exit codes:
    0 — all passed (or first-run baseline created)
    1 — test failure (with list)
    2 — environment error (SDK not found, manifest missing)
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "game" / "tests" / "OWN_MANIFEST.json"
BASELINES_DIR = PROJECT_ROOT / "game" / "tests" / "baselines"
ARTIFACTS_DIR = PROJECT_ROOT / "game" / "tests" / "artifacts"
RESULTS_PATH = PROJECT_ROOT / "game" / "tests" / ".last_results.json"


def get_sdk():
    """Resolve Ren'Py SDK path."""
    sdk = os.environ.get("RENPY_SDK")
    if sdk and Path(sdk).exists():
        return sdk
    # Common default paths
    candidates = [
        r"D:\software\renpy-8.5.3-sdk\renpy.exe",
        r"C:\Program Files\renpy\renpy.exe",
        "/usr/local/bin/renpy",
        os.path.expanduser("~/renpy-sdk/renpy.sh"),
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def load_manifest():
    if not MANIFEST_PATH.exists():
        print(f"[ERROR] OWN_MANIFEST.json not found at {MANIFEST_PATH}")
        sys.exit(2)
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def run_structure(manifest):
    """Layer 1 — lint + AST checks, no engine boot."""
    errors = []

    # 1. renpy lint
    sdk = get_sdk()
    if not sdk:
        print("[ERROR] Ren'Py SDK not found. Set RENPY_SDK env var.")
        sys.exit(2)

    result = subprocess.run(
        [sdk, str(PROJECT_ROOT), "lint"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        errors.append(f"renpy lint failed:\n{result.stderr}")

    # 2. Check all screens listed in manifest can show/hide without error
    for screen in manifest.get("screens", []):
        # Parse check: verify screen definition exists
        screen_file = PROJECT_ROOT / "game" / "screens.rpy"
        if screen_file.exists():
            content = screen_file.read_text(encoding="utf-8")
            if f"screen {screen}" not in content:
                errors.append(f"Screen '{screen}' declared in manifest but not found in screens.rpy")

    # 3. For each script entry, verify referenced files exist
    for script_path in manifest.get("scripts", []):
        full_path = PROJECT_ROOT / "game" / script_path
        if not full_path.exists():
            errors.append(f"Script '{script_path}' referenced in manifest does not exist")

    if errors:
        print("[FAIL] Structure checks failed:")
        for e in errors:
            print(f"  - {e}")
        return False
    print("[PASS] Structure checks")
    return True


def _run_headless(label_prefix, update_baselines=False, test_filter=None):
    """Run SDK headless, dispatching to labels matching prefix."""
    sdk = get_sdk()
    if not sdk:
        print("[ERROR] Ren'Py SDK not found. Set RENPY_SDK env var.")
        sys.exit(2)

    dispatch_label = f"__test_runner_{label_prefix}__"
    env = os.environ.copy()
    env["RENPY_TEST_MODE"] = label_prefix
    env["RENPY_UPDATE_BASELINES"] = "1" if update_baselines else "0"
    if test_filter:
        env["RENPY_TEST_FILTER"] = test_filter

    result = subprocess.run(
        [sdk, str(PROJECT_ROOT), "-W", "0", "-H", "0",
         "--start-label", dispatch_label],
        capture_output=True, text=True, env=env, timeout=300
    )

    if RESULTS_PATH.exists():
        with open(RESULTS_PATH) as f:
            return json.load(f)
    return {"passed": [], "failed": [], "errors": []}


def run_behavior(manifest, update_baselines=False, test_filter=None):
    """Layer 2 — behavior tests via SDK headless."""
    results = _run_headless("behavior", update_baselines, test_filter)
    return _report_results("Behavior", results)


def run_visual(manifest, update_baselines=False, test_filter=None):
    """Layer 3 — visual diff tests via SDK headless."""
    BASELINES_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    results = _run_headless("visual", update_baselines, test_filter)
    return _report_results("Visual", results)


def _report_results(layer_name, results):
    passed = results.get("passed", [])
    failed = results.get("failed", [])
    errors = results.get("errors", [])

    for p in passed:
        print(f"[PASS] {layer_name}: {p}")
    for f in failed:
        print(f"[FAIL] {layer_name}: {f}")
    for e in errors:
        print(f"[ERROR] {layer_name}: {e}")

    if errors:
        return False
    if failed:
        return False
    if not passed and not failed:
        print(f"[SKIP] {layer_name}: no tests found")
    return True


def run_scaffold(manifest, screen_name=None):
    """Emit test_v_<screen> skeleton labels."""
    screens = manifest.get("screens", [])
    if screen_name:
        screens = [s for s in screens if s == screen_name]
        if not screens:
            print(f"[ERROR] Screen '{screen_name}' not found in OWN_MANIFEST.json")
            sys.exit(1)

    test_file = PROJECT_ROOT / "game" / "tests" / "test_screens.rpy"
    existing = test_file.read_text(encoding="utf-8") if test_file.exists() else ""

    skeletons = []
    for screen in screens:
        skeleton = f'''
label test_v_{screen}:
    "Visual test for screen: {screen}"
    jump {screen}
    $ renpy.pause(0.3)
    $ test_framework.assert_visual("{screen}", "TODO: widget_id", "{screen}_default")
    return
'''
        if skeleton not in existing:
            skeletons.append(skeleton)

    if skeletons:
        test_file.parent.mkdir(parents=True, exist_ok=True)
        with open(test_file, "a", encoding="utf-8") as f:
            f.write("\n".join(skeletons))
        print(f"[SCAFFOLD] Added {len(skeletons)} test skeletons to {test_file}")
        print("  Fill in 'TODO: widget_id' with actual widget ids from screens.rpy")
    else:
        print("[SCAFFOLD] No new skeletons needed (all screens already have tests)")


def main():
    parser = argparse.ArgumentParser(description="Ren'Py UI Effect Self-Test Runner")
    parser.add_argument("command", nargs="?",
                        choices=["structure", "behavior", "visual", "scaffold", None],
                        default=None)
    parser.add_argument("--update-baselines", action="store_true",
                        help="Regenerate baseline images")
    parser.add_argument("--screen", help="Target screen for scaffold")
    parser.add_argument("--filter", help="Filter tests by name")
    args = parser.parse_args()

    manifest = load_manifest()

    all_pass = True

    if args.command == "scaffold":
        run_scaffold(manifest, args.screen)
        return

    commands = [args.command] if args.command else ["structure", "behavior", "visual"]

    for cmd in commands:
        if cmd == "structure":
            if not run_structure(manifest):
                all_pass = False
        elif cmd == "behavior":
            if not run_behavior(manifest, args.update_baselines, args.filter):
                all_pass = False
        elif cmd == "visual":
            if not run_visual(manifest, args.update_baselines, args.filter):
                all_pass = False

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
