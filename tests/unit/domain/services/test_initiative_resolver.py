"""Unit tests for InitiativeResolver domain service.

Tests verify initiative calculation and tie-breaker logic:
1. Initiative = character.agility + dice_roll
2. Higher total becomes attacker
3. Tie-breaker 1: Higher base agility wins when totals equal
4. Tie-breaker 2: First character wins when agility equal
"""

from modules.domain.model.character import Character
from modules.domain.services.initiative_resolver import InitiativeResolver
from tests.doubles.fixed_dice_roller import FixedDiceRoller


def test_higher_initiative_total_wins() -> None:
    """Test that character with higher initiative total becomes attacker.

    Business rule: Initiative = agility + D6 roll, higher total wins.

    Setup:
    - char1 (Hero): agility=65 (50 HP + 15 attack), roll=3 → total=68
    - char2 (Villain): agility=50 (40 HP + 10 attack), roll=2 → total=52

    Expected: Hero wins initiative (68 > 52), becomes attacker.
    """
    dice = FixedDiceRoller([3, 2])  # char1 rolls 3, char2 rolls 2
    resolver = InitiativeResolver(dice)

    char1 = Character(name="Hero", hp=50, attack_power=15)  # agility = 65
    char2 = Character(name="Villain", hp=40, attack_power=10)  # agility = 50

    result = resolver.roll_initiative(char1, char2)

    # char1: 65 + 3 = 68, char2: 50 + 2 = 52
    assert result.attacker.name == "Hero"
    assert result.defender.name == "Villain"
    assert result.attacker_total == 68
    assert result.defender_total == 52


def test_tie_breaker_higher_agility_wins() -> None:
    """Test that higher base agility wins when initiative totals are equal.

    Business rule: When initiative totals tie, character with higher base
    agility (hp + attack_power) becomes attacker.

    Setup (corrected to create proper tie scenario):
    - char1 (Hero): agility=50 (40 HP + 10 attack), roll=5 → total=55
    - char2 (Villain): agility=53 (30 HP + 23 attack), roll=2 → total=55

    CORRECTED: Changed character agilities to create tie scenario.
    Both totals equal (55 vs 55), but char2 has higher base agility (53 > 50).

    Expected: Villain wins tie-breaker by higher base agility.
    """
    char1 = Character(name="Hero", hp=40, attack_power=10)  # agility = 50
    char2 = Character(name="Villain", hp=30, attack_power=23)  # agility = 53

    dice = FixedDiceRoller([5, 2])  # char1: 50+5=55, char2: 53+2=55 (TIE)
    resolver = InitiativeResolver(dice)

    result = resolver.roll_initiative(char1, char2)

    # Totals equal (55 vs 55), but char2 has higher base agility (53 > 50)
    assert result.attacker.name == "Villain"  # Higher base agility wins
    assert result.defender.name == "Hero"
    assert result.attacker_total == 55
    assert result.defender_total == 55


def test_tie_breaker_first_character_wins_if_agility_equal() -> None:
    """Test that first character wins when both totals AND agility are equal.

    Business rule: When initiative totals AND base agility are equal,
    first character (char1 parameter) becomes attacker.

    Setup:
    - char1 (Hero): agility=50 (40 HP + 10 attack), roll=3 → total=53
    - char2 (Villain): agility=50 (30 HP + 20 attack), roll=3 → total=53

    Both have same agility (50), both roll 3 → totals equal (53).

    Expected: Hero wins (first parameter in roll_initiative call).
    """
    dice = FixedDiceRoller([3, 3])  # Both roll 3 (equal)
    resolver = InitiativeResolver(dice)

    char1 = Character(name="Hero", hp=40, attack_power=10)  # agility = 50
    char2 = Character(name="Villain", hp=30, attack_power=20)  # agility = 50

    result = resolver.roll_initiative(char1, char2)

    # Totals equal, agility equal → char1 (first parameter) wins
    assert result.attacker.name == "Hero"
    assert result.defender.name == "Villain"
    assert result.attacker_total == 53
    assert result.defender_total == 53


def test_char2_higher_initiative_wins() -> None:
    """Test that char2 wins when char2 has higher initiative total.

    Business rule: Initiative = agility + D6 roll, higher total wins.
    This validates the char2 victory path explicitly.

    Setup:
    - char1 (Hero): agility=50 (40 HP + 10 attack), roll=2 → total=52
    - char2 (Villain): agility=60 (30 HP + 30 attack), roll=5 → total=65

    Expected: Villain wins initiative (65 > 52), becomes attacker.
    """
    dice = FixedDiceRoller([2, 5])  # char1 rolls 2, char2 rolls 5
    resolver = InitiativeResolver(dice)

    char1 = Character(name="Hero", hp=40, attack_power=10)  # agility = 50
    char2 = Character(name="Villain", hp=30, attack_power=30)  # agility = 60

    result = resolver.roll_initiative(char1, char2)

    # char1: 50 + 2 = 52, char2: 60 + 5 = 65
    assert result.attacker.name == "Villain"  # char2 has higher total
    assert result.defender.name == "Hero"
    assert result.attacker_total == 65
    assert result.defender_total == 52
