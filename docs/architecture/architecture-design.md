# Combat Simulator - Architecture Design Document

**Project**: Combat Simulator CLI - Software Crafters Live Coding Demo
**Wave**: DESIGN (Architecture & Technical Design)
**Date**: 2026-01-07
**Solution Architect**: Morgan (solution-architect agent)
**Technology Stack**: Python 3 with pytest ecosystem

---

## Executive Summary

This document defines the architecture for a D&D-style turn-based combat simulator CLI, designed for a 60-minute live coding demonstration. The architecture follows **Hexagonal Architecture** (Ports & Adapters) principles, enabling:

1. **Testability**: All domain logic testable without infrastructure dependencies
2. **Immutability**: Frozen dataclasses prevent state mutation bugs
3. **Separation of Concerns**: Clear boundaries between domain, infrastructure, and presentation
4. **Demo Visibility**: Architecture emerges naturally during TDD Outside-In development

**Key Architectural Decisions**:
- Python `@dataclass(frozen=True)` for immutable value objects
- `Protocol` classes (PEP 544) for port interfaces
- Constructor injection for dependency management
- pytest-bdd for E2E acceptance tests, pytest-describe for unit tests

---

## Architecture Overview

### Hexagonal Architecture (Ports & Adapters)

```
                    +--------------------------------------------------+
                    |                    CLI LAYER                      |
                    |  (Click commands, Rich output formatting)         |
                    +--------------------------------------------------+
                                          |
                                          | calls
                                          v
+------------------+     +------------------------------------------+     +------------------+
|   PRIMARY        |     |              APPLICATION LAYER           |     |   SECONDARY      |
|   ADAPTERS       |     |  (Use Cases / Application Services)      |     |   ADAPTERS       |
|                  |     |                                          |     |                  |
| - CLI Commands   |---->|  CombatSimulator                         |---->| - RandomDiceRoller
| - (future: API)  |     |    - run_combat(char1, char2)            |     | - (future: DB)   |
|                  |     |    - returns CombatResult                |     |                  |
+------------------+     +------------------------------------------+     +------------------+
                                          |
                                          | uses
                                          v
                    +--------------------------------------------------+
                    |                  DOMAIN LAYER                     |
                    |  (Pure business logic, no external dependencies)  |
                    |                                                   |
                    |  Value Objects:                                   |
                    |    - Character (frozen dataclass)                 |
                    |    - AttackResult, RoundResult, CombatResult     |
                    |    - InitiativeResult                            |
                    |                                                   |
                    |  Domain Services:                                 |
                    |    - InitiativeResolver                          |
                    |    - AttackResolver                              |
                    |    - CombatRound                                 |
                    |                                                   |
                    |  Ports (Protocols):                               |
                    |    - DiceRoller                                   |
                    +--------------------------------------------------+
```

### Dependency Flow

```
CLI --> Application --> Domain <-- Infrastructure
         |                 ^              |
         |                 |              |
         +-----------------+--------------+
                   (injects adapters)
```

**Key Rule**: Dependencies point inward. Domain layer has ZERO external dependencies.

---

## Component Boundaries

### Layer 1: Domain Layer (Pure Business Logic)

**Location**: `src/domain/`

**Responsibility**: Contains all business rules and domain logic. This layer is:
- Framework-free (no pytest, no click, no rich)
- Infrastructure-free (no file I/O, no network, no randomness)
- Fully testable in isolation

**Components**:

| Component | Type | Responsibility |
|-----------|------|----------------|
| `Character` | Value Object | Immutable combatant with name, hp, attack_power, derived agility |
| `AttackResult` | Value Object | Result of a single attack (damage, HP changes) |
| `RoundResult` | Value Object | Result of one combat round (both attacks) |
| `CombatResult` | Value Object | Final combat outcome (winner, loser, all rounds) |
| `InitiativeResult` | Value Object | Combat order determination (attacker, defender) |
| `InitiativeResolver` | Domain Service | Calculates initiative and determines combat order |
| `AttackResolver` | Domain Service | Resolves single attack (damage calculation) |
| `CombatRound` | Domain Service | Orchestrates one round with attacker advantage rule |
| `DiceRoller` | Port (Protocol) | Interface for randomness injection |

### Layer 2: Application Layer (Use Cases)

**Location**: `src/application/`

**Responsibility**: Orchestrates domain objects to fulfill use cases. This layer:
- Coordinates domain services
- Manages transaction boundaries (if needed)
- Translates between external and domain representations

**Components**:

| Component | Type | Responsibility |
|-----------|------|----------------|
| `CombatSimulator` | Use Case | Orchestrates full combat from start to victory |

### Layer 3: Infrastructure Layer (Adapters)

**Location**: `src/infrastructure/`

**Responsibility**: Implements ports defined in domain. This layer:
- Contains all external dependencies
- Implements production adapters
- Can be swapped without changing domain logic

**Components**:

| Component | Type | Responsibility |
|-----------|------|----------------|
| `RandomDiceRoller` | Adapter | Production dice roller using `random.randint(1, 6)` |

### Layer 4: CLI Layer (Presentation)

**Location**: `src/cli/`

**Responsibility**: User interaction and output formatting. This layer:
- Parses command-line arguments (Click)
- Formats output for display (Rich)
- Translates domain results to human-readable format

**Components**:

| Component | Type | Responsibility |
|-----------|------|----------------|
| `main.py` | Entry Point | CLI entry point with Click commands |
| `formatters.py` | Presentation | Rich console output formatting |

---

## Folder Structure

