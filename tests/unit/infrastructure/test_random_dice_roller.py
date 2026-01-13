"""Unit tests for RandomDiceRoller adapter.

RandomDiceRoller is a production adapter implementing DiceRoller Protocol
using Python's random.randint for genuine randomness.

Tests verify statistical properties without mocking random - we test the real adapter.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.infrastructure.random_dice_roller import RandomDiceRoller


if TYPE_CHECKING:
    from src.domain.ports.dice_roller import DiceRoller


class TestRandomDiceRoller:
    """Test RandomDiceRoller production adapter."""

    def test_roll_returns_value_in_valid_range(self):
        """Single roll returns value between 1 and 6 inclusive."""
        roller = RandomDiceRoller()

        result = roller.roll()

        assert 1 <= result <= 6, f"Roll {result} outside valid range [1, 6]"

    def test_statistical_validation_100_rolls_all_in_range(self):
        """All rolls from 100 iterations stay within [1, 6]."""
        roller = RandomDiceRoller()

        results = [roller.roll() for _ in range(100)]

        # All values must be in valid range
        assert all(1 <= r <= 6 for r in results), (
            f"Some rolls outside [1, 6]: {[r for r in results if not (1 <= r <= 6)]}"
        )

        # Statistical sanity: should have some variety in 100 rolls
        unique_values = set(results)
        assert len(unique_values) >= 2, "100 rolls should produce at least 2 different values (probabilistically)"

    def test_satisfies_dice_roller_protocol(self):
        """RandomDiceRoller satisfies DiceRoller Protocol via structural typing."""
        roller: DiceRoller = RandomDiceRoller()

        # Protocol compliance verified by type checker
        # Runtime verification: has roll() method
        assert hasattr(roller, "roll"), "Missing roll() method"
        assert callable(roller.roll), "roll() is not callable"

        # Verify roll() returns int
        result = roller.roll()
        assert isinstance(result, int), f"roll() returned {type(result)}, expected int"
