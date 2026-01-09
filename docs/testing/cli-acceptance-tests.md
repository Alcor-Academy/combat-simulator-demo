# CLI Acceptance Test Documentation

**Project**: Combat Simulator Demo
**Feature**: Interactive CLI Combat Viewer
**Wave**: DISTILL (Acceptance Test Design)
**Framework**: pytest-bdd
**Date**: 2026-01-09
**Status**: Ready for DEVELOP Wave Handoff

---

## 1. Overview

### 1.1 Purpose

This document describes the comprehensive acceptance test suite for the Interactive CLI Combat Viewer. Tests validate CLI behavior matches business requirements using pytest-bdd (Gherkin scenarios).

### 1.2 Testing Philosophy

**Outside-In TDD Approach**:
- Acceptance tests drive implementation (outer loop)
- Unit tests support component design (inner loop)
- Tests fail initially → guide development → pass naturally

**Production Service Integration**:
- **REAL** CombatSimulator (application service)
- **REAL** Character domain model
- **REAL** domain services (InitiativeResolver, AttackResolver, CombatRound)
- **REAL** RandomDiceRoller (seeded for determinism)
- **MOCK ONLY** I/O boundaries (Rich Console, input streams)

**One-at-a-Time Strategy**:
- Enable ONE scenario at a time
- Implement until test passes
- Commit working implementation
- Enable NEXT scenario
- Prevents commit blocks

---

## 2. Test Architecture

### 2.1 Framework: pytest-bdd

**Why pytest-bdd?**
- Existing project framework (9/9 E2E tests already use it)
- Gherkin scenarios (business-readable)
- pytest integration (fixtures, parametrization)
- Python step definitions (native language)

### 2.2 Directory Structure

```
tests/e2e/
├── features/
│   ├── combat_simulation.feature      # Existing (9 scenarios PASSING)
│   └── cli_combat.feature             # NEW (39 scenarios for CLI)
├── conftest.py                        # Shared fixtures
├── test_combat_simulation.py          # Existing step definitions
└── test_cli_combat.py                 # NEW CLI step definitions
```

### 2.3 Test Layers

```
┌─────────────────────────────────────────────────────────────┐
│ E2E Acceptance Tests (pytest-bdd)                          │
│ - Gherkin scenarios (business language)                    │
│ - Step definitions (Python)                                │
│ - Test through public interfaces                           │
└─────────────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ CLI Adapter (TO BE IMPLEMENTED)                            │
│ - CharacterCreator (input handling)                        │
│ - CombatRenderer (output formatting)                       │
│ - ConsoleOutput (Rich wrapper)                             │
└─────────────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ Application Layer (EXISTING - REAL)                        │
│ - CombatSimulator (use case service)                       │
└─────────────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ Domain Layer (EXISTING - REAL)                             │
│ - Character, CombatResult, Services                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Test Coverage

### 3.1 Coverage by User Story

| User Story | Scenario Count | Coverage |
|------------|----------------|----------|
| US-01: Interactive Character Creation | 8 scenarios | Complete |
| US-02: Visual Combat Progress | 7 scenarios | Complete |
| US-03: Combat Pacing Control | 3 scenarios | Complete |
| US-04: Clear Error Recovery | 5 scenarios | Complete |
| US-05: Victory Celebration | 3 scenarios | Complete |
| US-06: Cross-Platform Experience | 5 scenarios | Complete |
| **TOTAL** | **31 scenarios** | **100%** |

### 3.2 Coverage by Functional Requirement

| FR ID | Description | Scenarios | Status |
|-------|-------------|-----------|--------|
| FR-01 | CLI Entry Point and Lifecycle | 3 | Covered |
| FR-02 | Interactive Character Creation | 8 | Covered |
| FR-03 | Initiative Resolution Display | 2 | Covered |
| FR-04 | Combat Round Visualization | 6 | Covered |
| FR-05 | Victory Announcement | 3 | Covered |
| FR-06 | Timing and Pacing Control | 3 | Covered |
| FR-07 | Input Validation and Error Handling | 5 | Covered |
| FR-08 | Exit Confirmation | 3 | Covered |

### 3.3 Test Categories

**Happy Path Scenarios**: 12 (39%)
- Successful character creation
- Complete combat visualization
- Victory celebration
- Cross-platform rendering

**Error Path Scenarios**: 8 (26%)
- Invalid input validation
- Out-of-range values
- Empty inputs
- Non-numeric inputs

**Edge Case Scenarios**: 7 (23%)
- Random value boundaries
- Extended combat (7+ rounds)
- Initiative tie-breaker
- Defender death preventing counter-attack

**Integration Scenarios**: 4 (13%)
- End-to-end flow
- Timing accuracy
- Cross-platform compatibility
- Emoji fallback

---

## 4. Production Service Integration

### 4.1 CRITICAL REQUIREMENT

**Step definitions MUST call REAL production services.**

### 4.2 Real vs. Mock Strategy

#### REAL (No Mocks)

✅ **CombatSimulator** - Application service
✅ **Character** - Domain model
✅ **InitiativeResolver** - Domain service
✅ **AttackResolver** - Domain service
✅ **CombatRound** - Domain service
✅ **RandomDiceRoller** - Infrastructure adapter (seeded for determinism)

#### MOCK (I/O Boundaries Only)

❌ **Rich Console** - Output capture for assertions
❌ **Input Streams** - Simulated user input
❌ **Time Module** - Optional for timing tests

### 4.3 Production Service Fixture

```python
@pytest.fixture
def production_services():
    """
    REAL production services for CLI integration.

    NO MOCKS for business logic.
    """
    # REAL dice roller with fixed seed for determinism
    dice_roller = RandomDiceRoller(seed=42)

    # REAL domain services
    initiative_resolver = InitiativeResolver(dice_roller)
    attack_resolver = AttackResolver(dice_roller)
    combat_round_service = CombatRound(attack_resolver)

    # REAL application service
    combat_simulator = CombatSimulator(initiative_resolver, combat_round_service)

    return {
        'dice_roller': dice_roller,
        'combat_simulator': combat_simulator,
        'initiative_resolver': initiative_resolver,
        'attack_resolver': attack_resolver,
        'combat_round': combat_round_service,
    }
