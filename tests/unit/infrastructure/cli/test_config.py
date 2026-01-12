"""Unit tests for CLIConfig emoji configuration."""

import pytest

from modules.infrastructure.cli.config import CLIConfig, DEFAULT_EMOJI, DEFAULT_FALLBACK


class TestCLIConfigEmoji:
    """Tests for CLIConfig emoji functionality."""

    def test_get_symbol_returns_emoji_when_enabled(self) -> None:
        """Test that get_symbol returns emoji when emoji_enabled is True."""
        config = CLIConfig(emoji_enabled=True)

        assert config.get_symbol("attack") == DEFAULT_EMOJI["attack"]
        assert config.get_symbol("damage") == DEFAULT_EMOJI["damage"]
        assert config.get_symbol("hp") == DEFAULT_EMOJI["hp"]
        assert config.get_symbol("dice") == DEFAULT_EMOJI["dice"]
        assert config.get_symbol("initiative") == DEFAULT_EMOJI["initiative"]
        assert config.get_symbol("victory") == DEFAULT_EMOJI["victory"]
        assert config.get_symbol("death") == DEFAULT_EMOJI["death"]
        assert config.get_symbol("defend") == DEFAULT_EMOJI["defend"]
        assert config.get_symbol("character") == DEFAULT_EMOJI["character"]

    def test_get_symbol_returns_fallback_when_disabled(self) -> None:
        """Test that get_symbol returns fallback text when emoji_enabled is False."""
        config = CLIConfig(emoji_enabled=False)

        assert config.get_symbol("attack") == "[ATK]"
        assert config.get_symbol("damage") == "[DMG]"
        assert config.get_symbol("hp") == "[HP]"
        assert config.get_symbol("dice") == "[D6]"
        assert config.get_symbol("initiative") == "[INIT]"
        assert config.get_symbol("victory") == "[WIN]"
        assert config.get_symbol("death") == "[DEAD]"
        assert config.get_symbol("defend") == "[DEF]"
        assert config.get_symbol("character") == "[CHAR]"

    def test_all_emoji_keys_have_fallbacks(self) -> None:
        """Test that every emoji key has a corresponding fallback."""
        emoji_keys = set(DEFAULT_EMOJI.keys())
        fallback_keys = set(DEFAULT_FALLBACK.keys())

        assert emoji_keys == fallback_keys, (
            f"Emoji and fallback keys must match. "
            f"Missing in fallback: {emoji_keys - fallback_keys}. "
            f"Extra in fallback: {fallback_keys - emoji_keys}"
        )

    def test_get_symbol_returns_key_if_not_found(self) -> None:
        """Test that get_symbol returns the key itself when key is not found."""
        config_emoji = CLIConfig(emoji_enabled=True)
        config_fallback = CLIConfig(emoji_enabled=False)

        # Unknown keys should return themselves (graceful degradation)
        assert config_emoji.get_symbol("unknown") == "unknown"
        assert config_fallback.get_symbol("unknown") == "unknown"
        assert config_emoji.get_symbol("foo_bar") == "foo_bar"
        assert config_fallback.get_symbol("foo_bar") == "foo_bar"

    def test_emoji_dict_has_nine_entries(self) -> None:
        """Test that emoji dict contains exactly 9 entries."""
        config = CLIConfig()

        assert len(config.emoji) == 9
        expected_keys = {
            "attack",
            "damage",
            "hp",
            "dice",
            "initiative",
            "victory",
            "death",
            "defend",
            "character",
        }
        assert set(config.emoji.keys()) == expected_keys

    def test_fallback_dict_has_matching_entries(self) -> None:
        """Test that fallback dict has same keys as emoji dict."""
        config = CLIConfig()

        assert len(config.fallback) == len(config.emoji)
        assert set(config.fallback.keys()) == set(config.emoji.keys())

    def test_test_mode_has_emoji_enabled_by_default(self) -> None:
        """Test that test_mode() still has emoji_enabled=True by default."""
        config = CLIConfig.test_mode()

        # Test mode should keep emoji enabled for output verification
        assert config.emoji_enabled is True
        assert config.get_symbol("attack") == DEFAULT_EMOJI["attack"]

    def test_emoji_contains_correct_unicode_characters(self) -> None:
        """Test that emoji dict contains correct Unicode emoji characters."""
        config = CLIConfig(emoji_enabled=True)

        # Verify specific emoji Unicode values
        assert "\u2694" in config.get_symbol("attack")  # Crossed swords base
        assert "\U0001F4A5" in config.get_symbol("damage")  # Collision
        assert "\u2764" in config.get_symbol("hp")  # Heart base
        assert "\U0001F3B2" in config.get_symbol("dice")  # Game die
        assert "\u26a1" in config.get_symbol("initiative")  # High voltage
        assert "\U0001F3C6" in config.get_symbol("victory")  # Trophy
        assert "\u2620" in config.get_symbol("death")  # Skull base
        assert "\U0001F6E1" in config.get_symbol("defend")  # Shield base
        assert "\U0001F9D9" in config.get_symbol("character")  # Mage

    def test_fallback_values_are_bracketed_text(self) -> None:
        """Test that all fallback values are bracketed text format."""
        config = CLIConfig(emoji_enabled=False)

        for key in DEFAULT_FALLBACK:
            value = config.get_symbol(key)
            assert value.startswith("["), f"Fallback '{key}' should start with '['"
            assert value.endswith("]"), f"Fallback '{key}' should end with ']'"
