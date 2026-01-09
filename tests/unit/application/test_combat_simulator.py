"""Unit tests for CombatSimulator application service."""

from unittest.mock import Mock

from modules.application.combat_simulator import CombatSimulator
from modules.domain.model.attack_result import AttackResult
from modules.domain.model.character import Character
from modules.domain.model.combat_result import CombatResult
from modules.domain.model.initiative_result import InitiativeResult
from modules.domain.model.round_result import RoundResult
from modules.domain.services.combat_round import CombatRound
from modules.domain.services.initiative_resolver import InitiativeResolver


class TestCombatSimulator:
    """Test suite for CombatSimulator."""

    def test_run_combat_rolls_initiative_once(self):
        """Initiative should be rolled exactly once at combat start."""
        # Arrange
        char1 = Character(name="Warrior", hp=100, attack_power=15)
        char2 = Character(name="Rogue", hp=80, attack_power=12)

        mock_initiative_resolver = Mock(spec=InitiativeResolver)
        mock_combat_round = Mock(spec=CombatRound)

        # Mock initiative result
        initiative_result = InitiativeResult(
            attacker=char1,
            defender=char2,
            attacker_roll=5,
            defender_roll=3,
            attacker_total=120,  # char1.agility (115) + roll (5)
            defender_total=95,  # char2.agility (92) + roll (3)
        )
        mock_initiative_resolver.roll_initiative.return_value = initiative_result

        # Mock combat round to end immediately
        # (attacker kills defender in one hit)
        dead_defender = Character(name="Rogue", hp=0, attack_power=12)
        attack_result = AttackResult(
            attacker_name="Warrior",
            defender_name="Rogue",
            dice_roll=6,
            attack_power=15,
            total_damage=21,
            defender_old_hp=80,
            defender_new_hp=0,
            defender_after=dead_defender,
        )
        round_result = RoundResult(
            round_number=1,
            attacker_action=attack_result,
            defender_action=None,  # Defender died
            attacker_hp_before=100,
            attacker_hp_after=100,
            defender_hp_before=80,
            defender_hp_after=0,
            combat_ended=True,
            winner=char1,
        )
        mock_combat_round.execute_round.return_value = round_result

        simulator = CombatSimulator(mock_initiative_resolver, mock_combat_round)

        # Act
        simulator.run_combat(char1, char2)

        # Assert
        mock_initiative_resolver.roll_initiative.assert_called_once_with(char1, char2)

    def test_run_combat_executes_rounds_until_victory(self):
        """Combat loop should execute rounds until one character dies."""
        # Arrange
        char1 = Character(name="Warrior", hp=100, attack_power=15)
        char2 = Character(name="Rogue", hp=80, attack_power=12)

        mock_initiative_resolver = Mock(spec=InitiativeResolver)
        mock_combat_round = Mock(spec=CombatRound)

        # Mock initiative
        initiative_result = InitiativeResult(
            attacker=char1,
            defender=char2,
            attacker_roll=5,
            defender_roll=3,
            attacker_total=120,
            defender_total=95,
        )
        mock_initiative_resolver.roll_initiative.return_value = initiative_result

        # Simulate 3 rounds of combat before victory
        # Round 1: Both alive
        round1_defender = Character(name="Rogue", hp=59, attack_power=12)
        round1_attacker = Character(name="Warrior", hp=88, attack_power=15)
        round1 = RoundResult(
            round_number=1,
            attacker_action=AttackResult(
                "Warrior",
                "Rogue",
                6,
                15,
                21,
                80,
                59,
                round1_defender,
            ),
            defender_action=AttackResult(
                "Rogue",
                "Warrior",
                6,
                12,
                18,
                100,
                88,
                round1_attacker,
            ),
            attacker_hp_before=100,
            attacker_hp_after=88,
            defender_hp_before=80,
            defender_hp_after=59,
            combat_ended=False,
            winner=None,
        )

        # Round 2: Both alive
        round2_defender = Character(name="Rogue", hp=38, attack_power=12)
        round2_attacker = Character(name="Warrior", hp=76, attack_power=15)
        round2 = RoundResult(
            round_number=2,
            attacker_action=AttackResult(
                "Warrior",
                "Rogue",
                6,
                15,
                21,
                59,
                38,
                round2_defender,
            ),
            defender_action=AttackResult(
                "Rogue",
                "Warrior",
                6,
                12,
                18,
                88,
                76,
                round2_attacker,
            ),
            attacker_hp_before=88,
            attacker_hp_after=76,
            defender_hp_before=59,
            defender_hp_after=38,
            combat_ended=False,
            winner=None,
        )

        # Round 3: Defender dies
        round3_defender = Character(name="Rogue", hp=0, attack_power=12)
        round3 = RoundResult(
            round_number=3,
            attacker_action=AttackResult(
                "Warrior",
                "Rogue",
                6,
                15,
                21,
                38,
                0,
                round3_defender,
            ),
            defender_action=None,  # Defender died
            attacker_hp_before=76,
            attacker_hp_after=76,
            defender_hp_before=38,
            defender_hp_after=0,
            combat_ended=True,
            winner=round2_attacker,
        )

        mock_combat_round.execute_round.side_effect = [
            round1,
            round2,
            round3,
        ]

        simulator = CombatSimulator(mock_initiative_resolver, mock_combat_round)

        # Act
        simulator.run_combat(char1, char2)

        # Assert - verify execute_round called 3 times
        assert mock_combat_round.execute_round.call_count == 3

    def test_run_combat_returns_combat_result(self):
        """Combat result should have all required fields."""
        # Arrange
        char1 = Character(name="Warrior", hp=100, attack_power=15)
        char2 = Character(name="Rogue", hp=80, attack_power=12)

        mock_initiative_resolver = Mock(spec=InitiativeResolver)
        mock_combat_round = Mock(spec=CombatRound)

        # Mock initiative
        initiative_result = InitiativeResult(
            attacker=char1,
            defender=char2,
            attacker_roll=5,
            defender_roll=3,
            attacker_total=120,
            defender_total=95,
        )
        mock_initiative_resolver.roll_initiative.return_value = initiative_result

        # Single round combat
        dead_defender = Character(name="Rogue", hp=0, attack_power=12)
        round_result = RoundResult(
            round_number=1,
            attacker_action=AttackResult(
                "Warrior",
                "Rogue",
                6,
                15,
                21,
                80,
                0,
                dead_defender,
            ),
            defender_action=None,
            attacker_hp_before=100,
            attacker_hp_after=100,
            defender_hp_before=80,
            defender_hp_after=0,
            combat_ended=True,
            winner=char1,
        )
        mock_combat_round.execute_round.return_value = round_result

        simulator = CombatSimulator(mock_initiative_resolver, mock_combat_round)

        # Act
        result = simulator.run_combat(char1, char2)

        # Assert - verify all fields present
        assert isinstance(result, CombatResult)
        assert hasattr(result, "winner")
        assert hasattr(result, "loser")
        assert hasattr(result, "total_rounds")
        assert hasattr(result, "rounds")
        assert hasattr(result, "initiative_result")

    def test_combat_result_has_all_rounds(self):
        """Rounds should be tuple with correct length."""
        # Arrange
        char1 = Character(name="Warrior", hp=100, attack_power=15)
        char2 = Character(name="Rogue", hp=80, attack_power=12)

        mock_initiative_resolver = Mock(spec=InitiativeResolver)
        mock_combat_round = Mock(spec=CombatRound)

        # Mock initiative
        initiative_result = InitiativeResult(
            attacker=char1,
            defender=char2,
            attacker_roll=5,
            defender_roll=3,
            attacker_total=120,
            defender_total=95,
        )
        mock_initiative_resolver.roll_initiative.return_value = initiative_result

        # Two rounds
        round1_defender = Character(name="Rogue", hp=59, attack_power=12)
        round1_attacker = Character(name="Warrior", hp=88, attack_power=15)
        round1 = RoundResult(
            round_number=1,
            attacker_action=AttackResult(
                "Warrior",
                "Rogue",
                6,
                15,
                21,
                80,
                59,
                round1_defender,
            ),
            defender_action=AttackResult(
                "Rogue",
                "Warrior",
                6,
                12,
                18,
                100,
                88,
                round1_attacker,
            ),
            attacker_hp_before=100,
            attacker_hp_after=88,
            defender_hp_before=80,
            defender_hp_after=59,
            combat_ended=False,
            winner=None,
        )

        round2_defender = Character(name="Rogue", hp=0, attack_power=12)
        round2 = RoundResult(
            round_number=2,
            attacker_action=AttackResult(
                "Warrior",
                "Rogue",
                6,
                15,
                21,
                59,
                0,
                round2_defender,
            ),
            defender_action=None,
            attacker_hp_before=88,
            attacker_hp_after=88,
            defender_hp_before=59,
            defender_hp_after=0,
            combat_ended=True,
            winner=round1_attacker,
        )

        mock_combat_round.execute_round.side_effect = [round1, round2]

        simulator = CombatSimulator(mock_initiative_resolver, mock_combat_round)

        # Act
        result = simulator.run_combat(char1, char2)

        # Assert
        assert isinstance(result.rounds, tuple)
        assert len(result.rounds) == result.total_rounds
        assert result.total_rounds == 2
