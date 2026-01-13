"""CombatRound domain service - orchestrates single combat round with ATTACKER ADVANTAGE.

Business rules (DR-06: Attacker Advantage):
1. Attacker strikes first
2. Defender counter-attacks ONLY if HP > 0 after attacker's strike
3. If defender dies from attacker's strike, defender_damage = 0 (no counter-attack)
4. Combat ends when either character reaches HP = 0
5. Winner identified when combat ends

Architecture: Domain service orchestrating AttackResolver calls with immutable state management.
"""

from src.domain.model.character import Character
from src.domain.model.round_result import RoundResult
from src.domain.services.attack_resolver import AttackResolver


class CombatRound:
    """Orchestrates single combat round with attacker advantage enforcement.

    Dependency injection: AttackResolver (domain service)
    """

    def __init__(self, attack_resolver: AttackResolver):
        """Initialize CombatRound with AttackResolver dependency.

        Args:
            attack_resolver: AttackResolver domain service for damage calculation
        """
        self._attack_resolver = attack_resolver

    def execute_round(self, attacker: Character, defender: Character, round_number: int) -> RoundResult:
        """Execute single combat round with ATTACKER ADVANTAGE.

        Business logic flow:
        1. Attacker attacks first (via AttackResolver)
        2. Check if defender survived (HP > 0)
        3. If defender alive: defender counter-attacks
        4. If defender dead: no counter-attack (defender_damage = 0)
        5. Determine combat_ended and winner
        6. Return immutable RoundResult

        Args:
            attacker: Character attacking first (initiative winner)
            defender: Character defending (attacks second if alive)
            round_number: Sequential round identifier (1-based)

        Returns:
            RoundResult: Immutable round outcome with complete state
        """
        # PHASE 1: Attacker strikes first (CRITICAL: attacker advantage)
        attacker_attack = self._attack_resolver.resolve_attack(attacker, defender)
        attacker_damage = attacker_attack.total_damage
        defender_after_attack = attacker_attack.defender_after

        # PHASE 2: Check if defender survived attacker's strike
        if not defender_after_attack.is_alive:
            # Defender died - NO COUNTER-ATTACK (attacker advantage enforcement)
            # Combat ends immediately with attacker as winner
            return RoundResult(
                round_number=round_number,
                attacker=attacker,  # Attacker unharmed (no counter-attack)
                defender=defender_after_attack,  # Defender dead (HP=0)
                attacker_damage=attacker_damage,
                defender_damage=0,  # CRITICAL: No counter-attack when dead
                combat_ended=True,
                winner=attacker,
            )

        # PHASE 3: Defender survived - execute counter-attack
        defender_attack = self._attack_resolver.resolve_attack(defender_after_attack, attacker)
        defender_damage = defender_attack.total_damage
        attacker_after_counter = defender_attack.defender_after

        # PHASE 4: Determine combat status
        combat_ended = not attacker_after_counter.is_alive
        winner = defender_after_attack if combat_ended else None

        # PHASE 5: Return immutable result
        return RoundResult(
            round_number=round_number,
            attacker=attacker_after_counter,
            defender=defender_after_attack,
            attacker_damage=attacker_damage,
            defender_damage=defender_damage,
            combat_ended=combat_ended,
            winner=winner,
        )