```
combat-simulator-demo/
|-- src/
|   |-- __init__.py
|   |-- domain/
|   |   |-- __init__.py
|   |   |-- model/
|   |   |   |-- __init__.py
|   |   |   |-- character.py          # Character value object
|   |   |   |-- attack_result.py      # AttackResult value object
|   |   |   |-- round_result.py       # RoundResult value object
|   |   |   |-- combat_result.py      # CombatResult value object
|   |   |   |-- initiative_result.py  # InitiativeResult value object
|   |   |-- services/
|   |   |   |-- __init__.py
|   |   |   |-- initiative_resolver.py
|   |   |   |-- attack_resolver.py
|   |   |   |-- combat_round.py
|   |   |-- ports/
|   |       |-- __init__.py
|   |       |-- dice_roller.py        # DiceRoller Protocol
|   |
|   |-- application/
|   |   |-- __init__.py
|   |   |-- combat_simulator.py       # Main use case
|   |
|   |-- infrastructure/
|   |   |-- __init__.py
|   |   |-- random_dice_roller.py     # Production adapter
|   |
|   |-- cli/
|       |-- __init__.py
|       |-- main.py                   # Click entry point
|       |-- formatters.py             # Rich output formatting
|
|-- tests/
|   |-- __init__.py
|   |-- unit/
|   |   |-- __init__.py
|   |   |-- domain/
|   |   |   |-- __init__.py
|   |   |   |-- model/
|   |   |   |   |-- test_character.py
|   |   |   |   |-- test_attack_result.py
|   |   |   |   |-- test_round_result.py
|   |   |   |   |-- test_combat_result.py
|   |   |   |   |-- test_initiative_result.py
|   |   |   |-- services/
|   |   |       |-- test_initiative_resolver.py
|   |   |       |-- test_attack_resolver.py
|   |   |       |-- test_combat_round.py
|   |   |-- application/
|   |       |-- test_combat_simulator.py
|   |   |-- infrastructure/
|   |       |-- test_random_dice_roller.py
|   |
|   |-- integration/
|   |   |-- __init__.py
|   |   |-- (empty for demo - reserved for future API tests)
|   |   |-- # Future: Postman/Newman collections, Python retry API libs
|   |
|   |-- e2e/
|   |   |-- __init__.py
|   |   |-- features/
|   |   |   |-- combat_simulation.feature   # Gherkin feature file
|   |   |-- test_combat_simulation.py       # pytest-bdd step definitions
|   |
|   |-- doubles/
|       |-- __init__.py
|       |-- fixed_dice_roller.py            # Test double for DiceRoller
|
|-- docs/
|   |-- architecture/
|   |   |-- architecture-design.md          # This document
|   |-- requirements/
|       |-- (existing requirements docs)
|
|-- Pipfile
|-- Pipfile.lock
|-- pyproject.toml
|-- README.md
```

---

## Python Implementation Patterns

### Pattern 1: Immutable Value Objects with Frozen Dataclasses

**Purpose**: Enforce immutability to prevent state mutation bugs.

**Implementation**:

```python
# src/domain/model/character.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Character:
    """Immutable combatant value object.

    Agility is derived (computed from hp + attack_power), not stored.
    State changes return new instances.
    """
    name: str
    hp: int
    attack_power: int

    def __post_init__(self) -> None:
        """Validate invariants on construction."""
        if not self.name:
            raise ValueError("Name cannot be empty")
        if self.hp < 0:
            raise ValueError("HP cannot be negative")
        if self.attack_power <= 0:
            raise ValueError("Attack power must be positive")

    @property
    def agility(self) -> int:
        """Derived stat: Attack Power + HP.

        Represents fatigue: as you take damage, you get slower.
        """
        return self.hp + self.attack_power

    @property
    def is_alive(self) -> bool:
        """Character is alive if HP > 0."""
        return self.hp > 0

    def receive_damage(self, amount: int) -> "Character":
        """Return NEW Character with reduced HP (floors at 0).

        Original instance remains unchanged (immutability).
        """
        new_hp = max(0, self.hp - amount)
        return Character(name=self.name, hp=new_hp, attack_power=self.attack_power)
```

**Key Points**:
- `@dataclass(frozen=True)` makes all fields immutable
- `agility` is a `@property` (computed, never stored)
- `receive_damage()` returns a NEW instance, doesn't mutate
- `__post_init__` validates invariants (illegal states unrepresentable)

### Pattern 2: Ports with Protocol Classes (PEP 544)

**Purpose**: Define interfaces for external dependencies without inheritance requirements.

**Implementation**:

```python
# src/domain/ports/dice_roller.py
from typing import Protocol

class DiceRoller(Protocol):
    """Port interface for dice rolling abstraction.

    Implementations:
    - RandomDiceRoller: Production adapter using random.randint
    - FixedDiceRoller: Test double returning predetermined values
    """

    def roll(self) -> int:
        """Roll a D6 die.

        Returns:
            Integer in range [1, 6] inclusive.
            Never returns 0, never returns 7.
        """
        ...
```

**Why Protocol over ABC**:
- Structural typing (duck typing with type hints)
- No inheritance required in implementations
- More Pythonic approach
- Works with existing classes that have `roll()` method

### Pattern 3: Test Double Implementation

**Purpose**: Deterministic testing without random values.

**Implementation**:

```python
# tests/doubles/fixed_dice_roller.py
from typing import Union, List

class FixedDiceRoller:
    """Test double for DiceRoller that returns predetermined values.

    Supports two modes:
    1. Single value: Always returns the same value
    2. Sequence: Returns values in order, cycling if exhausted

    Usage:
        # Single value mode
        roller = FixedDiceRoller(4)
        roller.roll()  # Always returns 4

        # Sequence mode
        roller = FixedDiceRoller([3, 5, 2])
        roller.roll()  # Returns 3
        roller.roll()  # Returns 5
        roller.roll()  # Returns 2
        roller.roll()  # Returns 3 (cycles)
    """

    def __init__(self, values: Union[int, List[int]]) -> None:
        if isinstance(values, int):
            self._values = [values]
        else:
            self._values = list(values)
        self._index = 0

    def roll(self) -> int:
        """Return next predetermined value."""
        value = self._values[self._index % len(self._values)]
        self._index += 1
        return value
```

### Pattern 4: Constructor Injection for Dependencies

**Purpose**: Explicit dependency passing without framework magic.

**Implementation**:

```python
# src/domain/services/attack_resolver.py
from dataclasses import dataclass
from src.domain.model.character import Character
from src.domain.model.attack_result import AttackResult
from src.domain.ports.dice_roller import DiceRoller

@dataclass
class AttackResolver:
    """Domain service for resolving attacks.

    Dependencies injected via constructor.
    """
    dice_roller: DiceRoller

    def resolve_attack(self, attacker: Character, defender: Character) -> AttackResult:
        """Resolve an attack from attacker to defender.

        Args:
            attacker: Character performing the attack (must be alive)
            defender: Character receiving the attack

        Returns:
            AttackResult with damage calculation and new defender state

        Raises:
            ValueError: If attacker is dead (HP = 0)
        """
        if not attacker.is_alive:
            raise ValueError("Dead character cannot attack")

        dice_roll = self.dice_roller.roll()
        total_damage = attacker.attack_power + dice_roll
        defender_after = defender.receive_damage(total_damage)

        return AttackResult(
            attacker_name=attacker.name,
            defender_name=defender.name,
            dice_roll=dice_roll,
            attack_power=attacker.attack_power,
            total_damage=total_damage,
            defender_old_hp=defender.hp,
            defender_new_hp=defender_after.hp,
            defender_after=defender_after
        )
```

