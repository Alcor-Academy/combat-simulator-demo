"""Unit tests for CharacterCreator - interactive character creation with validation."""

from unittest.mock import Mock, patch

import pytest

from modules.infrastructure.cli.character_creator import CharacterCreator


class TestCharacterCreator:
    """Test suite for CharacterCreator class."""

    @pytest.fixture
    def console(self):
        """Mock console for testing."""
        return Mock()

    @pytest.fixture
    def dice_roller(self):
        """Mock dice roller for testing."""
        return Mock()

    @pytest.fixture
    def creator(self, console, dice_roller):
        """Create CharacterCreator instance with mocked dependencies."""
        return CharacterCreator(console, dice_roller)

    def test_create_character_with_manual_input(self, creator):
        """Test basic character creation with valid inputs."""
        with (
            patch("rich.prompt.Prompt.ask", return_value="Hero"),
            patch("rich.prompt.IntPrompt.ask", side_effect=[50, 10]),
        ):
            char = creator.create_character(1)

        assert char.name == "Hero"
        assert char.hp == 50
        assert char.attack_power == 10

    def test_empty_name_triggers_reprompt(self, creator, console):
        """Test that empty name is rejected and user is re-prompted."""
        with (
            patch("rich.prompt.Prompt.ask", side_effect=["", "  ", "Hero"]),
            patch("rich.prompt.IntPrompt.ask", side_effect=[50, 10]),
        ):
            char = creator.create_character(1)

        assert char.name == "Hero"
        # Verify error message was shown (in red)
        error_calls = [
            c for c in console.print.call_args_list if len(c[0]) > 0 and "cannot be empty" in str(c[0][0]).lower()
        ]
        assert len(error_calls) >= 2  # Two rejections

    def test_hp_range_validation(self, creator, console):
        """Test HP validation enforces range [1-999]."""
        with (
            patch("rich.prompt.Prompt.ask", return_value="Hero"),
            patch("rich.prompt.IntPrompt.ask", side_effect=[0, 1000, 50, 10]),
        ):
            char = creator.create_character(1)

        assert char.hp == 50
        # Verify error messages were shown
        error_calls = [
            c
            for c in console.print.call_args_list
            if len(c[0]) > 0 and "hp" in str(c[0][0]).lower() and "between" in str(c[0][0]).lower()
        ]
        assert len(error_calls) >= 2  # Two rejections

    def test_attack_range_validation(self, creator, console):
        """Test attack power validation enforces range [1-99]."""
        with (
            patch("rich.prompt.Prompt.ask", return_value="Hero"),
            patch("rich.prompt.IntPrompt.ask", side_effect=[50, 0, 100, 10]),
        ):
            char = creator.create_character(1)

        assert char.attack_power == 10
        # Verify error messages were shown
        error_calls = [
            c
            for c in console.print.call_args_list
            if len(c[0]) > 0 and "attack" in str(c[0][0]).lower() and "between" in str(c[0][0]).lower()
        ]
        assert len(error_calls) >= 2  # Two rejections

    def test_character_card_displayed(self, creator, console):
        """Test that character confirmation card is displayed."""
        with (
            patch("rich.prompt.Prompt.ask", return_value="Hero"),
            patch("rich.prompt.IntPrompt.ask", side_effect=[50, 10]),
        ):
            creator.create_character(1)

        # Verify console was used to display card via print_panel
        assert console.print_panel.called

    def test_uses_console_and_dice_roller(self, console, dice_roller):
        """Test that CharacterCreator accepts and stores console and dice_roller."""
        creator = CharacterCreator(console, dice_roller)

        assert creator._console is console
        assert creator._dice_roller is dice_roller
