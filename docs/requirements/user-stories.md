# Combat Simulator - User Stories

**Project**: Combat Simulator CLI Demo
**Document Type**: User Story Catalog
**Date**: 2026-01-07
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

## Combat Rules Reference

All user stories implement these clarified combat rules:

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

## Story 1: Character Creation

**Story ID**: US-01
**Priority**: Critical (Foundation)
**Timeline**: 0:08-0:20 (15 minutes)
**Demo Wow Factor**: [***] (Derived Agility + Immutability demonstration)

### Story Statement
```
As a player
I want to create a character with randomly generated stats
So that I can participate in combat with unique characters
```

### Business Rules
- Characters are immutable value objects
- HP must be >= 0
- Attack Power must be > 0
- Name must be non-empty string
- Agility is derived: Attack Power + HP (not stored)
- Stats generated via DiceRoller (random for production, fixed for tests)

### Acceptance Criteria

#### AC-1.1: Character Creation with Random Stats
```gherkin
Scenario: Create character with random stats
  Given a DiceRoller that returns [4, 3] for HP rolls and [2] for Attack roll
  When I create a character named "Thorin"
  Then the character has name "Thorin"
  And the character has HP calculated from dice rolls
  And the character has Attack Power from dice roll
  And the character has Agility = Attack Power + HP (derived, not stored)
```

#### AC-1.2: Character Creation with Fixed Stats (Testing)
```gherkin
Scenario: Create character with fixed stats for testing
  Given a FixedDiceRoller configured for predictable values
  When I create a character "Thorin" resulting in 20 HP and 5 Attack
  Then the character has name "Thorin"
  And the character has 20 HP
  And the character has 5 Attack Power
  And the character has Agility of 25 (20 + 5)
```

#### AC-1.3: Character Liveness - Alive State
```gherkin
Scenario: Character with positive HP is alive
  Given a character with HP > 0
  When I check if the character is alive
  Then the result is true
```

#### AC-1.4: Character Liveness - Dead State (Zero HP)
```gherkin
Scenario: Character with zero HP is dead
  Given a character with HP = 0
  When I check if the character is alive
  Then the result is false
```

#### AC-1.5: Character Name Validation
```gherkin
Scenario: Character name cannot be empty
  Given I attempt to create a character with name ""
  Then creation fails with ValidationError "Name cannot be empty"
```

#### AC-1.6: Immutability on Damage
```gherkin
Scenario: Receiving damage returns new instance
  Given a character "Legolas" with 18 HP
  When the character receives 5 damage
  Then a new character instance is returned
  And the new character has 13 HP
  And the original character instance remains unchanged with 18 HP
```

### Technical Acceptance
- [ ] `Character` class implemented as immutable value object
- [ ] `agility` is a computed property: `get agility() { return this.hp + this.attackPower }`
- [ ] Factory method or constructor using DiceRoller for creation
- [ ] `isAlive(): boolean` method
- [ ] `receiveDamage(amount: number): Character` method (returns new instance)
- [ ] Zero public setters
- [ ] 5-6 unit tests covering all ACs

### Demo Script Notes
- **Start**: Write failing test for character creation with Agility
- **Middle**: Show derived Agility - "As you take damage, you get slower!"
- **End**: Run tests, demonstrate immutability - original unchanged after damage
- **Wow Moment**: Agility computed from HP + Attack, never stored

---

## Story 2: Dice Rolling System

**Story ID**: US-02
**Priority**: Critical (Architectural Foundation)
**Timeline**: 0:20-0:28 (10 minutes)
**Demo Wow Factor**: [*****] (Hexagonal Architecture emerges!)

### Story Statement
```
As a combat system
I need to generate random numbers simulating dice rolls
So that attack outcomes are varied and unpredictable
While keeping the system fully testable
```

### Business Rules
- Standard D6 dice: [1, 6] inclusive
- Never returns 0, never returns 7
- Randomness must be injectable for testing
- Production uses real randomness
- Tests use deterministic rolls
- Same DiceRoller used for combat AND character stat generation

### Acceptance Criteria

