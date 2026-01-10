from dataclasses import dataclass


@dataclass(frozen=True)
class CLIConfig:
    """Configuration for CLI timing and display settings."""

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
        )
