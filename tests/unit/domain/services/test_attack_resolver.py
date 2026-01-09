import pytest

from modules.domain.model.character import Character
from modules.domain.services.attack_resolver import AttackResolver
from tests.doubles.fixed_dice_roller import FixedDiceRoller


class TestAttackResolver:
    """Unit tests for AttackResolver domain service."""

    def test_resolve_attack_calculates_damage(self) -> None:
        """Test that attack damage is correctly calculated as attack_power + dice_roll."""
        # Arrange
        attacker = Character(name="Hero", hp=50, attack_power=10)
        defender = Character(name="Villain", hp=40, attack_power=5)
        resolver = AttackResolver(dice_roller=FixedDiceRoller(values=[4]))

        # Act
        result = resolver.resolve_attack(attacker, defender)

        # Assert
        assert result.total_damage == 14  # 10 (attack_power) + 4 (dice roll)
        assert result.defender_new_hp == 26  # 40 - 14
        assert result.defender_after.hp == 26

    def test_dead_attacker_raises_valueerror(self) -> None:
        """Test that a dead character (hp <= 0) cannot initiate an attack."""
        # Arrange
        dead_attacker = Character(name="Corpse", hp=0, attack_power=10)
        defender = Character(name="Hero", hp=50, attack_power=15)
        resolver = AttackResolver(dice_roller=FixedDiceRoller(values=[3]))

        # Act & Assert
        with pytest.raises(ValueError, match="Dead character cannot attack"):
            resolver.resolve_attack(dead_attacker, defender)

    def test_attack_result_includes_all_fields(self) -> None:
        """Test that AttackResult includes all 8 required fields."""
        # Arrange
        attacker = Character(name="Warrior", hp=60, attack_power=12)
        defender = Character(name="Monster", hp=45, attack_power=8)
        resolver = AttackResolver(dice_roller=FixedDiceRoller(values=[5]))

        # Act
        result = resolver.resolve_attack(attacker, defender)

        # Assert - Verify all 8 fields are populated
        assert result.attacker_name == "Warrior"
        assert result.defender_name == "Monster"
        assert result.dice_roll == 5
        assert result.attack_power == 12
        assert result.total_damage == 17  # 12 + 5
        assert result.defender_old_hp == 45
        assert result.defender_new_hp == 28  # 45 - 17
        assert result.defender_after.hp == 28

    def test_attack_damage_exceeds_defender_hp(self) -> None:
        """Test that damage overflow floors defender HP at 0 (not negative)."""
        # Arrange
        attacker = Character(name="Champion", hp=100, attack_power=50)
        defender = Character(name="Weakling", hp=30, attack_power=2)
        resolver = AttackResolver(dice_roller=FixedDiceRoller(values=[6]))

        # Act
        result = resolver.resolve_attack(attacker, defender)

        # Assert
        assert result.total_damage == 56  # 50 + 6
        assert result.defender_new_hp == 0  # Floored at 0, not -26
        assert result.defender_after.hp == 0  # Verify Character state matches
