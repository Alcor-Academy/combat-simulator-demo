"""Unit tests for InitiativeResolver domain service.

Tests validate initiative calculation, tie-breaker rules, and immutable result.

Business rules under test:
- Initiative = character.agility + D6 roll
- Higher total wins (becomes attacker)
- Tie-breaker #1: Higher base agility wins
- Tie-breaker #2: First character wins (deterministic)
- InitiativeResult is immutable frozen dataclass
"""

from src.domain.model.character import Character
from src.domain.model.initiative_result import InitiativeResult
from src.domain.services.initiative_resolver import InitiativeResolver
from tests.doubles.fixed_dice_roller import FixedDiceRoller


class TestInitiativeResult:
    """Tests for InitiativeResult value object."""

    def test_initiative_result_creation(self):
        """InitiativeResult captures attacker and defender with totals.

        Business rule: Initiative result immutably stores attacker, defender,
        their rolls, and calculated totals for combat execution.
        """
        thorin = Character(name="Thorin", hp=20, attack_power=5)
        goblin = Character(name="Goblin", hp=10, attack_power=3)

        result = InitiativeResult(
            attacker=thorin,
            defender=goblin,
            attacker_roll=3,
            defender_roll=5,
            attacker_total=28,  # agility=25 + roll=3
            defender_total=18,  # agility=13 + roll=5
        )

        assert result.attacker.name == "Thorin"
        assert result.defender.name == "Goblin"
        assert result.attacker_roll == 3
        assert result.defender_roll == 5
        assert result.attacker_total == 28
        assert result.defender_total == 18


class TestInitiativeResolver:
    """Tests for InitiativeResolver domain service."""

    def test_initiative_calculation(self):
        """Initiative = character.agility + dice roll.

        Business rule: Initiative total is sum of agility (hp + attack_power)
        and D6 roll. This determines combat order.
        """
        thorin = Character(name="Thorin", hp=20, attack_power=5)  # agility=25
        goblin = Character(name="Goblin", hp=10, attack_power=3)  # agility=13

        # Thorin rolls 3, Goblin rolls 5
        dice_roller = FixedDiceRoller([3, 5])
        resolver = InitiativeResolver(dice_roller=dice_roller)

        result = resolver.roll_initiative(thorin, goblin)

        # Thorin: 25 + 3 = 28
        # Goblin: 13 + 5 = 18
        assert result.attacker_total == 28
        assert result.defender_total == 18

    def test_higher_total_wins(self):
        """Higher initiative total determines attacker.

        Business rule: Character with higher (agility + roll) becomes attacker
        and strikes first in all combat rounds.
        """
        thorin = Character(name="Thorin", hp=20, attack_power=5)  # agility=25
        goblin = Character(name="Goblin", hp=10, attack_power=3)  # agility=13

        # Thorin rolls 3 → total 28, Goblin rolls 5 → total 18
        dice_roller = FixedDiceRoller([3, 5])
        resolver = InitiativeResolver(dice_roller=dice_roller)

        result = resolver.roll_initiative(thorin, goblin)

        assert result.attacker.name == "Thorin"
        assert result.defender.name == "Goblin"

    def test_tie_breaker_agility(self):
        """When totals equal, higher base agility wins.

        Business rule: If initiative totals match, character with higher
        base agility (hp + attack_power) becomes attacker.
        """
        # Create characters where totals will match but agility differs
        # Elf: agility=25, Dwarf: agility=23
        # Both need same total: Elf rolls 3 → 28, Dwarf rolls 5 → 28
        elf = Character(name="Elf", hp=18, attack_power=7)  # agility=25
        dwarf = Character(name="Dwarf", hp=20, attack_power=3)  # agility=23

        # Elf rolls 3 → total 28, Dwarf rolls 5 → total 28 (TIED)
        dice_roller = FixedDiceRoller([3, 5])
        resolver = InitiativeResolver(dice_roller=dice_roller)

        result = resolver.roll_initiative(elf, dwarf)

        # Elf has higher base agility (25 > 23) → wins tie
        assert result.attacker.name == "Elf"
        assert result.defender.name == "Dwarf"
        assert result.attacker_total == 28
        assert result.defender_total == 28
        # Verify agility difference
        assert result.attacker.agility == 25
        assert result.defender.agility == 23

    def test_tie_breaker_first_char(self):
        """When totals and agility equal, first character wins.

        Business rule: If initiative totals AND base agility match exactly,
        first character (char1 parameter) becomes attacker for determinism.
        """
        # Both have identical stats and rolls → perfect tie
        elf = Character(name="Elf", hp=15, attack_power=10)  # agility=25
        dwarf = Character(name="Dwarf", hp=20, attack_power=5)  # agility=25

        # Both roll 5 → both total 30, both agility 25
        dice_roller = FixedDiceRoller([5, 5])
        resolver = InitiativeResolver(dice_roller=dice_roller)

        result = resolver.roll_initiative(elf, dwarf)

        # First character (Elf) wins tie-breaker
        assert result.attacker.name == "Elf"
        assert result.defender.name == "Dwarf"
        assert result.attacker.agility == 25
        assert result.defender.agility == 25
        assert result.attacker_total == 30
        assert result.defender_total == 30

    def test_lower_total_character_becomes_defender(self):
        """Character with lower initiative total becomes defender.

        Business rule: Loser of initiative roll becomes defender and
        attacks second (if survives attacker's first strike).
        """
        warrior = Character(name="Warrior", hp=15, attack_power=4)  # agility=19
        mage = Character(name="Mage", hp=12, attack_power=6)  # agility=18

        # Warrior rolls 2 → total 21, Mage rolls 6 → total 24
        dice_roller = FixedDiceRoller([2, 6])
        resolver = InitiativeResolver(dice_roller=dice_roller)

        result = resolver.roll_initiative(warrior, mage)

        # Mage wins (24 > 21)
        assert result.attacker.name == "Mage"
        assert result.defender.name == "Warrior"
