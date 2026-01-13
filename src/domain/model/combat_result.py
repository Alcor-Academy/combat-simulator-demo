"""CombatResult value object - immutable complete combat outcome.

Captures entire combat history:
- Winner and loser (final character states)
- Total rounds executed
- All round results (immutable tuple)

Business rules:
- Immutability enforced via frozen dataclass
- rounds MUST be tuple (not list) for immutability
- Complete audit trail of combat from start to finish
"""

from dataclasses import dataclass

from src.domain.model.character import Character
from src.domain.model.round_result import RoundResult


@dataclass(frozen=True)
class CombatResult:
    """Immutable result of complete combat simulation.

    Contains full combat history from initiative roll through final victory.
    Immutability ensures result cannot be tampered with after combat ends.

    Fields:
        winner: Character who won (HP > 0)
        loser: Character who lost (HP = 0)
        total_rounds: Number of rounds executed
        rounds: Tuple of all RoundResult instances (immutable collection)
    """

    winner: Character
    loser: Character
    total_rounds: int
    rounds: tuple[RoundResult, ...]

    def __post_init__(self) -> None:
        """Validate combat result invariants.

        Business rules:
        - Winner must be alive (HP > 0)
        - Loser must be dead (HP = 0)
        - Total rounds must be positive
        - Rounds tuple must match total_rounds count
        """
        if not self.winner.is_alive:
            msg = f"Winner must be alive, but {self.winner.name} has HP={self.winner.hp}"
            raise ValueError(msg)

        if self.loser.is_alive:
            msg = f"Loser must be dead, but {self.loser.name} has HP={self.loser.hp}"
            raise ValueError(msg)

        if self.total_rounds <= 0:
            msg = f"Combat must have at least 1 round, got {self.total_rounds}"
            raise ValueError(msg)

        if len(self.rounds) != self.total_rounds:
            msg = f"Round count mismatch: total_rounds={self.total_rounds}, but rounds has {len(self.rounds)} entries"
            raise ValueError(msg)

        if not isinstance(self.rounds, tuple):
            msg = f"rounds must be tuple (immutable), got {type(self.rounds)}"
            raise TypeError(msg)
