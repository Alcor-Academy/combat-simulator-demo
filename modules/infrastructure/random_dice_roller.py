"""Production dice roller using Python's random module.

This module provides RandomDiceRoller, an infrastructure adapter that
implements the DiceRoller port interface using random number generation.
"""

import random


class RandomDiceRoller:
    """Production dice roller using Python's random module.

    Implements DiceRoller port interface with random number generation.
    Returns uniformly distributed random integers in range [1, 6].

    Note: Uses random.randint which is deterministic given seed,
    but not explicitly seeded for production use.
    """

    def roll(self) -> int:
        """Roll D6 and return random result.

        Returns:
            int: Random value in range [1, 6] inclusive
        """
        return random.randint(1, 6)  # noqa: S311  # nosec B311 - Game dice, not cryptographic
