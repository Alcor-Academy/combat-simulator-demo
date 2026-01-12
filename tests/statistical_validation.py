"""Statistical validation for random HP and attack generation.

Validates that random generation produces values within expected ranges
over multiple iterations.
"""

import sys
from unittest.mock import Mock

from modules.infrastructure.cli.character_creator import CharacterCreator
from modules.infrastructure.cli.config import CLIConfig
from modules.infrastructure.cli.console_output import ConsoleOutput
from modules.infrastructure.random_dice_roller import RandomDiceRoller


def validate_random_hp(iterations: int = 100) -> None:
    """Validate random HP generation over multiple iterations."""
    print(f"\n🎲 Random HP Validation ({iterations} iterations)")
    print("=" * 60)

    # Create dependencies
    dice_roller = RandomDiceRoller()  # No seed - truly random
    mock_console = Mock()
    config = CLIConfig.test_mode()
    console_output = ConsoleOutput(mock_console, config)
    creator = CharacterCreator(console_output, dice_roller)

    # Generate random HP values
    hp_values = []
    for _ in range(iterations):
        hp = creator._random_hp()
        hp_values.append(hp)

    # Statistical analysis
    min_hp = min(hp_values)
    max_hp = max(hp_values)
    avg_hp = sum(hp_values) / len(hp_values)

    # Expected range: [20-80]
    expected_min = 20
    expected_max = 80

    # Validation
    all_in_range = all(expected_min <= hp <= expected_max for hp in hp_values)

    print(f"Expected Range: [{expected_min}-{expected_max}]")
    print(f"Observed Range: [{min_hp}-{max_hp}]")
    print(f"Average HP: {avg_hp:.2f}")
    print(f"All values in range: {'✅ PASS' if all_in_range else '❌ FAIL'}")

    if not all_in_range:
        out_of_range = [hp for hp in hp_values if hp < expected_min or hp > expected_max]
        print(f"❌ Out of range values: {out_of_range}")
        raise AssertionError(f"Found {len(out_of_range)} values outside expected range")

    return min_hp, max_hp, avg_hp


def validate_random_attack(iterations: int = 100) -> None:
    """Validate random attack generation over multiple iterations."""
    print(f"\n⚔️  Random Attack Validation ({iterations} iterations)")
    print("=" * 60)

    # Create dependencies
    dice_roller = RandomDiceRoller()  # No seed - truly random
    mock_console = Mock()
    config = CLIConfig.test_mode()
    console_output = ConsoleOutput(mock_console, config)
    creator = CharacterCreator(console_output, dice_roller)

    # Generate random attack values
    attack_values = []
    for _ in range(iterations):
        attack = creator._random_attack()
        attack_values.append(attack)

    # Statistical analysis
    min_attack = min(attack_values)
    max_attack = max(attack_values)
    avg_attack = sum(attack_values) / len(attack_values)

    # Expected range: [5-15]
    expected_min = 5
    expected_max = 15

    # Validation
    all_in_range = all(expected_min <= atk <= expected_max for atk in attack_values)

    print(f"Expected Range: [{expected_min}-{expected_max}]")
    print(f"Observed Range: [{min_attack}-{max_attack}]")
    print(f"Average Attack: {avg_attack:.2f}")
    print(f"All values in range: {'✅ PASS' if all_in_range else '❌ FAIL'}")

    if not all_in_range:
        out_of_range = [atk for atk in attack_values if atk < expected_min or atk > expected_max]
        print(f"❌ Out of range values: {out_of_range}")
        raise AssertionError(f"Found {len(out_of_range)} values outside expected range")

    return min_attack, max_attack, avg_attack


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("STATISTICAL VALIDATION: Random Generation")
    print("=" * 60)

    try:
        # Run validations
        hp_min, hp_max, hp_avg = validate_random_hp(100)
        atk_min, atk_max, atk_avg = validate_random_attack(100)

        # Summary
        print("\n" + "=" * 60)
        print("✅ ALL VALIDATIONS PASSED")
        print("=" * 60)
        print(f"HP Range: [{hp_min}-{hp_max}] (avg: {hp_avg:.2f})")
        print(f"Attack Range: [{atk_min}-{atk_max}] (avg: {atk_avg:.2f})")
        print()

    except AssertionError as e:
        print("\n" + "=" * 60)
        print("❌ VALIDATION FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        sys.exit(1)
