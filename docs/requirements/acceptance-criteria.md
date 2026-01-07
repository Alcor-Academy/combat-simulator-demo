# Combat Simulator - Acceptance Criteria Catalog

**Project**: Combat Simulator CLI Demo
**Purpose**: Quick reference for all testable acceptance criteria
**Format**: Given-When-Then (Gherkin-compatible)
**Audience**: Developers (human + Claude Code), Testers, Acceptance Designers
**Date**: 2026-01-07

---

## How to Use This Document

This catalog provides **testable acceptance criteria** for all features. Each criterion:
- Is executable (can be automated as a test)
- Is unambiguous (single interpretation)
- Defines observable behavior (not implementation)
- Follows Given-When-Then format

**For DISTILL Wave**: Convert these criteria into executable acceptance tests.
**For DEVELOP Wave**: Implement code to make these criteria pass.

---

## Combat Rules Reference

Before reviewing acceptance criteria, understand these combat rules:

### Death Rule: Attacker Advantage
- First attacker resolves their attack fully
- Defender counter-attacks **only if they survive** (HP > 0)
- If attacker kills defender, round ends immediately - no counter-attack

### Attack Order: Initiative Roll
- Initiative rolled **once at fight start** (not every round)
- Each character rolls D6 + Agility (Attack Power + HP)
- Higher total wins initiative, attacks first every round

### Derived Stat: Agility
- **Agility = Attack Power + Current HP**
- Derived (computed property), not stored

### Dice Boundaries
- All dice return values in **[1, 6] inclusive**
- Never 0, never 7

---

## Feature 1: Character Creation

### AC-1.1: Character Creation with Random Stats
```gherkin
Scenario: Create character with random stats
  Given a DiceRoller that returns [4, 3] for HP rolls and [2] for Attack roll
  When I create a character named "Thorin"
  Then the character has name "Thorin"
  And the character has HP calculated from dice rolls
  And the character has Attack Power from dice roll
  And the character has Agility = Attack Power + HP (derived, not stored)
```

**Test Type**: Unit
**Priority**: Critical
**Estimated Assertions**: 4

---

### AC-1.2: Character Creation with Fixed Stats (Testing)
```gherkin
Scenario: Create character with fixed stats for testing
  Given a FixedDiceRoller configured for predictable values
  When I create a character "Thorin" resulting in 20 HP and 5 Attack
  Then the character has name "Thorin"
  And the character has 20 HP
  And the character has 5 Attack Power
  And the character has Agility of 25 (20 + 5)
```

**Test Type**: Unit
**Priority**: Critical
**Estimated Assertions**: 4

---

### AC-1.3: Character Liveness - Alive
```gherkin
Scenario: Character with positive HP is alive
  Given a character with HP > 0
  When I check if the character is alive
  Then the result is true
```

**Test Type**: Unit
**Priority**: Critical
**Estimated Assertions**: 1

---

### AC-1.4: Character Liveness - Dead (Zero HP)
```gherkin
Scenario: Character with zero HP is dead
  Given a character with 0 HP
  When I check if the character is alive
  Then the result is false
```

**Test Type**: Unit
**Priority**: Critical
**Estimated Assertions**: 1

---

### AC-1.5: Character Name Validation
```gherkin
Scenario: Character name cannot be empty
  Given I attempt to create a character with name ""
  Then creation fails with ValidationError "Name cannot be empty"
```

**Test Type**: Unit
**Priority**: High
**Estimated Assertions**: 1

---

### AC-1.6: Immutability on Damage
```gherkin
Scenario: Receiving damage returns new instance
  Given a character "Legolas" with 18 HP
  When the character receives 5 damage
  Then a new character instance is returned
  And the new character has 13 HP
  And the original character instance remains unchanged with 18 HP
```

**Test Type**: Unit
**Priority**: Critical (demonstrates immutability)
**Estimated Assertions**: 3

---

## Feature 2: Dice Rolling System

### AC-2.1: Random Dice Roll Range
```gherkin
Scenario: Roll d6 dice with random outcome
  Given a 6-sided dice roller (D6)
  When the dice is rolled
  Then the result is between 1 and 6 inclusive
  And it never returns 0
  And it never returns 7
```

**Test Type**: Unit
**Priority**: Critical
**Implementation Note**: Test RandomDiceRoller by rolling 100 times, asserting all results in [1,6]

---

### AC-2.2: Deterministic Test Double - Fixed Value
```gherkin
Scenario: Test double returns fixed value
  Given a fixed dice roller configured to return 4
  When the dice is rolled
  Then the result is 4

  When the dice is rolled again
  Then the result is still 4
```

