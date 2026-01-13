"""Unit tests for CombatRound domain service.

Business rule validation:
1. Attacker attacks first always (DR-06 enforcement)
2. Defender counter-attacks ONLY if HP > 0 after attacker's strike
3. If defender dies, defender_damage = 0 (no counter-attack)
4. combat_ended = True when someone reaches HP = 0
5. Winner identified when combat ends

Testing strategy: Classical TDD with real domain objects
- Use REAL AttackResolver with FixedDiceRoller for deterministic behavior
- Use REAL Character instances (domain entities)
- No mocking of domain services or entities (port-boundary compliance)
"""

import pytest

from src.domain.model.character import Character
from src.domain.services.attack_resolver import AttackResolver
from src.domain.services.combat_round import CombatRound
from tests.doubles.fixed_dice_roller import FixedDiceRoller


class TestCombatRoundShould:
    """Test suite for CombatRound service - attacker advantage enforcement."""

    def test_attacker_attacks_first_always(self):
        """Validate attacker strikes first in round execution.

        Business rule: DR-06 - Attacker advantage
        GIVEN: Two characters ready for combat
        WHEN: Combat round executes
        THEN: Attacker's attack is resolved before defender's counter-attack
        """
        # ARRANGE: Create characters and combat infrastructure
        attacker = Character(name="Thorin", hp=20, attack_power=5)
        defender = Character(name="Goblin", hp=10, attack_power=3)

        # Dice sequence: [attacker_damage_roll, defender_damage_roll]
        dice_roller = FixedDiceRoller([4, 2])
        attack_resolver = AttackResolver(dice_roller=dice_roller)
        combat_round = CombatRound(attack_resolver=attack_resolver)

        # ACT: Execute round
        result = combat_round.execute_round(attacker=attacker, defender=defender, round_number=1)

        # ASSERT: Attacker's attack processed first
        assert result.attacker_damage == 9  # 5 (attack_power) + 4 (dice_roll)
        assert result.round_number == 1
        assert result.attacker.name == "Thorin"
        assert result.defender.name == "Goblin"
        # Defender HP reduced by attacker's damage
        assert result.defender.hp == 1  # 10 - 9 = 1

    def test_defender_counter_attacks_if_alive(self):
        """Validate defender counter-attacks when surviving attacker's strike.

        Business rule: DR-06 - Defender counter-attacks ONLY if HP > 0
        GIVEN: Attacker's strike leaves defender with HP > 0
        WHEN: Combat round executes
        THEN: Defender counter-attacks dealing damage to attacker
        """
        # ARRANGE
        attacker = Character(name="Thorin", hp=20, attack_power=5)
        defender = Character(name="Goblin", hp=10, attack_power=3)

        # Dice: [attacker_roll=4, defender_roll=2]
        # Attacker damage: 5+4=9, Defender survives with 1 HP
        # Defender damage: 3+2=5, Attacker reduced to 15 HP
        dice_roller = FixedDiceRoller([4, 2])
        attack_resolver = AttackResolver(dice_roller=dice_roller)
        combat_round = CombatRound(attack_resolver=attack_resolver)

        # ACT
        result = combat_round.execute_round(attacker=attacker, defender=defender, round_number=1)

        # ASSERT: Defender counter-attacked
        assert result.defender_damage == 5  # 3 (attack_power) + 2 (dice_roll)
        assert result.attacker.hp == 15  # 20 - 5 = 15
        assert result.defender.hp == 1  # Survived attacker's strike
        assert result.defender.is_alive  # Still alive to counter-attack

    def test_no_counter_attack_if_defender_dies(self):
        """Validate NO counter-attack when defender dies from attacker's strike.

        Business rule: DR-06 - Dead defender cannot counter-attack (ATTACKER ADVANTAGE)
        GIVEN: Attacker's strike reduces defender HP to 0
        WHEN: Combat round executes
        THEN: Defender_damage = 0 (no counter-attack occurs)
        """
        # ARRANGE
        attacker = Character(name="Thorin", hp=20, attack_power=5)
        defender = Character(name="Goblin", hp=5, attack_power=3)  # Low HP - will die

        # Dice: [attacker_roll=6]
        # Attacker damage: 5+6=11, Defender dies (5 - 11 = 0, floored)
        # No counter-attack (defender dead)
        dice_roller = FixedDiceRoller([6])  # Only one roll needed (defender dies)
        attack_resolver = AttackResolver(dice_roller=dice_roller)
        combat_round = CombatRound(attack_resolver=attack_resolver)

        # ACT
        result = combat_round.execute_round(attacker=attacker, defender=defender, round_number=1)

        # ASSERT: No counter-attack damage (CRITICAL business rule)
        assert result.defender_damage == 0, "Dead defender cannot counter-attack"
        assert result.defender.hp == 0, "Defender should be dead"
        assert not result.defender.is_alive, "Defender should not be alive"
        assert result.attacker.hp == 20, "Attacker should be unharmed (no counter-attack)"

    def test_combat_ended_when_defender_dies(self):
        """Validate combat_ended flag set when defender dies.

        Business rule: Combat ends when any character reaches HP = 0
        GIVEN: Attacker kills defender
        WHEN: Combat round executes
        THEN: combat_ended = True, winner = attacker
        """
        # ARRANGE
        attacker = Character(name="Thorin", hp=20, attack_power=5)
        defender = Character(name="Goblin", hp=5, attack_power=3)

        dice_roller = FixedDiceRoller([6])  # Kills defender (5+6=11 damage)
        attack_resolver = AttackResolver(dice_roller=dice_roller)
        combat_round = CombatRound(attack_resolver=attack_resolver)

        # ACT
        result = combat_round.execute_round(attacker=attacker, defender=defender, round_number=1)

        # ASSERT: Combat ended with winner
        assert result.combat_ended is True, "Combat should end when defender dies"
        assert result.winner is not None, "Winner should be identified"
        assert result.winner.name == "Thorin", "Attacker should be winner"

    def test_combat_ended_when_attacker_dies_in_counter(self):
        """Validate combat_ended flag set when attacker dies during counter-attack.

        Business rule: Combat ends when any character reaches HP = 0
        GIVEN: Defender's counter-attack kills attacker
        WHEN: Combat round executes
        THEN: combat_ended = True, winner = defender
        """
        # ARRANGE: Attacker with low HP, strong defender
        attacker = Character(name="Weakling", hp=5, attack_power=2)
        defender = Character(name="Tank", hp=20, attack_power=8)

        # Dice: [attacker_roll=1, defender_roll=6]
        # Attacker damage: 2+1=3, Defender survives with 17 HP
        # Defender damage: 8+6=14, Attacker dies (5 - 14 = 0, floored)
        dice_roller = FixedDiceRoller([1, 6])
        attack_resolver = AttackResolver(dice_roller=dice_roller)
        combat_round = CombatRound(attack_resolver=attack_resolver)

        # ACT
        result = combat_round.execute_round(attacker=attacker, defender=defender, round_number=1)

        # ASSERT: Combat ended with defender as winner
        assert result.combat_ended is True, "Combat should end when attacker dies"
        assert result.winner is not None, "Winner should be identified"
        assert result.winner.name == "Tank", "Defender should be winner"
        assert result.attacker.hp == 0, "Attacker should be dead"

    def test_combat_continues_when_both_survive(self):
        """Validate combat_ended = False when both characters survive round.

        Business rule: Combat continues until one reaches HP = 0
        GIVEN: Both characters survive the round
        WHEN: Combat round executes
        THEN: combat_ended = False, winner = None
        """
        # ARRANGE
        attacker = Character(name="Thorin", hp=20, attack_power=5)
        defender = Character(name="Goblin", hp=10, attack_power=3)

        # Dice: [attacker_roll=4, defender_roll=2]
        # Both survive (Goblin: 1 HP, Thorin: 15 HP)
        dice_roller = FixedDiceRoller([4, 2])
        attack_resolver = AttackResolver(dice_roller=dice_roller)
        combat_round = CombatRound(attack_resolver=attack_resolver)

        # ACT
        result = combat_round.execute_round(attacker=attacker, defender=defender, round_number=1)

        # ASSERT: Combat continues
        assert result.combat_ended is False, "Combat should continue (both alive)"
        assert result.winner is None, "No winner yet"
        assert result.attacker.is_alive, "Attacker should be alive"
        assert result.defender.is_alive, "Defender should be alive"

    def test_round_result_is_immutable(self):
        """Validate RoundResult is frozen dataclass (immutability).

        Business rule: Value objects are immutable
        GIVEN: RoundResult created
        WHEN: Attempt to modify field
        THEN: Raises FrozenInstanceError
        """
        # ARRANGE
        attacker = Character(name="Thorin", hp=20, attack_power=5)
        defender = Character(name="Goblin", hp=10, attack_power=3)

        dice_roller = FixedDiceRoller([4, 2])
        attack_resolver = AttackResolver(dice_roller=dice_roller)
        combat_round = CombatRound(attack_resolver=attack_resolver)

        # ACT
        result = combat_round.execute_round(attacker=attacker, defender=defender, round_number=1)

        # ASSERT: Cannot modify frozen dataclass
        with pytest.raises(AttributeError):
            result.round_number = 999  # Should fail - frozen dataclass
