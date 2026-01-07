"""pytest-bdd fixtures and configuration for E2E acceptance tests.

This module provides shared fixtures for acceptance test scenarios,
managing test context and dependency injection for production services.
"""

import pytest
from typing import Dict, Any, List


@pytest.fixture
def combat_context() -> Dict[str, Any]:
    """Shared context for combat scenarios.

    This fixture provides a dictionary for storing scenario state across steps.
    It acts as the communication mechanism between Given/When/Then steps.

    Returns:
        Dictionary with keys:
            - characters: List of Character objects created in Given steps
            - dice_roller: FixedDiceRoller instance for deterministic tests
            - initiative_result: InitiativeResult from initiative roll
            - round_result: RoundResult from single round execution
            - combat_result: CombatResult from full combat simulation
            - original_character: Character instance before damage (for immutability tests)
            - damaged_character: Character instance after damage (for immutability tests)

    Usage in step definitions:
        @given('a character "Thorin" with 20 HP and 5 attack power')
        def create_character(combat_context):
            char = Character(name="Thorin", hp=20, attack_power=5)
            combat_context['characters'].append(char)
    """
    return {
        'characters': [],
        'dice_roller': None,
        'initiative_result': None,
        'round_result': None,
        'combat_result': None,
        'original_character': None,
        'damaged_character': None,
        'combat_rounds': [],
    }