#### AC-2.1: Random Dice Roll Range
```gherkin
Scenario: Roll D6 dice with random outcome
  Given a 6-sided dice roller (D6)
  When the dice is rolled
  Then the result is between 1 and 6 inclusive
  And it never returns 0
  And it never returns 7
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
- [ ] `DiceRoller` interface (Port) with `roll(): number`
- [ ] `RandomDiceRoller` class implementing DiceRoller (Adapter)
- [ ] `FixedDiceRoller` class implementing DiceRoller (Test Double)
- [ ] No direct `Math.random()` calls in domain logic
- [ ] 3-4 unit tests

### Demo Script Notes
- **Trigger**: "How do we test random dice rolls?"
- **Problem**: Can't assert on random values
- **Solution**: Claude suggests Port/Adapter pattern
- **Wow Moment**: "This is Hexagonal Architecture! It emerged from testability constraints, not upfront design."
- **Visual**: Draw hexagon diagram on whiteboard/slide

---

## Story 3: Initiative Roll

**Story ID**: US-03
**Priority**: Critical (Combat Order)
**Timeline**: 0:28-0:33 (5 minutes)
**Demo Wow Factor**: [**] (Quick win, sets up attacker advantage)

### Story Statement
```
As the combat system
I need to determine who attacks first based on an initiative roll at the start of combat
So that combat order is fair but determined upfront
```

### Business Rules
- Initiative rolled ONCE at fight start (not every round)
- Each character rolls D6 + Agility (Attack Power + HP)
- Higher total wins initiative for entire combat
- Winner is "attacker", loser is "defender"
- Ties resolved by higher base Agility, then first character in order

### Acceptance Criteria

#### AC-3.1: Initiative Calculation
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

#### AC-3.2: Initiative Tie-Breaker
```gherkin
Scenario: Initiative tie resolved deterministically
  Given two characters with equal initiative totals
  When initiative is rolled
  Then the character with higher base Agility wins
  Or if still tied, first character in order wins (deterministic)
```

### Technical Acceptance
- [ ] `InitiativeResult` value object with attacker and defender
- [ ] Initiative calculated using Agility + D6 roll
- [ ] Clear winner determination with tie-breaker rules
- [ ] Initiative stored for combat duration
- [ ] 2-3 unit tests

### Demo Script Notes
- **Start**: Quick implementation - initiative = Agility + D6
- **Show**: InitiativeResult determines who attacks first
- **Connect**: Sets up the attacker advantage rule in Feature 5

---

## Story 4: Attack Resolution

**Story ID**: US-04
**Priority**: Critical (Core Mechanic)
**Timeline**: 0:33-0:43 (15 minutes)
**Demo Wow Factor**: [***] (Immutability + Domain Services)

### Story Statement
```
As a player
I want to attack an enemy
So that I can see damage calculated based on my attack power and dice roll
And the enemy's HP reduced accordingly
```

### Business Rules
- Damage = Attacker's Attack Power + Dice Roll (1d6)
- HP cannot go below 0 (floor at 0)
- Dead characters (HP = 0) cannot attack
- Damage application returns new character instance (immutability)

### Acceptance Criteria

#### AC-4.1: Damage Calculation Formula
```gherkin
Scenario: Calculate total damage
  Given an attacker with 5 Attack Power
  And a dice roll of 3
  When the attack is resolved
  Then the total damage is 8 (5 + 3)
```

#### AC-4.2: Damage Application - Normal Case
```gherkin
Scenario: Apply damage to healthy defender
  Given a defender with 20 HP
  And an incoming attack dealing 8 damage
  When the damage is applied
  Then the defender's new HP is 12
  And a new defender instance is returned (immutability)
```

#### AC-4.3: Damage Application - Overkill (HP Floor)
```gherkin
Scenario: Damage exceeds remaining HP
  Given a defender with 5 HP
  And an incoming attack dealing 8 damage
  When the damage is applied
  Then the defender's new HP is 0 (not -3)
```

#### AC-4.4: Attack Result Structure
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

#### AC-4.5: Dead Character Cannot Attack
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
- [ ] 4-5 unit tests covering all scenarios

### Demo Script Notes
- **Refactoring Moment**: If Character has mutable HP, refactor to immutable
- **Show**: `const newDefender = defender.receiveDamage(damage)` pattern
- **Explain**: "Original defender unchanged - this prevents entire class of bugs"
- **Test**: Assert original and new instances are different objects

---

## Story 5: Combat Round

**Story ID**: US-05
**Priority**: Critical (Core Mechanic)
**Timeline**: 0:43-0:53 (15 minutes)
**Demo Wow Factor**: [*****] (Attacker Advantage in action!)

### Story Statement
```
As a player
I want to execute a combat round where the attacker strikes first
And the defender counter-attacks only if they survive
So that combat is fair but decisive
```

### Business Rules
- Attacker (initiative winner) attacks first
- Defender counter-attacks ONLY if they survive (HP > 0)
- If attacker kills defender, round ends immediately - no counter-attack
- Round results are structured data (not console prints)
- Ties are impossible due to sequential resolution

### Acceptance Criteria

#### AC-5.1: Full Combat Round - Both Survive
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

#### AC-5.2: Attacker Kills Defender - No Counter-Attack
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

#### AC-5.3: Round Result Data Structure
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

#### AC-5.4: No Console Prints in Domain Logic
```gherkin
Scenario: Domain logic returns data, does not print
  Given a combat round is executed
  Then no console output is produced by domain logic
  And all combat events are returned as structured data
  And the CLI layer is responsible for formatting output
