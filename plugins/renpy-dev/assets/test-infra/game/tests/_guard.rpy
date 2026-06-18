# _guard.rpy — init offset=-100, gate all test files from release builds
# Every .rpy file under game/tests/ must start with this guard.
# This file loads first (offset -100) so other test files inherit config.test.

init offset = -100:
    python early:
        if not hasattr(config, "test") or not config.test:
            return

        # Ensure test framework is available to all subsequent test files
        import sys
        import os
        test_dir = os.path.join(config.gamedir, "tests")
        if test_dir not in sys.path:
            sys.path.insert(0, test_dir)
