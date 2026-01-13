"""RoundResult value object - immutable result of single combat round.

Captures complete round state including:
- Round identification (round_number)
- Character states after round (attacker, defender with updated HP)
- Damage dealt by each character
- Combat status (combat_ended, winner if applicable)

Immutability enforced via frozen dataclass.
"""

from dataclasses import dataclass

from src.domain.model.character import Character


@dataclass(frozen=True)
class RoundResult:
    """Immutable result of single combat round execution.

    Enforces ATTACKER ADVANTAGE business rule (DR-06):
    - Attacker strikes first
    - Defender counter-attacks ONLY if HP > 0 after attacker's strike
    - If defender dies, defender_damage = 0 (no counter-attack)

    Fields:
        round_number: Sequential round identifier (1-based)
        attacker: Attacker character state AFTER round completion
        defender: Defender character state AFTER round completion
        attacker_damage: Damage dealt by attacker to defender
        defender_damage: Damage dealt by defender to attacker (0 if defender died)
        combat_ended: True if either character reached HP = 0
        winner: Character who won (if combat_ended), None otherwise
        attacker_hp_after: Convenience field for attacker HP after round
        defender_hp_after: Convenience field for defender HP after round
    """

    round_number: int
    attacker: Character
    defender: Character
    attacker_damage: int
    defender_damage: int
    combat_ended: bool
    winner: Character | None

    @property
    def attacker_hp_after(self) -> int:
        """Convenience property for attacker HP after round."""
        return self.attacker.hp

    @property
    def defender_hp_after(self) -> int:
        """Convenience property for defender HP after round."""
        return self.defender.hp