```

### Technical Acceptance
- [ ] `CombatRound` orchestrator that enforces attacker advantage
- [ ] `RoundResult` value object with all fields above
- [ ] Proper separation: domain returns data, CLI presents
- [ ] 4-5 unit tests including attacker advantage scenario

### Demo Script Notes
- **Big Moment**: "Watch what happens when Thorin kills Goblin"
- **Expected**: Goblin dies, NO counter-attack happens
- **Explain**: "Attacker Advantage - sequential resolution prevents unfair simultaneous death"
- **Wow Factor**: Core mechanic working correctly

---

## Story 6: Game Loop

**Story ID**: US-06
**Priority**: Critical (Grand Finale)
**Timeline**: 0:53-0:58 (10 minutes combined with US-07)
**Demo Wow Factor**: [*****] (It works! Complete game!)

### Story Statement
```
As a player
I want combat to run automatically through multiple rounds until one character dies
Seeing each round's action unfold
So that I can watch the complete battle
```

### Business Rules
- Combat is fully automated - no user interaction during fight
- Initiative determined at start sets attack order for all rounds
- Each round follows attacker advantage rule
- Combat ends immediately when a character reaches 0 HP
- Output shows round-by-round progression

### Acceptance Criteria

#### AC-6.1: Fully Automated Combat to Victory
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

#### AC-6.2: Combat Output Shows Progression
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

#### AC-6.3: Combat Ends Immediately on Death
```gherkin
Scenario: Combat ends mid-round when character dies
  Given combat in progress
  When a character reaches 0 HP mid-round
  Then combat ends immediately (attacker advantage)
  And no further rounds execute
  And survivor is declared winner
```

### Technical Acceptance
- [ ] `CombatSimulator` use case that orchestrates full combat
- [ ] Outputs detailed round-by-round log
- [ ] Victory message clearly identifies winner
- [ ] Fully automated - no user interaction during combat
- [ ] 3-4 unit tests

### Demo Script Notes
- **Big Moment**: Run the CLI, watch full combat unfold
- **Show**: Round-by-round output with damage and HP
- **Celebrate**: "55 minutes, rigorous TDD, and we have a working game!"

---

## Story 7: Victory Condition (REQUIRED)

**Story ID**: US-07
**Priority**: Critical (Game Completion)
**Timeline**: Part of 0:53-0:58 (combined with US-06)
**Demo Wow Factor**: [****] (Complete game with clear outcome)

### Story Statement
```
As a player
I want to know when combat is over and who won
So that I can see the final outcome clearly
```

### Business Rules
- Combat ends when one character reaches HP = 0
- Surviving character is the winner
- No draws (sequential resolution prevents ties)
- Victory message is clearly formatted

### Acceptance Criteria

#### AC-7.1: Victory Detection
```gherkin
Scenario: Combat ends when one character dies
  Given combat in progress
  When a character reaches 0 HP
  Then combat ends immediately
  And the surviving character is declared winner
  And victory message displays: "[Winner] wins! [Loser] has been defeated."
