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

    def _hp_color(self, current_hp: int, max_hp: int) -> str:
        """Return color based on HP percentage.

        Args:
            current_hp: Current HP value
            max_hp: Maximum HP value

        Returns:
            Color string for Rich styling (green/yellow/orange/red)
        """
        pct = current_hp / max_hp
        if pct >= 0.7:
            return "green"
        if pct >= 0.4:
            return "yellow"
        if pct >= 0.2:
            return "orange"
        return "red"

    def _render_initiative(self, init_result: InitiativeResult) -> None:
        """Display initiative resolution.

        Args:
            init_result: InitiativeResult containing roll details
        """
        dice = self._config.get_symbol("dice")
        init_symbol = self._config.get_symbol("initiative")

        self._console.print(f"{dice} Rolling Initiative...", style="bold cyan")
        self._console.print(f"{init_result.attacker.name}: {init_result.attacker_total}")
        self._console.print(f"{init_result.defender.name}: {init_result.defender_total}")
        self._console.print(f"{init_symbol} {init_result.attacker.name} attacks first!", style="bold yellow")
        self._console.display_with_delay("", self._config.initiative_winner_delay)

    def _render_round(self, round_result: RoundResult) -> None:
        """Display single combat round.

        Args:
            round_result: RoundResult containing round details
        """
        # Header with enhanced styling
        attack_emoji = self._config.get_symbol("attack")
        self._console.print(f"\n{'=' * 35}", style="dim")
        self._console.print(f"{attack_emoji}  ROUND {round_result.round_number}", style="bold magenta")
        self._console.print(f"{'=' * 35}", style="dim")
        self._console.display_with_delay("", self._config.round_header_delay)

        # Attacker action
        self._render_attack_action(round_result.attacker_action, is_counter=False)

        # Defender counter-attack (if alive)
        if round_result.defender_action:
            self._render_attack_action(round_result.defender_action, is_counter=True)
        else:
            defender_name = round_result.attacker_action.defender_name
            death = self._config.get_symbol("death")
            self._console.print(f"\n{death}  {defender_name} has been defeated!", style="bold red dim")
            self._console.display_with_delay("", self._config.death_delay)

    def _render_attack_action(self, action: AttackResult, is_counter: bool) -> None:
        """Display attack action details.

        Args:
            action: AttackResult containing attack details
            is_counter: Whether this is a counter-attack
        """
        attack_symbol = self._config.get_symbol("attack")
        defend_symbol = self._config.get_symbol("defend")
        damage_symbol = self._config.get_symbol("damage")
        dice_symbol = self._config.get_symbol("dice")
        hp_symbol = self._config.get_symbol("hp")

        action_symbol = defend_symbol if is_counter else attack_symbol
        attack_verb = "counter-attacks" if is_counter else "attacks"
        action_style = "bold blue" if is_counter else "bold cyan"

        self._console.print(f"\n{action_symbol}  {action.attacker_name} {attack_verb}!", style=action_style)
        self._console.print(
            f"   {dice_symbol} Roll: {action.dice_roll} + ⚔️  Power: {action.attack_power} = "
            f"{damage_symbol} {action.total_damage} damage",
            style="yellow",
        )

        # HP display with color gradient
        hp_color = self._hp_color(action.defender_new_hp, action.defender_old_hp)
        self._console.print(
            f"   {hp_symbol} {action.defender_name}: {action.defender_old_hp} HP → {action.defender_new_hp} HP",
            style=hp_color,
        )
        self._console.display_with_delay("", self._config.attack_delay)

    def _render_victory(self, result: CombatResult) -> None:
        """Display victory announcement.

        Args:
            result: Complete CombatResult with winner information
        """
        victory_symbol = self._config.get_symbol("victory")
        death_symbol = self._config.get_symbol("death")

        # Decorative victory banner with box drawing characters
        self._console.print(f"\n{'╔' + '═' * 35 + '╗'}", style="bold yellow")
        self._console.print(
            f"║  {victory_symbol}  {result.winner.name.upper()} WINS!  {victory_symbol}  ║", style="bold yellow"
        )
        self._console.print(f"{'╚' + '═' * 35 + '╝'}", style="bold yellow")

        self._console.print(f"\nCombat lasted {result.total_rounds} rounds", style="dim")
        self._console.print(f"{result.winner.name}: {result.winner.hp} HP remaining", style="green")
        self._console.print(f"{result.loser.name}: 0 HP {death_symbol} (defeated)", style="red dim")

        if self._config.prompt_for_exit:
            self._console.prompt_continue("\nPremi INVIO per uscire (o CTRL-C per terminare)")
