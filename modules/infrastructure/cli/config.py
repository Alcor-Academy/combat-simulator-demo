from dataclasses import dataclass, field
from typing import Dict


# Default emoji symbols for combat events
DEFAULT_EMOJI: Dict[str, str] = {
    "attack": "\u2694\ufe0f",  # Crossed swords
    "damage": "\U0001F4A5",  # Collision/explosion
    "hp": "\u2764\ufe0f",  # Red heart
    "dice": "\U0001F3B2",  # Game die
    "initiative": "\u26a1",  # High voltage
    "victory": "\U0001F3C6",  # Trophy
    "death": "\u2620\ufe0f",  # Skull and crossbones
    "defend": "\U0001F6E1\ufe0f",  # Shield
    "character": "\U0001F9D9",  # Mage
}

# Fallback text symbols for terminals without emoji support
DEFAULT_FALLBACK: Dict[str, str] = {
    "attack": "[ATK]",
    "damage": "[DMG]",
    "hp": "[HP]",
    "dice": "[D6]",
    "initiative": "[INIT]",
    "victory": "[WIN]",
    "death": "[DEAD]",
    "defend": "[DEF]",
    "character": "[CHAR]",
}


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

        # Get symbol for combat events
        attack_symbol = config.get_symbol('attack')  # Returns emoji or fallback
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

    # Emoji configuration
    emoji: Dict[str, str] = field(default_factory=lambda: DEFAULT_EMOJI.copy())
    fallback: Dict[str, str] = field(default_factory=lambda: DEFAULT_FALLBACK.copy())

    def get_symbol(self, key: str) -> str:
        """Get emoji or fallback symbol for a combat event.

        If key is not found in emoji/fallback dict, returns key itself.
        This ensures missing keys pass through unchanged (graceful degradation).

        Args:
            key: Symbol key (attack, damage, hp, dice, initiative, victory, death, defend, character)

        Returns:
            Emoji string if emoji_enabled, fallback text otherwise, or key if not found.

        Example:
            get_symbol('attack') returns '⚔️' if emoji_enabled else '[ATK]'
            get_symbol('unknown') returns 'unknown' (graceful fallback)
        """
        if self.emoji_enabled:
            return self.emoji.get(key, key)
        else:
            return self.fallback.get(key, key)

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