**Test Type**: Unit
**Priority**: Critical (test infrastructure)
**Estimated Assertions**: 2

---

### AC-2.3: Deterministic Test Double - Sequence
```gherkin
Scenario: Test double returns sequence of values
  Given a fixed dice roller configured to return [3, 5, 2]
  When the dice is rolled 3 times
  Then the first result is 3
  And the second result is 5
  And the third result is 2
```

**Test Type**: Unit
**Priority**: Critical (test infrastructure)
**Estimated Assertions**: 3

---

### AC-2.4: Port/Adapter Interchangeability
```gherkin
Scenario: Adapters are interchangeable via dependency injection
  Given a DiceRoller port interface
  And a RandomDiceRoller adapter (production)
  And a FixedDiceRoller adapter (testing)
  When either adapter is injected into a combat service
  Then the combat service operates correctly with either implementation
  And no code changes are required to switch adapters
```

**Test Type**: Integration (but can be demonstrated via unit tests)
**Priority**: Critical (architectural validation)
**Implementation Note**: Show dependency injection in action

---

## Feature 3: Initiative Roll

### AC-3.1: Initiative Calculation
```gherkin
Scenario: Determine initiative at combat start
  Given "Thorin" with Agility 25 (HP 20 + Attack 5)
  And "Goblin" with Agility 13 (HP 10 + Attack 3)
  And dice configured for [3, 5] (Thorin rolls 3, Goblin rolls 5)
  When initiative is rolled
  Then Thorin's initiative = 25 + 3 = 28
  And Goblin's initiative = 13 + 5 = 18
  And Thorin wins initiative (28 > 18)
  And Thorin is designated as "attacker" for all rounds
```

**Test Type**: Unit
**Priority**: Critical
**Estimated Assertions**: 4

---

### AC-3.2: Initiative Tie-Breaker
```gherkin
Scenario: Initiative tie resolved deterministically
  Given two characters with equal initiative totals
  When initiative is rolled
  Then the character with higher base Agility wins
  Or if still tied, first character in order wins (deterministic)
```

**Test Type**: Unit
**Priority**: High
**Estimated Assertions**: 2

---

## Feature 4: Attack Resolution

### AC-4.1: Damage Calculation Formula
```gherkin
Scenario: Calculate total damage
  Given an attacker with 5 Attack Power
  And a dice roll of 3
  When the attack is resolved
  Then the total damage is 8 (5 + 3)
```

**Test Type**: Unit
**Priority**: Critical
**Estimated Assertions**: 1

---

### AC-4.2: Damage Application - Normal Case
```gherkin
Scenario: Apply damage to healthy defender
  Given a defender with 20 HP
  And an incoming attack dealing 8 damage
  When the damage is applied
  Then the defender's new HP is 12
  And a new defender instance is returned (immutability)
```

**Test Type**: Unit
**Priority**: Critical
**Estimated Assertions**: 2

---

### AC-4.3: Damage Application - Overkill (HP Floor at 0)
```gherkin
Scenario: Damage exceeds remaining HP
  Given a defender with 5 HP
  And an incoming attack dealing 8 damage
  When the damage is applied
  Then the defender's new HP is 0 (not -3)
```

**Test Type**: Unit
**Priority**: High (edge case)
**Estimated Assertions**: 1

---

### AC-4.4: Attack Result Structure
```gherkin
Scenario: Attack result contains all relevant data
  Given an attack from "Thorin" to "Goblin"
  And Thorin has 5 Attack Power
  And the dice roll is 4
  And Goblin has 15 HP
  When the attack is resolved
  Then the attack result contains:
    | Field          | Value    |
    | attacker       | "Thorin" |
    | defender       | "Goblin" |
    | diceRoll       | 4        |
    | attackPower    | 5        |
    | totalDamage    | 9        |
    | defenderOldHP  | 15       |
    | defenderNewHP  | 6        |
```

**Test Type**: Unit
**Priority**: High (data structure validation)
**Estimated Assertions**: 7

---

### AC-4.5: Dead Character Cannot Attack
```gherkin
Scenario: Dead character attempts attack
  Given a character "Ghost" with 0 HP
  When the character attempts to attack
  Then the attack is rejected
  And an error or null result is returned
  And the defender is not harmed
```

**Test Type**: Unit
**Priority**: Critical
**Estimated Assertions**: 2-3

---

## Feature 5: Combat Round