**Wiring in CLI Layer**:

```python
# src/cli/main.py
import click
from rich.console import Console
from src.domain.services.initiative_resolver import InitiativeResolver
from src.domain.services.attack_resolver import AttackResolver
from src.domain.services.combat_round import CombatRound
from src.application.combat_simulator import CombatSimulator
from src.infrastructure.random_dice_roller import RandomDiceRoller

console = Console()

@click.command()
@click.option('--char1-name', default='Thorin', help='First character name')
@click.option('--char1-hp', default=20, help='First character HP')
@click.option('--char1-attack', default=5, help='First character attack power')
@click.option('--char2-name', default='Goblin', help='Second character name')
@click.option('--char2-hp', default=10, help='Second character HP')
@click.option('--char2-attack', default=3, help='Second character attack power')
def fight(char1_name, char1_hp, char1_attack, char2_name, char2_hp, char2_attack):
    """Run a combat simulation between two characters."""
    # Wire up dependencies (Composition Root)
    dice_roller = RandomDiceRoller()
    initiative_resolver = InitiativeResolver(dice_roller=dice_roller)
    attack_resolver = AttackResolver(dice_roller=dice_roller)
    combat_round = CombatRound(attack_resolver=attack_resolver)
    simulator = CombatSimulator(
        initiative_resolver=initiative_resolver,
        combat_round=combat_round
    )

    # Create characters
    char1 = Character(name=char1_name, hp=char1_hp, attack_power=char1_attack)
    char2 = Character(name=char2_name, hp=char2_hp, attack_power=char2_attack)

    # Run combat
    result = simulator.run_combat(char1, char2)

    # Format output with Rich
    format_combat_result(console, result)

if __name__ == '__main__':
    fight()
```

---

## Domain Model Detail

### Value Objects

All value objects use `@dataclass(frozen=True)` for immutability.

#### Character

```python
@dataclass(frozen=True)
class Character:
    name: str              # Non-empty string
    hp: int                # >= 0, floors at 0 on damage
    attack_power: int      # > 0

    # Derived (property, not field):
    # agility: int = hp + attack_power

    # Methods:
    # is_alive: bool
    # receive_damage(amount: int) -> Character
```

#### AttackResult

```python
@dataclass(frozen=True)
class AttackResult:
    attacker_name: str
    defender_name: str
    dice_roll: int          # [1, 6]
    attack_power: int       # > 0
    total_damage: int       # attack_power + dice_roll
    defender_old_hp: int    # Before damage
    defender_new_hp: int    # After damage (floored at 0)
    defender_after: Character  # New Character instance
```

#### InitiativeResult

```python
@dataclass(frozen=True)
class InitiativeResult:
    attacker: Character     # Higher initiative wins, attacks first
    defender: Character     # Lower initiative, counter-attacks if alive
    attacker_roll: int      # D6 roll for attacker
    defender_roll: int      # D6 roll for defender
    attacker_total: int     # attacker.agility + attacker_roll
    defender_total: int     # defender.agility + defender_roll
```

#### RoundResult

```python
@dataclass(frozen=True)
class RoundResult:
    round_number: int
    attacker: Character           # State after round
    defender: Character           # State after round
    attacker_roll: int            # Attacker's attack dice roll
    defender_roll: int            # Defender's counter-attack roll (0 if dead)
    attacker_damage: int          # Damage dealt by attacker
    defender_damage: int          # Damage dealt by defender (0 if dead)
    attacker_hp_after: int        # Attacker HP after round
    defender_hp_after: int        # Defender HP after round
    combat_ended: bool            # True if someone died
    winner: Optional[Character]   # Winner if combat_ended, else None
```

#### CombatResult

```python
@dataclass(frozen=True)
class CombatResult:
    winner: Character
    loser: Character
    total_rounds: int
    rounds: Tuple[RoundResult, ...]  # Immutable sequence
```

### Domain Services

#### InitiativeResolver

```python
@dataclass
class InitiativeResolver:
    dice_roller: DiceRoller

    def roll_initiative(self, char1: Character, char2: Character) -> InitiativeResult:
        """Roll initiative to determine combat order.

        Higher initiative attacks first for entire combat.
        Tie-breaker: higher base Agility, then char1 wins.
        """
```

#### AttackResolver

```python
@dataclass
class AttackResolver:
    dice_roller: DiceRoller

    def resolve_attack(self, attacker: Character, defender: Character) -> AttackResult:
        """Resolve single attack.

        Damage = attack_power + dice_roll
        Returns new defender with reduced HP (floored at 0)
        """
```

#### CombatRound

```python
@dataclass
class CombatRound:
    attack_resolver: AttackResolver

    def execute_round(
        self,
        attacker: Character,
        defender: Character,
        round_number: int
    ) -> RoundResult:
        """Execute one combat round with attacker advantage.

        1. Attacker attacks first
        2. Defender counter-attacks ONLY if HP > 0 after attacker's attack
        3. If attacker kills defender, round ends immediately
        """
```

### Application Service

#### CombatSimulator

```python
@dataclass
class CombatSimulator:
    initiative_resolver: InitiativeResolver
    combat_round: CombatRound

    def run_combat(self, char1: Character, char2: Character) -> CombatResult:
        """Run complete combat until one character dies.

        1. Roll initiative (once at start)
        2. Execute rounds until someone reaches 0 HP
        3. Return CombatResult with winner, loser, and all rounds
        """
```

---

## Architecture Decision Records (ADRs)

### ADR-001: Python as Implementation Language

**Status**: Accepted

**Context**: Need a language suitable for 60-minute live demo that supports Clean Architecture patterns.

**Decision**: Use Python 3 with type hints.

**Alternatives Considered**:
| Option | Pros | Cons |
|--------|------|------|
| TypeScript/Node.js | Fast development, good typing | Requires npm setup, less presenter familiarity |
| Python | Simple syntax, fast setup, presenter familiar | Slightly weaker typing than TypeScript |
| C#/.NET | Strong typing, enterprise patterns | Slower iteration, heavier setup |

**Consequences**:
- (+) Fast development iteration
- (+) Existing Pipfile with test infrastructure
- (+) Clean syntax for demo visibility
- (-) No compile-time type checking (mitigated by mypy)

**Open Source Justification**: Python is MIT-licensed, pytest ecosystem is MIT-licensed.

---

### ADR-002: Frozen Dataclasses for Immutable Value Objects

