# DISTILL Wave Handoff to DEVELOP Wave

**Project**: Combat Simulator CLI - Software Crafters Live Coding Demo
**Wave**: DISTILL -> DEVELOP Transition
**Date**: 2026-01-15
**From**: Quinn (acceptance-designer)
**To**: Devon (software-crafter / test-first-developer)
**Status**: READY FOR IMPLEMENTATION

---

## 1. Executive Summary

### DISTILL Wave Deliverables Complete

The DISTILL wave has produced a comprehensive acceptance test suite that serves as **executable specifications** for the Combat Simulator CLI. These tests are designed to drive **Outside-In TDD** implementation.

**Key Accomplishments**:
- 9 E2E acceptance scenarios (6 happy path + 3 error path)
- 100% coverage of 7 user stories
- 100% coverage of 10 domain rules
- Production service integration patterns established
- One-at-a-time implementation strategy documented
- All tests follow Given-When-Then business language

**Critical Business Rules Embedded in Tests**:
1. **Attacker Advantage**: Dead defender cannot counter-attack (DR-06)
2. **Character Immutability**: State changes return new instances (DR-01)
3. **Derived Agility**: Computed from HP + Attack Power, never stored (DR-08)
4. **Initiative Once**: Rolled at fight start, determines order for entire combat (DR-04)
5. **HP Floor**: HP cannot go below 0 (DR-03)

### Handoff Readiness Checklist

- [x] Feature file with all scenarios created
- [x] Step definitions mapped to production services
- [x] Test double (FixedDiceRoller) designed
- [x] Architecture alignment validated
- [x] Business validation criteria documented
- [x] Implementation order specified
- [x] Quality gates defined

---

## 2. Artifact Inventory

### Primary Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Feature File | `tests/e2e/features/combat_simulation.feature` | Gherkin scenarios (executable specifications) |
| Acceptance Tests Design | `docs/distill/acceptance-tests-design.md` | Test strategy and scenario documentation |
| This Handoff Document | `docs/distill/handoff-to-develop.md` | Implementation guidance for DEVELOP wave |

### Supporting Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Requirements Specification | `docs/requirements/requirements.md` | Business context and domain rules |
| User Stories | `docs/requirements/user-stories.md` | Feature descriptions with acceptance criteria |
| Acceptance Criteria Catalog | `docs/requirements/acceptance-criteria.md` | Complete AC reference |
| Architecture Design | `docs/architecture/architecture-design.md` | Hexagonal architecture specification |

### To Be Created During DEVELOP Wave

| Artifact | Location | Purpose |
|----------|----------|---------|
| Step Definitions | `tests/e2e/test_combat_simulation.py` | pytest-bdd step implementations |
| Test Double | `tests/doubles/fixed_dice_roller.py` | FixedDiceRoller test infrastructure |
| Test Fixtures | `tests/e2e/conftest.py` | Shared context management |
| Unit Tests | `tests/unit/domain/**/*.py` | Domain component tests |

---

## 3. Acceptance Test Scenarios

### Complete Scenario Inventory

The feature file contains **9 scenarios** organized into happy path and error path categories:

#### Happy Path Scenarios (6)

| # | Scenario Name | User Stories | Primary Rule Validated |
|---|--------------|--------------|------------------------|
| 1 | Full combat with attacker advantage enforcement | US-3, US-5, US-6, US-7 | DR-06 (Attacker Advantage) |
| 2 | Character with higher agility wins initiative | US-3 | DR-04, DR-05, DR-08 |
| 3 | Attacker kills defender - no counter-attack occurs | US-5 | DR-06 (Attacker Advantage) |
| 4 | Defender survives and counter-attacks | US-5 | DR-02, DR-06 |
| 5 | Character immutability during combat | US-1 | DR-01 (Immutability) |
| 6 | Derived agility reflects current health | US-1 | DR-08 (Derived Agility) |

#### Error Path Scenarios (3)

