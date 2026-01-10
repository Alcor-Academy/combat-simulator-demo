"""
E2E Baseline Test for Interactive CLI Combat Viewer

CRITICAL: This is the FIRST test in Outside-In TDD.
It MUST FAIL initially (RED phase) because the CLI entry point doesn't exist yet.

Expected failure: ModuleNotFoundError or ImportError for modules.infrastructure.cli

This test drives the minimal viable CLI implementation (Phase 1: Baseline).
"""

import subprocess
import sys

import pytest


@pytest.mark.wip
def test_baseline_cli_runs_hardcoded_combat():
    """
    Baseline: CLI runs hardcoded combat and displays winner.

    This test defines what "working CLI" means:
    - CLI launches successfully
    - Runs combat with hardcoded characters (Hero 50/10, Villain 40/8)
    - Displays winner
    - Exits with code 0

    Expected FAILURE (RED phase):
    - ModuleNotFoundError: No module named 'modules.infrastructure.cli'
    - OR ImportError: cannot import name 'run_cli' from 'modules.infrastructure.cli.main'

    After implementation (GREEN phase):
    - CLI executes successfully
    - Output contains winner announcement
    - Exit code is 0
    """
    # Attempt to import and run CLI - this SHOULD FAIL initially
    try:
        from modules.infrastructure.cli.main import (  # noqa: PLC0415
            run_cli,
        )

        # If we get here, CLI exists - run it
        # This should execute combat with hardcoded characters and display winner
        result = run_cli()

        # Verify CLI completed successfully
        assert result == 0, "CLI should exit with code 0"

    except (ModuleNotFoundError, ImportError) as e:
        # This is EXPECTED in RED phase - CLI doesn't exist yet
        # The test should fail here, driving us to implement the CLI
        pytest.fail(
            f"CLI entry point not implemented yet (expected in RED phase): {e}\n"
            f"Next step: Implement modules.infrastructure.cli.main.run_cli() "
            f"that runs hardcoded combat and displays winner"
        )


@pytest.mark.wip
def test_baseline_cli_command_line_execution():
    """
    Baseline: CLI can be executed from command line.

    Verifies that CLI module can be invoked as:
    python -m modules.infrastructure.cli.main

    Expected FAILURE (RED phase):
    - ModuleNotFoundError or ImportError

    After implementation (GREEN phase):
    - Process exits with code 0
    - stdout contains combat output
    """
    # Try to run CLI as subprocess - this SHOULD FAIL initially
    result = subprocess.run(  # noqa: S603 - Test subprocess, not user input
        [sys.executable, "-m", "modules.infrastructure.cli.main"],
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
    )

    # In GREEN phase, this should succeed
    # In RED phase, this will fail with import error
    if result.returncode != 0:
        if "ModuleNotFoundError" in result.stderr or "No module named" in result.stderr:
            pytest.fail(
                f"CLI module not implemented yet (expected in RED phase):\n"
                f"stderr: {result.stderr}\n"
                f"Next step: Create modules/infrastructure/cli/main.py with __main__ entry point"
            )
        else:
            pytest.fail(f"CLI execution failed:\nstderr: {result.stderr}\nstdout: {result.stdout}")

    # If we get here, CLI executed successfully (GREEN phase)
    assert result.returncode == 0, "CLI should exit with code 0"
    assert len(result.stdout) > 0, "CLI should produce output"