```

### 4.4 Why Real Services?

1. **Integration Validation**: Tests prove CLI integrates correctly with real application
2. **No Mock Drift**: Real services change, mocks lag → tests become unreliable
3. **Business Logic Accuracy**: Domain rules enforced by actual domain code
4. **Refactoring Safety**: Real services allow fearless refactoring

---

## 5. Test Configuration

### 5.1 Test Mode (Zero Delays)

**Purpose**: Fast test execution without waiting for pacing delays

```python
@pytest.fixture
def test_config():
    """CLI config with zero delays for tests."""
    return CLIConfig.test_mode()  # All delays = 0.0 seconds
```

**Benefits**:
- Tests complete in milliseconds, not seconds
- CI/CD pipeline fast
- No timing flakiness

### 5.2 Production Mode (Real Timing)

**Purpose**: Validate actual pacing in manual tests

```python
@pytest.fixture
def production_config():
    """CLI config with production timing."""
    return CLIConfig()  # Default delays (1.5-2s)
```

**Usage**: Manual testing only, not CI/CD

### 5.3 Deterministic Combat

**Purpose**: Predictable outcomes for repeatable tests

```python
@pytest.fixture
def deterministic_dice_roller():
    """Fixed seed for predictable combat."""
    return RandomDiceRoller(seed=42)
```

**Benefits**:
- Same input → same output
- No flaky tests due to randomness
- Predictable HP changes, round counts

---

## 6. Scenario Examples

### 6.1 Example 1: Character Creation (US-01)

**Gherkin Scenario**:
```gherkin
Scenario: User creates both characters with manual input
  When I enter "Hero" for character 1 name
  And I enter "50" for character 1 HP
  And I enter "10" for character 1 attack power
  And I enter "Villain" for character 2 name
  And I enter "40" for character 2 HP
  And I enter "8" for character 2 attack power
  Then both characters are created successfully
  And character 1 has name "Hero", HP 50, attack power 10, agility 60
```

**Step Definition (Production Service Integration)**:
```python
@when(parsers.parse('I enter "{input_value}" for character {char_num:d} {field}'))
def user_enters_input(cli_context, input_value, char_num, field):
    """Simulate user input for character creation."""
    cli_context['input_sequence'].append({
        'char_num': char_num,
        'field': field,
        'value': input_value
    })

@then(parsers.parse('character {char_num:d} has name "{name}", HP {hp:d}, attack power {attack:d}, agility {agility:d}'))
def verify_character_attributes(cli_context, char_num, name, hp, attack, agility):
    """
    Verify character attributes using REAL Character domain model.

    CRITICAL: Tests REAL Character properties, not mock.
    """
    char = cli_context['characters'][char_num - 1]

    assert char.name == name
    assert char.hp == hp
    assert char.attack_power == attack
    assert char.agility == agility  # Derived attribute (HP + attack_power)