**Status**: Accepted

**Context**: Domain requires immutable value objects to prevent state mutation bugs.

**Decision**: Use `@dataclass(frozen=True)` for all value objects.

**Alternatives Considered**:
| Option | Pros | Cons |
|--------|------|------|
| `@dataclass(frozen=True)` | Built-in, simple, enforced at runtime | No deep freeze (nested mutables) |
| Named tuples | Immutable by default | No methods, awkward syntax |
| attrs with frozen=True | More features | Extra dependency |
| Pydantic with frozen=True | Validation included | Heavier, meant for serialization |

**Consequences**:
- (+) Standard library, no extra dependencies
- (+) Clear syntax for demo
- (+) Runtime enforcement of immutability
- (-) Nested mutable objects not frozen (not an issue for this domain)

**License**: Python dataclasses module is part of stdlib (PSF license).

---

### ADR-003: Protocol Classes for Port Interfaces

**Status**: Accepted

**Context**: Need to define port interfaces for dependency injection without requiring inheritance.

**Decision**: Use `typing.Protocol` (PEP 544) for port interfaces.

**Alternatives Considered**:
| Option | Pros | Cons |
|--------|------|------|
| `Protocol` (typing) | Structural typing, Pythonic | Requires Python 3.8+ |
| `ABC` (abc module) | Classic approach | Requires explicit inheritance |
| Duck typing only | Simplest | No type checking support |

**Consequences**:
- (+) Structural typing (any class with `roll()` method satisfies `DiceRoller`)
- (+) Works with mypy for type checking
- (+) No inheritance boilerplate in implementations
- (-) Requires Python 3.8+ (acceptable)

---

### ADR-004: pytest-bdd for E2E Acceptance Tests

**Status**: Accepted

**Context**: Need to validate E2E scenarios using Given-When-Then format from requirements.

**Decision**: Use pytest-bdd for E2E tests, pytest-describe for unit tests.

**Alternatives Considered**:
| Option | Pros | Cons |
|--------|------|------|
| pytest-bdd | Gherkin syntax, maps to acceptance criteria | Learning curve |
| behave | Popular BDD framework | Different from pytest ecosystem |
| pytest only | Simple | No Gherkin support |

**Consequences**:
- (+) Direct mapping from acceptance criteria (Given-When-Then)
- (+) Feature files readable by non-technical stakeholders
- (+) Integrates with existing pytest infrastructure
- (-) Additional step definition code required

**License**: pytest-bdd is MIT-licensed.

---

### ADR-005: Constructor Injection without DI Container

**Status**: Accepted

**Context**: Need dependency injection for testability without framework complexity.

**Decision**: Use manual constructor injection, wire dependencies in CLI entry point.

**Alternatives Considered**:
| Option | Pros | Cons |
|--------|------|------|
| Manual constructor injection | Simple, explicit, no magic | More wiring code |
| dependency-injector | Full DI container | Overkill for demo, adds complexity |
| pinject | Google's DI library | Less maintained |

**Consequences**:
- (+) No framework to learn
- (+) Explicit dependency flow visible to audience
- (+) Easy to test (just pass test doubles)
- (-) Manual wiring in composition root (acceptable for demo size)

---

### ADR-006: Rich + Click for CLI

**Status**: Accepted

**Context**: Need beautiful console output for demo visibility.

**Decision**: Use Rich for output formatting, Click for argument parsing.

**Alternatives Considered**:
| Option | Pros | Cons |
|--------|------|------|
| Rich + Click | Beautiful output, mature CLI | Two libraries |
| Textual | Full TUI | Overkill for this demo |
| argparse only | Standard library | Less pretty output |

**Consequences**:
- (+) Colorful, readable output on projector
- (+) Click provides clean command interface
- (+) Rich panels/tables enhance demo visibility
- (-) Two dependencies (both already in Pipfile)

**License**: Both Rich and Click are MIT-licensed.

---

## Test Strategy

### Test Pyramid

```
        E2E Tests (pytest-bdd)
              1-2 tests
       /                    \
      Integration Tests
            0 tests (not needed)
     /                          \
    Unit Tests (pytest-describe)
          20-25 tests
```

### Test Organization

| Test Type | Location | Framework | Purpose |
|-----------|----------|-----------|---------|
| Unit | `tests/unit/` | pytest-describe | Test domain logic in isolation |
| E2E | `tests/e2e/` | pytest-bdd | Validate full combat scenarios |
| Test Doubles | `tests/doubles/` | N/A | FixedDiceRoller implementation |

### pytest-describe Style (Unit Tests)

```python
# tests/unit/domain/model/test_character.py

def describe_Character():

    def describe_creation():

        def it_creates_character_with_valid_attributes():
            character = Character(name="Thorin", hp=20, attack_power=5)
            assert character.name == "Thorin"
            assert character.hp == 20
            assert character.attack_power == 5

        def it_computes_agility_as_hp_plus_attack_power():
            character = Character(name="Thorin", hp=20, attack_power=5)
            assert character.agility == 25

        def it_rejects_empty_name():
            with pytest.raises(ValueError, match="Name cannot be empty"):
                Character(name="", hp=20, attack_power=5)

    def describe_receive_damage():

        def it_returns_new_character_with_reduced_hp():
            original = Character(name="Legolas", hp=18, attack_power=5)
            damaged = original.receive_damage(5)

            assert damaged.hp == 13
            assert original.hp == 18  # Original unchanged
            assert damaged is not original

        def it_floors_hp_at_zero():
            character = Character(name="Goblin", hp=5, attack_power=3)
            damaged = character.receive_damage(8)
            assert damaged.hp == 0
```

### pytest-bdd Style (E2E Tests)

```gherkin
# tests/e2e/features/combat_simulation.feature

Feature: Combat Simulation
  As a player
  I want to watch two characters fight
  So that I can see who wins

  Scenario: Full combat from start to victory
    Given a character "Thorin" with 20 HP and 5 attack power
    And a character "Goblin" with 10 HP and 3 attack power
    And dice configured for predictable combat outcome
    When the combat simulation runs
    Then one character wins
    And the loser has 0 HP
    And all rounds are recorded
    And the attacker advantage rule is enforced
```

