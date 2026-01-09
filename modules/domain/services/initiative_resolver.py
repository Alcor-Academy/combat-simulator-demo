"""Initiative resolver domain service.

Determines combat order by rolling initiative for both characters.
Initiative is calculated ONCE at combat start and determines who attacks
first for the ENTIRE combat, not per round.

Business rules:
- Initiative = character.agility + D6 roll
- Higher total becomes attacker (attacks first)
- Tie-breaker 1: If totals equal, higher base agility wins
- Tie-breaker 2: If agility equal, first character (char1) wins
"""

from modules.domain.model.character import Character
from modules.domain.model.initiative_result import InitiativeResult
from modules.domain.ports.dice_roller import DiceRoller


class InitiativeResolver:
    """Resolves initiative to determine combat order.

    Uses dependency injection for dice rolling to enable deterministic testing.
    Applies two-level tie-breaker rules to ensure deterministic combat order.
    """

    def __init__(self, dice_roller: DiceRoller) -> None:
        """Initialize resolver with dice rolling capability.

        Args:
            dice_roller: Port for rolling D6 dice (dependency injection).
        """
        self._dice_roller = dice_roller

    def roll_initiative(self, char1: Character, char2: Character) -> InitiativeResult:
        """Roll initiative for both characters and determine combat order.

        Calculates initiative (agility + D6) for both characters and applies
        tie-breaker rules to determine attacker (who strikes first) and
        defender (who strikes second).

        Business logic:
        1. Roll D6 for each character
        2. Calculate totals: agility + roll
        3. Higher total wins (becomes attacker)
        4. Tie-breaker 1: If totals equal, higher base agility wins
        5. Tie-breaker 2: If agility equal, first character wins

        Args:
            char1: First character in combat
            char2: Second character in combat

        Returns:
            InitiativeResult with attacker, defender, rolls, and totals
        """
        # Roll initiative for both characters
        char1_roll = self._dice_roller.roll()
        char2_roll = self._dice_roller.roll()

        # Calculate initiative totals
        char1_total = char1.agility + char1_roll
        char2_total = char2.agility + char2_roll

        # Determine winner with tie-breaker logic
        if char1_total > char2_total:
            # char1 wins outright (higher initiative total)
            attacker, defender = char1, char2
            attacker_roll, defender_roll = char1_roll, char2_roll
            attacker_total, defender_total = char1_total, char2_total
        elif char2_total > char1_total:
            # char2 wins outright (higher initiative total)
            attacker, defender = char2, char1
            attacker_roll, defender_roll = char2_roll, char1_roll
            attacker_total, defender_total = char2_total, char1_total
        # Tie on totals - apply tie-breaker by base agility
        elif char1.agility >= char2.agility:
            # char1 wins tie-breaker (higher or equal base agility)
            # Note: >= ensures first character wins when agility equal
            attacker, defender = char1, char2
            attacker_roll, defender_roll = char1_roll, char2_roll
            attacker_total, defender_total = char1_total, char2_total
        else:
            # char2 wins tie-breaker (higher base agility)
            attacker, defender = char2, char1
            attacker_roll, defender_roll = char2_roll, char1_roll
            attacker_total, defender_total = char2_total, char1_total

        return InitiativeResult(
            attacker=attacker,
            defender=defender,
            attacker_roll=attacker_roll,
            defender_roll=defender_roll,
            attacker_total=attacker_total,
            defender_total=defender_total,
        )