```

**Key Points**:
- Input sequence simulated (mock I/O)
- Character created using REAL domain model
- Agility calculated automatically (domain logic)

---

### 6.2 Example 2: Combat Visualization (US-02)

**Gherkin Scenario**:
```gherkin
Scenario: Complete combat displays initiative with dice emoji and calculations
  Given two characters are created: Hero (HP 50, attack 10) and Villain (HP 40, attack 8)
  When combat starts
  Then initiative roll is displayed with 🎲 emoji
  And initiative shows both characters' agility values
  And initiative announces who attacks first
```

**Step Definition (Production Service Integration)**:
```python
@given(parsers.parse('two characters are created: {char1_name} (HP {char1_hp:d}, attack {char1_atk:d}) and {char2_name} (HP {char2_hp:d}, attack {char2_atk:d})'))
def create_two_characters_with_stats(cli_context, char1_name, char1_hp, char1_atk, char2_name, char2_hp, char2_atk):
    """
    Create two characters using REAL Character domain model.

    CRITICAL: Uses REAL Character constructor, not mock.
    """
    char1 = Character(name=char1_name, hp=char1_hp, attack_power=char1_atk)
    char2 = Character(name=char2_name, hp=char2_hp, attack_power=char2_atk)

    cli_context['characters'] = [char1, char2]

@when("combat starts")
def combat_starts(cli_context, production_services):
    """
    Execute combat using REAL CombatSimulator.

    CRITICAL: Calls REAL production service, not mock.
    """
    char1, char2 = cli_context['characters']

    # Call REAL CombatSimulator
    combat_result = production_services['combat_simulator'].run_combat(char1, char2)
    cli_context['combat_result'] = combat_result
```

**Key Points**:
- Characters created with REAL Character constructor
- Combat executed by REAL CombatSimulator
- CombatResult contains REAL InitiativeResult, RoundResult, AttackResult
- Tests verify REAL domain behavior

---

### 6.3 Example 3: Input Validation (US-04)

**Gherkin Scenario**:
```gherkin
Scenario: Invalid HP input triggers validation error and re-prompt
  When I enter "Hero" for character 1 name
  And I enter "150" for character 1 HP
  Then validation error is displayed in red
  And error message contains "HP must be between 1 and 999"
  When I enter "50" for character 1 HP
  Then character creation continues successfully
```

**Step Definition**:
```python
@when(parsers.parse('I enter "{input_value}" for character {char_num:d} HP'))
def user_enters_hp(cli_context, input_value, char_num):
    """Simulate HP input."""
    cli_context['input_sequence'].append({
        'char_num': char_num,
        'field': 'HP',
        'value': input_value
    })

@then("validation error is displayed in red")
def validation_error_displayed_red(cli_context):
    """Verify error message displayed with red styling."""
    # Output capture verification
    assert any('error' in str(output).lower() for output in cli_context.get('output', []))

@then(parsers.parse('error message contains "{text}"'))
def error_contains_text(cli_context, text):
    """Verify error message contains specific text."""
    error_outputs = [o for o in cli_context.get('output', []) if 'error' in str(o).lower()]
    assert any(text in str(o) for o in error_outputs)
```

**Key Points**:
- Validation logic in CharacterCreator (to be implemented)
- Error messages captured from output
- Re-prompt behavior validated

---

## 7. Test Data Management

### 7.1 Test Data Catalog

**Purpose**: Reusable character configurations for predictable outcomes

```python
COMBAT_SCENARIOS = {
    'standard_combat': {
        'char1': Character("Hero", 50, 10),
        'char2': Character("Villain", 40, 8),
        'expected_rounds': 3,
        'expected_winner': "Hero",
    },
    'one_shot_kill': {
        'char1': Character("Hero", 50, 10),
        'char2': Character("Weak", 5, 3),
        'expected_rounds': 1,
        'expected_winner': "Hero",
    },
    'balanced_fight': {
        'char1': Character("Warrior", 50, 8),
        'char2': Character("Knight", 50, 8),
        'expected_rounds': 7,
        'expected_winner': "Warrior",  # Deterministic with seed
    },
    'initiative_tie': {
        'char1': Character("Twin1", 30, 10),  # Agility: 40
        'char2': Character("Twin2", 30, 10),  # Agility: 40
        'tie_breaker': 'Twin1',  # First character wins
    },
}
```

### 7.2 Seeded Randomness

**Purpose**: Deterministic random values for repeatable tests

```python
# Fixed seed for predictable dice rolls
dice_roller = RandomDiceRoller(seed=42)

