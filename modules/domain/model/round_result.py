"""Combat round result value object.

Immutable dataclass representing the complete state and outcome of a single combat round.
Contains both attacker and defender actions, HP changes, and combat end state.
"""

from dataclasses import dataclass

from modules.domain.model.attack_result import AttackResult
from modules.domain.model.character import Character


@dataclass(frozen=True)
class RoundResult:
    """Immutable record of one complete combat round.

    Captures attacker advantage rule: attacker strikes first, defender counter-attacks
    ONLY if still alive after attacker's strike.

    Attributes:
        round_number: Sequential round number (1-indexed)
        attacker_action: Result of attacker's strike
        defender_action: Result of defender's counter-attack, None if defender died
        attacker_hp_before: Attacker HP at round start
        attacker_hp_after: Attacker HP at round end
        defender_hp_before: Defender HP at round start
        defender_hp_after: Defender HP at round end
        combat_ended: True if one character died this round
        winner: Victor if combat ended, None if both alive
    """

    round_number: int
    attacker_action: AttackResult
    defender_action: AttackResult | None
    attacker_hp_before: int
    attacker_hp_after: int
    defender_hp_before: int
    defender_hp_after: int
    combat_ended: bool
    winner: Character | None
