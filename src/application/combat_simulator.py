"""CombatSimulator application service - orchestrates full combat flow.

Main use case for combat simulation:
1. Roll initiative ONCE at combat start (determines attacker/defender for ALL rounds)
2. Execute combat rounds while both characters alive
3. Update character states after each round (immutability pattern)
4. Detect victory condition (HP = 0)
5. Return complete CombatResult with winner, loser, all rounds

Architecture:
- Application layer orchestration (no business logic)
- Delegates to domain services (InitiativeResolver, CombatRound)
- Uses dependency injection for testability
- Returns immutable value objects (CombatResult)

Business rules enforced:
- DR-04: Initiative rolled ONCE, roles persist entire combat
- DR-06: Attacker advantage (enforced by CombatRound)
- Victory condition: Combat ends when either character reaches HP = 0
"""

from typing import TYPE_CHECKING

from src.domain.model.character import Character
from src.domain.model.combat_result import CombatResult
from src.domain.services.combat_round import CombatRound
from src.domain.services.initiative_resolver import InitiativeResolver


if TYPE_CHECKING:
    from src.domain.model.round_result import RoundResult


class CombatSimulator:
    """Application service orchestrating complete combat simulation.

    Coordinates domain services to execute full combat from initiative
    through victory, maintaining immutable state throughout.

    Dependencies:
        initiative_resolver: Domain service for rolling initiative once at start
        combat_round: Domain service for executing individual rounds
    """

    def __init__(self, initiative_resolver: InitiativeResolver, combat_round: CombatRound) -> None:
        """Initialize CombatSimulator with domain service dependencies.

        Args:
            initiative_resolver: Service for rolling initiative (ONCE at start)
            combat_round: Service for executing single rounds with attacker advantage
        """
        self._initiative_resolver = initiative_resolver
        self._combat_round = combat_round

    def run_combat(self, char1: Character, char2: Character) -> CombatResult:
        """Execute complete combat simulation from start to victory.

        Business flow:
        1. Roll initiative ONCE to determine attacker/defender
        2. Loop: Execute rounds while both characters alive
        3. Update character states after each round (immutability)
        4. Break when combat_ended (someone died)
        5. Determine winner/loser based on final states
        6. Return CombatResult with complete history

        Args:
            char1: First character (advantage in tie-breaker)
            char2: Second character

        Returns:
            CombatResult: Complete combat history with winner, loser, all rounds
        """
        # PHASE 1: Roll initiative ONCE at combat start (DR-04)
        initiative = self._initiative_resolver.roll_initiative(char1, char2)
        attacker = initiative.attacker
        defender = initiative.defender

        # PHASE 2: Execute combat loop until victory
        rounds: list[RoundResult] = []
        round_number = 1

        while True:
            # Execute single round with current attacker/defender states
            round_result = self._combat_round.execute_round(
                attacker=attacker, defender=defender, round_number=round_number
            )

            # Record round in history
            rounds.append(round_result)

            # Check victory condition
            if round_result.combat_ended:
                break

            # Update character states for next round (immutability pattern)
            # Both characters update because both attacked
            attacker = round_result.attacker  # May have taken damage from counter-attack
            defender = round_result.defender  # May have taken damage from attacker

            round_number += 1

        # PHASE 3: Determine winner and loser from final round
        final_round = rounds[-1]
        if final_round.winner is not None:
            # Winner determined in final round
            winner = final_round.winner
            loser = final_round.defender if winner.name == final_round.attacker.name else final_round.attacker
        # Should never happen - combat_ended implies winner exists
        # But handle gracefully for robustness
        elif final_round.attacker.is_alive:
            winner = final_round.attacker
            loser = final_round.defender
        else:
            winner = final_round.defender
            loser = final_round.attacker

        # PHASE 4: Return immutable result with tuple (not list)
        return CombatResult(
            winner=winner,
            loser=loser,
            total_rounds=len(rounds),
            rounds=tuple(rounds),  # CRITICAL: Convert to tuple for immutability
        )
