"""Unit tests for RandomDiceRoller infrastructure adapter."""

from modules.infrastructure.random_dice_roller import RandomDiceRoller


def test_roll_returns_value_between_1_and_6():
    """Test that roll() returns a valid D6 value [1, 6].

    Statistical validation: 100 rolls should all be in range.
    This validates the adapter satisfies DiceRoller Protocol contract.
    """
    roller = RandomDiceRoller()

    # Statistical validation: 100 rolls should all be in range
    for _ in range(100):
        result = roller.roll()
        assert 1 <= result <= 6, f"Roll {result} outside valid range [1, 6]"
