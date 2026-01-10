"""Production dice roller using Python's random module.

This module provides RandomDiceRoller, an infrastructure adapter that
implements the DiceRoller port interface using random number generation.
"""

import random


class RandomDiceRoller:
    """Production dice roller using Python's random module.

    Implements DiceRoller port interface with random number generation.
    Returns uniformly distributed random integers in range [1, 6].

    Can be seeded for deterministic testing or left unseeded for production use.
    """

    def __init__(self, seed: int | None = None) -> None:
        """Initialize dice roller with optional seed.

        Args:
            seed: Optional seed for deterministic testing.
                  If None, uses default random state.
        """
        if seed is not None:
            random.seed(seed)

    def roll(self) -> int:
        """Roll D6 and return random result.

        Returns:
            int: Random value in range [1, 6] inclusive
        """
        return random.randint(1, 6)  # noqa: S311  # nosec B311 - Game dice, not cryptographic
