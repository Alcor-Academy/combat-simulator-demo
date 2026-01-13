"""InitiativeResolver domain service - determines combat turn order.

InitiativeResolver implements initiative calculation with tie-breaker rules,
using dependency injection for the DiceRoller port.

Business rules:
- Initiative = character.agility + D6 roll
- Higher total wins and becomes attacker
- Tie-breaker #1: Higher base agility wins
- Tie-breaker #2: First character wins (deterministic)
- Attacker/defender roles persist for entire combat
"""

from src.domain.model.character import Character
from src.domain.model.initiative_result import InitiativeResult
from src.domain.ports.dice_roller import DiceRoller


class InitiativeResolver:
    """Domain service for rolling initiative and determining combat order.

    Initiative determines who attacks first for the ENTIRE combat.
    Rolled once at combat start, result persists through all rounds.

    Attributes:
        _dice_roller: DiceRoller port for D6 rolls (injected dependency)
    """

    def __init__(self, dice_roller: DiceRoller) -> None:
        """Initialize resolver with DiceRoller dependency.

        Args:
            dice_roller: Port implementation for rolling D6 dice
        """
        self._dice_roller = dice_roller

    def roll_initiative(self, char1: Character, char2: Character) -> InitiativeResult:
        """Roll initiative for two characters and determine attacker/defender.

        Business logic:
        1. Roll D6 for each character
        2. Calculate totals: agility + roll
        3. Compare totals with tie-breaker rules
        4. Assign attacker (winner) and defender (loser)

        Tie-breaker rules (in order):
        - Higher total wins
        - If totals equal: higher base agility wins
        - If agility equal: first character (char1) wins

        Args:
            char1: First character (wins tie if all else equal)
            char2: Second character

        Returns:
            InitiativeResult with attacker/defender assigned
        """
        roll1 = self._dice_roller.roll()
        roll2 = self._dice_roller.roll()
        total1 = char1.agility + roll1
        total2 = char2.agility + roll2

        winner = self._determine_winner(char1, char2, total1, total2)

        if winner == char1:
            return self._create_result(char1, char2, roll1, roll2, total1, total2)
        return self._create_result(char2, char1, roll2, roll1, total2, total1)

    def _determine_winner(self, char1: Character, char2: Character, total1: int, total2: int) -> Character:
        """Determine initiative winner with tie-breaker logic.

        Args:
            char1: First character
            char2: Second character
            total1: char1 initiative total
            total2: char2 initiative total

        Returns:
            Character who wins initiative (becomes attacker)
        """
        if total1 > total2:
            return char1
        if total2 > total1:
            return char2
        # Totals equal → apply tie-breaker
        return self._apply_tie_breaker(char1, char2)

    def _apply_tie_breaker(self, char1: Character, char2: Character) -> Character:
        """Apply tie-breaker rules when initiative totals equal.

        Rules (in order):
        1. Higher base agility wins
        2. First character wins (deterministic)

        Args:
            char1: First character
            char2: Second character

        Returns:
            Character who wins tie-breaker
        """
        if char1.agility > char2.agility:
            return char1
        if char2.agility > char1.agility:
            return char2
        # Perfect tie → first character wins
        return char1

    def _create_result(  # noqa: PLR0913
        self,
        attacker: Character,
        defender: Character,
        attacker_roll: int,
        defender_roll: int,
        attacker_total: int,
        defender_total: int,
    ) -> InitiativeResult:
        """Create InitiativeResult with attacker/defender assigned.

        Args:
            attacker: Character who won initiative
            defender: Character who lost initiative
            attacker_roll: D6 value for attacker
            defender_roll: D6 value for defender
            attacker_total: Initiative total for attacker
            defender_total: Initiative total for defender

        Returns:
            InitiativeResult value object
        """
        return InitiativeResult(
            attacker=attacker,
            defender=defender,
            attacker_roll=attacker_roll,
            defender_roll=defender_roll,
            attacker_total=attacker_total,
            defender_total=defender_total,
        )
