"""AttackResolver domain service - calculates attack damage and applies to defender.

Business rules:
1. Damage = attack_power + D6 dice roll
2. Dead character (HP=0) cannot attack - raise ValueError
3. Defender HP reduced by damage (via Character.receive_damage())
4. HP floors at 0 (delegated to Character.receive_damage())
5. Returns immutable AttackResult with complete combat details
"""

from src.domain.model.attack_result import AttackResult
from src.domain.model.character import Character
from src.domain.ports.dice_roller import DiceRoller


class AttackResolver:
    """Resolves single attack action between attacker and defender.

    Dependency injection: DiceRoller (port boundary)
    """

    def __init__(self, dice_roller: DiceRoller):
        """Initialize AttackResolver with dice roller dependency.

        Args:
            dice_roller: DiceRoller implementation (port - can be real or test double)
        """
        self._dice_roller = dice_roller

    def resolve_attack(self, attacker: Character, defender: Character) -> AttackResult:
        """Calculate damage and apply to defender.

        Business logic:
        1. Validate attacker is alive (fail-fast)
        2. Roll D6 for damage variance
        3. Calculate total damage = attack_power + dice_roll
        4. Apply damage to defender (immutably via receive_damage)
        5. Return AttackResult with complete combat details

        Args:
            attacker: Character performing attack (must be alive)
            defender: Character receiving attack

        Returns:
            AttackResult: Immutable result with damage details and updated defender

        Raises:
            ValueError: If attacker is dead (HP=0)
        """
        # Business rule: Dead character cannot attack (fail-fast validation)
        if not attacker.is_alive:
            raise ValueError("Dead character cannot attack")

        # Roll dice for damage variance
        dice_roll = self._dice_roller.roll()

        # Calculate total damage
        total_damage = attacker.attack_power + dice_roll

        # Apply damage to defender (immutably)
        defender_after = defender.receive_damage(total_damage)

        # Return immutable result with complete combat details
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