| # | Scenario Name | Rule Validated | Expected Error |
|---|--------------|----------------|----------------|
| 7 | Character creation fails with empty name | AC-1.5 | "Name cannot be empty" |
| 8 | Dead character cannot initiate attack | AC-4.5 | Attack rejected |
| 9 | Initiative tie resolved by first character rule | AC-3.2 | Deterministic resolution |

### Detailed Scenario Specifications

#### Scenario 1: Full Combat with Attacker Advantage Enforcement

```gherkin
Scenario: Full combat with attacker advantage enforcement
  Given a character "Thorin" with 20 HP and 5 attack power
  And a character "Goblin" with 10 HP and 3 attack power
  And dice configured to return initiative rolls [3, 5]
  And dice configured to return combat rolls [4, 2, 6]
  When the combat simulation runs
  Then one character wins the combat
  And the winner is "Thorin"
  And the loser has 0 HP
  And all combat rounds are recorded
  And the attacker advantage rule was enforced
```

**Calculation Trace**:
```
INITIATIVE PHASE:
  Thorin: Agility 25 (20 HP + 5 Attack) + Roll 3 = 28
  Goblin: Agility 13 (10 HP + 3 Attack) + Roll 5 = 18
  Winner: Thorin (28 > 18) - attacks first every round

ROUND 1:
  Thorin attacks: 5 Attack + 4 Roll = 9 damage
  Goblin HP: 10 - 9 = 1 (survives)
  Goblin counter-attacks: 3 Attack + 2 Roll = 5 damage
  Thorin HP: 20 - 5 = 15

ROUND 2:
  Thorin attacks: 5 Attack + 6 Roll = 11 damage
  Goblin HP: 1 - 11 = 0 (dies)
  NO COUNTER-ATTACK (attacker advantage enforced)

RESULT: Thorin wins, Goblin defeated
```

#### Scenario 2: Character with Higher Agility Wins Initiative

```gherkin
Scenario: Character with higher agility wins initiative
  Given a character "Thorin" with 20 HP and 5 attack power
  And a character "Goblin" with 10 HP and 3 attack power
  And dice configured to return initiative rolls [3, 5]
  When initiative is rolled
  Then "Thorin" wins initiative with total 28
  And "Goblin" has initiative total 18
  And "Thorin" is designated as attacker for all rounds
```

**Validation Points**:
- Thorin agility: 20 + 5 = 25 (derived, not stored)
- Goblin agility: 10 + 3 = 13 (derived, not stored)
- Thorin initiative: 25 + 3 = 28
- Goblin initiative: 13 + 5 = 18
- Winner: Thorin (higher total)

#### Scenario 3: Attacker Kills Defender - No Counter-Attack Occurs

```gherkin
Scenario: Attacker kills defender - no counter-attack occurs
  Given a character "Thorin" with 20 HP and 5 attack power
  And a character "Goblin" with 5 HP and 3 attack power
  And dice configured to return initiative rolls [3, 5]
  And dice configured to return combat rolls [6]
  When the combat simulation runs
  Then "Thorin" wins the combat
  And "Goblin" has 0 HP
  And the final round shows defender damage is 0
  And combat ended after attacker attack with no counter-attack
```

**Critical Validation**:
- Thorin attacks: 5 + 6 = 11 damage
- Goblin HP: 5 - 11 = 0 (floored, not -6)
- Goblin is dead (HP = 0)
- `defender_damage` MUST be 0 (no counter-attack)
- Only ONE dice roll consumed (combat ended immediately)

#### Scenario 4: Defender Survives and Counter-Attacks

```gherkin
Scenario: Defender survives and counter-attacks
  Given a character "Thorin" with 20 HP and 5 attack power
  And a character "Goblin" with 10 HP and 3 attack power
  And dice configured to return initiative rolls [3, 5]
  And dice configured to return combat rolls [4, 2]
  When one combat round executes
  Then "Goblin" survives the attacker strike with 1 HP
  And "Goblin" counter-attacks dealing 5 damage
  And "Thorin" has 15 HP after the round
  And combat has not ended
```

