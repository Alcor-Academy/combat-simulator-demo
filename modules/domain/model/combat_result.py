"""Combat simulation result value object."""

from dataclasses import dataclass

from modules.domain.model.character import Character
from modules.domain.model.initiative_result import InitiativeResult
from modules.domain.model.round_result import RoundResult


@dataclass(frozen=True)
class CombatResult:
    """Immutable combat simulation result.

    Contains complete combat outcome with winner, loser, and all round history.
    """

    winner: Character
    loser: Character
    total_rounds: int
    rounds: tuple[RoundResult, ...]  # Immutable tuple, not list
    initiative_result: InitiativeResult
