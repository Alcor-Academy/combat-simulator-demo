"""Combat simulation application service."""

from modules.domain.model.character import Character
from modules.domain.model.combat_result import CombatResult
from modules.domain.services.combat_round import CombatRound
from modules.domain.services.initiative_resolver import InitiativeResolver


class CombatSimulator:
    """Orchestrates complete combat simulation from initiative to victory.

    This is the top-level use case service that coordinates the domain services
    to simulate a full combat encounter.
    """

    def __init__(
        self,
        initiative_resolver: InitiativeResolver,
        combat_round: CombatRound,
    ):
        """Initialize combat simulator with domain services.

        Args:
            initiative_resolver: Service to determine combat order
            combat_round: Service to execute individual combat rounds
        """
        self._initiative_resolver = initiative_resolver
        self._combat_round = combat_round

    def run_combat(self, char1: Character, char2: Character) -> CombatResult:
        """Execute complete combat simulation.

        Rolls initiative once at start, then executes combat rounds
        until one character is defeated.

        Args:
            char1: First combatant
            char2: Second combatant

        Returns:
            CombatResult with winner, loser, and complete round history
        """
        # Roll initiative once at start
        initiative = self._initiative_resolver.roll_initiative(char1, char2)
        attacker = initiative.attacker
        defender = initiative.defender

        rounds_list = []
        round_number = 1

        # Combat loop - continue while both alive
        while attacker.is_alive and defender.is_alive:
            round_result = self._combat_round.execute_round(attacker, defender, round_number)
            rounds_list.append(round_result)

            # Update character states from round result
            # Defender always updated from attacker's action
            defender = round_result.attacker_action.defender_after

            # Attacker only updated if defender counter-attacked
            if round_result.defender_action:
                attacker = round_result.defender_action.defender_after

            round_number += 1

        # Determine winner/loser
        winner = attacker if attacker.is_alive else defender
        loser = defender if not defender.is_alive else attacker

        return CombatResult(
            winner=winner,
            loser=loser,
            total_rounds=len(rounds_list),
            rounds=tuple(rounds_list),  # Convert list to tuple
            initiative_result=initiative,
        )
