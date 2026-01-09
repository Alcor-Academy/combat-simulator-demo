import pytest

from modules.domain.model.character import Character


def test_character_creation_with_valid_attributes() -> None:
    character = Character(name="Hero", hp=50, attack_power=15)
    assert character.name == "Hero"
    assert character.hp == 50
    assert character.attack_power == 15


def test_agility_computed_from_hp_plus_attack_power() -> None:
    character = Character(name="Hero", hp=50, attack_power=15)
    assert character.agility == 65  # 50 + 15
    character2 = Character(name="Villain", hp=30, attack_power=20)
    assert character2.agility == 50  # 30 + 20


def test_is_alive_when_hp_greater_than_zero() -> None:
    alive = Character(name="Hero", hp=50, attack_power=15)
    assert alive.is_alive is True
    dead = Character(name="Corpse", hp=0, attack_power=10)
    assert dead.is_alive is False


def test_receive_damage_returns_new_instance() -> None:
    original = Character(name="Hero", hp=50, attack_power=15)
    damaged = original.receive_damage(10)
    assert damaged.hp == 40
    assert original.hp == 50  # Original unchanged (immutability)
    assert damaged is not original  # Different instance


def test_receive_damage_floors_hp_at_zero() -> None:
    character = Character(name="Hero", hp=10, attack_power=15)
    overkill = character.receive_damage(50)
    assert overkill.hp == 0  # Not -40
    assert overkill.is_alive is False


def test_validation_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="Name cannot be empty"):
        Character(name="", hp=50, attack_power=15)


def test_validation_rejects_negative_hp() -> None:
    with pytest.raises(ValueError, match="HP must be non-negative"):
        Character(name="Hero", hp=-10, attack_power=15)


def test_validation_rejects_non_positive_attack_power() -> None:
    with pytest.raises(ValueError, match="Attack power must be positive"):
        Character(name="Hero", hp=50, attack_power=0)
    with pytest.raises(ValueError, match="Attack power must be positive"):
        Character(name="Hero", hp=50, attack_power=-5)