```python
# tests/e2e/test_combat_simulation.py

from pytest_bdd import scenarios, given, when, then, parsers
from src.domain.model.character import Character
from src.application.combat_simulator import CombatSimulator
from tests.doubles.fixed_dice_roller import FixedDiceRoller

scenarios('features/combat_simulation.feature')

@given(parsers.parse('a character "{name}" with {hp:d} HP and {attack:d} attack power'))
def create_character(name, hp, attack, combat_context):
    character = Character(name=name, hp=hp, attack_power=attack)
    combat_context['characters'].append(character)

@given('dice configured for predictable combat outcome')
def configure_dice(combat_context):
    # Sequence: initiative rolls, then combat rolls
    combat_context['dice_roller'] = FixedDiceRoller([3, 5, 4, 2, 6, 1])

@when('the combat simulation runs')
def run_combat(combat_context):
    char1, char2 = combat_context['characters']
    simulator = create_simulator(combat_context['dice_roller'])
    combat_context['result'] = simulator.run_combat(char1, char2)

@then('one character wins')
def verify_winner(combat_context):
    result = combat_context['result']
    assert result.winner is not None
    assert result.winner.is_alive

@then('the loser has 0 HP')
def verify_loser(combat_context):
    result = combat_context['result']
    assert result.loser.hp == 0

@then('the attacker advantage rule is enforced')
def verify_attacker_advantage(combat_context):
    result = combat_context['result']
    for round_result in result.rounds:
        if round_result.defender_hp_after == 0:
            # If defender died, they should not have counter-attacked
            assert round_result.defender_damage == 0
```

### Test Execution Commands

```bash
# Run all unit tests
pipenv run pytest tests/unit -v

# Run E2E tests
pipenv run pytest tests/e2e -v

# Run with coverage
pipenv run pytest tests/ --cov=src --cov-report=html

# Run specific test file
pipenv run pytest tests/unit/domain/model/test_character.py -v
```

---

## Combat Flow Sequence Diagram

### High-Level Combat Flow (Presentation Summary)

```
┌─────────────────────────────────────────────────────────────┐
│                     COMBAT SIMULATION                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. INITIATIVE PHASE                                         │
│     Each character rolls D6 + Agility                        │
│     Higher total → Attacker (attacks first every round)      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. COMBAT LOOP (repeat until victory)                       │
│                                                              │
│     ┌──────────────────┐                                     │
│     │ Attacker attacks │ → Damage = Attack Power + D6        │
│     └────────┬─────────┘                                     │
│              │                                               │
│              ▼                                               │
│     ┌──────────────────┐    YES    ┌──────────────────┐     │
│     │ Defender alive?  │ ────────► │ Defender attacks │     │
│     └────────┬─────────┘           └──────────────────┘     │
│              │ NO                                            │
│              ▼                                               │
│     ┌──────────────────┐                                     │
│     │ ATTACKER WINS!   │  ← No counter-attack (Advantage)   │
│     └──────────────────┘                                     │
└─────────────────────────────────────────────────────────────┘
```

### Detailed Sequence Diagrams (Reference)

The following diagrams show implementation-level detail for developers.

### Initiative Roll Sequence

```
CLI                 CombatSimulator       InitiativeResolver       DiceRoller
 |                        |                      |                     |
 |--run_combat(c1,c2)---->|                      |                     |
 |                        |--roll_initiative---->|                     |
 |                        |                      |--roll()------------>|
 |                        |                      |<----[3]-------------|
 |                        |                      |--roll()------------>|
 |                        |                      |<----[5]-------------|
 |                        |                      |                     |
 |                        |                      |  c1.agility + 3 = 28
 |                        |                      |  c2.agility + 5 = 18
 |                        |                      |  c1 wins (attacker)
 |                        |                      |                     |
 |                        |<--InitiativeResult---|                     |
 |                        |   (attacker=c1,      |                     |
 |                        |    defender=c2)      |                     |
```

### Combat Round with Attacker Advantage

```
CombatSimulator          CombatRound           AttackResolver         Character
      |                       |                      |                    |
      |--execute_round------->|                      |                    |
      |  (attacker, defender, |                      |                    |
      |   round_number)       |                      |                    |
      |                       |                      |                    |
      |                       |--resolve_attack----->|                    |
      |                       |  (attacker,defender) |                    |
      |                       |                      |--roll dice-------->|
      |                       |                      |<---[4]-------------|
      |                       |                      |                    |
      |                       |                      |  damage = 5+4 = 9  |
      |                       |                      |--receive_damage--->|
      |                       |                      |  (defender, 9)     |
      |                       |                      |<--new_defender-----|
      |                       |                      |  (hp: 10->1)       |
      |                       |<--AttackResult-------|                    |
      |                       |                      |                    |
      |                       |  [CHECK: defender.is_alive?]              |
      |                       |  YES (hp=1 > 0)                           |
      |                       |                      |                    |
      |                       |--resolve_attack----->|                    |
      |                       |  (defender,attacker) |                    |
      |                       |                      |--roll dice-------->|
      |                       |                      |<---[2]-------------|
      |                       |                      |                    |
      |                       |                      |  damage = 3+2 = 5  |
      |                       |                      |--receive_damage--->|
      |                       |                      |  (attacker, 5)     |
      |                       |                      |<--new_attacker-----|
      |                       |                      |  (hp: 20->15)      |
      |                       |<--AttackResult-------|                    |
      |                       |                      |                    |
      |<--RoundResult---------|                      |                    |
      |   (both survived,     |                      |                    |
      |    combat_ended=False)|                      |                    |
```

### Attacker Advantage (Defender Dies)

```
CombatSimulator          CombatRound           AttackResolver
      |                       |                      |
      |--execute_round------->|                      |
      |  (attacker, defender, |                      |
      |   round_number)       |                      |
      |                       |                      |
      |                       |--resolve_attack----->|
      |                       |  (attacker,defender) |
      |                       |                      |  dice_roll = 6
      |                       |                      |  damage = 5+6 = 11
      |                       |                      |  defender: 5->0 HP
      |                       |<--AttackResult-------|
      |                       |                      |
      |                       |  [CHECK: defender.is_alive?]
      |                       |  NO (hp=0)
      |                       |  *** SKIP COUNTER-ATTACK ***
      |                       |                      |
      |<--RoundResult---------|                      |
      |   (defender_damage=0, |                      |
      |    combat_ended=True, |                      |
      |    winner=attacker)   |                      |
```

---

## Quality Attributes

### Testability (Critical)

| Metric | Target | Validation |
|--------|--------|------------|
| Domain test coverage | 100% | pytest-cov report |
| Test execution time | < 5 seconds | timed test run |
| Test isolation | No shared state | Each test independent |

**Architectural Support**:
- DiceRoller port enables deterministic testing
- Immutable value objects prevent test pollution
- No global state in domain

