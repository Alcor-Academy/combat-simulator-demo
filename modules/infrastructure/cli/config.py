from dataclasses import dataclass


@dataclass(frozen=True)
class CLIConfig:
    """Configuration for CLI timing and display settings.

    Use production defaults for interactive CLI experience with delays.
    Use test_mode() for E2E/integration tests requiring zero delays.

    Example:
        # Production CLI with delays
        config = CLIConfig()

        # Fast E2E testing without delays
        config = CLIConfig.test_mode()
    """

    # Timing delays (seconds)
    initiative_roll_delay: float = 1.0
    initiative_winner_delay: float = 1.5
    round_header_delay: float = 0.5
    attack_delay: float = 1.5
    death_delay: float = 2.0
    round_separator_delay: float = 0.5
    exit_delay: float = 2.0

    # Display settings
    emoji_enabled: bool = True
    colors_enabled: bool = True
    prompt_for_exit: bool = True

    @staticmethod
    def test_mode() -> "CLIConfig":
        """Zero delays for testing."""
        return CLIConfig(
            initiative_roll_delay=0.0,
            initiative_winner_delay=0.0,
            round_header_delay=0.0,
            attack_delay=0.0,
            death_delay=0.0,
            round_separator_delay=0.0,
            exit_delay=0.0,
            prompt_for_exit=False,  # Don't wait for input in tests
        )
