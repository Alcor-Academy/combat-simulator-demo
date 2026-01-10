"""Combat renderer for formatting combat events for display."""

from modules.domain.model.attack_result import AttackResult
from modules.domain.model.combat_result import CombatResult
from modules.domain.model.initiative_result import InitiativeResult
from modules.domain.model.round_result import RoundResult
from modules.infrastructure.cli.config import CLIConfig
from modules.infrastructure.cli.console_output import ConsoleOutput


class CombatRenderer:
    """Formats combat events for display."""

    def __init__(self, console: ConsoleOutput, config: CLIConfig):
        """Initialize CombatRenderer with console and configuration.

        Args:
            console: ConsoleOutput instance for displaying text
            config: CLIConfig instance for timing control
        """
        self._console = console
        self._config = config

    def render_combat(self, result: CombatResult) -> None:
        """Render complete combat (plain text for baseline).

        Args:
            result: Complete combat result to render
        """
        self._render_initiative(result.initiative_result)

        for round_result in result.rounds:
            self._render_round(round_result)

        self._render_victory(result)

    def _render_initiative(self, init_result: InitiativeResult) -> None:
        """Display initiative resolution.

        Args:
            init_result: InitiativeResult containing roll details
        """
        self._console.print("Rolling Initiative...")
        self._console.print(f"{init_result.attacker.name}: {init_result.attacker_total}")
        self._console.print(f"{init_result.defender.name}: {init_result.defender_total}")
        self._console.print(f"{init_result.attacker.name} attacks first!")
        self._console.display_with_delay("", self._config.initiative_winner_delay)

    def _render_round(self, round_result: RoundResult) -> None:
        """Display single combat round.

        Args:
            round_result: RoundResult containing round details
        """
        self._console.print(f"\n=== ROUND {round_result.round_number} ===")
        self._console.display_with_delay("", self._config.round_header_delay)

        # Attacker action
        self._render_attack_action(round_result.attacker_action, is_counter=False)

        # Defender counter-attack (if alive)
        if round_result.defender_action:
            self._render_attack_action(round_result.defender_action, is_counter=True)
        else:
            defender_name = round_result.attacker_action.defender_name
            self._console.print(f"{defender_name} has been defeated!")
            self._console.display_with_delay("", self._config.death_delay)

    def _render_attack_action(self, action: AttackResult, is_counter: bool) -> None:
        """Display attack action details.

        Args:
            action: AttackResult containing attack details
            is_counter: Whether this is a counter-attack
        """
        attack_verb = "counter-attacks" if is_counter else "attacks"
        self._console.print(f"{action.attacker_name} {attack_verb}!")
        self._console.print(f"  Damage: {action.total_damage}")
        self._console.print(f"  {action.defender_name}: {action.defender_old_hp} HP -> {action.defender_new_hp} HP")
        self._console.display_with_delay("", self._config.attack_delay)

    def _render_victory(self, result: CombatResult) -> None:
        """Display victory announcement.

        Args:
            result: Complete CombatResult with winner information
        """
        self._console.print(f"\n=== {result.winner.name.upper()} WINS! ===")
        self._console.print(f"Combat lasted {result.total_rounds} rounds")
        self._console.print(f"{result.winner.name}: {result.winner.hp} HP remaining")
        self._console.print(f"{result.loser.name}: 0 HP (defeated)")
        self._console.prompt_continue("\nPress ENTER to exit...")
