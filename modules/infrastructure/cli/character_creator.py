"""CharacterCreator - Interactive character creation with input validation."""

from typing import TYPE_CHECKING

from rich.panel import Panel
from rich.prompt import Prompt

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

    def create_character(self, num: int) -> Character:  # noqa: C901
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

        # HP input (with validation, allow empty for random)
        while True:
            hp_input = Prompt.ask("HP [1-999] (INVIO per random [20-80])", default="")
            if hp_input == "":
                # Empty input → random HP
                hp = self._random_hp()
                self._console.print(f"🎲 Random HP: {hp}", style="cyan")
                break
            try:
                hp = int(hp_input)
                if 1 <= hp <= 999:
                    break
                self._console.print("❌ HP must be between 1 and 999.", style="red")
            except ValueError:
                self._console.print("❌ HP must be a whole number.", style="red")

        # Attack input (with validation, allow empty for random)
        while True:
            attack_input = Prompt.ask("Potere d'attacco [1-99] (INVIO per random [5-15])", default="")
            if attack_input == "":
                # Empty input → random attack
                attack = self._random_attack()
                self._console.print(f"🎲 Random Attack: {attack}", style="cyan")
                break
            try:
                attack = int(attack_input)
                if 1 <= attack <= 99:
                    break
                self._console.print("❌ Attack power must be between 1 and 99.", style="red")
            except ValueError:
                self._console.print("❌ Attack power must be a whole number.", style="red")

        # Create Character
        char = Character(name, hp, attack)

        # Display confirmation
        self._display_character_card(char)

        return char

    def _random_hp(self) -> int:
        """
        Generate random HP in range [20-80].

        Uses dice_roller to generate random value.
        Range: [20-80] = 61 possible values
        Implementation: roll_range(61) returns [1-61], add 19 to get [20-80]

        Returns:
            Random HP value in range [20-80]
        """
        return self._dice_roller.roll_range(61) + 19

    def _random_attack(self) -> int:
        """
        Generate random attack power in range [5-15].

        Uses dice_roller to generate random value.
        Range: [5-15] = 11 possible values
        Implementation: roll_range(11) returns [1-11], add 4 to get [5-15]

        Returns:
            Random attack power in range [5-15]
        """
        return self._dice_roller.roll_range(11) + 4

    def _display_character_card(self, char: Character) -> None:
        """
        Display character information card.

        Args:
            char: Character to display
        """
        card_text = f"🧙 {char.name}\n❤️  HP: {char.hp}\n⚔️  Attack: {char.attack_power}\n⚡ Agility: {char.agility}"
        panel = Panel(card_text, title="Character Created", border_style="green")
        self._console.print_panel(panel)