### AC-5.1: Full Combat Round - Both Survive (Attacker Advantage)
```gherkin
Scenario: Both characters attack in one round (defender survives)
  Given "Thorin" (attacker) with 20 HP and 5 Attack Power
  And "Goblin" (defender) with 10 HP and 3 Attack Power
  And dice configured for [4, 2] (Thorin's attack roll, Goblin's counter-attack roll)
  When I execute a combat round
  Then Thorin's attack resolves FIRST: deals 9 damage (5+4) to Goblin
  And Goblin survives with 1 HP (10-9)
  And Goblin's counter-attack resolves SECOND: deals 5 damage (3+2) to Thorin
  And Thorin has 15 HP remaining
  And round result shows both attacks in sequence
```

**Test Type**: Unit (with FixedDiceRoller)
**Priority**: Critical
**Estimated Assertions**: 4-5

---

### AC-5.2: Attacker Kills Defender - No Counter-Attack
```gherkin
Scenario: Attacker advantage - no counter-attack when defender dies
  Given "Thorin" (attacker) with 20 HP and 5 Attack Power
  And "Goblin" (defender) with 5 HP and 3 Attack Power
  And dice configured for [6] (only one roll needed - Goblin dies)
  When I execute a combat round
  Then Thorin's attack resolves: deals 11 damage (5+6) to Goblin
  And Goblin reaches 0 HP and is dead
  And Goblin does NOT get to counter-attack
  And round ends immediately
  And victory condition is met
```

**Test Type**: Unit
**Priority**: Critical (core mechanic)
**Estimated Assertions**: 4

---

### AC-5.3: Round Result Data Structure
```gherkin
Scenario: Round result contains complete data
  Given a completed combat round
  When RoundResult is created
  Then it contains:
    | Field          | Description                          |
    | attacker       | Character who attacked first         |
    | defender       | Character who defended               |
    | attackerRoll   | Die roll for attacker                |
    | defenderRoll   | Die roll for defender (0 if dead)    |
    | attackerDamage | Damage dealt by attacker             |
    | defenderDamage | Damage dealt by defender (0 if dead) |
    | attackerHPAfter| Attacker HP after round              |
    | defenderHPAfter| Defender HP after round              |
    | combatEnded    | Boolean - true if someone died       |
    | winner         | Character or null                    |
```

**Test Type**: Unit
**Priority**: High (data structure validation)
**Estimated Assertions**: 10

---

### AC-5.4: No Console Prints in Domain Logic
```gherkin
Scenario: Domain logic returns data, does not print
  Given a combat round is executed
  Then no console output is produced by domain logic
  And all combat events are returned as structured data
  And the CLI layer is responsible for formatting output
```

**Test Type**: Unit (architectural constraint)
**Priority**: Medium (design principle validation)
**Implementation Note**: Can be validated via code review or spy on console.log

---

## Feature 6: Game Loop

### AC-6.1: Fully Automated Combat to Victory
```gherkin
Scenario: Combat runs automatically until one character dies
  Given "Thorin" with 20 HP, 5 Attack
  And "Goblin" with 10 HP, 3 Attack
  And Thorin wins initiative
  When I execute "fight"
  Then combat runs automatically round by round
  And each round displays attacker action and defender reaction
  And combat continues until one character has 0 HP
  And winner is declared with victory message
```

**Test Type**: Unit/E2E
**Priority**: Critical
**Estimated Assertions**: 3-4

---

### AC-6.2: Combat Output Shows Progression
```gherkin
Scenario: Combat output shows round-by-round progression
  Given combat between Thorin and Goblin
  When combat executes
  Then output shows:
    | Round 1: Thorin attacks... Goblin counter-attacks... |
    | Round 2: Thorin attacks... Goblin counter-attacks... |
    | ... |
    | VICTORY: Thorin wins! Goblin has been defeated. |
```

**Test Type**: Unit/E2E
**Priority**: High
**Estimated Assertions**: 2-3

---

### AC-6.3: Combat Ends Immediately on Death
```gherkin
Scenario: Combat ends mid-round when character dies
  Given combat in progress
  When a character reaches 0 HP mid-round
  Then combat ends immediately (attacker advantage)
  And no further rounds execute
  And survivor is declared winner
```

**Test Type**: Unit
**Priority**: Critical
**Estimated Assertions**: 3

---

## Feature 7: Victory Condition (REQUIRED)

### AC-7.1: Victory Detection
```gherkin
Scenario: Combat ends when one character dies
  Given combat in progress
  When a character reaches 0 HP
  Then combat ends immediately
  And the surviving character is declared winner
  And victory message displays: "[Winner] wins! [Loser] has been defeated."
```