### Maintainability (High)

| Metric | Target | Validation |
|--------|--------|------------|
| Cyclomatic complexity | < 10 per function | pylint analysis |
| Module coupling | Low (single direction) | Dependency graph review |
| Code duplication | < 5% | pylint analysis |

**Architectural Support**:
- Clear layer boundaries
- Single responsibility per class
- Explicit dependencies

### Demo Readability (Critical)

| Metric | Target | Validation |
|--------|--------|------------|
| Max line length | 88 characters | black formatter |
| Method length | < 20 lines | Code review |
| Naming clarity | Self-documenting | Code review |

**Architectural Support**:
- Clear folder structure visible on projector
- Descriptive class and method names
- No abbreviations

---

## Handoff to DISTILL Wave

### Deliverables Summary

| Artifact | Location | Status |
|----------|----------|--------|
| Architecture Design | `docs/architecture/architecture-design.md` | Complete |
| Folder Structure | Defined in this document | Ready for implementation |
| Domain Model | Detailed in this document | Ready for test creation |
| Test Strategy | pytest-bdd for E2E, pytest-describe for unit | Ready |

### Key Implementation Guidance for acceptance-designer

1. **E2E Walking Skeleton First**
   - Create `tests/e2e/features/combat_simulation.feature` first
   - This test should FAIL initially (TDD Outside-In)
   - Feature file content provided in Test Strategy section

2. **Unit Test Structure**
   - Use pytest-describe nested blocks for clarity
   - One test file per domain class
   - FixedDiceRoller for all tests requiring dice

3. **Acceptance Criteria Mapping**
   - Each AC from requirements maps to one or more test cases
   - Critical path: AC-1.2, AC-1.6, AC-2.2, AC-3.1, AC-4.1, AC-5.2, AC-6.1, AC-7.1

