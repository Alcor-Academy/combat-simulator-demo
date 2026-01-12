"""Temporary script to test emoji fallback mode."""

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


def run_cli_fallback() -> None:
    """CLI with emoji fallback mode (emoji_enabled=False)."""
    try:
        # Configuration with emoji DISABLED for testing
        config = CLIConfig(emoji_enabled=False)

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
        creator = CharacterCreator(console, dice_roller)

        # Welcome
        console.print("\n=== COMBAT SIMULATOR (FALLBACK MODE) ===\n")

        # Characters
        char1 = creator.create_character(1)
        char2 = creator.create_character(2)

        console.print("")

        # Run combat
        result = combat_simulator.run_combat(char1, char2)

        # Display combat
        renderer.render_combat(result)

        # Normal exit
        sys.exit(0)

    except KeyboardInterrupt:
        console.print("\n⚠️  Combat interrupted by user. Exiting...", style="yellow")
        sys.exit(130)
    except ValueError as e:
        console.print(f"\n❌ Invalid input: {e}", style="red")
        console.print("Please try again.", style="dim")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Unexpected error occurred: {e}", style="red")
        console.print("Please report this issue.", style="dim")
        sys.exit(1)


if __name__ == "__main__":
    run_cli_fallback()
