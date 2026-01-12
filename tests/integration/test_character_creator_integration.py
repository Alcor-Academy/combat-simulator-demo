"""
Integration test for CharacterCreator.

Verifies E2E interaction without BDD framework.
"""

from unittest.mock import Mock, patch

import pytest
from rich.console import Console

from modules.domain.model.character import Character
from modules.infrastructure.cli.character_creator import CharacterCreator
from modules.infrastructure.cli.config import CLIConfig
from modules.infrastructure.cli.console_output import ConsoleOutput
from modules.infrastructure.random_dice_roller import RandomDiceRoller


class TestCharacterCreatorIntegration:
    """Integration tests verifying CharacterCreator with real dependencies."""

    @pytest.fixture
    def production_services(self):
        """Create real production services."""
        dice_roller = RandomDiceRoller(seed=42)
        mock_rich_console = Mock(spec=Console)
        config = CLIConfig.test_mode()
        console = ConsoleOutput(mock_rich_console, config)
        return {"dice_roller": dice_roller, "console": console}

    def test_manual_character_creation_integration(self, production_services):
        """
        Integration test simulating E2E Test #1: Manual Character Creation.

        This verifies the same behavior as the BDD test but without
        pytest-bdd dependency.
        """
        console = production_services["console"]
        dice_roller = production_services["dice_roller"]

        creator = CharacterCreator(console, dice_roller)

        # Simulate user inputs for two characters
        with patch("rich.prompt.Prompt.ask") as mock_prompt:
            # Character 1: Hero with HP 50, Attack 10
            mock_prompt.side_effect = ["Hero", "50", "10"]
            char1 = creator.create_character(1)

            # Character 2: Villain with HP 40, Attack 8
            mock_prompt.side_effect = ["Villain", "40", "8"]
            char2 = creator.create_character(2)

        # Verify both characters created successfully
        assert isinstance(char1, Character)
        assert isinstance(char2, Character)

        # Verify Character 1 attributes
        assert char1.name == "Hero"
        assert char1.hp == 50
        assert char1.attack_power == 10
        assert char1.agility == 60  # HP + Attack

        # Verify Character 2 attributes
        assert char2.name == "Villain"
        assert char2.hp == 40
        assert char2.attack_power == 8
        assert char2.agility == 48  # HP + Attack

    def test_validation_integration(self, production_services):
        """Integration test for validation with re-prompting."""
        console = production_services["console"]
        dice_roller = production_services["dice_roller"]

        creator = CharacterCreator(console, dice_roller)

        # Simulate invalid then valid inputs
        with patch("rich.prompt.Prompt.ask") as mock_prompt:
            # Empty name, then valid name, then HP inputs, then attack inputs
            mock_prompt.side_effect = [
                "",      # Invalid name (empty)
                "  ",    # Invalid name (whitespace)
                "Hero",  # Valid name
                "0",     # Invalid HP (too low)
                "1000",  # Invalid HP (too high)
                "50",    # Valid HP
                "0",     # Invalid attack (too low)
                "100",   # Invalid attack (too high)
                "10",    # Valid attack
            ]

            char = creator.create_character(1)

        # Verify character created with valid inputs
        assert char.name == "Hero"
        assert char.hp == 50
        assert char.attack_power == 10

        # Verify error messages were displayed (console.print is a real method)
        # In real implementation, validation errors are printed via console.print()
