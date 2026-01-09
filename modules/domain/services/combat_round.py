"""Combat round orchestration service.

Executes one complete combat round with attacker advantage rule:
- Attacker strikes first
- Defender counter-attacks ONLY if alive after attacker's strike
- Returns complete round state including HP changes and combat outcome
"""

from modules.domain.model.character import Character
from modules.domain.model.round_result import RoundResult
from modules.domain.services.attack_resolver import AttackResolver


class CombatRound:
    """Orchestrates one combat round with attacker advantage.

    Business rule: Dead defender cannot counter-attack (attacker advantage).
    """

    def __init__(self, attack_resolver: AttackResolver) -> None:
        """Initialize combat round service with attack resolver.

        Args:
            attack_resolver: Service to resolve individual attacks
        """
        self._attack_resolver = attack_resolver

    def execute_round(self, attacker: Character, defender: Character, round_number: int) -> RoundResult:
        """Execute one complete combat round.

        Args:
            attacker: Character attacking first this round
            defender: Character defending and potentially counter-attacking
            round_number: Sequential round number (1-indexed)

        Returns:
            Complete round result with both actions and final state
        """
        attacker_hp_before = attacker.hp
        defender_hp_before = defender.hp

        # Attacker strikes first
        attacker_attack = self._attack_resolver.resolve_attack(attacker, defender)
        defender_after_first_strike = attacker_attack.defender_after

        # Defender counter-attacks if alive (attacker advantage rule)
        if defender_after_first_strike.is_alive:
            # Defender survived and can counter-attack
            defender_attack = self._attack_resolver.resolve_attack(defender_after_first_strike, attacker)
            attacker_after_counter = defender_attack.defender_after

            return RoundResult(
                round_number=round_number,
                attacker_action=attacker_attack,
                defender_action=defender_attack,
                attacker_hp_before=attacker_hp_before,
                attacker_hp_after=attacker_after_counter.hp,
                defender_hp_before=defender_hp_before,
                defender_hp_after=defender_after_first_strike.hp,
                combat_ended=not attacker_after_counter.is_alive,
                winner=(defender_after_first_strike if not attacker_after_counter.is_alive else None),
            )
        # Defender dead, no counter-attack (critical business rule)
        return RoundResult(
            round_number=round_number,
            attacker_action=attacker_attack,
            defender_action=None,
            attacker_hp_before=attacker_hp_before,
            attacker_hp_after=attacker.hp,
            defender_hp_before=defender_hp_before,
            defender_hp_after=defender_after_first_strike.hp,
            combat_ended=True,
            winner=attacker,
        )
