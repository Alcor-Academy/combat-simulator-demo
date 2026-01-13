"""DiceRoller port - interface for dice rolling abstraction in Hexagonal Architecture.

This port defines the contract for dice rolling, enabling dependency injection
and testability through the adapter pattern.
"""

from typing import Protocol


class DiceRoller(Protocol):
    """Port interface for dice rolling abstraction.

    This protocol enables Hexagonal Architecture by defining an interface
    that can be satisfied by multiple implementations without inheritance.

    Implementations:
        - RandomDiceRoller: Production adapter using random.randint(1, 6)
        - FixedDiceRoller: Test double returning predetermined values

    FixedDiceRoller Interface (Test Double):
        The test double supports two modes for deterministic testing:

        Sequence Mode:
            Returns values in order, cycling when exhausted.

            Example:
                roller = FixedDiceRoller([3, 5, 2, 6, 1])
                assert roller.roll() == 3  # First call
                assert roller.roll() == 5  # Second call
                assert roller.roll() == 2  # Third call
                assert roller.roll() == 6  # Fourth call
                assert roller.roll() == 1  # Fifth call
                assert roller.roll() == 3  # Cycles back to start

        Fixed Value Mode:
            Always returns the same value.

            Example:
                roller = FixedDiceRoller(fixed_value=4)
                assert roller.roll() == 4
                assert roller.roll() == 4
                assert roller.roll() == 4

    Note:
        Python's Protocol (PEP 544) enables structural typing - implementations
        satisfy this interface through duck typing, not explicit inheritance.
    """

    def roll(self) -> int:
        """Roll a D6 die.

        Returns:
            Integer in range [1, 6] inclusive.

        Note:
            Production implementation (RandomDiceRoller) uses random.randint(1, 6).
            Test double (FixedDiceRoller) returns predetermined values.
        """
        ...
