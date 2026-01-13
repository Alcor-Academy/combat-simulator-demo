"""Unit tests for Character value object.

Character is an immutable value object (frozen dataclass) representing
a combatant with name, HP, attack power, and derived agility.

Business rules tested:
- Immutability: receive_damage returns NEW instance, original unchanged
- Validation: Name non-empty, HP >= 0, Attack power > 0
- Derived agility: agility = hp + attack_power (computed property)
- Liveness: is_alive = hp > 0
- HP flooring: HP never goes negative
"""

from dataclasses import FrozenInstanceError

import pytest

from src.domain.model.character import Character


class TestCharacterCreation:
    """Test character creation and validation."""

    def test_creates_character_with_valid_attributes(self):
        """Character created with valid name, HP, and attack power."""
        character = Character(name="Thorin", hp=20, attack_power=5)

        assert character.name == "Thorin"
        assert character.hp == 20
        assert character.attack_power == 5

    def test_rejects_empty_name(self):
        """Character creation fails when name is empty."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            Character(name="", hp=20, attack_power=5)

    def test_rejects_negative_hp(self):
        """Character creation fails when HP is negative."""
        with pytest.raises(ValueError, match="HP cannot be negative"):
            Character(name="Thorin", hp=-5, attack_power=5)

    def test_rejects_non_positive_attack_power(self):
        """Character creation fails when attack power is <= 0."""
        with pytest.raises(ValueError, match="Attack power must be positive"):
            Character(name="Thorin", hp=20, attack_power=0)


class TestAgilityProperty:
    """Test derived agility property (hp + attack_power)."""

    def test_calculates_agility_as_hp_plus_attack(self):
        """Agility equals HP + attack_power."""
        character = Character(name="Warrior", hp=20, attack_power=5)

        assert character.agility == 25  # 20 + 5

    def test_updates_agility_when_hp_decreases(self):
        """Agility decreases automatically when HP drops."""
        original = Character(name="Warrior", hp=20, attack_power=5)
        damaged = original.receive_damage(10)

        assert original.agility == 25  # Original unchanged: 20 + 5
        assert damaged.agility == 15  # Damaged: 10 + 5


class TestIsAliveProperty:
    """Test is_alive property (hp > 0)."""

    def test_returns_true_when_hp_positive(self):
        """Character is alive when HP > 0."""
        character = Character(name="Alive", hp=10, attack_power=5)

        assert character.is_alive is True

    def test_returns_false_when_hp_zero(self):
        """Character is dead when HP = 0."""
        character = Character(name="Dead", hp=0, attack_power=5)

        assert character.is_alive is False


class TestReceiveDamage:
    """Test immutable damage application."""

    def test_returns_new_instance_with_reduced_hp(self):
        """receive_damage returns NEW Character with HP reduced."""
        original = Character(name="Thorin", hp=20, attack_power=5)
        damaged = original.receive_damage(7)

        # New instance with reduced HP
        assert damaged.hp == 13  # 20 - 7
        assert damaged.name == "Thorin"
        assert damaged.attack_power == 5

        # Original unchanged (immutability)
        assert original.hp == 20
        assert damaged is not original  # Different instances

    def test_floors_hp_at_zero(self):
        """HP never goes negative - floors at 0."""
        character = Character(name="Weak", hp=5, attack_power=3)
        damaged = character.receive_damage(10)  # Overkill damage

        assert damaged.hp == 0  # Floored at 0, not -5

    def test_preserves_immutability_when_flooring(self):
        """Original remains unchanged even when damage exceeds HP."""
        original = Character(name="Fragile", hp=5, attack_power=3)
        damaged = original.receive_damage(100)  # Massive overkill

        assert original.hp == 5  # Original unchanged
        assert damaged.hp == 0  # New instance floored at 0


class TestFrozenDataclass:
    """Test that Character is truly immutable (frozen)."""

    def test_prevents_attribute_mutation(self):
        """Frozen dataclass prevents field mutation."""
        character = Character(name="Immutable", hp=20, attack_power=5)

        # Attempting to mutate should raise FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            character.hp = 15  # type: ignore