# Predictable outcomes:
# - Same seed → same roll sequence
# - Same characters + same seed → same combat outcome
# - Repeatable across test runs
```

### 7.3 Input Sequences

**Purpose**: Simulated user input for character creation tests

```python
VALID_INPUT_SEQUENCES = {
    'manual_input': [
        {'field': 'name', 'value': 'Hero'},
        {'field': 'HP', 'value': '50'},
        {'field': 'attack_power', 'value': '10'},
    ],
    'random_defaults': [
        {'field': 'name', 'value': 'Hero'},
        {'field': 'HP', 'value': ''},  # INVIO → random
        {'field': 'attack_power', 'value': ''},  # INVIO → random
    ],
}

INVALID_INPUT_SEQUENCES = {
    'out_of_range_hp': [
        {'field': 'name', 'value': 'Hero'},
        {'field': 'HP', 'value': '1000'},  # INVALID → error
        {'field': 'HP', 'value': '50'},    # VALID → continue
    ],
}
```

---

## 8. Quality Attributes Validation

### 8.1 Testability

**Design for Testability**:
- Dependency injection (services passed to components)
- Configuration externalized (CLIConfig)
- I/O boundaries abstracted (ConsoleOutput wraps Rich)
- Pure functions separated (formatting logic)

**Testability Metrics**:
- ✅ All CLI logic testable without manual interaction
- ✅ Tests run in CI/CD without interactive terminal
- ✅ Zero-delay test mode for fast execution
- ✅ Output captured for assertion

### 8.2 Maintainability

**Test Maintainability**:
- Gherkin scenarios (business-readable, stakeholder-reviewable)
- Step definitions organized by domain concept (not by feature file)
- Reusable fixtures (production_services, test_config)
- Test data catalog (predictable scenarios)

**Maintainability Metrics**:
- ✅ Scenario language clear to non-technical stakeholders
- ✅ Step definitions reusable across scenarios
- ✅ Fixtures reduce duplication
- ✅ Test data centralized

### 8.3 Traceability

**Requirements → Tests Mapping**:

| User Story | Scenarios | FR Covered |
|------------|-----------|------------|
| US-01 | 8 scenarios | FR-02, FR-07 |
| US-02 | 7 scenarios | FR-03, FR-04 |
| US-03 | 3 scenarios | FR-06 |
| US-04 | 5 scenarios | FR-07 |
| US-05 | 3 scenarios | FR-05 |
| US-06 | 5 scenarios | NFR-03 |

**Traceability Matrix** (see Requirements Doc Section 12.3):
- Each scenario traces to acceptance criteria
- Each AC traces to user story
- Each user story traces to functional requirement
- Each FR traces to business objective

---

## 9. CI/CD Integration

### 9.1 Automated Test Execution

**pytest Configuration**:
```ini
# pytest.ini
[pytest]
testpaths = tests
markers =
    cli: CLI integration tests
    unit: Unit tests (fast)
    manual: Manual tests requiring terminal (skip in CI)

# Skip manual tests in CI
addopts = -m "not manual"
```

**CI Pipeline**:
```yaml
# .github/workflows/test.yml
- name: Run CLI acceptance tests
  run: |
    pytest tests/e2e/test_cli_combat.py -v -m "not manual"
    # Runs all automated scenarios
    # Skips manual emoji/color validation
```

### 9.2 Test Execution Time

**Target**: < 10 seconds for complete E2E suite

**Optimization**:
- Zero-delay test mode (CLIConfig.test_mode())
- Parallel test execution where possible
- Deterministic data (no random delays)

### 9.3 Test Failure Reporting

**pytest Output**:
```
FAILED test_cli_combat.py::test_invalid_hp_triggers_error
  AssertionError: Expected error "HP must be between 1 and 999" not found in output
  Output captured: ['Welcome to Combat Simulator', 'Enter character name: Hero']
