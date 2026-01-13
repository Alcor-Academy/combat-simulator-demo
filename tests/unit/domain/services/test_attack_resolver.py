"""Unit tests for AttackResolver domain service.

Business rules tested:
1. Damage calculation: damage = attack_power + dice_roll
2. HP reduction: defender HP reduced by damage amount
3. HP flooring: defender HP cannot go below 0
4. Dead attacker validation: dead character (HP=0) cannot attack
5. Immutability: defender_after is NEW instance, original unchanged

Test strategy: Classical TDD with real Characters.
Mock boundary: DiceRoller (port) - use FixedDiceRoller test double.
"""

import pytest

from src.domain.model.character import Character
from src.domain.services.attack_resolver import AttackResolver
from tests.doubles.fixed_dice_roller import FixedDiceRoller


class TestAttackResolver:
    """Test suite for AttackResolver.resolve_attack() method."""

    def test_damage_calculation(self):
        """Damage = attack_power + dice_roll.

        GIVEN: Attacker with 8 attack_power, defender with 20 HP
        WHEN: resolve_attack() is called with dice rolling 4
        THEN: Total damage is 12 (8 + 4)
        """
        attacker = Character(name="Warrior", hp=25, attack_power=8)
        defender = Character(name="Goblin", hp=20, attack_power=3)
        dice_roller = FixedDiceRoller([4])

        resolver = AttackResolver(dice_roller=dice_roller)
        result = resolver.resolve_attack(attacker, defender)

        assert result.attack_power == 8
        assert result.dice_roll == 4
        assert result.total_damage == 12

    def test_hp_reduction(self):
        """Defender HP reduced correctly by damage amount.

        GIVEN: Defender with 20 HP, attack dealing 12 damage
        WHEN: resolve_attack() is called
        THEN: Defender HP reduced from 20 to 8
        """
        attacker = Character(name="Warrior", hp=25, attack_power=8)
        defender = Character(name="Goblin", hp=20, attack_power=3)
        dice_roller = FixedDiceRoller([4])

        resolver = AttackResolver(dice_roller=dice_roller)
        result = resolver.resolve_attack(attacker, defender)

        assert result.defender_old_hp == 20
        assert result.defender_new_hp == 8
        assert result.defender_after.hp == 8

    def test_hp_flooring(self):
        """HP floors at 0 when damage exceeds current HP.

        GIVEN: Defender with 5 HP, attack dealing 20 damage
        WHEN: resolve_attack() is called
        THEN: Defender HP floors at 0 (not negative)
        """
        attacker = Character(name="Warrior", hp=25, attack_power=15)
        defender = Character(name="Goblin", hp=5, attack_power=3)
        dice_roller = FixedDiceRoller([5])  # Total damage: 15 + 5 = 20

        resolver = AttackResolver(dice_roller=dice_roller)
        result = resolver.resolve_attack(attacker, defender)

        assert result.total_damage == 20
        assert result.defender_old_hp == 5
        assert result.defender_new_hp == 0  # Floors at 0, not -15
        assert result.defender_after.hp == 0
        assert not result.defender_after.is_alive

    def test_dead_attacker_error(self):
        """Dead character cannot attack - raises ValueError.

        GIVEN: Attacker with 0 HP (dead), defender with 20 HP
        WHEN: resolve_attack() is called
        THEN: ValueError raised with message 'Dead character cannot attack'
        """
        dead_attacker = Character(name="Ghost", hp=0, attack_power=5)
        defender = Character(name="Target", hp=20, attack_power=3)
        dice_roller = FixedDiceRoller([4])

        resolver = AttackResolver(dice_roller=dice_roller)

        with pytest.raises(ValueError, match="Dead character cannot attack") as exc_info:
            resolver.resolve_attack(dead_attacker, defender)

        assert str(exc_info.value) == "Dead character cannot attack"

    def test_immutability(self):
        """defender_after is NEW instance, original defender unchanged.

        GIVEN: Original defender with 20 HP
        WHEN: resolve_attack() is called dealing 12 damage
        THEN: Original defender still has 20 HP (immutability)
              defender_after is different instance with 8 HP
        """
        attacker = Character(name="Warrior", hp=25, attack_power=8)
        original_defender = Character(name="Goblin", hp=20, attack_power=3)
        dice_roller = FixedDiceRoller([4])

        resolver = AttackResolver(dice_roller=dice_roller)
        result = resolver.resolve_attack(attacker, original_defender)

        # Original unchanged
        assert original_defender.hp == 20

        # New instance returned
        assert result.defender_after.hp == 8
        assert result.defender_after is not original_defender
        assert result.defender_after.name == original_defender.name

    def test_attack_result_contains_all_combat_details(self):
        """AttackResult contains complete combat information.

        GIVEN: Combat between two characters
        WHEN: resolve_attack() is called
        THEN: AttackResult contains all required fields
        """
        attacker = Character(name="Warrior", hp=25, attack_power=8)
        defender = Character(name="Goblin", hp=20, attack_power=3)
        dice_roller = FixedDiceRoller([4])

        resolver = AttackResolver(dice_roller=dice_roller)
        result = resolver.resolve_attack(attacker, defender)

        assert result.attacker_name == "Warrior"
        assert result.defender_name == "Goblin"
        assert result.dice_roll == 4
        assert result.attack_power == 8
        assert result.total_damage == 12
        assert result.defender_old_hp == 20
        assert result.defender_new_hp == 8
        assert result.defender_after is not None
