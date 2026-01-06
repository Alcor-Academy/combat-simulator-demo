# Combat Simulator - User Stories

**Project**: Combat Simulator CLI Demo
**Document Type**: User Story Catalog
**Date**: 2026-01-06
**Format**: ATDD-compliant (Given-When-Then acceptance criteria)

---

## Epic: Combat Simulator CLI

**Epic Statement**:
```
As a Software Crafter
I want to see a combat simulator built via disciplined TDD
So that I can learn how to use Claude Code effectively with rigorous methodology
```

**Epic Value**: Educational demonstration of AI-assisted development with professional practices

---

## Story 1: Character Creation

**Story ID**: US-01
**Priority**: Critical (Foundation)
**Timeline**: 0:08-0:23 (15 minutes)
**Demo Wow Factor**: ⭐⭐⭐ (Immutability demonstration)

### Story Statement
```
As a player
I want to create a character with name, HP, and attack power
So that I can participate in combat simulations
```

### Business Rules
- Characters are immutable value objects
- HP must be ≥ 0
- Attack Power must be > 0
- Name must be non-empty string

### Acceptance Criteria

#### AC-1.1: Valid Character Creation
```gherkin
Scenario: Create character with valid attributes
  Given no character exists
  When I create a character named "Thorin" with 20 HP and 5 Attack Power
  Then the character's name is "Thorin"
  And the character's HP is 20
  And the character's Attack Power is 5
```

#### AC-1.2: Character Liveness - Alive State
```gherkin
Scenario: Character with positive HP is alive
  Given a character with 15 HP
  When I check if the character is alive
  Then the result is true
```

#### AC-1.3: Character Liveness - Dead State (Zero HP)
```gherkin
Scenario: Character with zero HP is dead
  Given a character with 0 HP
  When I check if the character is alive
  Then the result is false
```

#### AC-1.4: Character Liveness - Dead State (Negative HP)
```gherkin
Scenario: Character with negative HP is dead
  Given a character with -5 HP
  When I check if the character is alive
  Then the result is false
```

#### AC-1.5: Immutability on Damage
```gherkin
Scenario: Receiving damage returns new instance
  Given a character "Legolas" with 18 HP
  When the character receives 5 damage
  Then a new character instance is returned
  And the new character has 13 HP
  And the original character instance remains unchanged with 18 HP
```

### Technical Acceptance
- [ ] `Character` class implemented as value object
- [ ] Constructor or factory method for creation
- [ ] `isAlive(): boolean` method
- [ ] `receiveDamage(amount: number): Character` method (returns new instance)
- [ ] Zero public setters
- [ ] 4+ unit tests covering all ACs

### Demo Script Notes
- **Start**: Write failing test for character creation
- **Middle**: Show immutability via `receiveDamage()` returning new instance
- **End**: Run tests, all green
- **Wow Moment**: Original character unchanged after damage - demonstrate with debugger or assertion

---

## Story 2: Dice Rolling System

**Story ID**: US-02
**Priority**: Critical (Architectural Foundation)
**Timeline**: 0:23-0:33 (10 minutes)
**Demo Wow Factor**: ⭐⭐⭐⭐⭐ (Hexagonal Architecture emerges!)

### Story Statement
```
As a combat system
I need to generate random numbers simulating dice rolls
So that attack outcomes are varied and unpredictable
While keeping the system fully testable
```

### Business Rules
- Standard d6 dice (1-6 range)
- Randomness must be injectable for testing
- Production uses real randomness
- Tests use deterministic rolls

### Acceptance Criteria

#### AC-2.1: Random Dice Roll Range
```gherkin
Scenario: Roll d6 dice with random outcome
  Given a 6-sided dice roller
  When the dice is rolled
  Then the result is between 1 and 6 inclusive
```

#### AC-2.2: Deterministic Test Double - Fixed Value
```gherkin
Scenario: Test double returns fixed value
  Given a fixed dice roller configured to return 4
  When the dice is rolled
  Then the result is 4

  When the dice is rolled again
  Then the result is still 4
```

