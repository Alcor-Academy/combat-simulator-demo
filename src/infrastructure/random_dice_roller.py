"""RandomDiceRoller adapter - production implementation of DiceRoller port.

This adapter provides genuine randomness for combat mechanics using Python's
random module. It satisfies the DiceRoller Protocol through structural typing.
"""

import random


class RandomDiceRoller:
    """Production adapter for DiceRoller using random.randint.

    Implements DiceRoller Protocol via structural typing (duck typing).
    No explicit inheritance required due to Python's Protocol support (PEP 544).

    This adapter is used in production for genuine randomness in:
    - Initiative rolls (agility + D6)
    - Attack damage (attack_power + D6)

    For testing, use FixedDiceRoller test double with predetermined values.
    """

    def roll(self) -> int:
        """Roll a D6 die with genuine randomness.

        Returns:
            Integer in range [1, 6] inclusive, randomly selected.

        Note:
            Uses random.randint(1, 6) for uniform distribution across D6 range.
            This is intentionally NOT cryptographically secure - it's for game dice.
        """
        return random.randint(1, 6)  # noqa: S311
