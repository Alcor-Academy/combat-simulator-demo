"""Port interface for dice rolling operations.

This module defines the DiceRoller Protocol for Hexagonal Architecture.
Services depend on this abstraction, not concrete implementations.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable  # Enable isinstance() checks in DI container and tests
class DiceRoller(Protocol):
    """Port interface for dice rolling operations.

    Implementations must provide roll() method returning int in range [1, 6].
    This represents a standard six-sided die (D6).

    This Protocol uses structural typing (PEP 544) - implementations do not
    need to explicitly inherit from DiceRoller. They only need to implement
    the roll() method with the correct signature.

    Examples:
        FixedDiceRoller (test double) - deterministic rolls for testing
        RandomDiceRoller (production) - random rolls using random.randint

    Architecture:
        Layer: Domain - Ports (abstractions)
        Dependency direction: Services → Port ← Adapters
        Pattern: Structural typing (duck typing formalized)
    """

    def roll(self) -> int:
        """Roll the die and return result.

        Returns:
            int: Result in range [1, 6] inclusive
        """
        ...