#### AC-2.3: Deterministic Test Double - Sequence
```gherkin
Scenario: Test double returns sequence of values
  Given a fixed dice roller configured to return [3, 5, 2]
  When the dice is rolled 3 times
  Then the first result is 3
  And the second result is 5
  And the third result is 2
```

#### AC-2.4: Port/Adapter Interchangeability
```gherkin
Scenario: Adapters are interchangeable via dependency injection
  Given a DiceRoller port interface
  And a RandomDiceRoller adapter (production)
  And a FixedDiceRoller adapter (testing)
  When either adapter is injected into a combat service
  Then the combat service operates correctly with either implementation
  And no code changes are required to switch adapters
```

### Technical Acceptance
- [ ] `DiceRoller` interface (Port)
- [ ] `RandomDiceRoller` class implementing DiceRoller (Adapter)
- [ ] `FixedDiceRoller` class implementing DiceRoller (Test Double)
- [ ] No direct `Math.random()` calls in domain logic
- [ ] 3+ unit tests

### Demo Script Notes
- **Trigger**: "How do we test random dice rolls?"
- **Problem**: Can't assert on random values
- **Solution**: Claude suggests Port/Adapter pattern
- **Wow Moment**: "This is Hexagonal Architecture! It emerged from testability constraints, not upfront design."
- **Visual**: Draw hexagon diagram on whiteboard/slide

---

## Story 3: Attack Resolution

**Story ID**: US-03
**Priority**: Critical (Core Mechanic)
**Timeline**: 0:33-0:48 (15 minutes)
**Demo Wow Factor**: ⭐⭐⭐ (Immutability + Domain Services)

### Story Statement
```
As a player
I want to attack an enemy
So that I can see damage calculated based on my attack power and dice roll
And the enemy's HP reduced accordingly
```

### Business Rules
- Damage = Attacker's Attack Power + Dice Roll
- HP cannot go below 0
- Dead characters (HP ≤ 0) cannot attack
- Damage application returns new character instance (immutability)

### Acceptance Criteria

#### AC-3.1: Damage Calculation Formula
```gherkin
Scenario: Calculate total damage
  Given an attacker with 5 Attack Power
  And a dice roll of 3
  When the attack is resolved
  Then the total damage is 8 (5 + 3)
```

#### AC-3.2: Damage Application - Normal Case
```gherkin
Scenario: Apply damage to healthy defender
  Given a defender with 20 HP
  And an incoming attack dealing 8 damage
  When the damage is applied
  Then the defender's new HP is 12
  And a new defender instance is returned
```

#### AC-3.3: Damage Application - Overkill (HP Floor)
```gherkin
Scenario: Damage exceeds remaining HP
  Given a defender with 5 HP
  And an incoming attack dealing 8 damage
  When the damage is applied
  Then the defender's new HP is 0 (not -3)
```

#### AC-3.4: Attack Result Structure
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

#### AC-3.5: Dead Character Cannot Attack
```gherkin
Scenario: Dead character attempts attack
  Given a character "Ghost" with 0 HP
  When the character attempts to attack
  Then the attack is rejected
  And an error or null result is returned
  And the defender is not harmed
```

### Technical Acceptance
- [ ] `AttackResult` value object
- [ ] `AttackResolver` or `CombatService` domain service
- [ ] `Character.receiveDamage(amount)` returns new Character
- [ ] `Character.performAttack(defender, diceRoll)` method or separate service
- [ ] 5+ unit tests covering all scenarios

### Demo Script Notes
- **Refactoring Moment**: If Character has mutable HP, refactor to immutable
- **Show**: `const newDefender = defender.receiveDamage(damage)` pattern
- **Explain**: "Original defender unchanged - this prevents entire class of bugs"
- **Test**: Assert original and new instances are different objects

---

## Story 4: Combat Round Orchestration