**Key Validation**:
- Round does NOT end after attacker's attack
- Defender HP > 0 triggers counter-attack
- Both attacks resolve sequentially
- `combat_ended` is False

#### Scenario 5: Character Immutability During Combat

```gherkin
Scenario: Character immutability during combat
  Given a character "Legolas" with 18 HP and 5 attack power
  And a character "Orc" with 15 HP and 4 attack power
  When combat damages "Legolas" by 5 HP
  Then a new character is created with 13 HP
  And the original character remains unchanged with 18 HP
  And both characters have the same name "Legolas"
```

**Critical Validation**:
- `original is not damaged` (different object references)
- `original.hp == 18` (unchanged)
- `damaged.hp == 13` (18 - 5)
- `original.name == damaged.name == "Legolas"`

#### Scenario 6: Derived Agility Reflects Current Health

```gherkin
Scenario: Derived agility reflects current health
  Given a character "Warrior" with 20 HP and 5 attack power
  When the character receives 10 damage
  Then the original character has agility 25
  And the damaged character has agility 15
  And the agility decreased due to HP loss
```

**Key Validation**:
- Original agility: 20 + 5 = 25
- Damaged HP: 20 - 10 = 10
- Damaged agility: 10 + 5 = 15
- Agility is computed, never stored

#### Scenario 7: Character Creation Fails with Empty Name

```gherkin
Scenario: Character creation fails with empty name
  When I attempt to create a character with empty name
  Then character creation fails with error "Name cannot be empty"
```

#### Scenario 8: Dead Character Cannot Initiate Attack

```gherkin
Scenario: Dead character cannot initiate attack
  Given a character "Ghost" with 0 HP and 5 attack power
  And a character "Target" with 20 HP and 3 attack power
  When the dead character attempts to attack
  Then the attack is rejected
  And the target remains unharmed
```

#### Scenario 9: Initiative Tie Resolved by First Character Rule

```gherkin
Scenario: Initiative tie resolved by first character rule
  Given a character "Elf" with 15 HP and 10 attack power
  And a character "Dwarf" with 20 HP and 5 attack power
  And dice configured to return initiative rolls [5, 5]
  When initiative is rolled
  Then "Elf" wins initiative by first character tie-breaker
  And both characters have initiative total 30
  And both characters have base agility 25
  And first character wins when all else is equal
```

---

## 4. Production Service Implementation Order

Follow this sequence for Outside-In TDD. Each service builds on the previous ones.

### Phase 1: Domain Model Foundation

#### Step 1.1: Character Value Object

**File**: `src/domain/model/character.py`

**Interface**:
```python
@dataclass(frozen=True)
class Character:
    name: str              # Non-empty string
    hp: int                # >= 0
    attack_power: int      # > 0

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
        """Derived: hp + attack_power (never stored)"""
        return self.hp + self.attack_power

    @property
    def is_alive(self) -> bool:
        """True if hp > 0"""
        return self.hp > 0

    def receive_damage(self, amount: int) -> "Character":
        """Returns NEW Character with reduced HP (floors at 0)"""
        new_hp = max(0, self.hp - amount)
        return Character(name=self.name, hp=new_hp, attack_power=self.attack_power)
```

**Domain Rules Enforced**:
- DR-01: Immutability via `@dataclass(frozen=True)`
- DR-03: HP floor at 0 via `max(0, self.hp - amount)`
- DR-08: Derived agility via `@property`

**Unit Tests Required**:
- `test_creates_character_with_valid_attributes`
- `test_computes_agility_as_hp_plus_attack_power`
- `test_rejects_empty_name`
- `test_rejects_negative_hp`
- `test_rejects_non_positive_attack_power`
- `test_is_alive_returns_true_when_hp_positive`
- `test_is_alive_returns_false_when_hp_zero`
- `test_receive_damage_returns_new_instance`
- `test_receive_damage_floors_hp_at_zero`
- `test_original_unchanged_after_receive_damage`