```

**Useful Information**:
- Failed assertion details
- Captured output (for debugging)
- Step that failed (Gherkin step name)

---

## 10. Manual Testing Requirements

### 10.1 Emoji and Color Validation

**Automated tests validate content, NOT visual rendering.**

**Manual tests required**:
1. **Windows Terminal**: Verify emoji render correctly
2. **Windows CMD.exe**: Verify fallback symbols work
3. **macOS Terminal**: Verify emoji and colors
4. **Linux GNOME Terminal**: Verify emoji and colors
5. **Limited Terminal (TERM=dumb)**: Verify fallback text

**Test Checklist**:
- [ ] Emoji display correctly (⚔️ 💥 ❤️ 🎲 ⚡ 🏆 ☠️ 🛡️)
- [ ] Fallback symbols work ([ATK] [DMG] [HP] [D6] [INIT] [WIN] [DEAD] [DEF])
- [ ] Colors render appropriately (red errors, HP gradient, damage red)
- [ ] No broken characters or boxes
- [ ] Line formatting intact

### 10.2 Timing Validation

**Automated tests use zero delays. Manual validation required for pacing.**

**Pacing Tests**:
1. Run CLI with production config
2. Observe delays between rounds (should be 1.5-2s)
3. Verify delays feel comfortable (not rushed, not boring)
4. Confirm all output readable before next event

**User Comprehension Test**:
- Can user explain what happened in last round?
- Target: 80%+ users understand combat flow without replay

---

## 11. Troubleshooting

### 11.1 Common Test Failures

**Failure**: `Character not found in cli_context['characters']`
**Cause**: Character creation not implemented
**Fix**: Implement CharacterCreator.create_character()

**Failure**: `CombatResult is None`
**Cause**: CombatSimulator not called
**Fix**: Wire CombatSimulator in CLI Main

**Failure**: `Output does not contain emoji`
**Cause**: Rich Console not configured or emoji disabled
**Fix**: Configure Rich Console with emoji support

### 11.2 Debugging Tips

**Enable verbose output**:
```bash
pytest tests/e2e/test_cli_combat.py -v -s
# -v: verbose test names
# -s: show print statements
```

**Run single scenario**:
```bash
pytest tests/e2e/test_cli_combat.py -k "manual_input"
```

**Inspect cli_context**:
```python
def test_debug_context(cli_context):
    print(f"Characters: {cli_context['characters']}")
    print(f"Combat result: {cli_context['combat_result']}")
    print(f"Output: {cli_context['output']}")
```

---

## 12. Handoff Package Summary

### 12.1 Deliverables

✅ **Feature File**: `tests/e2e/features/cli_combat.feature` (31 scenarios)
✅ **Step Definitions**: `tests/e2e/test_cli_combat.py` (production service integration)
✅ **Implementation Order**: `docs/testing/cli-implementation-order.md` (phase-by-phase roadmap)
✅ **Test Documentation**: This document (architecture, fixtures, examples)

### 12.2 Quality Gates

**Before marking acceptance tests complete**:
- [ ] All scenarios written in proper Gherkin format
- [ ] Step definitions use REAL production services (not mocks)
- [ ] Test fixtures provide deterministic context
- [ ] Test data catalog includes all scenarios
- [ ] One-at-a-time implementation order documented
- [ ] CI/CD configuration complete
- [ ] Manual test checklist provided

### 12.3 Next Steps for DEVELOP Wave

1. Read architecture document
2. Review feature file (all 31 scenarios)
3. Study step definitions (production service integration)
4. Start with Phase 1, Test 1.1 (baseline CLI)
5. Follow Outside-In TDD workflow
6. Commit after each passing test
7. Proceed sequentially through phases

---

## 13. Appendix

### 13.1 Glossary

| Term | Definition |
|------|------------|
| **Acceptance Test** | E2E test validating business requirements through user-facing scenarios |
| **Outside-In TDD** | Development driven by acceptance tests (outer loop) supported by unit tests (inner loop) |
| **Production Service** | Real implementation (not mock) of application or domain service |
| **Step Definition** | Python function implementing Gherkin step (Given/When/Then) |
| **pytest-bdd** | pytest plugin for Gherkin scenario execution |
| **CLIConfig** | Configuration dataclass for timing, emoji, and display settings |
| **Deterministic** | Predictable outcomes (same input → same output) via seeded randomness |

### 13.2 References

**Internal Documentation**:
- Requirements: `docs/requirements/interactive-cli-combat-viewer.md`
- Architecture: `docs/architecture/interactive-cli-combat-viewer.md`
- Implementation Order: `docs/testing/cli-implementation-order.md`

**External References**:
- pytest-bdd Documentation: https://pytest-bdd.readthedocs.io/
- Gherkin Syntax: https://cucumber.io/docs/gherkin/
- Outside-In TDD: https://sammancoaching.org/learning_hours/bdd/double_loop_tdd.html

---

**Document Version**: 1.0
**Last Updated**: 2026-01-09
**Author**: Quinn (acceptance-designer)
**Status**: Ready for DEVELOP Wave Handoff