**Test Type**: Unit or E2E
**Priority**: Critical
**Estimated Assertions**: 3

---

### AC-7.2: Victory Message Format
```gherkin
Scenario: Victory message is clearly formatted
  Given Thorin defeats Goblin
  When victory is declared
  Then output shows:
    | ================================== |
    | VICTORY! Thorin wins!              |
    | Goblin has been defeated.          |
    | Final HP: Thorin 15 | Goblin 0     |
    | ================================== |
```

**Test Type**: Unit
**Priority**: High
**Estimated Assertions**: 4

---

## End-to-End Acceptance Criteria

### E2E-1: Complete Combat Simulation (Walking Skeleton)
```gherkin
Scenario: Full combat from start to victory
  Given I have created two characters:
    | Name   | HP | Attack Power |
    | Thorin | 20 | 5            |
    | Goblin | 10 | 3            |
  And initiative determines attack order
  And I have started a combat simulation
  When the combat runs until completion
  Then one character reaches 0 HP
  And the other character is declared the winner
  And I can see a log of all combat rounds
  And the log includes all attacks and damage dealt
  And the log shows attacker advantage (no counter-attack on death)
```

**Test Type**: E2E
**Priority**: Critical (validates entire system)
**Implementation**: This is the first test written (TDD Outside-In)
**Expected**: Fails initially, passes after Feature 6+7 completes

---

## Acceptance Criteria Summary

### By Feature
| Feature | Critical ACs | High ACs | Medium ACs | Low ACs | Total |
|---------|--------------|----------|------------|---------|-------|
| Feature 1: Character | 5 | 1 | 0 | 0 | 6 |
| Feature 2: Dice | 3 | 1 | 0 | 0 | 4 |
| Feature 3: Initiative | 1 | 1 | 0 | 0 | 2 |
| Feature 4: Attack | 3 | 2 | 0 | 0 | 5 |
| Feature 5: Combat Round | 2 | 1 | 1 | 0 | 4 |
| Feature 6: Game Loop | 2 | 1 | 0 | 0 | 3 |
| Feature 7: Victory | 1 | 1 | 0 | 0 | 2 |
| E2E | 1 | 0 | 0 | 0 | 1 |
| **Total** | **18** | **8** | **1** | **0** | **27** |

### By Priority
- **Critical**: 18 ACs (must pass for demo success)
- **High**: 8 ACs (should pass for quality)
- **Medium**: 1 AC (nice to have)
- **Low**: 0 ACs

### By Test Type
- **Unit Tests**: 25 ACs
- **Integration Tests**: 1 AC (Port/Adapter, can be shown via units)
- **E2E Tests**: 1 AC (Walking Skeleton)

---

## Test Implementation Guide

### Test Structure Template

```typescript
// Example: AC-1.2 - Character Creation with Fixed Stats
describe('Character Creation', () => {
  it('should create character with valid attributes and derived agility', () => {
    // Given: FixedDiceRoller configured for predictable values
    const diceRoller = new FixedDiceRoller([/* values for 20 HP, 5 Attack */]);

    // When: I create a character
    const character = Character.create('Thorin', diceRoller);

    // Then: verify attributes including derived agility
    expect(character.name).toBe('Thorin');
    expect(character.hp).toBe(20);
    expect(character.attackPower).toBe(5);
    expect(character.agility).toBe(25); // Derived: 20 + 5
  });
});
```

### Test Naming Convention

**Format**: `should [expected behavior] when [condition]`

**Examples**:
- `should return true when character has positive HP`
- `should return new instance when receiving damage`
- `should calculate damage as attack power plus dice roll`
- `should designate higher initiative as attacker`
- `should not allow counter-attack when defender dies`
- `should end combat immediately when character reaches 0 HP`

### Arrange-Act-Assert Pattern

All tests should follow AAA:

1. **Arrange**: Set up test data (Given)
2. **Act**: Execute the behavior (When)
3. **Assert**: Verify the outcome (Then)

---

## Testability Requirements

### All Acceptance Criteria Must Be:

- **Observable**: Can verify outcome through public API
- **Repeatable**: Same inputs always produce same outputs
- **Isolated**: No dependencies on external state (except injected dependencies)
- **Fast**: Each test completes in milliseconds
- **Deterministic**: Uses FixedDiceRoller, not RandomDiceRoller

### Red Flags (Anti-Patterns):

