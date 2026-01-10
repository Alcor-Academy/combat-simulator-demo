"""CharacterCreator - Interactive character creation with input validation."""

from typing import TYPE_CHECKING

from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt

from modules.domain.model.character import Character


if TYPE_CHECKING:
    from modules.infrastructure.cli.console_output import ConsoleOutput
    from modules.infrastructure.random_dice_roller import RandomDiceRoller


class CharacterCreator:
    """Handles interactive character creation with validation."""

    def __init__(self, console: "ConsoleOutput", dice_roller: "RandomDiceRoller") -> None:
        """
        Initialize CharacterCreator with dependencies.

        Args:
            console: ConsoleOutput instance for user interaction
            dice_roller: DiceRoller instance (for future random generation)
        """
        self._console = console
        self._dice_roller = dice_roller

    def create_character(self, num: int) -> Character:
        """
        Create a character through interactive prompts with validation.

        Args:
            num: Character number (for display purposes)

        Returns:
            Character instance with validated attributes
        """
        self._console.print(f"\n--- Create Character {num} ---")

        # Name input (with validation)
        while True:
            name = Prompt.ask(f"Nome personaggio {num}").strip()
            if name:
                break
            self._console.print("❌ Name cannot be empty. Please enter a name.", style="red")

        # HP input (with validation)
        while True:
            hp = IntPrompt.ask("HP [1-999]")
            if 1 <= hp <= 999:
                break
            self._console.print("❌ HP must be between 1 and 999.", style="red")

        # Attack input (with validation)
        while True:
            attack = IntPrompt.ask("Potere d'attacco [1-99]")
            if 1 <= attack <= 99:
                break
            self._console.print("❌ Attack power must be between 1 and 99.", style="red")

        # Create Character
        char = Character(name, hp, attack)

        # Display confirmation
        self._display_character_card(char)

        return char

    def _display_character_card(self, char: Character) -> None:
        """
        Display character information card.

        Args:
            char: Character to display
        """
        card_text = f"🧙 {char.name}\n❤️  HP: {char.hp}\n⚔️  Attack: {char.attack_power}\n⚡ Agility: {char.agility}"
        panel = Panel(card_text, title="Character Created", border_style="green")
        self._console.print_panel(panel)
