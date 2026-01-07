"""Test double for DiceRoller port - provides deterministic dice rolls for testing.

This test double implements the DiceRoller protocol with predetermined values,
enabling predictable test scenarios without randomness.
"""

from typing import Union, List


class FixedDiceRoller:
    """Test double for DiceRoller that returns predetermined values.

    Supports two modes:
    1. Single value mode: Always returns the same value
    2. Sequence mode: Returns values in order, cycling if exhausted

    This implements the DiceRoller protocol through structural typing (duck typing).
    No explicit inheritance required due to Python's Protocol support (PEP 544).

    Usage:
        # Single value mode - always returns 4
        roller = FixedDiceRoller(4)
        assert roller.roll() == 4
        assert roller.roll() == 4

        # Sequence mode - returns values in order, then cycles
        roller = FixedDiceRoller([3, 5, 2])
        assert roller.roll() == 3
        assert roller.roll() == 5
        assert roller.roll() == 2
        assert roller.roll() == 3  # Cycles back to start

    Attributes:
        _values: List of predetermined values to return
        _index: Current position in the sequence
    """

    def __init__(self, values: Union[int, List[int]]) -> None:
        """Initialize with predetermined dice values.

        Args:
            values: Either a single integer (always return this value)
                   or a list of integers (cycle through these values)

        Examples:
            FixedDiceRoller(4)           # Always returns 4
            FixedDiceRoller([3, 5, 2])   # Returns 3, 5, 2, 3, 5, 2, ...
        """
        if isinstance(values, int):
            self._values = [values]
        else:
            self._values = list(values)
        self._index = 0

    def roll(self) -> int:
        """Return next predetermined value from the sequence.

        Returns:
            Integer from predetermined sequence. Cycles back to start when exhausted.

        Note:
            This method signature matches the DiceRoller protocol.
            In production, DiceRoller.roll() returns random values in range [1, 6].
            This test double returns predetermined values for deterministic testing.
        """
        value = self._values[self._index % len(self._values)]
        self._index += 1
        return value

    def reset(self) -> None:
        """Reset sequence index to beginning.

        Useful for resetting state between test scenarios.
        """
        self._index = 0
