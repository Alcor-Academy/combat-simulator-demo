"""Character value object - immutable combatant in combat simulation.

Character is a frozen dataclass representing a combatant with name, HP,
attack power, and derived agility. All instances are immutable - state
changes create NEW instances (functional programming paradigm).

Business rules:
- Immutability: @dataclass(frozen=True) prevents field mutation
- Validation: Name non-empty, HP >= 0, Attack power > 0
- Derived agility: agility = hp + attack_power (computed property)
- Liveness: is_alive = hp > 0
- HP flooring: receive_damage never allows negative HP
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Character:
    """Immutable combatant with name, HP, attack power, and derived agility.

    Attributes:
        name: Character identifier (non-empty string)
        hp: Current hit points (>= 0)
        attack_power: Base damage per attack (> 0)

    Properties:
        agility: Derived stat = hp + attack_power (computed)
        is_alive: True if hp > 0, False otherwise
    """

    name: str
    hp: int
    attack_power: int

    def __post_init__(self) -> None:
        """Validate business rules on creation.

        Raises:
            ValueError: If name empty, HP negative, or attack power non-positive
        """
        if not self.name:
            raise ValueError("Name cannot be empty")
        if self.hp < 0:
            raise ValueError("HP cannot be negative")
        if self.attack_power <= 0:
            raise ValueError("Attack power must be positive")

    @property
    def agility(self) -> int:
        """Derived agility stat (hp + attack_power).

        Agility is COMPUTED, not stored. It automatically decreases
        as HP drops during combat (fatigue effect).

        Returns:
            Sum of current HP and attack power
        """
        return self.hp + self.attack_power

    @property
    def is_alive(self) -> bool:
        """Check if character is alive.

        Returns:
            True if HP > 0, False if HP = 0 (dead)
        """
        return self.hp > 0

    def receive_damage(self, amount: int) -> "Character":
        """Apply damage and return NEW Character instance (immutability).

        Original instance remains unchanged. HP is floored at 0 (never negative).

        Args:
            amount: Damage to apply (positive integer)

        Returns:
            NEW Character instance with reduced HP
        """
        new_hp = max(0, self.hp - amount)
        return Character(name=self.name, hp=new_hp, attack_power=self.attack_power)