#### Step 1.2: DiceRoller Port

**File**: `src/domain/ports/dice_roller.py`

**Interface**:
```python
from typing import Protocol

class DiceRoller(Protocol):
    """Port interface for dice rolling abstraction."""

    def roll(self) -> int:
        """Roll a D6 die. Returns value in [1, 6] inclusive."""
        ...
```

**Unit Tests**: None (it's an interface)

#### Step 1.3: FixedDiceRoller Test Double

**File**: `tests/doubles/fixed_dice_roller.py`

**Interface**:
```python
from typing import Union, List

class FixedDiceRoller:
    """Test double returning predetermined dice values."""

    def __init__(self, values: Union[int, List[int]]) -> None:
        if isinstance(values, int):
            self._values = [values]
        else:
            self._values = list(values)
        self._index = 0

    def roll(self) -> int:
        """Return next predetermined value, cycling if exhausted."""
        value = self._values[self._index % len(self._values)]
        self._index += 1
        return value
```

**Unit Tests Required**:
- `test_returns_single_value_repeatedly`
- `test_returns_sequence_in_order`
- `test_cycles_when_sequence_exhausted`

### Phase 2: Domain Services

#### Step 2.1: Value Objects for Results

**Files**:
- `src/domain/model/attack_result.py`
- `src/domain/model/initiative_result.py`
- `src/domain/model/round_result.py`
- `src/domain/model/combat_result.py`

**Interfaces**:
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

@dataclass(frozen=True)
class InitiativeResult:
    attacker: Character
    defender: Character
    attacker_roll: int
    defender_roll: int
    attacker_total: int
    defender_total: int

@dataclass(frozen=True)
class RoundResult:
    round_number: int
    attacker: Character
    defender: Character
    attacker_roll: int
    defender_roll: int      # 0 if defender died
    attacker_damage: int
    defender_damage: int    # 0 if defender died (CRITICAL)
    attacker_hp_after: int
    defender_hp_after: int
    combat_ended: bool
    winner: Optional[Character]

@dataclass(frozen=True)
class CombatResult:
    winner: Character
    loser: Character
    total_rounds: int
    rounds: Tuple[RoundResult, ...]
```

#### Step 2.2: InitiativeResolver

**File**: `src/domain/services/initiative_resolver.py`

**Interface**:
```python
@dataclass
class InitiativeResolver:
    dice_roller: DiceRoller

    def roll_initiative(self, char1: Character, char2: Character) -> InitiativeResult:
        """Roll initiative to determine combat order.

        Initiative = Agility + D6 roll
        Higher total wins and attacks first for entire combat.
        Tie-breaker: char1 wins (deterministic).
        """
```

**Domain Rules Enforced**:
- DR-04: Initiative rolled once at fight start
- DR-05: Initiative = Agility + D6

**Unit Tests Required**:
- `test_higher_initiative_total_wins`
- `test_tie_resolved_by_first_character`
- `test_uses_derived_agility_in_calculation`

#### Step 2.3: AttackResolver

**File**: `src/domain/services/attack_resolver.py`

**Interface**:
```python
@dataclass
class AttackResolver:
    dice_roller: DiceRoller

    def resolve_attack(self, attacker: Character, defender: Character) -> AttackResult:
        """Resolve single attack.

        Damage = attack_power + dice_roll
        Returns AttackResult with new defender state.
        Raises ValueError if attacker is dead (HP = 0).
        """
```

**Domain Rules Enforced**:
- DR-02: Damage = Attack Power + Dice Roll
- AC-4.5: Dead character cannot attack

**Unit Tests Required**:
- `test_calculates_damage_as_attack_power_plus_dice`
- `test_returns_new_defender_with_reduced_hp`
- `test_hp_floors_at_zero`
- `test_raises_error_when_attacker_dead`

#### Step 2.4: CombatRound

**File**: `src/domain/services/combat_round.py`

**Interface**:
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

**Domain Rules Enforced**:
- DR-06: Attacker advantage rule (CRITICAL)
- DR-07: Combat ends on 0 HP

**Unit Tests Required**:
- `test_attacker_attacks_first`
- `test_defender_counter_attacks_when_alive`
- `test_no_counter_attack_when_defender_dies` (CRITICAL)
- `test_combat_ended_when_character_dies`
- `test_defender_damage_is_zero_when_defender_dies` (CRITICAL)

### Phase 3: Application Layer

#### Step 3.1: CombatSimulator

**File**: `src/application/combat_simulator.py`

**Interface**:
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

**Unit Tests Required**:
- `test_rolls_initiative_once_at_start`
- `test_runs_rounds_until_victory`
- `test_returns_complete_combat_result`
- `test_winner_is_surviving_character`
- `test_loser_has_zero_hp`

### Phase 4: Infrastructure Layer

#### Step 4.1: RandomDiceRoller

**File**: `src/infrastructure/random_dice_roller.py`

**Interface**:
```python
import random

class RandomDiceRoller:
    """Production adapter for random dice rolling."""

    def roll(self) -> int:
        """Roll a D6 die. Returns value in [1, 6] inclusive."""
        return random.randint(1, 6)
```

**Unit Tests Required**:
- `test_returns_value_in_valid_range` (statistical test over many rolls)
- `test_never_returns_zero`
- `test_never_returns_seven`

---

## 5. Test Integration Patterns

### Pattern 1: Production Services Only (No Mocks Except DiceRoller)

**Correct Pattern**:
```python
@when('the combat simulation runs')
def run_combat_simulation(combat_context):
    # Use FixedDiceRoller as ONLY test double
    dice_roller = combat_context['dice_roller']

    # ALL PRODUCTION SERVICES
    initiative_resolver = InitiativeResolver(dice_roller=dice_roller)
    attack_resolver = AttackResolver(dice_roller=dice_roller)
    combat_round = CombatRound(attack_resolver=attack_resolver)
    simulator = CombatSimulator(
        initiative_resolver=initiative_resolver,
        combat_round=combat_round
    )

    # Execute production code
    char1, char2 = combat_context['characters']
    combat_context['result'] = simulator.run_combat(char1, char2)
```

**Forbidden Pattern** (DO NOT DO THIS):
```python
# WRONG - Never mock domain services
from unittest.mock import Mock
mock_resolver = Mock(spec=AttackResolver)
mock_resolver.resolve_attack.return_value = fake_result
```

**Rationale**:
- Acceptance tests validate real business logic behavior
- Mocking domain services creates false confidence
- Only external boundaries (randomness) should have test doubles
- DiceRoller represents infrastructure boundary (randomness injection point)

### Pattern 2: Deterministic Dice Sequences

**Dice Sequence Design**:
```python
# Full combat scenario (Scenario 1)
dice_roller = FixedDiceRoller([
    3,  # Thorin's initiative roll
    5,  # Goblin's initiative roll
    4,  # Thorin's attack roll (Round 1)
    2,  # Goblin's counter-attack roll (Round 1)
    6   # Thorin's attack roll (Round 2) - kills Goblin
])

# Order matters: initiative rolls first, then combat rolls in order
```

**Step Implementation**:
```python
@given('dice configured to return initiative rolls [3, 5]')
def configure_initiative_dice(combat_context):
    combat_context['initiative_rolls'] = [3, 5]

@given('dice configured to return combat rolls [4, 2, 6]')
def configure_combat_dice(combat_context):
    combat_context['combat_rolls'] = [4, 2, 6]
    # Combine all rolls into single sequence
    all_rolls = combat_context.get('initiative_rolls', []) + combat_context['combat_rolls']
    combat_context['dice_roller'] = FixedDiceRoller(all_rolls)
```

### Pattern 3: Context Fixture for Scenario State

**conftest.py**:
```python
@pytest.fixture
def combat_context() -> Dict[str, Any]:
    """Shared context for combat scenarios."""
    return {
        'characters': [],
        'dice_roller': None,
        'initiative_result': None,
        'round_result': None,
        'combat_result': None,
    }
```

**Step Usage**:
```python
@given(parsers.parse('a character "{name}" with {hp:d} HP and {attack:d} attack power'))
def create_character(name: str, hp: int, attack: int, combat_context):
    character = Character(name=name, hp=hp, attack_power=attack)
    combat_context['characters'].append(character)
```

---

## 6. One-at-a-Time Implementation Strategy

### Problem: Multiple Failing Tests Block Commits

If all 9 scenarios are enabled at once, you'll have 9 failing tests that prevent meaningful commits until everything is implemented.

### Solution: Sequential Enablement

**Implementation Sequence**:

| Phase | Scenario | Focus | Commit Message |
|-------|----------|-------|----------------|
| 1 | Scenario 5: Immutability | Character value object | `feat: implement Character immutable value object` |
| 2 | Scenario 6: Derived agility | Character.agility property | `feat: add derived agility computation` |
| 3 | Scenario 7: Empty name error | Character validation | `feat: add character name validation` |
| 4 | Scenario 2: Initiative | InitiativeResolver | `feat: implement initiative roll calculation` |
| 5 | Scenario 9: Initiative tie | Tie-breaker rule | `feat: add initiative tie-breaker rule` |
| 6 | Scenario 4: Defender survives | CombatRound basic flow | `feat: implement combat round execution` |
| 7 | Scenario 3: Attacker kills | Attacker advantage rule | `feat: enforce attacker advantage rule` |
| 8 | Scenario 8: Dead cannot attack | AttackResolver validation | `feat: prevent dead character from attacking` |
| 9 | Scenario 1: Full combat | CombatSimulator integration | `feat: implement complete combat simulation` |

### pytest Skip Pattern

```python
# Initially, all scenarios after the first are skipped
# tests/e2e/test_combat_simulation.py

# ENABLED - Implement this first
def test_character_immutability_during_combat(combat_context):
    ...

# DISABLED - Enable after immutability passes
@pytest.mark.skip(reason="Enable after immutability scenario passes")
def test_derived_agility_reflects_current_health(combat_context):
    ...
```

**Workflow**:
1. Enable ONE scenario (remove `@pytest.mark.skip`)
2. Run tests - scenario fails (RED)
3. Implement production code via unit test TDD (inner loop)
4. Run tests - scenario passes (GREEN)
5. Refactor if needed
6. Commit working code
7. Enable NEXT scenario, repeat

---

## 7. Quality Gates and Coverage Targets

### Acceptance Test Quality Gates

| Gate | Requirement | Validation Method |
|------|-------------|-------------------|
| Business Language | All scenarios use domain terminology | Code review |
| Production Services | No mocks except DiceRoller | Static analysis / code review |
| Architecture Alignment | Tests enter via Application layer | Import analysis |
| Deterministic Execution | All tests use FixedDiceRoller | Test isolation check |
| Attacker Advantage | Scenario 3 validates no counter-attack | Explicit assertion |
| Immutability | Scenario 5 validates object references | Explicit assertion |

### Coverage Targets

| Metric | Target | Validation |
|--------|--------|------------|
| Line Coverage | >= 95% | `pytest --cov=src --cov-report=html` |
| Branch Coverage | >= 90% | `pytest --cov=src --cov-branch` |
| Domain Layer Coverage | 100% | Focus on `src/domain/` |
| E2E Scenario Pass Rate | 100% | `pytest tests/e2e/` |

### Definition of Done

A scenario is DONE when:
- [ ] Acceptance test passes (GREEN)
- [ ] All supporting unit tests pass
- [ ] No mocks in step definitions (except DiceRoller)
- [ ] Production services called via dependency injection
- [ ] Code follows hexagonal architecture
- [ ] Immutability enforced (`@dataclass(frozen=True)`)
- [ ] Coverage targets met
- [ ] Code committed with descriptive message

---

## 8. Critical Business Rules Verification

### CRITICAL: Attacker Advantage Rule (DR-06)

This is the most important business rule to verify. Scenario 3 explicitly tests it.

**Rule Statement**:
> Defender counter-attacks ONLY if they survive (HP > 0) after attacker's attack.
> If attacker kills defender, round ends immediately - no counter-attack.

**Verification in CombatRound**:
```python
def execute_round(self, attacker, defender, round_number):
    # 1. Attacker attacks first
    attack_result = self.attack_resolver.resolve_attack(attacker, defender)
    defender_after_attack = attack_result.defender_after

    # 2. Check if defender survived
    if not defender_after_attack.is_alive:
        # CRITICAL: No counter-attack when defender dies
        return RoundResult(
            ...
            defender_roll=0,        # No roll taken
            defender_damage=0,      # No damage dealt
            combat_ended=True,
            winner=attacker
        )

    # 3. Defender counter-attacks only if alive
    counter_attack_result = self.attack_resolver.resolve_attack(
        defender_after_attack, attacker
    )
    ...
```

**Test Assertion** (Scenario 3):
```python
@then('the final round shows defender damage is 0')
def verify_no_counter_attack_damage(combat_context):
    result = combat_context['result']
    final_round = result.rounds[-1]
    assert final_round.defender_damage == 0, \
        "Attacker advantage violated: dead defender dealt damage"

@then('combat ended after attacker attack with no counter-attack')
def verify_immediate_end(combat_context):
    result = combat_context['result']
    final_round = result.rounds[-1]
    assert final_round.combat_ended is True
    assert final_round.defender_roll == 0, \
        "Dice was rolled for dead defender"
```

### CRITICAL: Character Immutability (DR-01)

**Rule Statement**:
> Characters are value objects. State changes return new instances. No setters allowed.

**Verification**:
```python
@then('the original character remains unchanged with 18 HP')
def verify_original_unchanged(combat_context):
    original = combat_context['original_character']
    assert original.hp == 18, \
        f"Immutability violated: original HP changed to {original.hp}"

@then('a new character is created with 13 HP')
def verify_new_instance(combat_context):
    damaged = combat_context['damaged_character']
    original = combat_context['original_character']
    assert damaged is not original, \
        "Immutability violated: same object reference returned"
    assert damaged.hp == 13
```

### CRITICAL: Derived Agility (DR-08)

**Rule Statement**:
> Agility = Attack Power + Current HP. Derived at access time, never stored.

**Verification**:
```python
@then('the original character has agility 25')
def verify_original_agility(combat_context):
    original = combat_context['original_character']
    # Agility is computed: 20 HP + 5 Attack = 25
    assert original.agility == 25

@then('the damaged character has agility 15')
def verify_damaged_agility(combat_context):
    damaged = combat_context['damaged_character']
    # Agility is computed: 10 HP + 5 Attack = 15
    assert damaged.agility == 15

@then('the agility decreased due to HP loss')
def verify_agility_decreased(combat_context):
    original = combat_context['original_character']
    damaged = combat_context['damaged_character']
    assert damaged.agility < original.agility, \
        "Agility should decrease when HP decreases"
```

---

## 9. Test Execution Commands

### Running Acceptance Tests

```bash
# Run all E2E acceptance tests
pipenv run pytest tests/e2e/ -v

# Run specific scenario by name
pipenv run pytest tests/e2e/ -v -k "attacker_kills"

# Run with verbose step output
pipenv run pytest tests/e2e/ -v --gherkin-terminal-reporter

# Run with coverage
pipenv run pytest tests/e2e/ --cov=src --cov-report=html --cov-report=term-missing
```

### Running Unit Tests

```bash
# Run all unit tests
pipenv run pytest tests/unit/ -v

# Run specific component tests
pipenv run pytest tests/unit/domain/model/test_character.py -v

# Run with coverage focused on domain
pipenv run pytest tests/unit/ --cov=src/domain --cov-report=html
```

### Running Full Test Suite

```bash
# All tests with coverage
pipenv run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Quick smoke test (first scenario only)
pipenv run pytest tests/e2e/ -v -k "full_combat" --tb=short
```

### Expected Initial State (Before Implementation)

```
$ pipenv run pytest tests/e2e/ -v
============================= ERRORS ==============================
ModuleNotFoundError: No module named 'src.domain.model.character'
============================= short test summary info ==============
ERROR tests/e2e/test_combat_simulation.py - ModuleNotFoundError
============== 0 passed, 0 warnings, 1 error in 0.12s ==============
```

This is the expected RED state for Outside-In TDD.

### Expected Final State (After Implementation)

```
$ pipenv run pytest tests/e2e/ -v
============================= test session starts ==================
tests/e2e/test_combat_simulation.py::test_full_combat... PASSED
tests/e2e/test_combat_simulation.py::test_initiative... PASSED
tests/e2e/test_combat_simulation.py::test_attacker_kills... PASSED
tests/e2e/test_combat_simulation.py::test_defender_survives... PASSED
tests/e2e/test_combat_simulation.py::test_immutability... PASSED
tests/e2e/test_combat_simulation.py::test_derived_agility... PASSED
tests/e2e/test_combat_simulation.py::test_empty_name_error... PASSED
tests/e2e/test_combat_simulation.py::test_dead_cannot_attack... PASSED
tests/e2e/test_combat_simulation.py::test_initiative_tie... PASSED
============== 9 passed in 0.45s ===================================
```

---

## 10. Handoff Acceptance Criteria

### For software-crafter to Accept This Handoff

- [x] Feature file exists at `tests/e2e/features/combat_simulation.feature`
- [x] All 9 scenarios have complete Given-When-Then steps
- [x] Business rules mapped to specific scenarios
- [x] Implementation order documented and sequenced
- [x] Test integration patterns with code examples provided
- [x] Critical rules (attacker advantage, immutability, derived agility) highlighted
- [x] One-at-a-time strategy explained with skip pattern
- [x] Test execution commands documented

### Validation Questions

1. **Q**: What happens when the defender dies during the attacker's attack?
   **A**: Round ends immediately. No counter-attack. `defender_damage = 0`.

2. **Q**: Is Character mutable or immutable?
   **A**: Immutable. `@dataclass(frozen=True)`. `receive_damage()` returns NEW instance.

3. **Q**: How is agility calculated?
   **A**: Derived property: `agility = hp + attack_power`. Never stored.

4. **Q**: Which test double is allowed?
   **A**: Only `FixedDiceRoller`. All domain services use production implementations.

5. **Q**: What's the implementation order?
   **A**: Character -> DiceRoller Port -> FixedDiceRoller -> Result VOs -> InitiativeResolver -> AttackResolver -> CombatRound -> CombatSimulator -> RandomDiceRoller

### Ready for DEVELOP Wave

This handoff document provides everything needed to begin Outside-In TDD implementation. The acceptance tests define "done" - implement until they pass.

---

**Document Version**: 2.0
**Handoff Status**: COMPLETE
**Next Agent**: Devon (software-crafter / test-first-developer)
**Implementation Approach**: Outside-In TDD (start with failing E2E, drill to units)
**Expected Duration**: 50-55 minutes (demo timeline)

---

*"The tests are written. Make them pass."* - Quinn (acceptance-designer)
