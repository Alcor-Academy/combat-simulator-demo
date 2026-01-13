"""Unit tests for CombatSimulator application service.

Tests validate orchestration logic:
- Initiative rolled ONCE at combat start (persists entire combat)
- Round loop continues until victory condition
- Combat ends when HP = 0
- CombatResult complete with winner, loser, all rounds
- Immutable result (rounds as tuple)

Classical TDD approach:
- Use REAL InitiativeResolver and CombatRound (domain services)
- Use FixedDiceRoller test double at port boundary
- No mocking of domain objects
"""

import pytest

from src.domain.model.character import Character
from src.domain.services.attack_resolver import AttackResolver
from src.domain.services.combat_round import CombatRound
from src.domain.services.initiative_resolver import InitiativeResolver
from tests.doubles.fixed_dice_roller import FixedDiceRoller


# Import production code (will fail initially - Outside-In TDD)
try:
    from src.application.combat_simulator import CombatSimulator
except ImportError:
    CombatSimulator = None

try:
    from src.domain.model.combat_result import CombatResult
except ImportError:
    CombatResult = None


class TestCombatSimulator:
    """Test suite for CombatSimulator orchestration logic."""

    def test_initiative_rolled_once_at_combat_start(self):
        """Verify initiative rolled ONCE at start, roles persist entire combat.

        Business rule (DR-04): Initiative determines attacker/defender for ALL rounds.
        Roles do NOT change mid-combat.
        """
        if CombatSimulator is None:
            pytest.skip("CombatSimulator not yet implemented")

        # GIVEN: Two characters with different agility
        warrior = Character(name="Warrior", hp=30, attack_power=8)
        mage = Character(name="Mage", hp=20, attack_power=6)

        # Initiative rolls: Warrior wins (agility=38+5=43 vs Mage=26+3=29)
        # Combat rolls: Enough for 3 rounds
        dice = FixedDiceRoller([5, 3, 4, 2, 6, 1, 5, 3])

        # Wire up production services
        initiative_resolver = InitiativeResolver(dice_roller=dice)
        attack_resolver = AttackResolver(dice_roller=dice)
        combat_round = CombatRound(attack_resolver=attack_resolver)
        simulator = CombatSimulator(initiative_resolver=initiative_resolver, combat_round=combat_round)

        # WHEN: Combat runs
        result = simulator.run_combat(warrior, mage)

        # THEN: Warrior attacks first in ALL rounds (initiative winner)
        assert result.rounds is not None
        assert len(result.rounds) > 0

        # Verify same attacker in all rounds (initiative persists)
        for round_result in result.rounds:
            assert round_result.attacker.name == "Warrior", (
                f"Round {round_result.round_number}: Initiative should persist - "
                f"Warrior should attack first in ALL rounds"
            )

    def test_round_loop_continues_until_victory(self):
        """Verify combat executes rounds until one character reaches HP = 0.

        Business rule: Combat continues while both characters alive.
        """
        if CombatSimulator is None:
            pytest.skip("CombatSimulator not yet implemented")

        # GIVEN: Two characters
        fighter = Character(name="Fighter", hp=25, attack_power=7)
        archer = Character(name="Archer", hp=18, attack_power=9)

        # Configure dice for deterministic combat
        # Initiative: Fighter wins (32+6=38 vs 27+4=31)
        # Combat: Multiple rounds until someone dies
        dice = FixedDiceRoller([6, 4, 5, 4, 6, 3, 5, 2, 6, 5, 4, 3])

        initiative_resolver = InitiativeResolver(dice_roller=dice)
        attack_resolver = AttackResolver(dice_roller=dice)
        combat_round = CombatRound(attack_resolver=attack_resolver)
        simulator = CombatSimulator(initiative_resolver=initiative_resolver, combat_round=combat_round)

        # WHEN: Combat runs
        result = simulator.run_combat(fighter, archer)

        # THEN: Combat executed multiple rounds until victory
        assert result.total_rounds > 1, "Combat should have multiple rounds"
        assert len(result.rounds) == result.total_rounds, "All rounds should be recorded"

        # Final round shows combat ended
        final_round = result.rounds[-1]
        assert final_round.combat_ended, "Final round should mark combat ended"

    def test_combat_ends_when_hp_reaches_zero(self):
        """Verify combat ends immediately when either character reaches HP = 0.

        Business rule: Victory condition is HP = 0.
        """
        if CombatSimulator is None:
            pytest.skip("CombatSimulator not yet implemented")

        # GIVEN: Characters where one will die quickly
        tank = Character(name="Tank", hp=40, attack_power=10)
        glass_cannon = Character(name="Glass", hp=8, attack_power=15)

        # Glass has low HP - will die in 1 hit
        # Initiative: Tank wins
        # Combat: Tank kills Glass in first round
        dice = FixedDiceRoller([6, 2, 6])  # Initiative + one attack

        initiative_resolver = InitiativeResolver(dice_roller=dice)
        attack_resolver = AttackResolver(dice_roller=dice)
        combat_round = CombatRound(attack_resolver=attack_resolver)
        simulator = CombatSimulator(initiative_resolver=initiative_resolver, combat_round=combat_round)

        # WHEN: Combat runs
        result = simulator.run_combat(tank, glass_cannon)

        # THEN: Combat ended when Glass reached 0 HP
        assert result.loser.hp == 0, "Loser must have exactly 0 HP"
        assert not result.loser.is_alive, "Loser must be dead"
        assert result.winner.hp > 0, "Winner must have HP remaining"
        assert result.winner.is_alive, "Winner must be alive"

    def test_combat_result_contains_complete_information(self):
        """Verify CombatResult contains winner, loser, total_rounds, all round data.

        Business rule: Result is complete audit trail of combat.
        """
        if CombatSimulator is None:
            pytest.skip("CombatSimulator not yet implemented")

        # GIVEN: Two characters
        hero = Character(name="Hero", hp=30, attack_power=8)
        villain = Character(name="Villain", hp=25, attack_power=7)

        dice = FixedDiceRoller([5, 3, 4, 2, 5, 3, 6, 4, 5, 2])

        initiative_resolver = InitiativeResolver(dice_roller=dice)
        attack_resolver = AttackResolver(dice_roller=dice)
        combat_round = CombatRound(attack_resolver=attack_resolver)
        simulator = CombatSimulator(initiative_resolver=initiative_resolver, combat_round=combat_round)

        # WHEN: Combat runs
        result = simulator.run_combat(hero, villain)

        # THEN: Result contains all required fields
        assert result.winner is not None, "Result must have winner"
        assert result.loser is not None, "Result must have loser"
        assert result.total_rounds > 0, "Result must record round count"
        assert result.rounds is not None, "Result must contain round details"
        assert len(result.rounds) == result.total_rounds, "Round count must match"

        # Verify winner/loser are correct character instances
        assert result.winner.is_alive, "Winner must be alive"
        assert not result.loser.is_alive, "Loser must be dead"

    def test_combat_result_rounds_is_immutable_tuple(self):
        """Verify CombatResult.rounds is tuple (immutable), not list.

        Business rule: Value object immutability prevents result tampering.
        """
        if CombatSimulator is None:
            pytest.skip("CombatSimulator not yet implemented")
        if CombatResult is None:
            pytest.skip("CombatResult not yet implemented")

        # GIVEN: Two characters
        char1 = Character(name="Paladin", hp=35, attack_power=9)
        char2 = Character(name="Rogue", hp=22, attack_power=11)

        dice = FixedDiceRoller([6, 4, 5, 3, 4, 2, 6, 5])

        initiative_resolver = InitiativeResolver(dice_roller=dice)
        attack_resolver = AttackResolver(dice_roller=dice)
        combat_round = CombatRound(attack_resolver=attack_resolver)
        simulator = CombatSimulator(initiative_resolver=initiative_resolver, combat_round=combat_round)

        # WHEN: Combat runs
        result = simulator.run_combat(char1, char2)

        # THEN: rounds field is tuple (immutable)
        assert isinstance(result.rounds, tuple), (
            f"CombatResult.rounds must be tuple (immutable), got {type(result.rounds)}"
        )

        # Verify tuple cannot be modified (will raise TypeError)
        with pytest.raises(TypeError):
            result.rounds[0] = None  # type: ignore

    def test_combat_simulator_with_attacker_killing_defender_first_round(self):
        """Verify combat ends immediately if attacker kills defender in round 1.

        Business rule: No counter-attack if defender dies (attacker advantage).
        """
        if CombatSimulator is None:
            pytest.skip("CombatSimulator not yet implemented")

        # GIVEN: Strong attacker vs weak defender
        berserker = Character(name="Berserker", hp=50, attack_power=20)
        peasant = Character(name="Peasant", hp=5, attack_power=2)

        # Berserker wins initiative and kills peasant in one hit
        dice = FixedDiceRoller([6, 2, 6])  # Initiative + killing blow

        initiative_resolver = InitiativeResolver(dice_roller=dice)
        attack_resolver = AttackResolver(dice_roller=dice)
        combat_round = CombatRound(attack_resolver=attack_resolver)
        simulator = CombatSimulator(initiative_resolver=initiative_resolver, combat_round=combat_round)

        # WHEN: Combat runs
        result = simulator.run_combat(berserker, peasant)

        # THEN: Combat ended in 1 round
        assert result.total_rounds == 1, "Combat should end in 1 round"
        assert result.winner.name == "Berserker"
        assert result.loser.name == "Peasant"
        assert result.loser.hp == 0

        # Verify no counter-attack occurred (defender died)
        final_round = result.rounds[0]
        assert final_round.defender_damage == 0, "Dead defender cannot counter-attack"

    def test_multiple_rounds_with_both_characters_alive_until_final(self):
        """Verify combat correctly handles multiple rounds with counter-attacks.

        Business rule: Both characters attack each round until one dies.
        """
        if CombatSimulator is None:
            pytest.skip("CombatSimulator not yet implemented")

        # GIVEN: Evenly matched characters (multiple rounds expected)
        knight = Character(name="Knight", hp=28, attack_power=6)
        samurai = Character(name="Samurai", hp=26, attack_power=6)

        # Configure for 3+ rounds of combat
        dice = FixedDiceRoller([5, 3, 3, 3, 4, 4, 3, 3, 5, 5, 4, 4, 6, 2])

        initiative_resolver = InitiativeResolver(dice_roller=dice)
        attack_resolver = AttackResolver(dice_roller=dice)
        combat_round = CombatRound(attack_resolver=attack_resolver)
        simulator = CombatSimulator(initiative_resolver=initiative_resolver, combat_round=combat_round)

        # WHEN: Combat runs
        result = simulator.run_combat(knight, samurai)

        # THEN: Multiple rounds executed
        assert result.total_rounds >= 2, "Should have multiple rounds"

        # Verify all rounds except last have both characters alive
        for i, round_result in enumerate(result.rounds[:-1]):
            assert not round_result.combat_ended, f"Round {i + 1} should not end combat (both alive)"
            assert round_result.defender_damage > 0, f"Round {i + 1} defender should counter-attack (still alive)"

        # Final round ends combat
        assert result.rounds[-1].combat_ended, "Final round should end combat"