**Story ID**: US-04
**Priority**: Critical (E2E Completion)
**Timeline**: 0:48-0:58 (10 minutes)
**Demo Wow Factor**: ⭐⭐⭐⭐⭐ (E2E test turns green!)

### Story Statement
```
As a player
I want to execute a combat round where both characters attack each other
So that I can see the progression of battle
And determine who is winning
```

### Business Rules
- Both characters attack once per round (if alive)
- Turn order: Character A attacks B, then B attacks A
- Dead characters skip their attack turn
- Round results are structured data (not console prints)

### Acceptance Criteria

#### AC-4.1: Full Combat Round - Both Alive
```gherkin
Scenario: Both characters attack in one round
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

#### AC-4.2: Combat Round - One Character Dead
```gherkin
Scenario: Dead character cannot attack in round
  Given "Thorin" with 10 HP and 5 Attack Power
  And "Goblin" with 0 HP and 3 Attack Power (already dead)
  And dice roll is 4
  When a combat round is executed
  Then only Thorin attacks
  And Goblin does not attack
  And the round result indicates "Goblin could not attack (dead)"
```

#### AC-4.3: Round Result Data Structure
```gherkin
Scenario: Round result contains complete data
  Given a combat round is executed
  Then the round result contains:
    - Round number
    - Attacker 1 action details (attack result or skip reason)
    - Attacker 2 action details (attack result or skip reason)
    - Character 1 updated state
    - Character 2 updated state
    - Combat status (ongoing or finished)
```

#### AC-4.4: No Console Prints in Domain Logic
```gherkin
Scenario: Domain logic returns data, does not print
  Given a combat round is executed
  Then no console output is produced by domain logic
  And all combat events are returned as structured data
  And the CLI layer is responsible for formatting output
```

### Technical Acceptance
- [ ] `CombatRound` orchestrator class or function
- [ ] `RoundResult` value object
- [ ] Proper separation: domain returns data, CLI presents
- [ ] E2E test passing (this is the walking skeleton from minute 3!)
- [ ] 4+ unit tests

### Demo Script Notes
- **Big Moment**: "Remember that failing E2E test? Let's run it now."
- **Expected**: Test goes from red to green
- **Celebrate**: "We built exactly what the test specified. TDD works!"
- **Run CLI**: `npm start` or equivalent - show live combat
- **Wow Factor**: Functional software in <60 minutes with 100% test coverage

---

## Story 5: Victory Condition (Optional Buffer)

**Story ID**: US-05
**Priority**: Nice-to-Have (Buffer)
**Timeline**: 0:58-1:00 (2 minutes if time allows)
**Demo Wow Factor**: ⭐⭐ (Polish, not critical)

### Story Statement
```
As a player
I want to know when combat ends and who won
So that I can see the final outcome
```

### Business Rules
- Combat ends when one character reaches HP ≤ 0
- Surviving character is the winner
- No draws in this simplified ruleset

### Acceptance Criteria

#### AC-5.1: Victory Detection
```gherkin
Scenario: Combat ends when one character dies
  Given a combat in progress
  And Character A has 2 HP
  And Character B has 5 HP
  When Character A receives fatal damage
  Then the combat ends immediately
  And Character B is declared the winner
```

#### AC-5.2: Combat Result Structure
```gherkin
Scenario: Combat result contains outcome data
  Given combat has ended with a winner
  Then the combat result contains:
    - Winner name
    - Winner's remaining HP
    - Loser name
    - Total rounds fought
    - Victory message
