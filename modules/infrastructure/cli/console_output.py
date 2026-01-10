"""Rich Console wrapper with timing control for CLI output."""

import time

from rich.console import Console

from modules.infrastructure.cli.config import CLIConfig


class ConsoleOutput:
    """Wraps Rich Console with timing control.

    Provides abstraction layer over Rich Console for:
    - Testability (mock Console behavior in unit tests)
    - Timing control (zero delays in test mode, configurable delays in production)
    - Consistent output interface across CLI components

    Example:
        # Production CLI with delays
        console = Console()
        config = CLIConfig()
        output = ConsoleOutput(console, config)
        output.display_with_delay("Rolling initiative...", 1.0)

        # Fast testing without delays
        config = CLIConfig.test_mode()
        output = ConsoleOutput(mock_console, config)
        output.display_with_delay("Test message", 0.0)
    """

    def __init__(self, console: Console, config: CLIConfig):
        """Initialize ConsoleOutput with Rich Console and configuration.

        Args:
            console: Rich Console instance for output
            config: CLI configuration for timing and display settings
        """
        self._console = console
        self._config = config

    def print(self, text: str, style: str = "", end: str = "\n") -> None:
        """Print text with optional styling.

        Args:
            text: Text to print
            style: Optional Rich style string (e.g., 'bold red', 'green')
            end: String appended after text (default: newline)
        """
        if style:
            self._console.print(text, style=style, end=end)
        else:
            self._console.print(text, end=end)

    def display_with_delay(self, message: str, delay: float) -> None:
        """Display message and pause for specified duration.

        Args:
            message: Message to display
            delay: Delay in seconds (0 or negative = no delay)
        """
        self._console.print(message)
        if delay > 0:
            time.sleep(delay)

    def prompt_continue(self, message: str) -> None:
        """Block until user presses ENTER.

        Args:
            message: Prompt message to display
        """
        self._console.input(message)
