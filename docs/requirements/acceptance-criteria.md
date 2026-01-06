# Combat Simulator - Acceptance Criteria Catalog

**Project**: Combat Simulator CLI Demo
**Purpose**: Quick reference for all testable acceptance criteria
**Format**: Given-When-Then (Gherkin-compatible)
**Audience**: Developers (human + Claude Code), Testers, Acceptance Designers

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

## Feature 1: Character Creation

### AC-1.1: Valid Character Creation
```gherkin
Given no character exists
When I create a character named "Thorin" with 20 HP and 5 Attack Power
Then the character's name is "Thorin"
And the character's HP is 20
And the character's Attack Power is 5
```

**Test Type**: Unit
**Priority**: Critical
**Estimated Assertions**: 3

---

### AC-1.2: Character Liveness - Alive
```gherkin
Given a character with 15 HP
When I check if the character is alive
Then the result is true
```

**Test Type**: Unit
**Priority**: Critical
**Estimated Assertions**: 1

---

### AC-1.3: Character Liveness - Dead (Zero HP)
```gherkin
Given a character with 0 HP
When I check if the character is alive
Then the result is false
```

**Test Type**: Unit
**Priority**: Critical
**Estimated Assertions**: 1

---

### AC-1.4: Character Liveness - Dead (Negative HP)
```gherkin
Given a character with -5 HP
When I check if the character is alive
Then the result is false
```

**Test Type**: Unit
**Priority**: High
**Estimated Assertions**: 1

---

### AC-1.5: Immutability on Damage
```gherkin
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
Given a 6-sided dice roller
When the dice is rolled
Then the result is between 1 and 6 inclusive
```

**Test Type**: Unit
**Priority**: High
**Implementation Note**: Test RandomDiceRoller by rolling 100 times, asserting all results in [1,6]

---

### AC-2.2: Deterministic Test Double - Fixed Value
```gherkin
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

## Feature 3: Attack Resolution

### AC-3.1: Damage Calculation Formula
```gherkin
Given an attacker with 5 Attack Power
And a dice roll of 3
When the attack is resolved
Then the total damage is 8 (5 + 3)
```

**Test Type**: Unit
**Priority**: Critical
**Estimated Assertions**: 1

---

### AC-3.2: Damage Application - Normal Case
```gherkin
Given a defender with 20 HP
And an incoming attack dealing 8 damage
When the damage is applied
Then the defender's new HP is 12
And a new defender instance is returned
```

**Test Type**: Unit
**Priority**: Critical
**Estimated Assertions**: 2

---

### AC-3.3: Damage Application - Overkill (HP Floor)
```gherkin
Given a defender with 5 HP
And an incoming attack dealing 8 damage
When the damage is applied
Then the defender's new HP is 0 (not -3)
```

**Test Type**: Unit
**Priority**: High (edge case)
**Estimated Assertions**: 1

---

### AC-3.4: Attack Result Structure
```gherkin
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

### AC-3.5: Dead Character Cannot Attack
```gherkin
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

## Feature 4: Combat Round Orchestration

### AC-4.1: Full Combat Round - Both Alive
```gherkin
Given "Thorin" with 20 HP and 5 Attack Power
And "Goblin" with 10 HP and 3 Attack Power
And dice rolls are [4, 2] (Thorin's roll, then Goblin's roll)
When a combat round is executed
Then Thorin deals 9 damage (5 + 4) to Goblin
And Goblin deals 5 damage (3 + 2) to Thorin
And Goblin's new HP is 1 (10 - 9)
And Thorin's new HP is 15 (20 - 5)
And both characters' updated states are returned
```

**Test Type**: Unit (with FixedDiceRoller)
**Priority**: Critical
**Estimated Assertions**: 4-5

---

### AC-4.2: Combat Round - One Character Dead
```gherkin
Given "Thorin" with 10 HP and 5 Attack Power
And "Goblin" with 0 HP and 3 Attack Power (already dead)
And dice roll is 4
When a combat round is executed
Then only Thorin attacks
And Goblin does not attack
And the round result indicates "Goblin could not attack (dead)"
```

**Test Type**: Unit
**Priority**: High
**Estimated Assertions**: 3

---

### AC-4.3: Round Result Data Structure
```gherkin
Given a combat round is executed
Then the round result contains:
  - Round number
  - Attacker 1 action details (attack result or skip reason)
  - Attacker 2 action details (attack result or skip reason)
  - Character 1 updated state
  - Character 2 updated state
  - Combat status (ongoing or finished)