```

#### AC-7.2: Victory Message Format
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

### Technical Acceptance
- [ ] `CombatResult` value object with winner, loser, final states
- [ ] Victory condition check after each attack
- [ ] Clear, formatted victory message
- [ ] 2 unit tests

### Demo Script Notes
- **Trigger**: Final combat result display
- **Show**: Clear winner announcement with HP summary
- **Payoff**: Complete game from start to finish

---

## Story Map: Visual Flow

```
Epic: Combat Simulator CLI
|
+-- US-01: Character Creation (Foundation)
|   +-- Outputs: Character value object, isAlive(), receiveDamage(), agility (derived)
|
+-- US-02: Dice Rolling System (Architecture)
|   +-- Outputs: DiceRoller port, RandomDiceRoller, FixedDiceRoller
|
+-- US-03: Initiative Roll (Combat Order)
|   +-- Outputs: InitiativeResult with attacker/defender assignment
|
+-- US-04: Attack Resolution (Core Mechanic)
|   +-- Outputs: AttackResult, AttackResolver, damage calculation
|
+-- US-05: Combat Round (Core Mechanic)
|   +-- Outputs: CombatRound, RoundResult, attacker advantage enforcement
|
+-- US-06: Game Loop (Automation)
|   +-- Outputs: CombatSimulator, round-by-round execution
|
+-- US-07: Victory Condition (REQUIRED)
    +-- Outputs: CombatResult, victory message, game completion
```

---

## Demo Execution Checklist

### Pre-Demo Setup
- [ ] Terminal font size >= 18pt
- [ ] CLAUDE.md file created and visible
- [ ] Timer started (visible to presenter)
- [ ] Test framework configured
- [ ] Git initialized (for commit demonstrations)

### During Demo - Story Completion Checklist

**US-01: Character Creation**
- [ ] Write failing test for character creation with Agility
- [ ] Implement Character class with derived agility
- [ ] Write failing test for isAlive()
- [ ] Implement isAlive() method
- [ ] Write failing test for receiveDamage() immutability
- [ ] Refactor to return new instance
- [ ] All tests green
- [ ] Show derived Agility demonstration

**US-02: Dice Rolling System**
- [ ] Encounter testability problem with randomness
- [ ] Ask Claude: "How do we test random dice?"
- [ ] Claude suggests Port/Adapter pattern
- [ ] Implement DiceRoller interface
- [ ] Implement FixedDiceRoller test double
- [ ] Implement RandomDiceRoller for production
- [ ] Tests use FixedDiceRoller
- [ ] Explain: "Architecture emerged from constraints"

**US-03: Initiative Roll**
- [ ] Write failing test for initiative calculation
- [ ] Implement InitiativeResult
- [ ] Test higher Agility + roll wins
- [ ] Test tie-breaker scenarios
- [ ] All tests green

**US-04: Attack Resolution**
- [ ] Write failing test for damage calculation
- [ ] Implement AttackResolver or similar
- [ ] Write test for damage application
- [ ] Ensure receiveDamage() returns new Character
- [ ] Write test for HP floor (cannot go below 0)
- [ ] Write test for dead character cannot attack
- [ ] All tests green
- [ ] Refactoring: ensure immutability throughout

**US-05: Combat Round**
- [ ] Write failing test for full round (both survive)
- [ ] Write failing test for attacker advantage (defender dies)
- [ ] Implement CombatRound orchestrator
- [ ] Implement RoundResult value object
- [ ] Ensure domain returns data (no prints)
- [ ] All tests green
- [ ] Show attacker advantage in action

**US-06: Game Loop**
- [ ] Write failing test for automated combat
- [ ] Implement CombatSimulator use case
- [ ] Test round-by-round progression
- [ ] Test immediate end on death
- [ ] Create CLI layer (main.ts)
- [ ] All tests green
- [ ] Run CLI - show live combat

**US-07: Victory Condition**
- [ ] Write test for victory detection
- [ ] Implement CombatResult
- [ ] Test victory message format
- [ ] Show winner announcement
- [ ] CELEBRATE!

### Post-Demo Validation
- [ ] Run all tests - 100% pass
- [ ] Show coverage report - aim for 100%
- [ ] Show folder structure - Clean Architecture visible
- [ ] Git log - show TDD commit messages (red, green, refactor)

---

## Acceptance Criteria Quick Reference

| Story | Total ACs | Critical ACs | Test Count |
|-------|-----------|--------------|------------|
| US-01 | 6         | 5            | 5-6        |
| US-02 | 4         | 4            | 3-4        |
| US-03 | 2         | 2            | 2-3        |
| US-04 | 5         | 3            | 4-5        |
| US-05 | 4         | 2            | 4-5        |
| US-06 | 3         | 2            | 3-4        |
| US-07 | 2         | 1            | 2          |
| **Total** | **26** | **19** | **23-29** |

**Expected Total Test Count**: 23-29 unit tests + 1 E2E test = ~25-30 tests total

---

**Document Status**: Ready for Development
**Next Phase**: DESIGN (Architecture Definition)
**Estimated Development Time**: 50-55 minutes (5-minute buffer)
