"""Unit tests for CombatRound domain service.

Tests the orchestration of one combat round with attacker advantage rule:
- Attacker attacks first
- Defender counter-attacks ONLY if alive after attacker's strike
- Dead defender cannot counter-attack (critical business rule)
"""

from unittest.mock import Mock

from modules.domain.model.attack_result import AttackResult
from modules.domain.model.character import Character
from modules.domain.model.round_result import RoundResult
from modules.domain.services.attack_resolver import AttackResolver
from modules.domain.services.combat_round import CombatRound


class TestCombatRoundShould:
    """Test suite for CombatRound service."""

    def test_attacker_attacks_first(self) -> None:
        """Attacker should execute their attack first in the round.

        GIVEN: Two characters in combat
        WHEN: execute_round is called
        THEN: attacker_action contains AttackResult from attacker's strike
              AND attacker's strike is the FIRST attack resolved
        """
        # Arrange
        attacker = Character(name="Warrior", hp=100, attack_power=15)
        defender = Character(name="Goblin", hp=50, attack_power=8)

        # Mock AttackResolver to control attack outcome
        mock_attack_resolver = Mock(spec=AttackResolver)

        # Attacker's strike deals 15 damage, defender survives with 35 HP
        defender_after_attack = Character(name="Goblin", hp=35, attack_power=8)
        attacker_attack_result = AttackResult(
            attacker_name="Warrior",
            defender_name="Goblin",
            dice_roll=4,
            attack_power=15,
            total_damage=15,
            defender_old_hp=50,
            defender_new_hp=35,
            defender_after=defender_after_attack,
        )

        # Defender's counter-attack (needed since defender survives)
        attacker_after_counter = Character(name="Warrior", hp=92, attack_power=15)
        defender_counter_result = AttackResult(
            attacker_name="Goblin",
            defender_name="Warrior",
            dice_roll=3,
            attack_power=8,
            total_damage=8,
            defender_old_hp=100,
            defender_new_hp=92,
            defender_after=attacker_after_counter,
        )

        # Configure mock to return results for both attacks
        mock_attack_resolver.resolve_attack.side_effect = [
            attacker_attack_result,
            defender_counter_result,
        ]

        combat_round = CombatRound(attack_resolver=mock_attack_resolver)

        # Act
        result = combat_round.execute_round(attacker, defender, round_number=1)

        # Assert - attacker attacks first
        assert isinstance(result, RoundResult)
        assert result.attacker_action == attacker_attack_result
        assert result.round_number == 1
        # Verify first call was attacker → defender
        first_call = mock_attack_resolver.resolve_attack.call_args_list[0]
        assert first_call[0][0] == attacker
        assert first_call[0][1] == defender

    def test_defender_counter_attacks_if_alive(self) -> None:
        """Defender should counter-attack if still alive after attacker's strike.

        GIVEN: Attacker deals non-lethal damage (defender survives with HP > 0)
        WHEN: execute_round is called
        THEN: defender_action contains AttackResult from defender's counter-attack
              AND attacker HP is reduced by counter-attack
        """
        # Arrange
        attacker = Character(name="Warrior", hp=100, attack_power=15)
        defender = Character(name="Goblin", hp=50, attack_power=8)

        # Mock AttackResolver
        mock_attack_resolver = Mock(spec=AttackResolver)

        # Attacker's strike: 15 damage, defender survives with 35 HP
        defender_after_attack = Character(name="Goblin", hp=35, attack_power=8)
        attacker_attack_result = AttackResult(
            attacker_name="Warrior",
            defender_name="Goblin",
            dice_roll=4,
            attack_power=15,
            total_damage=15,
            defender_old_hp=50,
            defender_new_hp=35,
            defender_after=defender_after_attack,
        )

        # Defender's counter-attack: 8 damage, attacker reduced to 92 HP
        attacker_after_counter = Character(name="Warrior", hp=92, attack_power=15)
        defender_counter_result = AttackResult(
            attacker_name="Goblin",
            defender_name="Warrior",
            dice_roll=3,
            attack_power=8,
            total_damage=8,
            defender_old_hp=100,
            defender_new_hp=92,
            defender_after=attacker_after_counter,
        )

        # Configure mock to return different results for two calls
        mock_attack_resolver.resolve_attack.side_effect = [
            attacker_attack_result,
            defender_counter_result,
        ]

        combat_round = CombatRound(attack_resolver=mock_attack_resolver)

        # Act
        result = combat_round.execute_round(attacker, defender, round_number=1)

        # Assert - defender should counter-attack since alive
        assert result.defender_action is not None
        assert result.defender_action == defender_counter_result
        assert result.attacker_hp_after == 92  # Reduced by counter-attack
        assert result.defender_hp_after == 35  # Reduced by initial attack
        assert result.combat_ended is False  # Both still alive
        assert result.winner is None  # No winner yet

    def test_defender_no_counter_attack_if_dead(self) -> None:
        """Dead defender should NOT counter-attack (critical business rule).

        GIVEN: Attacker deals lethal damage (defender HP → 0)
        WHEN: execute_round is called
        THEN: defender_action is None (no counter-attack)
              AND attacker HP unchanged (no counter-attack damage)
              AND combat_ended is True
              AND attacker is winner
        """
        # Arrange
        attacker = Character(name="Warrior", hp=100, attack_power=50)
        defender = Character(name="Goblin", hp=20, attack_power=8)

        # Mock AttackResolver
        mock_attack_resolver = Mock(spec=AttackResolver)

        # Attacker's strike deals 50 damage, defender dies (HP → 0)
        defender_dead = Character(name="Goblin", hp=0, attack_power=8)
        attacker_attack_result = AttackResult(
            attacker_name="Warrior",
            defender_name="Goblin",
            dice_roll=6,
            attack_power=50,
            total_damage=50,
            defender_old_hp=20,
            defender_new_hp=0,
            defender_after=defender_dead,
        )

        # Only one attack should happen (no counter-attack)
        mock_attack_resolver.resolve_attack.return_value = attacker_attack_result

        combat_round = CombatRound(attack_resolver=mock_attack_resolver)

        # Act
        result = combat_round.execute_round(attacker, defender, round_number=1)

        # Assert - dead defender cannot counter-attack
        assert result.defender_action is None  # No counter-attack
        assert result.attacker_hp_after == 100  # Unchanged
        assert result.defender_hp_after == 0  # Dead
        assert result.combat_ended is True
        assert result.winner == attacker
        # Verify resolve_attack called only once (no counter-attack)
        mock_attack_resolver.resolve_attack.assert_called_once()

    def test_round_result_includes_all_details(self) -> None:
        """RoundResult should contain all 9 required fields.

        GIVEN: Any combat scenario
        WHEN: execute_round completes
        THEN: RoundResult contains all 9 fields with complete round state
        """
        # Arrange
        attacker = Character(name="Warrior", hp=100, attack_power=15)
        defender = Character(name="Goblin", hp=50, attack_power=8)

        mock_attack_resolver = Mock(spec=AttackResolver)

        # Setup attack results
        defender_after_attack = Character(name="Goblin", hp=35, attack_power=8)
        attacker_attack_result = AttackResult(
            attacker_name="Warrior",
            defender_name="Goblin",
            dice_roll=4,
            attack_power=15,
            total_damage=15,
            defender_old_hp=50,
            defender_new_hp=35,
            defender_after=defender_after_attack,
        )

        attacker_after_counter = Character(name="Warrior", hp=92, attack_power=15)
        defender_counter_result = AttackResult(
            attacker_name="Goblin",
            defender_name="Warrior",
            dice_roll=3,
            attack_power=8,
            total_damage=8,
            defender_old_hp=100,
            defender_new_hp=92,
            defender_after=attacker_after_counter,
        )

        mock_attack_resolver.resolve_attack.side_effect = [
            attacker_attack_result,
            defender_counter_result,
        ]

        combat_round = CombatRound(attack_resolver=mock_attack_resolver)

        # Act
        result = combat_round.execute_round(attacker, defender, round_number=2)

        # Assert - verify all 9 fields present and correct
        assert result.round_number == 2
        assert result.attacker_action == attacker_attack_result
        assert result.defender_action == defender_counter_result
        assert result.attacker_hp_before == 100
        assert result.attacker_hp_after == 92
        assert result.defender_hp_before == 50
        assert result.defender_hp_after == 35
        assert result.combat_ended is False
        assert result.winner is None
