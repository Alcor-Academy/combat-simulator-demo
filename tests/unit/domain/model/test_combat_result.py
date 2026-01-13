"""Unit tests for CombatResult validation logic.

Tests defensive validations in CombatResult.__post_init__:
- Winner must be alive (HP > 0)
- Loser must be dead (HP = 0)
- Total rounds must be positive
- Rounds tuple must match total_rounds count
- Rounds must be tuple (not list)

These tests achieve 100% coverage of defensive validation error paths.
"""

import pytest

from src.domain.model.character import Character
from src.domain.model.combat_result import CombatResult
from src.domain.model.round_result import RoundResult


class TestCombatResultValidation:
    """Test CombatResult validation invariants."""

    def test_creates_valid_combat_result(self) -> None:
        """Valid combat result creation succeeds."""
        winner = Character(name="Winner", hp=10, attack_power=5)
        loser = Character(name="Loser", hp=0, attack_power=5)
        round_result = RoundResult(
            round_number=1,
            attacker=winner,
            defender=loser,
            attacker_damage=5,
            defender_damage=0,
            combat_ended=True,
            winner=winner,
        )

        result = CombatResult(
            winner=winner,
            loser=loser,
            total_rounds=1,
            rounds=(round_result,),
        )

        assert result.winner == winner
        assert result.loser == loser
        assert result.total_rounds == 1

    def test_rejects_dead_winner(self) -> None:
        """Winner must be alive (HP > 0)."""
        dead_winner = Character(name="DeadWinner", hp=0, attack_power=5)
        loser = Character(name="Loser", hp=0, attack_power=5)

        with pytest.raises(ValueError, match="Winner must be alive"):
            CombatResult(
                winner=dead_winner,
                loser=loser,
                total_rounds=1,
                rounds=(),
            )

    def test_rejects_alive_loser(self) -> None:
        """Loser must be dead (HP = 0)."""
        winner = Character(name="Winner", hp=10, attack_power=5)
        alive_loser = Character(name="AliveLoser", hp=5, attack_power=5)

        with pytest.raises(ValueError, match="Loser must be dead"):
            CombatResult(
                winner=winner,
                loser=alive_loser,
                total_rounds=1,
                rounds=(),
            )

    def test_rejects_zero_rounds(self) -> None:
        """Combat must have at least 1 round."""
        winner = Character(name="Winner", hp=10, attack_power=5)
        loser = Character(name="Loser", hp=0, attack_power=5)

        with pytest.raises(ValueError, match="Combat must have at least 1 round"):
            CombatResult(
                winner=winner,
                loser=loser,
                total_rounds=0,
                rounds=(),
            )

    def test_rejects_negative_rounds(self) -> None:
        """Total rounds must be positive."""
        winner = Character(name="Winner", hp=10, attack_power=5)
        loser = Character(name="Loser", hp=0, attack_power=5)

        with pytest.raises(ValueError, match="Combat must have at least 1 round"):
            CombatResult(
                winner=winner,
                loser=loser,
                total_rounds=-1,
                rounds=(),
            )

    def test_rejects_round_count_mismatch(self) -> None:
        """Rounds tuple must match total_rounds count."""
        winner = Character(name="Winner", hp=10, attack_power=5)
        loser = Character(name="Loser", hp=0, attack_power=5)
        round_result = RoundResult(
            round_number=1,
            attacker=winner,
            defender=loser,
            attacker_damage=5,
            defender_damage=0,
            combat_ended=True,
            winner=winner,
        )

        with pytest.raises(ValueError, match="Round count mismatch"):
            CombatResult(
                winner=winner,
                loser=loser,
                total_rounds=2,  # Mismatch: says 2 rounds
                rounds=(round_result,),  # But only 1 round provided
            )

    def test_rejects_list_instead_of_tuple(self) -> None:
        """Rounds must be tuple (immutable), not list."""
        winner = Character(name="Winner", hp=10, attack_power=5)
        loser = Character(name="Loser", hp=0, attack_power=5)
        round_result = RoundResult(
            round_number=1,
            attacker=winner,
            defender=loser,
            attacker_damage=5,
            defender_damage=0,
            combat_ended=True,
            winner=winner,
        )

        with pytest.raises(TypeError, match="rounds must be tuple"):
            CombatResult(
                winner=winner,
                loser=loser,
                total_rounds=1,
                rounds=[round_result],  # List instead of tuple
            )
