"""Unit tests for CombatRenderer class."""

from unittest.mock import Mock

import pytest

from modules.domain.model.attack_result import AttackResult
from modules.domain.model.character import Character
from modules.domain.model.combat_result import CombatResult
from modules.domain.model.initiative_result import InitiativeResult
from modules.domain.model.round_result import RoundResult
from modules.infrastructure.cli.combat_renderer import CombatRenderer
from modules.infrastructure.cli.config import CLIConfig
from modules.infrastructure.cli.console_output import ConsoleOutput


@pytest.fixture
def mock_console():
    """Create a mock ConsoleOutput for testing."""
    return Mock(spec=ConsoleOutput)


@pytest.fixture
def config():
    """Create test configuration with zero delays."""
    return CLIConfig.test_mode()


@pytest.fixture
def renderer(mock_console, config):
    """Create CombatRenderer instance for testing."""
    return CombatRenderer(mock_console, config)


@pytest.fixture
def hero():
    """Create test hero character."""
    return Character("Hero", 50, 10)


@pytest.fixture
def villain():
    """Create test villain character."""
    return Character("Villain", 40, 8)


def test_render_initiative_displays_rolls(renderer, mock_console, hero, villain):
    """Test that initiative rendering displays character names and totals."""
    # Create InitiativeResult with known values
    init_result = InitiativeResult(
        attacker=hero,
        defender=villain,
        attacker_roll=5,
        defender_roll=3,
        attacker_total=65,
        defender_total=51,
    )

    renderer._render_initiative(init_result)

    # Verify output contains expected text
    calls = [str(call) for call in mock_console.print.call_args_list]
    assert any("Rolling Initiative" in str(call) for call in calls)
    assert any("Hero" in str(call) and "65" in str(call) for call in calls)
    assert any("Villain" in str(call) and "51" in str(call) for call in calls)
    assert any("attacks first" in str(call) for call in calls)

    # Verify delay was called
    mock_console.display_with_delay.assert_called_once()


def test_render_round_displays_attacker_action(renderer, mock_console, hero, villain):
    """Test that round rendering displays attacker action details."""
    # Create attack result
    villain_after_damage = villain.receive_damage(12)
    attack_result = AttackResult(
        attacker_name="Hero",
        defender_name="Villain",
        dice_roll=2,
        attack_power=10,
        total_damage=12,
        defender_old_hp=40,
        defender_new_hp=28,
        defender_after=villain_after_damage,
    )

    # Create round result with attacker action only (defender dies)
    round_result = RoundResult(
        round_number=1,
        attacker_action=attack_result,
        defender_action=None,
        attacker_hp_before=50,
        attacker_hp_after=50,
        defender_hp_before=40,
        defender_hp_after=0,
        combat_ended=True,
        winner=hero,
    )

    renderer._render_round(round_result)

    # Verify attacker action is displayed
    calls = [str(call) for call in mock_console.print.call_args_list]
    assert any("ROUND 1" in str(call) for call in calls)
    assert any("Hero attacks" in str(call) for call in calls)
    assert any("Damage: 12" in str(call) for call in calls)
    assert any("40 HP -> 28 HP" in str(call) for call in calls)


def test_render_round_displays_counter_if_alive(renderer, mock_console, hero, villain):
    """Test that round rendering displays defender counter-attack when defender survives."""
    # Create attacker action (hero attacks villain)
    villain_after_damage = villain.receive_damage(12)
    attacker_action = AttackResult(
        attacker_name="Hero",
        defender_name="Villain",
        dice_roll=2,
        attack_power=10,
        total_damage=12,
        defender_old_hp=40,
        defender_new_hp=28,
        defender_after=villain_after_damage,
    )

    # Create defender counter-attack (villain counter-attacks hero)
    hero_after_damage = hero.receive_damage(10)
    defender_action = AttackResult(
        attacker_name="Villain",
        defender_name="Hero",
        dice_roll=2,
        attack_power=8,
        total_damage=10,
        defender_old_hp=50,
        defender_new_hp=40,
        defender_after=hero_after_damage,
    )

    # Create round result with both actions
    round_result = RoundResult(
        round_number=1,
        attacker_action=attacker_action,
        defender_action=defender_action,
        attacker_hp_before=50,
        attacker_hp_after=40,
        defender_hp_before=40,
        defender_hp_after=28,
        combat_ended=False,
        winner=None,
    )

    renderer._render_round(round_result)

    # Verify both actions are displayed
    calls = [str(call) for call in mock_console.print.call_args_list]
    assert any("Hero attacks" in str(call) for call in calls)
    assert any("Villain counter-attacks" in str(call) for call in calls)
    assert any("Damage: 10" in str(call) for call in calls)


