"""Domain service for resolving combat attacks with damage calculation."""

from modules.domain.model.attack_result import AttackResult
from modules.domain.model.character import Character
from modules.domain.ports.dice_roller import DiceRoller


class AttackResolver:
    """Domain service that resolves combat attacks with damage calculation."""

    def __init__(self, dice_roller: DiceRoller) -> None:
        """Initialize AttackResolver with dice roller dependency."""
        self._dice_roller = dice_roller

    def resolve_attack(self, attacker: Character, defender: Character) -> AttackResult:
        """
        Resolve a single attack from attacker to defender.

        Calculates damage as attack_power + D6 dice roll, applies it to defender,
        and returns complete attack details.

        Args:
            attacker: The attacking character
            defender: The defending character receiving damage

        Returns:
            AttackResult with complete attack resolution details

        Raises:
            ValueError: If attacker is not alive (hp <= 0)
        """
        if not attacker.is_alive:
            raise ValueError("Dead character cannot attack")

        dice_roll = self._dice_roller.roll()
        total_damage = attacker.attack_power + dice_roll
        defender_after = defender.receive_damage(total_damage)

        return AttackResult(
            attacker_name=attacker.name,
            defender_name=defender.name,
            dice_roll=dice_roll,
            attack_power=attacker.attack_power,
            total_damage=total_damage,
            defender_old_hp=defender.hp,
            defender_new_hp=defender_after.hp,
            defender_after=defender_after,
        )
