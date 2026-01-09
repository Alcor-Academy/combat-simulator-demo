"""Initiative result value object.

This immutable value object contains the complete results of an initiative roll,
including which character won (attacker), which lost (defender), the dice rolls,
and the final totals used to determine combat order.

Initiative is calculated once at combat start and determines who attacks first
for the ENTIRE combat, not just one round.
"""

from dataclasses import dataclass

from modules.domain.model.character import Character


@dataclass(frozen=True)
class InitiativeResult:
    """Immutable result of initiative roll determining combat order.

    Initiative calculation: character.agility + dice_roll
    Higher total becomes attacker (attacks first for entire combat).

    Tie-breaker rules (applied in order):
    1. Higher initiative total wins
    2. If totals equal, higher base agility wins
    3. If agility equal, first character (char1 parameter) wins

    Attributes:
        attacker: Character who won initiative (attacks first)
        defender: Character who lost initiative (attacks second)
        attacker_roll: D6 die roll result for attacker (1-6)
        defender_roll: D6 die roll result for defender (1-6)
        attacker_total: attacker.agility + attacker_roll
        defender_total: defender.agility + defender_roll
    """

    attacker: Character
    defender: Character
    attacker_roll: int
    defender_roll: int
    attacker_total: int
    defender_total: int