def test_render_round_no_counter_if_defender_dead(renderer, mock_console, hero, villain):
    """Test that round rendering shows defeat message when defender dies."""
    # Create lethal attack (defender dies)
    villain_after_damage = villain.receive_damage(40)
    attack_result = AttackResult(
        attacker_name="Hero",
        defender_name="Villain",
        dice_roll=5,
        attack_power=10,
        total_damage=15,
        defender_old_hp=40,
        defender_new_hp=0,
        defender_after=villain_after_damage,
    )

    # Create round result with no counter-attack
    round_result = RoundResult(
        round_number=2,
        attacker_action=attack_result,
        defender_action=None,
        attacker_hp_before=50,
        attacker_hp_after=50,
        defender_hp_before=40,
        defender_hp_after=0,
        combat_ended=True,
        winner=hero,
    )

    renderer._render_round(round_result)

    # Verify defeat message is displayed
    calls = [str(call) for call in mock_console.print.call_args_list]
    assert any("has been defeated" in str(call) for call in calls)
    assert any("Villain" in str(call) for call in calls)
    # Verify NO counter-attack is displayed
    assert not any("counter-attacks" in str(call) for call in calls)


def test_render_victory_displays_winner(renderer, mock_console, hero, villain):
    """Test that victory rendering displays winner stats and combat summary."""
    # Create minimal combat result
    init_result = InitiativeResult(
        attacker=hero,
        defender=villain,
        attacker_roll=5,
        defender_roll=3,
        attacker_total=65,
        defender_total=51,
    )

    villain_defeated = villain.receive_damage(40)
    combat_result = CombatResult(
        winner=hero,
        loser=villain_defeated,
        total_rounds=3,
        rounds=(),  # Empty tuple for this test
        initiative_result=init_result,
    )

    renderer._render_victory(combat_result)

    # Verify victory announcement
    calls = [str(call) for call in mock_console.print.call_args_list]
    assert any("HERO WINS" in str(call) for call in calls)
    assert any("Combat lasted 3 rounds" in str(call) for call in calls)
    assert any("50 HP remaining" in str(call) for call in calls)
    assert any("0 HP (defeated)" in str(call) for call in calls)

    # Verify prompt_continue was called
    mock_console.prompt_continue.assert_called_once()


def test_render_combat_orchestrates_full_visualization(renderer, mock_console, hero, villain):
    """Test that render_combat calls all rendering methods in correct order."""
    # Create complete combat result
    init_result = InitiativeResult(
        attacker=hero,
        defender=villain,
        attacker_roll=5,
        defender_roll=3,
        attacker_total=65,
        defender_total=51,
    )

    # Create round result
    villain_after_damage = villain.receive_damage(40)
    attack_result = AttackResult(
        attacker_name="Hero",
        defender_name="Villain",
        dice_roll=5,
        attack_power=10,
        total_damage=15,
        defender_old_hp=40,
        defender_new_hp=0,
        defender_after=villain_after_damage,
    )

    round_result = RoundResult(
        round_number=1,
        attacker_action=attack_result,
        defender_action=None,
        attacker_hp_before=50,
        attacker_hp_after=50,
        defender_hp_before=40,
        defender_hp_after=0,
        combat_ended=True,
        winner=hero,
    )

    combat_result = CombatResult(
        winner=hero,
        loser=villain_after_damage,
        total_rounds=1,
        rounds=(round_result,),
        initiative_result=init_result,
    )

    renderer.render_combat(combat_result)

    # Verify all sections are rendered
    calls = [str(call) for call in mock_console.print.call_args_list]
    assert any("Rolling Initiative" in str(call) for call in calls)
    assert any("ROUND 1" in str(call) for call in calls)
    assert any("HERO WINS" in str(call) for call in calls)