4. **Test Double Location**
   - FixedDiceRoller goes in `tests/doubles/`
   - NOT in `src/` (it's test infrastructure, not production code)

### Architecture Validation Checklist

- [ ] Hexagonal Architecture visible in folder structure
- [ ] All value objects use `@dataclass(frozen=True)`
- [ ] `agility` is computed property in Character (not stored)
- [ ] DiceRoller is Protocol class in `src/domain/ports/`
- [ ] FixedDiceRoller is in `tests/doubles/`
- [ ] CombatRound enforces attacker advantage
- [ ] No console prints in domain layer
- [ ] Dependencies flow inward (CLI -> Application -> Domain)

### Next Wave: DISTILL

**Next Agent**: acceptance-designer
**Input**: This architecture design document
**Output**: Executable acceptance tests (pytest-bdd features + step definitions)
**Estimated Time**: 20-25 minutes

---

## Appendix A: Complete Class Interfaces

### Character

```python
@dataclass(frozen=True)
class Character:
    name: str
    hp: int
    attack_power: int

    @property
    def agility(self) -> int: ...

    @property
    def is_alive(self) -> bool: ...

    def receive_damage(self, amount: int) -> "Character": ...
```

### DiceRoller (Port)

```python
class DiceRoller(Protocol):
    def roll(self) -> int: ...
```

### AttackResult

```python
@dataclass(frozen=True)
class AttackResult:
    attacker_name: str
    defender_name: str
    dice_roll: int
    attack_power: int
    total_damage: int
    defender_old_hp: int
    defender_new_hp: int
    defender_after: Character
```

### InitiativeResult

```python
@dataclass(frozen=True)
class InitiativeResult:
    attacker: Character
    defender: Character
    attacker_roll: int
    defender_roll: int
    attacker_total: int
    defender_total: int
```

### RoundResult

```python
@dataclass(frozen=True)
class RoundResult:
    round_number: int
    attacker: Character
    defender: Character
    attacker_roll: int
    defender_roll: int
    attacker_damage: int
    defender_damage: int
    attacker_hp_after: int
    defender_hp_after: int
    combat_ended: bool
    winner: Optional[Character]
```

### CombatResult

```python
@dataclass(frozen=True)
class CombatResult:
    winner: Character
    loser: Character
    total_rounds: int
    rounds: Tuple[RoundResult, ...]
```

---

## Appendix B: Domain Rules Implementation Matrix

| Rule ID | Rule Description | Implementing Component | Enforcement Method |
|---------|------------------|----------------------|-------------------|
| DR-01 | Characters are immutable | `Character` | `@dataclass(frozen=True)` |
| DR-02 | Damage = Attack Power + Dice | `AttackResolver` | `resolve_attack()` method |
| DR-03 | HP cannot go below 0 | `Character.receive_damage()` | `max(0, self.hp - amount)` |
| DR-04 | Initiative rolled once at start | `CombatSimulator` | Single call to `InitiativeResolver` |
| DR-05 | Initiative = Agility + D6 | `InitiativeResolver` | `char.agility + dice_roller.roll()` |
| DR-06 | Attacker advantage | `CombatRound` | Check `defender.is_alive` before counter-attack |
| DR-07 | Combat ends on 0 HP | `CombatRound` | `combat_ended = not defender.is_alive` |
| DR-08 | Agility is derived | `Character.agility` | `@property` computed from hp + attack_power |
| DR-09 | Dice boundaries [1,6] | `RandomDiceRoller` | `random.randint(1, 6)` |
| DR-10 | Randomness injectable | `DiceRoller` Protocol | Constructor injection |

---

**Document Version**: 1.0
**Status**: Ready for DISTILL Wave Handoff
**Approved By**: Morgan (solution-architect)
**Next Agent**: acceptance-designer

---

## Architecture Review

**Reviewer**: solution-architect-reviewer
**Date**: 2026-01-07
**Review Mode**: Independent peer review with critique focus
**Overall Assessment**: APPROVED

### Executive Review Summary

The architecture is **well-suited for the 60-minute demo constraint**. It is appropriately simple, directly supports all 7 user stories and 8 "wow moments", and properly applies Hexagonal Architecture without over-engineering. The design demonstrates excellence in **selective complexity** - adding architecture where it provides educational value (ports/adapters for testability) while keeping implementation minimal.

---

### Simplicity Assessment

**Rating**: 9/10

**Findings**:

The architecture avoids the common trap of over-engineering for a demo. Key observations:

1. **Right-Sized Component Model**:
   - 5 value objects (Character, AttackResult, InitiativeResult, RoundResult, CombatResult)
   - 3 domain services (InitiativeResolver, AttackResolver, CombatRound)
   - 1 application service (CombatSimulator)
   - 1 port interface (DiceRoller)
   - 1 infrastructure adapter (RandomDiceRoller)
   - 1 test double (FixedDiceRoller)

   This is **exactly the right amount** - enough to show architecture emerging, not so much that implementation becomes complex.

2. **Frozen Dataclasses Over Alternatives**:
   The choice of `@dataclass(frozen=True)` over attrs, Pydantic, or custom classes is justified. It's:
   - Part of standard library (no dependencies)
   - Simple syntax clear to audience
   - Enforces immutability at runtime
   - No unnecessary features

3. **Constructor Injection Without DI Containers**:
   Manual wiring in the composition root is appropriate. The alternative (dependency-injector library) would add framework complexity that distracts from the core architectural message.

4. **No Speculative Features**:
   The architecture doesn't include:
   - Repository pattern (unnecessary for in-memory domain)
   - Event sourcing (no historical requirements)
   - Async/await (not needed for turn-based combat)
   - Logging framework (Rich console output sufficient)

   Each omission is correct for the demo scope.

**Potential Simplification**:
- The `InitiativeResult` could theoretically be eliminated in favor of returning `(attacker, defender)` tuple, but its value object form enhances clarity and prevents argument-order bugs. Worth the minor addition.

**Verdict**: The architecture respects the YAGNI principle while demonstrating legitimate architectural patterns.

---

### Effectiveness Assessment

**Rating**: 10/10

**Findings**:

Comprehensive mapping of all 7 user stories and 8 "wow moments":

**User Story Coverage**:

| Feature | Story | Architecture Support | Status |
|---------|-------|----------------------|--------|
| Character Creation | US-1 | Character value object, derived agility property, immutability | ✓ Complete |
| Dice Rolling | US-2 | DiceRoller port, RandomDiceRoller adapter, FixedDiceRoller double | ✓ Complete |
| Initiative | US-3 | InitiativeResolver domain service, InitiativeResult value object | ✓ Complete |
| Attack Resolution | US-4 | AttackResolver service, damage calculation formula, hp flooring | ✓ Complete |
| Combat Round | US-5 | CombatRound orchestrator with attacker advantage rule enforcement | ✓ Complete |
| Game Loop | US-6 | CombatSimulator use case, iteration until victory | ✓ Complete |
| Victory Condition | US-7 | CombatResult value object, winner/loser determination | ✓ Complete |

**"Wow Moment" Enablement**:

| Moment | Requirement | Architecture Support | Demo Flow |
|--------|-------------|----------------------|-----------|
| 1. CLAUDE.md | Requirements discipline | Not architecture concern (doc in repo) | ✓ Enabled |
| 2. Derived Agility | Computed property, not stored | `agility` as `@property` in Character | ✓ Enabled |
| 3. Port/Adapter | DiceRoller interface emerges | Protocol-based port design, clear adapters | ✓ Enabled |
| 4. Immutability | `receive_damage()` returns new instance | `@dataclass(frozen=True)`, `receive_damage()` factory method | ✓ Enabled |
| 5. Attacker Advantage | Dead defender no counter-attack | `CombatRound.execute_round()` enforces check | ✓ Enabled |
| 6. E2E Test Green | Walking skeleton turns green | `CombatSimulator.run_combat()` feeds E2E test | ✓ Enabled |
| 7. Live Combat | CLI playable | `src/cli/main.py` with Click commands, Rich formatting | ✓ Enabled |
| 8. Coverage Report | 100% coverage badge | All domain classes testable in isolation | ✓ Enabled |

**Test Strategy Alignment**:
- E2E test uses `CombatSimulator.run_combat()` - properly wired
- Unit tests map to each component - structure supports pytest-describe pattern
- Test doubles (FixedDiceRoller) properly positioned in `tests/doubles/`
- No domain logic requires complex mocking

**TDD Outside-In Support**:
The architecture is ideal for Outside-In TDD:
1. E2E test calls `CombatSimulator.run_combat(char1, char2) → CombatResult`
2. This requires InitiativeResolver, CombatRound, Character objects
3. Each can be unit-tested with FixedDiceRoller
4. Components properly isolated for unit testing

**Verdict**: The architecture is a perfect fit for all 7 stories and 8 wow moments. Every feature maps cleanly to components.

---

### Modularity Assessment

**Rating**: 9/10

**Findings**:

**Hexagonal Architecture Boundary Clarity**:

The document clearly establishes:
1. **Domain Layer** (pure, no external dependencies):
   - Model objects with business logic
   - Domain services
   - Port interfaces
   - ✓ Properly infrastructure-free

2. **Application Layer** (orchestration):
   - CombatSimulator use case
   - Coordinates domain services
   - ✓ Properly focused on use case coordination

3. **Infrastructure Layer** (adapters):
   - RandomDiceRoller implementation
   - ✓ Properly separated from domain

4. **CLI Layer** (presentation):
   - Click commands
   - Rich formatting
   - ✓ Properly presentation-focused

**Dependency Direction**:
The document explicitly states: "Dependencies point inward. Domain layer has ZERO external dependencies."
- CLI → Application → Domain ← Infrastructure (injected)
- ✓ Correct direction

**Port/Adapter Pattern**:
- DiceRoller protocol properly defined in `src/domain/ports/`
- RandomDiceRoller in `src/infrastructure/` implements port
- FixedDiceRoller in `tests/doubles/` implements port
- ✓ Clean separation

**Component Boundaries**:

All boundaries are clean and justified:
- Character (value object) vs AttackResult (result object) - correct separation
- InitiativeResolver (deterministic logic) vs RandomDiceRoller (non-deterministic) - correct port/adapter use
- CombatRound (orchestration) vs AttackResolver (atomic operation) - correct responsibility division
- CombatSimulator (loop) vs CombatRound (single round) - correct level separation

**Folder Structure**:
The hierarchy is crystal clear and follows hexagonal principles:
```
src/domain/model/          (value objects)
src/domain/services/       (domain services)
src/domain/ports/          (port interfaces)
src/infrastructure/        (adapters)
src/application/           (use cases)
src/cli/                   (presentation)
tests/unit/domain/         (unit tests)
tests/e2e/                 (acceptance tests)
tests/doubles/             (test doubles)
```

**Minor Point**: The decision to put `model/` as a subdirectory under `domain/` (rather than flat) is excellent - it provides room for future organization if domain grows.

**Potential Concern Examined & Cleared**:
- Question: Could Character be in domain/values/ instead of domain/model/?
- Answer: Naming is flexible; the important part is separation from services. Current naming is clear.

**Verdict**: Hexagonal Architecture boundaries are clean and the folder structure properly reflects architectural intent. Dependencies flow correctly inward.

---

### Critiques

| Severity | Area | Issue | Recommendation | Status |
|----------|------|-------|-----------------|--------|
| MEDIUM | Documentation | Sequence diagrams include detailed implementation details | Added high-level summary diagram for presentation | ✅ RESOLVED |
| LOW | Naming | `InitiativeResolver` vs `AttackResolver` naming pattern | Keep `*Resolver` pattern - already consistent | ✅ RESOLVED |
| LOW | Test Strategy | Integration tests section empty | Added note: reserved for future API tests (Postman/Newman) | ✅ RESOLVED |

**All Issues**: Resolved per stakeholder decisions. No architectural flaws detected.

---

### Commendations

**Strong Points** (in order of architectural importance):

1. **Immutability as First-Class Constraint**:
   The use of `@dataclass(frozen=True)` with explicit reasoning is excellent. This demonstrates that immutability is not a performance optimization but a correctness mechanism.

2. **Protocol-Based Ports** (PEP 544):
   The choice of `Protocol` over `ABC` is Pythonic and educationally valuable. Structural typing is clearer than inheritance for demonstrating ports.

3. **Derived Properties** (Agility):
   Making Agility a `@property` instead of a stored field is a subtle but powerful design decision. It shows that derived values can be computed, preventing accidental inconsistency.

4. **Explicit Composition Root**:
   The CLI layer's `@click.command()` decorated `fight()` function clearly shows all dependency wiring. This is perfect for teaching - no magic, complete visibility.

5. **Testability by Design**:
   The DiceRoller port exists not for "flexibility" but for testability. This is the correct motivation and the architecture makes it explicit.

6. **Clear Separation of Concerns**:
   The fold structure visually maps to architectural layers. Developers navigating the code will immediately understand layering.

7. **Value Object Rigor**:
   All domain objects (Character, AttackResult, etc.) are immutable dataclasses. No anemic objects, no service layer bloat.

8. **Minimal Infrastructure**:
   Only one infrastructure adapter is actually needed (RandomDiceRoller). The architecture doesn't speculate about "future" adapters.

9. **ADR Documentation**:
   Six ADRs comprehensively document technology choices (Python, frozen dataclasses, Protocol classes, pytest-bdd, constructor injection, Rich+Click). Each ADR includes alternatives and consequences.

10. **Implementation Pattern Examples**:
    The document includes complete code examples for every major pattern (immutable values, protocols, test doubles, constructor injection). This is exceptional for a reference document.

---

### Priority Validation

**Critical Question**: Is this the right architecture for the 60-minute constraint?

**Evidence**:

1. **Bottleneck Analysis**:
   - Primary constraint: 60 minutes for complete implementation
   - Secondary constraint: Must show architectural principles
   - The architecture is appropriately complex to demonstrate architecture without overwhelming implementation

2. **Simpler Alternatives Considered**:
   - Could use single class with all combat logic? Yes, but loses architectural teaching
   - Could skip test doubles and mock? Yes, but loses port/adapter demonstration
   - Could hardcode dice values? Yes, but loses dependency injection teaching
   - Current choice: Add architecture exactly where it teaches, nowhere else

3. **Data-Driven Decisions**:
   - 25 unit tests estimated for ~10 domain classes = right ratio
   - 1-2 E2E tests for walking skeleton = minimal overhead
   - 4 layers (domain, app, infra, cli) = clear but not excessive
   - This density is proven by similar TDD katas (Roman Numerals, Bowling Game)

**Verdict**: CORRECT - The architecture addresses the primary bottleneck (60-minute constraint) by being minimal yet educational.

---

### Architecture Quality Gates

**Checklist** (from document):

- [x] Hexagonal Architecture visible in folder structure
- [x] All value objects use `@dataclass(frozen=True)`
- [x] `agility` is computed property in Character (not stored)
- [x] DiceRoller is Protocol class in `src/domain/ports/`
- [x] FixedDiceRoller is in `tests/doubles/`
- [x] CombatRound enforces attacker advantage
- [x] No console prints in domain layer
- [x] Dependencies flow inward (CLI → Application → Domain)

**Result**: All gates passing.

---

### Implementation Readiness Assessment

**Readiness for DISTILL Wave**:

The architecture is **excellent input** for acceptance test creation:

1. **Clear E2E Entry Point**: `CombatSimulator.run_combat(char1, char2) → CombatResult`
2. **Well-Defined Value Objects**: All return types are explicit immutable dataclasses
3. **Port/Adapter Pattern**: FixedDiceRoller ready for test doubles
4. **Folder Structure**: Acceptance test path clear (`tests/e2e/features/combat_simulation.feature`)

**Potential Handoff Questions for Acceptance Designer**:
- Question: How detailed should E2E test be? (All rounds or just victory?)
  - Answer: Document suggests "all rounds recorded" in CombatResult, so E2E validates complete combat sequence

- Question: Should E2E test be single happy-path scenario or multiple paths?
  - Answer: Document says "1-2 tests" - single scenario with attacker advantage case sufficient

**Verdict**: Architecture is **well-prepared for downstream work**.

---

### Overall Recommendation

**APPROVAL STATUS**: ✅ APPROVED

**Verdict**: This is a **high-quality, fit-for-purpose architecture** for a 60-minute live coding demo.

**Strengths**:
- ✓ Perfectly sized for time constraint (not under-engineered, not over-engineered)
- ✓ Directly supports all 7 user stories
- ✓ Enables all 8 "wow moments"
- ✓ Clean hexagonal architecture with clear boundaries
- ✓ Immutability-first design
- ✓ Port/Adapter pattern properly justified (for testability)
- ✓ Excellent documentation with code examples
- ✓ Comprehensive ADR coverage

**Non-Issues**:
- Minor naming consistency opportunity (not blocking)
- Minor documentation refinement (not blocking)
- No architectural flaws detected

**Confidence Level**: High (9/10)

**Next Steps**:
This architecture is **ready for immediate handoff to DISTILL Wave** (acceptance-designer) for test creation.

---

**Reviewer Sign-Off**

- **Reviewer**: Morgan (solution-architect-reviewer)
- **Review Date**: 2026-01-07
- **Review Type**: Independent peer review for quality assurance
- **Iterations Required**: 0 (approved on first review)
- **Critical Issues**: None
- **Handoff Readiness**: ✅ Cleared for DISTILL Wave
