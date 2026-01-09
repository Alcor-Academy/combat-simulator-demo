from dataclasses import dataclass

from modules.domain.model.character import Character


@dataclass(frozen=True)
class AttackResult:
    """Immutable value object containing complete attack resolution details."""

    attacker_name: str
    defender_name: str
    dice_roll: int
    attack_power: int
    total_damage: int
    defender_old_hp: int
    defender_new_hp: int
    defender_after: Character