```

**Test Type**: Unit
**Priority**: High (data structure validation)
**Estimated Assertions**: 6

---

### AC-4.4: No Console Prints in Domain Logic
```gherkin
Given a combat round is executed
Then no console output is produced by domain logic
And all combat events are returned as structured data
And the CLI layer is responsible for formatting output
```

**Test Type**: Unit (architectural constraint)
**Priority**: Medium (design principle validation)
**Implementation Note**: Can be validated via code review or spy on console.log

---

## Feature 5: Victory Condition (Optional)

### AC-5.1: Victory Detection
```gherkin
Given a combat in progress
And Character A has 2 HP
And Character B has 5 HP
When Character A receives fatal damage
Then the combat ends immediately
And Character B is declared the winner
```

**Test Type**: Unit or E2E
**Priority**: Low (buffer feature)
**Estimated Assertions**: 2

---

### AC-5.2: Combat Result Structure
```gherkin
Given combat has ended with a winner
Then the combat result contains:
  - Winner name
  - Winner's remaining HP
  - Loser name
  - Total rounds fought
  - Victory message
```

**Test Type**: Unit
**Priority**: Low (buffer feature)
**Estimated Assertions**: 5

---

## End-to-End Acceptance Criteria

### E2E-1: Complete Combat Simulation (Walking Skeleton)
```gherkin
Given I have created two characters:
  | Name   | HP | Attack Power |
  | Thorin | 20 | 5            |
  | Goblin | 10 | 3            |
