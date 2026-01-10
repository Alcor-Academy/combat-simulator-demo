"""Unit tests for ConsoleOutput (Rich Console wrapper)."""

import time
from unittest.mock import Mock

from rich.console import Console

from modules.infrastructure.cli.config import CLIConfig
from modules.infrastructure.cli.console_output import ConsoleOutput


class TestConsoleOutputPrint:
    """Test print() method behavior."""

    def test_print_without_style(self):
        """Print text without styling delegates to Rich Console."""
        mock_console = Mock(spec=Console)
        config = CLIConfig.test_mode()
        output = ConsoleOutput(mock_console, config)

        output.print("Test message")

        mock_console.print.assert_called_once_with("Test message", end="\n")

    def test_print_with_style(self):
        """Print text with styling passes style to Rich Console."""
        mock_console = Mock(spec=Console)
        config = CLIConfig.test_mode()
        output = ConsoleOutput(mock_console, config)

        output.print("Styled text", style="bold red")

        mock_console.print.assert_called_once_with("Styled text", style="bold red", end="\n")

    def test_print_with_custom_end(self):
        """Print text with custom end parameter."""
        mock_console = Mock(spec=Console)
        config = CLIConfig.test_mode()
        output = ConsoleOutput(mock_console, config)

        output.print("No newline", end="")

        mock_console.print.assert_called_once_with("No newline", end="")


class TestConsoleOutputDisplayWithDelay:
    """Test display_with_delay() timing behavior."""

    def test_display_with_delay_respects_duration(self):
        """Display with delay should pause for specified duration."""
        mock_console = Mock(spec=Console)
        config = CLIConfig()  # Production config with delays
        output = ConsoleOutput(mock_console, config)

        start = time.time()
        output.display_with_delay("Test message", 0.1)
        elapsed = time.time() - start

        # Allow small timing variance
        assert elapsed >= 0.09
        assert elapsed < 0.2
        mock_console.print.assert_called_once_with("Test message")

    def test_display_with_delay_zero_in_test_mode(self):
        """Display with zero delay should not pause (critical for fast tests)."""
        mock_console = Mock(spec=Console)
        config = CLIConfig.test_mode()
        output = ConsoleOutput(mock_console, config)

        start = time.time()
        output.display_with_delay("Test message", 0.0)
        elapsed = time.time() - start

        # No delay - should be instant
        assert elapsed < 0.01
        mock_console.print.assert_called_once_with("Test message")

    def test_display_with_delay_negative_duration_no_pause(self):
        """Display with negative delay should not pause."""
        mock_console = Mock(spec=Console)
        config = CLIConfig.test_mode()
        output = ConsoleOutput(mock_console, config)

        start = time.time()
        output.display_with_delay("Test message", -1.0)
        elapsed = time.time() - start

        # No delay for negative values
        assert elapsed < 0.01
        mock_console.print.assert_called_once_with("Test message")


class TestConsoleOutputPromptContinue:
    """Test prompt_continue() blocking behavior."""

    def test_prompt_continue_blocks(self):
        """Prompt continue blocks on Console.input()."""
        mock_console = Mock(spec=Console)
        mock_console.input.return_value = ""  # Simulate user pressing ENTER
        config = CLIConfig.test_mode()
        output = ConsoleOutput(mock_console, config)

        output.prompt_continue("Press ENTER to continue...")

        mock_console.input.assert_called_once_with("Press ENTER to continue...")

    def test_prompt_continue_returns_after_input(self):
        """Prompt continue returns after user input."""
        mock_console = Mock(spec=Console)
        mock_console.input.return_value = ""
        config = CLIConfig.test_mode()
        output = ConsoleOutput(mock_console, config)

        # Should not raise exception or hang
        result = output.prompt_continue("Press ENTER...")

        # Method should return None
        assert result is None
        mock_console.input.assert_called_once()