- **Time-dependent tests**: Relying on `Date.now()` or timers
- **Network calls**: Hitting real APIs or databases
- **File I/O**: Reading/writing files during tests
- **Mocking implementation details**: Only mock ports (interfaces), not concrete classes
- **Console assertions**: Testing `console.log` output (separate concern)

---

## Coverage Targets

**Target**: 100% line and branch coverage for domain logic

**Acceptable Exceptions**:
- CLI presentation layer (main.ts) - can be excluded from coverage
- Error handling for impossible states (type system prevents them)

**Coverage Report Location**: `coverage/lcov-report/index.html` (or framework equivalent)

---

## Acceptance Criteria Traceability Matrix

| AC ID | Story | Feature | Test File (Future) | Status |
|-------|-------|---------|-------------------|--------|
| AC-1.1 | US-01 | Character Creation | Character.test.ts | Pending |
| AC-1.2 | US-01 | Character Creation | Character.test.ts | Pending |
| AC-1.3 | US-01 | Character Creation | Character.test.ts | Pending |
| AC-1.4 | US-01 | Character Creation | Character.test.ts | Pending |
| AC-1.5 | US-01 | Character Creation | Character.test.ts | Pending |
| AC-1.6 | US-01 | Character Creation | Character.test.ts | Pending |
| AC-2.1 | US-02 | Dice Rolling | RandomDiceRoller.test.ts | Pending |
| AC-2.2 | US-02 | Dice Rolling | FixedDiceRoller.test.ts | Pending |
| AC-2.3 | US-02 | Dice Rolling | FixedDiceRoller.test.ts | Pending |
| AC-2.4 | US-02 | Dice Rolling | CombatService.test.ts | Pending |
| AC-3.1 | US-03 | Initiative Roll | InitiativeResult.test.ts | Pending |
| AC-3.2 | US-03 | Initiative Roll | InitiativeResult.test.ts | Pending |
| AC-4.1 | US-04 | Attack Resolution | AttackResolver.test.ts | Pending |
| AC-4.2 | US-04 | Attack Resolution | Character.test.ts | Pending |
| AC-4.3 | US-04 | Attack Resolution | Character.test.ts | Pending |
| AC-4.4 | US-04 | Attack Resolution | AttackResult.test.ts | Pending |
| AC-4.5 | US-04 | Attack Resolution | AttackResolver.test.ts | Pending |
| AC-5.1 | US-05 | Combat Round | CombatRound.test.ts | Pending |
| AC-5.2 | US-05 | Combat Round | CombatRound.test.ts | Pending |
| AC-5.3 | US-05 | Combat Round | RoundResult.test.ts | Pending |
| AC-5.4 | US-05 | Combat Round | Code Review | Pending |
| AC-6.1 | US-06 | Game Loop | CombatSimulator.test.ts | Pending |
| AC-6.2 | US-06 | Game Loop | CombatSimulator.test.ts | Pending |
| AC-6.3 | US-06 | Game Loop | CombatSimulator.test.ts | Pending |
| AC-7.1 | US-07 | Victory Condition | CombatResult.test.ts | Pending |
| AC-7.2 | US-07 | Victory Condition | CombatResult.test.ts | Pending |
| E2E-1 | Epic | Full System | CombatSimulator.e2e.test.ts | Pending |

**Status Legend**:
- **Pending**: Awaiting implementation
- **In Progress**: Test written, failing (red phase)
- **Passing**: Test green
- **Refactored**: Test passing after refactoring

---

## Demo Execution Notes

### Critical Path Acceptance Criteria (Must Pass for Demo Success)

1. **AC-1.2** (Character creation with Agility) - Foundation
2. **AC-1.6** (Immutability) - Key wow moment
3. **AC-2.2** (Test double) - Enables testability
4. **AC-2.4** (Port/Adapter) - Architecture wow moment
5. **AC-3.1** (Initiative roll) - Combat order determination
6. **AC-4.1** (Damage calculation) - Core mechanic
7. **AC-4.2** (Damage application) - Immutability again
8. **AC-5.1** (Combat round - both survive) - Integration
9. **AC-5.2** (Attacker advantage) - Core mechanic wow moment
10. **AC-6.1** (Game loop) - Full automation
11. **AC-7.1** (Victory condition) - Game completion
12. **E2E-1** (Walking skeleton) - Final validation

**If these 12 ACs pass, the demo is a success.** All others are polish or edge cases.

---

**Document Status**: Ready for Test Implementation
**Next Phase**: DISTILL (Convert ACs to executable tests)
**Estimated Test Writing Time**: 20-25 minutes (if automated via tooling)