And I have started a combat simulation
When the combat runs until completion
Then one character reaches 0 HP
And the other character is declared the winner
And I can see a log of all combat rounds
And the log includes all attacks and damage dealt
```

**Test Type**: E2E
**Priority**: Critical (validates entire system)
**Implementation**: This is the first test written (TDD Outside-In)
**Expected**: Fails initially, passes after Feature 4 completes

---

## Acceptance Criteria Summary

### By Feature
| Feature | Critical ACs | High ACs | Medium ACs | Low ACs | Total |
|---------|--------------|----------|------------|---------|-------|
| Feature 1 | 4 | 1 | 0 | 0 | 5 |
| Feature 2 | 3 | 1 | 0 | 0 | 4 |
| Feature 3 | 3 | 2 | 0 | 0 | 5 |
| Feature 4 | 2 | 2 | 1 | 0 | 5 |
| Feature 5 | 0 | 0 | 0 | 2 | 2 |
| E2E | 1 | 0 | 0 | 0 | 1 |
| **Total** | **13** | **6** | **1** | **2** | **22** |

### By Priority
- **Critical**: 13 ACs (must pass for demo success)
- **High**: 6 ACs (should pass for quality)
- **Medium**: 1 AC (nice to have)
- **Low**: 2 ACs (optional buffer feature)

### By Test Type
- **Unit Tests**: 20 ACs
- **Integration Tests**: 1 AC (Port/Adapter, can be shown via units)
- **E2E Tests**: 1 AC (Walking Skeleton)

---

## Test Implementation Guide

### Test Structure Template

```typescript
// Example: AC-1.1 - Valid Character Creation
describe('Character Creation', () => {
  it('should create character with valid attributes', () => {
    // Given: no character exists (implicit)

    // When: I create a character
    const character = new Character('Thorin', 20, 5);

    // Then: verify attributes
    expect(character.name).toBe('Thorin');
    expect(character.hp).toBe(20);
    expect(character.attackPower).toBe(5);
  });
});
```

### Test Naming Convention

**Format**: `should [expected behavior] when [condition]`

**Examples**:
- `should return true when character has positive HP`
- `should return new instance when receiving damage`
- `should calculate damage as attack power plus dice roll`
- `should prevent dead character from attacking`

### Arrange-Act-Assert Pattern

All tests should follow AAA:

1. **Arrange**: Set up test data (Given)
2. **Act**: Execute the behavior (When)
3. **Assert**: Verify the outcome (Then)

---

## Testability Requirements

### All Acceptance Criteria Must Be:

✅ **Observable**: Can verify outcome through public API
✅ **Repeatable**: Same inputs always produce same outputs
✅ **Isolated**: No dependencies on external state (except injected dependencies)
✅ **Fast**: Each test completes in milliseconds
✅ **Deterministic**: Uses FixedDiceRoller, not RandomDiceRoller

### Red Flags (Anti-Patterns):

❌ **Time-dependent tests**: Relying on `Date.now()` or timers
❌ **Network calls**: Hitting real APIs or databases
❌ **File I/O**: Reading/writing files during tests
❌ **Mocking implementation details**: Only mock ports (interfaces), not concrete classes
❌ **Console assertions**: Testing `console.log` output (separate concern)

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
| AC-2.1 | US-02 | Dice Rolling | RandomDiceRoller.test.ts | Pending |
| AC-2.2 | US-02 | Dice Rolling | FixedDiceRoller.test.ts | Pending |
| AC-2.3 | US-02 | Dice Rolling | FixedDiceRoller.test.ts | Pending |
| AC-2.4 | US-02 | Dice Rolling | CombatService.test.ts | Pending |
| AC-3.1 | US-03 | Attack Resolution | AttackResolver.test.ts | Pending |
| AC-3.2 | US-03 | Attack Resolution | Character.test.ts | Pending |
| AC-3.3 | US-03 | Attack Resolution | Character.test.ts | Pending |
| AC-3.4 | US-03 | Attack Resolution | AttackResult.test.ts | Pending |
| AC-3.5 | US-03 | Attack Resolution | AttackResolver.test.ts | Pending |
| AC-4.1 | US-04 | Combat Round | CombatRound.test.ts | Pending |
| AC-4.2 | US-04 | Combat Round | CombatRound.test.ts | Pending |
| AC-4.3 | US-04 | Combat Round | RoundResult.test.ts | Pending |
| AC-4.4 | US-04 | Combat Round | Code Review | Pending |
| AC-5.1 | US-05 | Victory Condition | CombatSimulator.test.ts | Pending |
| AC-5.2 | US-05 | Victory Condition | CombatResult.test.ts | Pending |
| E2E-1 | Epic | Full System | CombatSimulator.e2e.test.ts | Pending |

**Status Legend**:
- **Pending**: Awaiting implementation
- **In Progress**: Test written, failing (red phase)
- **Passing**: Test green
- **Refactored**: Test passing after refactoring

---

## Demo Execution Notes

### Critical Path Acceptance Criteria (Must Pass for Demo Success)

1. **AC-1.1** (Character creation) - Foundation
2. **AC-1.5** (Immutability) - Key wow moment
3. **AC-2.2** (Test double) - Enables testability
4. **AC-2.4** (Port/Adapter) - Architecture wow moment
5. **AC-3.1** (Damage calculation) - Core mechanic
6. **AC-3.2** (Damage application) - Immutability again
7. **AC-4.1** (Full combat round) - Integration
8. **E2E-1** (Walking skeleton) - Final validation

**If these 8 ACs pass, the demo is a success.** All others are polish or edge cases.

---

**Document Status**: Ready for Test Implementation
**Next Phase**: DISTILL (Convert ACs to executable tests)
**Estimated Test Writing Time**: 15-20 minutes (if automated via tooling)
