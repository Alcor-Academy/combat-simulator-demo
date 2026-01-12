"""Unit tests for CharacterCreator - interactive character creation with validation."""

from unittest.mock import Mock, patch

import pytest

from modules.infrastructure.cli.character_creator import CharacterCreator
from modules.infrastructure.cli.config import CLIConfig
from modules.infrastructure.cli.console_output import ConsoleOutput
from modules.infrastructure.random_dice_roller import RandomDiceRoller


class TestCharacterCreator:
    """Test suite for CharacterCreator class."""

    @pytest.fixture
    def mock_rich_console(self):
        """Mock Rich Console for I/O boundary only."""
        console = Mock()
        console.output_buffer = []

        def capture_print(*args, **kwargs):
            """Capture print calls to buffer."""
            console.output_buffer.append(str(args))

        console.print = Mock(side_effect=capture_print)
        console.print_panel = Mock()
        return console

    @pytest.fixture
    def console(self, mock_rich_console):
        """REAL ConsoleOutput with mocked Rich Console (I/O boundary)."""
        config = CLIConfig.test_mode()
        return ConsoleOutput(mock_rich_console, config)

    @pytest.fixture
    def dice_roller(self):
        """REAL RandomDiceRoller with seed for determinism."""
        return RandomDiceRoller(seed=42)

    @pytest.fixture
    def creator(self, console, dice_roller):
        """Create CharacterCreator instance with REAL dependencies."""
        return CharacterCreator(console, dice_roller)

    def test_create_character_with_manual_input(self, creator):
        """Test basic character creation with valid inputs."""
        with patch("rich.prompt.Prompt.ask", side_effect=["Hero", "50", "10"]):
            char = creator.create_character(1)

        assert char.name == "Hero"
        assert char.hp == 50
        assert char.attack_power == 10

    def test_empty_name_triggers_reprompt(self, creator, mock_rich_console):
        """Test that empty name is rejected and user is re-prompted."""
        with patch("rich.prompt.Prompt.ask", side_effect=["", "  ", "Hero", "50", "10"]):
            char = creator.create_character(1)

        assert char.name == "Hero"
        # TODO: Extract validation messages to constants for i18n readiness
        # Verify error message was shown (in red)
        error_calls = [
            c
            for c in mock_rich_console.print.call_args_list
            if len(c[0]) > 0 and "cannot be empty" in str(c[0][0]).lower()
        ]
        assert len(error_calls) >= 2  # Two rejections

    def test_hp_range_validation(self, creator, mock_rich_console):
        """Test HP validation enforces range [1-999]."""
        with patch("rich.prompt.Prompt.ask", side_effect=["Hero", "0", "1000", "50", "10"]):
            char = creator.create_character(1)

        assert char.hp == 50
        # TODO: Extract validation messages to constants for i18n readiness
        # Verify error messages were shown
        error_calls = [
            c
            for c in mock_rich_console.print.call_args_list
            if len(c[0]) > 0 and "hp" in str(c[0][0]).lower() and "between" in str(c[0][0]).lower()
        ]
        assert len(error_calls) >= 2  # Two rejections

    def test_attack_range_validation(self, creator, mock_rich_console):
        """Test attack power validation enforces range [1-99]."""
        with patch("rich.prompt.Prompt.ask", side_effect=["Hero", "50", "0", "100", "10"]):
            char = creator.create_character(1)

        assert char.attack_power == 10
        # TODO: Extract validation messages to constants for i18n readiness
        # Verify error messages were shown
        error_calls = [
            c
            for c in mock_rich_console.print.call_args_list
            if len(c[0]) > 0 and "attack" in str(c[0][0]).lower() and "between" in str(c[0][0]).lower()
        ]
        assert len(error_calls) >= 2  # Two rejections

    def test_character_card_displayed(self, creator, mock_rich_console):
        """Test that character confirmation card is displayed."""
        with patch("rich.prompt.Prompt.ask", side_effect=["Hero", "50", "10"]):
            char = creator.create_character(1)

        # Verify character was created successfully
        assert char.name == "Hero"
        assert char.hp == 50
        assert char.attack_power == 10

        # Verify Rich console print was called (ConsoleOutput.print_panel calls console.print)
        # The panel display goes through console.print, not print_panel
        assert mock_rich_console.print.called

    def test_random_hp_generates_value_in_valid_range(self, creator):
        """Test _random_hp() generates HP in range [20-80]."""
        # Deterministic testing of boundaries using REAL dice roller with seed.
        # E2E tests validate distribution with multiple samples.
        hp = creator._random_hp()

        assert 20 <= hp <= 80

    def test_random_attack_generates_value_in_valid_range(self, creator):
        """Test _random_attack() generates attack in range [5-15]."""
        # Deterministic testing of boundaries using REAL dice roller with seed.
        # E2E tests validate distribution with multiple samples.
        attack = creator._random_attack()

        assert 5 <= attack <= 15

    def test_empty_input_triggers_random_generation(self, creator):
        """Test that pressing INVIO (empty input) triggers random HP and attack generation."""
        # Uses REAL dice roller with seed for deterministic behavior.
        # E2E tests validate actual random distribution.
        with patch("rich.prompt.Prompt.ask", side_effect=["Hero", "", ""]):  # Name, empty HP, empty attack
            char = creator.create_character(1)

        assert char.name == "Hero"
        # Random HP should be in valid range [20-80]
        assert 20 <= char.hp <= 80
        # Random attack should be in valid range [5-15]
        assert 5 <= char.attack_power <= 15

    def test_hp_boundary_values_accepted(self, creator):
        """Test HP boundary values 1 and 999 are accepted."""
        # Test minimum valid HP (1)
        with patch("rich.prompt.Prompt.ask", side_effect=["Hero", "1", "10"]):
            char = creator.create_character(1)
        assert char.hp == 1

        # Test maximum valid HP (999)
        with patch("rich.prompt.Prompt.ask", side_effect=["Hero", "999", "10"]):
            char = creator.create_character(1)
        assert char.hp == 999

    def test_attack_boundary_values_accepted(self, creator):
        """Test attack power boundary values 1 and 99 are accepted."""
        # Test minimum valid attack (1)
        with patch("rich.prompt.Prompt.ask", side_effect=["Hero", "50", "1"]):
            char = creator.create_character(1)
        assert char.attack_power == 1

        # Test maximum valid attack (99)
        with patch("rich.prompt.Prompt.ask", side_effect=["Hero", "50", "99"]):
            char = creator.create_character(1)
        assert char.attack_power == 99

    def test_non_numeric_hp_input_triggers_validation_error(self, creator, mock_rich_console):
        """Test that non-numeric HP input shows error and re-prompts."""
        with patch("rich.prompt.Prompt.ask", side_effect=["Hero", "invalid_hp", "50", "10"]):
            char = creator.create_character(1)

        assert char.name == "Hero"
        assert char.hp == 50
        assert char.attack_power == 10

        # Verify console printed error message for non-numeric input
        # (The ValueError exception path in _prompt_for_hp_with_validation is exercised)
        error_calls = [
            c
            for c in mock_rich_console.print.call_args_list
            if len(c[0]) > 0 and "whole number" in str(c[0][0]).lower() and "hp" in str(c[0][0]).lower()
        ]
        assert len(error_calls) >= 1  # At least one rejection for non-numeric input

    def test_non_numeric_attack_input_triggers_validation_error(self, creator, mock_rich_console):
        """Test that non-numeric attack input shows error and re-prompts."""
        with patch("rich.prompt.Prompt.ask", side_effect=["Hero", "50", "abc", "10"]):
            char = creator.create_character(1)

        assert char.name == "Hero"
        assert char.hp == 50
        assert char.attack_power == 10

        # Verify console printed error message for non-numeric input
        # (The ValueError exception path in _prompt_for_attack_with_validation is exercised)
        error_calls = [
            c
            for c in mock_rich_console.print.call_args_list
            if len(c[0]) > 0 and "whole number" in str(c[0][0]).lower() and "attack" in str(c[0][0]).lower()
        ]
        assert len(error_calls) >= 1  # At least one rejection for non-numeric input
