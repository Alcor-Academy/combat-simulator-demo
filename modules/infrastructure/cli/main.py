"""CLI Main Entry Point."""

import sys

from rich.console import Console

from modules.application.combat_simulator import CombatSimulator
from modules.domain.services.attack_resolver import AttackResolver
from modules.domain.services.combat_round import CombatRound
from modules.domain.services.initiative_resolver import InitiativeResolver
from modules.infrastructure.cli.character_creator import CharacterCreator
from modules.infrastructure.cli.combat_renderer import CombatRenderer
from modules.infrastructure.cli.config import CLIConfig
from modules.infrastructure.cli.console_output import ConsoleOutput
from modules.infrastructure.random_dice_roller import RandomDiceRoller


def run_cli() -> None:
    """Main CLI entry point."""
    try:
        # Configuration
        config = CLIConfig()  # Production mode (with delays)

        # Rich Console
        rich_console = Console()
        console = ConsoleOutput(rich_console, config)

        # Domain services
        dice_roller = RandomDiceRoller()
        attack_resolver = AttackResolver(dice_roller)
        initiative_resolver = InitiativeResolver(dice_roller)
        combat_round = CombatRound(attack_resolver)

        # Application service
        combat_simulator = CombatSimulator(initiative_resolver, combat_round)

        # CLI components
        renderer = CombatRenderer(console, config)
        creator = CharacterCreator(console, dice_roller)  # Phase 2: Active character creation

        # Welcome
        console.print("\n=== COMBAT SIMULATOR ===\n")

        # Characters created through interactive CLI (Phase 2)
        char1 = creator.create_character(1)  # Prompts user for name, HP, attack
        char2 = creator.create_character(2)  # Prompts user for name, HP, attack

        console.print("")

        # Run combat
        result = combat_simulator.run_combat(char1, char2)

        # Display combat
        renderer.render_combat(result)

    except KeyboardInterrupt:
        console.print("\n⚠️  Combat interrupted by user. Exiting...", style="yellow")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n❌ Unexpected error: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    run_cli()