```

### Technical Acceptance
- [ ] `CombatResult` value object
- [ ] `CombatSimulator` use case with game loop
- [ ] Victory condition check after each round
- [ ] 2+ tests

### Demo Script Notes
- **If Time Allows**: Implement quickly
- **If No Time**: "This is Feature 5 - we designed it as optional. We've proven the methodology already."
- **Fallback**: Show how you'd implement it if you had 5 more minutes

---

## Story Map: Visual Flow

```
Epic: Combat Simulator CLI
│
├─ US-01: Character Creation (Foundation)
│   └─ Outputs: Character value object, isAlive(), receiveDamage()
│
├─ US-02: Dice Rolling System (Architecture)
│   └─ Outputs: DiceRoller port, RandomDiceRoller, FixedDiceRoller
│
├─ US-03: Attack Resolution (Core Mechanic)
│   └─ Outputs: AttackResult, AttackResolver, damage calculation
│
├─ US-04: Combat Round (E2E Integration)
│   └─ Outputs: CombatRound, RoundResult, working CLI
│
└─ US-05: Victory Condition (Polish) [Optional]
    └─ Outputs: CombatResult, game loop with end condition
```

---

## Demo Execution Checklist

### Pre-Demo Setup
- [ ] Terminal font size ≥ 18pt
- [ ] CLAUDE.md file created and visible
- [ ] Timer started (visible to presenter)
- [ ] Test framework configured
- [ ] Git initialized (for commit demonstrations)

### During Demo - Story Completion Checklist

**US-01: Character Creation**
- [ ] Write failing test for character creation
- [ ] Implement Character class
- [ ] Write failing test for isAlive()
- [ ] Implement isAlive() method
- [ ] Write failing test for receiveDamage() immutability
- [ ] Refactor to return new instance
- [ ] All tests green
- [ ] Show "original unchanged" assertion

**US-02: Dice Rolling System**
- [ ] Encounter testability problem with randomness
- [ ] Ask Claude: "How do we test random dice?"
- [ ] Claude suggests Port/Adapter pattern
- [ ] Implement DiceRoller interface
- [ ] Implement FixedDiceRoller test double
- [ ] Implement RandomDiceRoller for production
- [ ] Tests use FixedDiceRoller
- [ ] Draw hexagon diagram
- [ ] Explain: "Architecture emerged from constraints"

**US-03: Attack Resolution**
- [ ] Write failing test for damage calculation
- [ ] Implement AttackResolver or similar
- [ ] Write test for damage application
- [ ] Ensure receiveDamage() returns new Character
- [ ] Write test for HP floor (cannot go below 0)
- [ ] Write test for dead character cannot attack
- [ ] All tests green
- [ ] Refactoring: ensure immutability throughout

**US-04: Combat Round Orchestration**
- [ ] Write failing test for full round
- [ ] Implement CombatRound orchestrator
- [ ] Implement RoundResult value object
- [ ] Write test for dead character skips attack
- [ ] Ensure domain returns data (no prints)
- [ ] Create CLI layer (main.ts)
- [ ] Run E2E test - SHOULD PASS NOW
- [ ] Run CLI - show live combat
- [ ] CELEBRATE!

**US-05: Victory Condition (if time)**
- [ ] Write test for victory detection
- [ ] Implement CombatResult
- [ ] Add game loop to CLI
- [ ] Show winner announcement

### Post-Demo Validation
- [ ] Run all tests - 100% pass
- [ ] Show coverage report - aim for 100%
- [ ] Show folder structure - Clean Architecture visible
- [ ] Git log - show TDD commit messages (red, green, refactor)

---

## Acceptance Criteria Quick Reference

| Story | Total ACs | Critical ACs | Test Count |
|-------|-----------|--------------|------------|
| US-01 | 5         | 5            | 4-5        |
| US-02 | 4         | 4            | 3-4        |
| US-03 | 5         | 5            | 5-6        |
| US-04 | 4         | 4            | 4-5        |
| US-05 | 2         | 0 (optional) | 2          |
| **Total** | **20** | **18** | **18-22** |

**Expected Total Test Count**: 18-22 unit tests + 1 E2E test = ~20-23 tests total

---

**Document Status**: Ready for Development
**Next Phase**: DESIGN (Architecture Definition)
**Estimated Development Time**: 50-55 minutes (5-minute buffer)
