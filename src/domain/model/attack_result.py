"""AttackResult value object - immutable combat result.

Contains complete attack information including damage calculation,
HP changes, and updated defender state.
"""

from dataclasses import dataclass

from src.domain.model.character import Character


@dataclass(frozen=True)
class AttackResult:
    """Immutable result of single attack action.

    Business rules:
    - Frozen dataclass (immutable)
    - Contains all combat details for logging/history
    - defender_after is NEW Character instance (immutability)

    Attributes:
        attacker_name: Name of attacking character
        defender_name: Name of defending character
        dice_roll: D6 roll result for damage calculation
        attack_power: Attacker's attack power stat
        total_damage: Calculated damage (attack_power + dice_roll)
        defender_old_hp: Defender HP before attack
        defender_new_hp: Defender HP after attack (floors at 0)
        defender_after: NEW Character instance with updated HP
    """

    attacker_name: str
    defender_name: str
    dice_roll: int
    attack_power: int
    total_damage: int
    defender_old_hp: int
    defender_new_hp: int
    defender_after: Character
