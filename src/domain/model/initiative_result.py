"""InitiativeResult value object - immutable record of initiative roll outcome.

InitiativeResult captures the complete state of initiative determination,
including both characters, their dice rolls, calculated totals, and the
assigned attacker/defender roles for the entire combat.

Business rules:
- Immutability: @dataclass(frozen=True) prevents field mutation
- Attacker: Character who won initiative (attacks first all rounds)
- Defender: Character who lost initiative (attacks second if alive)
- Totals: Calculated initiative values (agility + roll)
- Rolls: Individual D6 dice values for transparency
"""

from dataclasses import dataclass

from src.domain.model.character import Character


@dataclass(frozen=True)
class InitiativeResult:
    """Immutable result of initiative roll determining combat order.

    Initiative is rolled ONCE at combat start. Winner becomes attacker
    and strikes first in ALL combat rounds (attacker advantage).

    Attributes:
        attacker: Character who won initiative (strikes first)
        defender: Character who lost initiative (strikes second)
        attacker_roll: D6 value rolled for attacker
        defender_roll: D6 value rolled for defender
        attacker_total: Initiative total (attacker.agility + attacker_roll)
        defender_total: Initiative total (defender.agility + defender_roll)
    """

    attacker: Character
    defender: Character
    attacker_roll: int
    defender_roll: int
    attacker_total: int
    defender_total: int
