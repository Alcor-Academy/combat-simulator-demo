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


# ============================================================================
# Test Configuration Constants
# ============================================================================

CLI_MODULE_PATH = "modules.infrastructure.cli.main"
CLI_EXECUTION_TIMEOUT_SECONDS = 5
EXPECTED_SUCCESS_EXIT_CODE = 0


# ============================================================================
# Test Helper Methods - Level 2 Refactoring
# ============================================================================


def _is_module_not_found_error(error: Exception) -> bool:
    """Check if error indicates missing CLI module (expected in RED phase)."""
    return isinstance(error, ModuleNotFoundError | ImportError)


def _create_red_phase_failure_message(error: Exception) -> str:
    """Create clear failure message explaining RED phase expectations."""
    return (
        f"CLI entry point not implemented yet (expected in RED phase): {error}\n"
        f"Next step: Implement {CLI_MODULE_PATH}.run_cli() "
        f"that runs hardcoded combat and displays winner"
    )


def _is_subprocess_module_not_found(stderr: str) -> bool:
    """Check if subprocess stderr indicates missing CLI module."""
    return "ModuleNotFoundError" in stderr or "No module named" in stderr


def _create_subprocess_red_phase_message(stderr: str) -> str:
    """Create clear failure message for subprocess execution in RED phase."""
    return (
        f"CLI module not implemented yet (expected in RED phase):\n"
        f"stderr: {stderr}\n"
        f"Next step: Create {CLI_MODULE_PATH.replace('.', '/')}.py with __main__ entry point"
    )


def _verify_cli_execution_success(exit_code: int, output: str) -> None:
    """Verify CLI executed successfully with correct exit code and output."""
    assert exit_code == EXPECTED_SUCCESS_EXIT_CODE, "CLI should exit with code 0"
    assert len(output) > 0, "CLI should produce output"


# ============================================================================
# E2E Tests - Baseline CLI Combat
# ============================================================================


@pytest.mark.wip
def test_baseline_cli_runs_hardcoded_combat(capsys):
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
    try:
        cli_exit_code = _attempt_cli_import_and_execution()
        captured = capsys.readouterr()
        _verify_cli_execution_success(cli_exit_code, captured.out)

    except (ModuleNotFoundError, ImportError) as module_error:
        _fail_with_red_phase_explanation(module_error)


def _attempt_cli_import_and_execution() -> int:
    """
    Import CLI module and execute hardcoded combat.

    Returns:
        Exit code from CLI execution

    Raises:
        ModuleNotFoundError: If CLI module doesn't exist (expected in RED phase)
        ImportError: If run_cli cannot be imported (expected in RED phase)
    """
    from modules.infrastructure.cli.main import run_cli  # noqa: PLC0415

    return run_cli()


def _fail_with_red_phase_explanation(error: Exception) -> None:
    """
    Fail test with clear explanation of RED phase expectations.

    Args:
        error: The import error that occurred
    """
    failure_message = _create_red_phase_failure_message(error)
    pytest.fail(failure_message)


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
    cli_execution_result = _execute_cli_as_subprocess()
    _validate_subprocess_execution_result(cli_execution_result)


def _execute_cli_as_subprocess() -> subprocess.CompletedProcess:
    """
    Execute CLI module as subprocess using python -m invocation.

    Returns:
        Completed process result with exit code, stdout, and stderr
    """
    cli_command_args = [sys.executable, "-m", CLI_MODULE_PATH]

    return subprocess.run(  # noqa: S603 - Test subprocess, not user input
        cli_command_args,
        check=False,
        capture_output=True,
        text=True,
        timeout=CLI_EXECUTION_TIMEOUT_SECONDS,
    )


def _validate_subprocess_execution_result(
    result: subprocess.CompletedProcess,
) -> None:
    """
    Validate CLI subprocess execution result.

    Handles both RED phase (module not found) and GREEN phase (success) scenarios.

    Args:
        result: Completed subprocess execution result
    """
    if _is_execution_failure(result):
        _handle_subprocess_failure(result)
    else:
        _verify_cli_execution_success(result.returncode, result.stdout)


def _is_execution_failure(result: subprocess.CompletedProcess) -> bool:
    """Check if subprocess execution failed (non-zero exit code)."""
    return result.returncode != EXPECTED_SUCCESS_EXIT_CODE


def _handle_subprocess_failure(result: subprocess.CompletedProcess) -> None:
    """
    Handle subprocess execution failure.

    Distinguishes between RED phase (expected) and unexpected failures.

    Args:
        result: Failed subprocess execution result
    """
    if _is_subprocess_module_not_found(result.stderr):
        _fail_with_subprocess_red_phase_message(result.stderr)
    else:
        _fail_with_unexpected_execution_error(result)


def _fail_with_subprocess_red_phase_message(stderr: str) -> None:
    """
    Fail test with RED phase explanation for subprocess execution.

    Args:
        stderr: Standard error output from subprocess
    """
    failure_message = _create_subprocess_red_phase_message(stderr)
    pytest.fail(failure_message)


def _fail_with_unexpected_execution_error(
    result: subprocess.CompletedProcess,
) -> None:
    """
    Fail test with detailed error information for unexpected failures.

    Args:
        result: Failed subprocess execution result
    """
    pytest.fail(f"CLI execution failed:\nstderr: {result.stderr}\nstdout: {result.stdout}")
