# Combat Simulator Demo - Requirements Specification

**Project**: Combat Simulator CLI - Software Crafters Live Coding Demo
**Wave**: DISCUSS (Requirements Gathering)
**Date**: 2026-01-07
**Requirements Analyst**: Riley (product-owner agent)
**Stakeholders**: Alex (Demo Presenter), Software Crafters Audience, Claude Code (Developer)

---

## Executive Summary

### Business Context

This project demonstrates how **Claude Code + disciplined engineering practices** produces production-ready software. The deliverable is a D&D-style turn-based combat simulator CLI, built live in 60 minutes using:

- **ATDD** (Acceptance Test-Driven Development)
- **TDD Outside-In** (start with E2E test, drill down to units)
- **Clean Architecture** (Hexagonal/Ports & Adapters)
- **Immutable Domain Models**
- **100% test coverage** (no shortcuts)

**Key Message**: *"AI amplifies your practices. Discipline -> excellent code. No discipline -> fast garbage."*

### Success Criteria

**Functional Success:**
- Playable combat simulator with two characters fighting to death
- All features implemented via TDD (red-green-refactor cycle visible)
- Clean Architecture patterns emerge naturally
- 100% test coverage achieved

**Demonstration Success:**
- Completed within 60-minute timeline
- Minimum 4 "wow moments" delivered (documented below)
- Audience understands methodology, not just the AI tool
- Code quality demonstrates professional software craftsmanship

### Business Value

**Primary Value**: Educational demonstration proving that AI coding assistants, when guided by disciplined practices, produce maintainable, tested, architecturally sound code.

**Secondary Value**: Reusable reference implementation for Software Crafters adopting AI-assisted development.

---

## Combat Rules (Clarified)

These rules govern all combat mechanics. They are explicit to prevent implementation ambiguity.

### Death Rule: Attacker Advantage

- First attacker resolves their attack fully
- Defender counter-attacks **only if they survive** (HP > 0)
- If attacker kills defender, round ends immediately - no counter-attack
- Ties are **impossible** due to sequential resolution

### Attack Order: Initiative Roll

- Initiative is rolled **once at fight start** (not every round)
- Each character rolls a D6 and adds their **Agility bonus**
- Higher total wins initiative and attacks first **every round** for the entire combat
- Winner of initiative is called the "attacker", loser is "defender"

### Derived Stat: Agility

- **Agility = Attack Power + Current HP**
- This is a derived stat, not stored separately
- Represents fatigue: as you take damage, HP drops, so Agility drops
- Used only for initiative calculation at fight start (uses starting HP)

### Dice Boundaries

- All dice are D6: returns value in range **[1, 6] inclusive**
- Never returns 0, never returns 7
- Same DiceRoller port used for combat rolls AND character stat generation

### Damage Calculation

- **Total Damage = Attack Power + Die Roll**
- No caps, no floors, no armor, no critical hits (simplified D&D)
- HP cannot go below 0 (floor at 0)

---

## Domain Analysis

### Ubiquitous Language

**Core Domain Terms:**

| Term | Definition | Usage Context |
|------|------------|---------------|
| **Character** | A combatant with name, hit points (HP), attack power, and derived agility | Value Object (immutable) |
| **Hit Points (HP)** | Health of a character; 0 HP = death | Integer >= 0 |
| **Attack Power** | Base damage a character can inflict | Integer > 0 |
| **Agility** | Derived stat: Attack Power + HP; used for initiative | Computed property |
| **Dice Roll** | Random number generation simulating D&D dice | [1, 6] for D6 dice |
| **Damage** | Total harm inflicted = Attack Power + Dice Roll | Calculated value |
| **Initiative** | Roll at combat start determining attack order | D6 + Agility |
| **Attacker** | Character who won initiative, attacks first every round | Role assignment |
| **Defender** | Character who lost initiative, counter-attacks if alive | Role assignment |
| **Combat Round** | One turn where attacker strikes, defender counter-attacks if alive | Orchestration unit |
| **Attack Resolution** | Process of calculating and applying damage | Domain service |
| **Victory Condition** | State where one combatant reaches 0 HP | Business rule |
| **Port** | Interface abstracting external dependencies (e.g., randomness) | Hexagonal Architecture |
| **Adapter** | Concrete implementation of a port | Hexagonal Architecture |
| **Test Double** | Fake implementation of a port for testing | Testing pattern |

### Domain Rules

**DR-01: Character Immutability**
- Characters are value objects
- State changes return new instances
- No setters allowed
- Illegal states unrepresentable via type system

**DR-02: Combat Mechanics - Damage**
- Damage = Attacker's Attack Power + Dice Roll (1d6)
- HP reduction = Current HP - Damage
- HP floors at 0 (cannot go negative)

**DR-03: Victory Determination**
- Combat ends when one character reaches HP = 0
- Surviving character is declared winner
- No draws (sequential resolution prevents ties)

**DR-04: Turn Order - Initiative System**
- Initiative is rolled ONCE at fight start
- Each character rolls D6 + Agility (Attack Power + HP)
- Higher total wins initiative for entire combat
- Winner is "attacker", loser is "defender"

**DR-05: Attacker Advantage Rule**
- Attacker resolves their attack first
- Defender counter-attacks ONLY if they survive (HP > 0)
- If attacker kills defender, round ends immediately
- No simultaneous attacks - sequential resolution

**DR-06: Dice Boundaries**
- All dice rolls return values in [1, 6] inclusive
- Never 0, never 7
- Same DiceRoller port for combat and character generation

**DR-07: Derived Agility**
- Agility = Attack Power + Current HP
- Derived at access time, never stored
- Used for initiative calculation at fight start

**DR-08: Testability Requirement**
- All randomness must be injectable
- Tests must use deterministic dice rolls
- Production uses real randomness

---

## Feature Breakdown

### Epic: Combat Simulator CLI

**Epic Goal**: Enable two characters to engage in turn-based combat with visible outcomes, demonstrating TDD and Clean Architecture principles.

**Epic Acceptance Criteria**:
```gherkin
Given two characters are created
When they engage in combat
Then initiative is rolled to determine attack order
And combat proceeds in rounds until one dies
And the winner is announced
And all combat actions are logged
```

---

### Feature 1: Character Creation (Timeline: 0:08-0:20, 15 minutes)

#### Business Value
Foundation for all combat mechanics. Demonstrates value object immutability, derived stats, and type-driven design.

#### User Story
```
As a player
I want to create a character with randomly generated stats
So that I can participate in combat with unique characters
```

#### Acceptance Criteria

**AC-1.1: Character Creation with Random Stats**
```gherkin
Given a DiceRoller that returns [4, 3] for HP rolls and [2] for Attack roll
When I create a character named "Thorin"
Then the character has name "Thorin"
And the character has HP calculated from dice rolls
And the character has Attack Power from dice roll
And the character has Agility = Attack Power + HP (derived, not stored)
```

**AC-1.2: Character Creation with Fixed Stats (Testing)**
```gherkin
Given a FixedDiceRoller configured for predictable values
When I create a character "Thorin" resulting in 20 HP and 5 Attack
Then the character has name "Thorin"
And the character has 20 HP
And the character has 5 Attack Power
And the character has Agility of 25 (20 + 5)
```

**AC-1.3: Character Liveness Check - Alive**
```gherkin
Given a character with HP > 0
When I check if it's alive
Then it returns true
```

**AC-1.4: Character Liveness Check - Dead**
```gherkin
Given a character with HP = 0
When I check if it's alive
Then it returns false
```

**AC-1.5: Character Name Validation**
```gherkin
Given I attempt to create a character with name ""
Then creation fails with ValidationError "Name cannot be empty"
```

**AC-1.6: Immutability on Damage**
```gherkin
Given a character "Legolas" with 18 HP
When the character receives 5 damage
Then a new character instance is returned
And the new character has 13 HP
And the original character instance remains unchanged with 18 HP
```

#### Technical Outcomes
- `Character` immutable value object with: name, hp, attackPower
- `agility` is a computed property: `get agility() { return this.hp + this.attackPower }`
- Factory method using DiceRoller for random generation
- FixedDiceRoller for deterministic tests
- No setters, illegal state not representable
- 5-6 unit tests

#### Wow Moment
**"Derived Agility stat"** - "Agility isn't stored - it's computed from HP + Attack. As you take damage, you get slower!"

#### Risks & Mitigations
- **Risk**: Claude suggests mutable design with setters
- **Mitigation**: Explicitly guide toward immutable value object pattern

---

### Feature 2: Dice Rolling System (Timeline: 0:20-0:28, 10 minutes)

#### Business Value
Separates randomness from business logic, enabling testable combat mechanics. Introduces Hexagonal Architecture pattern.

#### User Story
```
As a combat system
I need to generate random numbers simulating dice rolls
So that attack outcomes are varied and unpredictable
While keeping the system fully testable
```

#### Acceptance Criteria

**AC-2.1: Random Dice Roll Range**
```gherkin
Given a 6-sided dice roller (D6)
When the dice is rolled
Then the result is between 1 and 6 inclusive
And it never returns 0
And it never returns 7
```

**AC-2.2: Deterministic Test Double - Fixed Value**
```gherkin
Given a fixed dice roller configured to return 4
When the dice is rolled
Then the result is 4

When the dice is rolled again
Then the result is still 4
```

**AC-2.3: Deterministic Test Double - Sequence**
```gherkin
Given a fixed dice roller configured to return [3, 5, 2]
When the dice is rolled 3 times
Then the first result is 3
And the second result is 5
And the third result is 2
```

**AC-2.4: Port/Adapter Interchangeability**
```gherkin
Given a DiceRoller port interface
And a RandomDiceRoller adapter (production)
And a FixedDiceRoller adapter (testing)
When either adapter is injected into a combat service
Then the combat service operates correctly with either implementation
And no code changes are required to switch adapters
```

#### Technical Outcomes
- `DiceRoller` interface (Port) with `roll(): number`
- `RandomDiceRoller` adapter for production
- `FixedDiceRoller` test double with constructor injection: `new FixedDiceRoller([4, 2, 6])` or `new FixedDiceRoller(4)`
- Dependency Injection via constructor for all consumers
- 3-4 unit tests

#### Wow Moment
**"Hexagonal Architecture Emerges Naturally"** - Audience sees Port/Adapter pattern applied to something simple (dice). Demonstrates how architecture emerges from design constraints (testability).

#### Risks & Mitigations
- **Risk**: Claude uses `Math.random()` directly in domain logic
- **Mitigation**: Emphasize testability requirement, ask "How do we test this?"

---

### Feature 3: Initiative Roll (Timeline: 0:28-0:33, 5 minutes)

#### Business Value
Determines combat order at fight start. Quick win that sets up the attacker advantage mechanic.

#### User Story
```
As the combat system
I need to determine who attacks first based on an initiative roll at the start of combat
So that combat order is fair but determined upfront
```

#### Acceptance Criteria

**AC-3.1: Initiative Calculation**
```gherkin
Given "Thorin" with Agility 25 (HP 20 + Attack 5)
And "Goblin" with Agility 13 (HP 10 + Attack 3)
And dice configured for [3, 5] (Thorin rolls 3, Goblin rolls 5)
When initiative is rolled
Then Thorin's initiative = 25 + 3 = 28
And Goblin's initiative = 13 + 5 = 18
And Thorin wins initiative (28 > 18)
And Thorin is designated as "attacker" for all rounds
```

**AC-3.2: Initiative Tie-Breaker**
```gherkin
Given two characters with equal initiative totals
When initiative is rolled
Then the character with higher base Agility wins
Or if still tied, first character in order wins (deterministic)
```

#### Technical Outcomes
- `InitiativeResult` value object with attacker and defender
- Initiative calculated once, stored for combat duration
- Clear winner determination with tie-breaker rules
- 2-3 unit tests

---

### Feature 4: Attack Resolution (Timeline: 0:33-0:43, 15 minutes)

#### Business Value
Implements core combat mechanics. Demonstrates domain services and value objects working together.

#### User Story
```
As a player
I want to attack an enemy
So that I can see damage calculated based on my attack power and dice roll
And the enemy's HP reduced accordingly
```

#### Acceptance Criteria

**AC-4.1: Damage Calculation Formula**
```gherkin
Given an attacker with 5 Attack Power
And a dice roll of 3
When the attack is resolved
Then the total damage is 8 (5 + 3)
```

**AC-4.2: Damage Application - Normal Case**
```gherkin
Given a defender with 20 HP
And an incoming attack dealing 8 damage
When the damage is applied
Then the defender's new HP is 12
And a new defender instance is returned (immutability)
```

**AC-4.3: Damage Application - Overkill (HP Floor at 0)**
```gherkin
Given a defender with 5 HP
And an incoming attack dealing 8 damage
When the damage is applied
Then the defender's new HP is 0 (not -3)
```

**AC-4.4: Attack Result Structure**
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

**AC-4.5: Dead Character Cannot Attack**
```gherkin
Given a character "Ghost" with 0 HP
When the character attempts to attack
Then the attack is rejected
And an error or null result is returned
And the defender is not harmed
```

#### Technical Outcomes
- `AttackResult` value object with: attacker, defender, dieRoll, damage, defenderAfter
- `Character.receiveDamage(amount)` returns new Character instance (immutability)
- 4-5 unit tests

#### Wow Moment
**"Immutability in Practice"** - Character.receiveDamage() returns new Character, doesn't mutate. Audience sees immutability in practice.

#### Risks & Mitigations
- **Risk**: Mutable state sneaks in under time pressure
- **Mitigation**: Refactoring step explicitly enforces immutability

---

### Feature 5: Combat Round (Timeline: 0:43-0:53, 15 minutes)

#### Business Value
Implements the attacker advantage rule. Core mechanic demo showing sequential resolution.

#### User Story
```
As a player
I want to execute a combat round where the attacker strikes first
And the defender counter-attacks only if they survive
So that combat is fair but decisive
```

#### Acceptance Criteria

**AC-5.1: Both Characters Attack (Defender Survives)**
```gherkin
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

**AC-5.2: Attacker Kills Defender - No Counter-Attack**
```gherkin
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

**AC-5.3: Round Result Output Format**
```gherkin
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

#### CLI Output Format
```
Round 1:
  Thorin attacks Goblin for 9 damage!
  Goblin (1 HP) counter-attacks Thorin for 5 damage!
  Status: Thorin 15 HP | Goblin 1 HP
```

#### Technical Outcomes
- `CombatRound` orchestrator that enforces attacker advantage rule
- `RoundResult` value object with all fields above
- DiceRoller injected via constructor
- Working CLI walking skeleton
- 4-5 unit tests

#### Wow Moment
**"Attacker Advantage in action"** - "Watch what happens when Thorin kills Goblin - no counter-attack!"

#### Risks & Mitigations
- **Risk**: Time pressure leads to `console.log` in domain logic
- **Mitigation**: Emphasize separation of concerns - domain returns data, CLI handles presentation

---

### Feature 6: Game Loop (Timeline: 0:53-0:58, 10 minutes)

#### Business Value
Fully automated combat with round-by-round output. Grand finale demonstrating complete system.

#### User Story
```
As a player
I want combat to run automatically through multiple rounds until one character dies
Seeing each round's action unfold
So that I can watch the complete battle
```

#### Acceptance Criteria

**AC-6.1: Fully Automated Combat to Victory**
```gherkin
Given "Thorin" with 20 HP, 5 Attack
And "Goblin" with 10 HP, 3 Attack
And Thorin wins initiative
When I execute "fight"
Then combat runs automatically round by round
And each round displays attacker action and defender reaction
And combat continues until one character has 0 HP
And winner is declared with victory message
```

**AC-6.2: Combat Output Shows Progression**
```gherkin
Given combat between Thorin and Goblin
When combat executes
Then output shows:
  | Round 1: Thorin attacks... Goblin counter-attacks... |
  | Round 2: Thorin attacks... Goblin counter-attacks... |
  | ... |
  | VICTORY: Thorin wins! Goblin has been defeated. |
```

**AC-6.3: Combat Ends Immediately on Death**
```gherkin
Given combat in progress
When a character reaches 0 HP mid-round
Then combat ends immediately (attacker advantage)
And no further rounds execute
And survivor is declared winner
```

#### Technical Outcomes
- `CombatSimulator` use case that orchestrates full combat
- Outputs detailed round-by-round log
- Victory message clearly identifies winner
- Fully automated - no user interaction during combat
- 3-4 unit tests

#### Wow Moment
**"The game works!"** - CLI run, live combat with round-by-round output. "55 minutes, rigorous TDD, and we have a working game"

---

### Feature 7: Victory Condition (Timeline: part of Feature 6, 5 minutes) - REQUIRED

#### Business Value
Completes the game loop. Clear winner determination with formatted output.

#### User Story
```
As a player
I want to know when combat is over and who won
So that I can see the final outcome clearly
```

#### Acceptance Criteria

**AC-7.1: Victory When Opponent Dies**
```gherkin
Given combat in progress
When a character reaches 0 HP
Then combat ends immediately
And the surviving character is declared winner
And victory message displays: "[Winner] wins! [Loser] has been defeated."
```

**AC-7.2: Victory Message Format**
```gherkin
Given Thorin defeats Goblin
When victory is declared
Then output shows:
  | ================================== |
  | VICTORY! Thorin wins!              |
  | Goblin has been defeated.          |
  | Final HP: Thorin 15 | Goblin 0     |
  | ================================== |
```

#### Technical Outcomes
- `CombatResult` value object with winner, loser, final states
- Clear, formatted victory message for audience readability
- 2 unit tests

---

## Non-Functional Requirements

### NFR-1: Performance
**Requirement**: Combat round resolution must complete in under 10ms on standard hardware.
**Rationale**: Demo must feel responsive during live execution.
**Validation**: No explicit measurement required (qualitative assessment sufficient for demo).

### NFR-2: Test Coverage
**Requirement**: 100% line and branch coverage for domain logic.
**Rationale**: Demonstrates TDD rigor and quality standards.
**Validation**: Coverage report generated and shown to audience.

### NFR-3: Code Readability
**Requirement**: All code must be readable by audience on projector (large fonts, clear names).
**Rationale**: Audience must understand code during live demo.
**Validation**: Subjective - presenter comfort with code visibility.

### NFR-4: Architecture Compliance
**Requirement**: Codebase must demonstrate Hexagonal Architecture (Ports & Adapters).
**Rationale**: Educational goal - show Clean Architecture in practice.
**Validation**: Visual inspection of folder structure and dependency flow.

### NFR-5: Immutability
**Requirement**: All domain objects must be immutable.
**Rationale**: Demonstrate functional programming principles and bug prevention.
**Validation**: Code review - no setters, all state changes return new instances.

### NFR-6: Demo Timeline
**Requirement**: All features must be completable within 60-minute window.
**Rationale**: Conference session time constraint.
**Validation**: Timed rehearsal.

---

## Detailed Timeline

| Phase | Time | Activity | Presenter Notes |
| ----- | ---- | -------- | --------------- |
| **Setup** | 0:00-0:03 | Show CLAUDE.md, explain the framework | "Here are the rules Claude must follow" |
| **Walking Skeleton** | 0:03-0:08 | Failing E2E test, base structure | First wow: Claude understands outside-in |
| **Feature 1** | 0:08-0:20 | Character with TDD + Agility | Show red-green-refactor cycle |
| **Feature 2** | 0:20-0:28 | DiceRoller + Port/Adapter | Wow: Hexagonal emerges |
| **Feature 3** | 0:28-0:33 | Initiative Roll | Quick win, sets up combat order |
| **Feature 4** | 0:33-0:43 | Attack with immutability | Wow: no mutations |
| **Feature 5** | 0:43-0:53 | Combat Round with Attacker Advantage | Core mechanic demo |
| **Feature 6+7** | 0:53-0:58 | Game Loop + Victory | Grand finale: it works! |
| **Q&A** | 0:58-1:00 | Questions | |

---

## Risk Assessment

### Demo Execution Risks

| Risk ID | Risk Description | Probability | Impact | Mitigation Strategy |
|---------|------------------|-------------|--------|---------------------|
| **R-01** | Claude Code goes off methodology | Medium | High | CLAUDE.md with strict rules; manual interruption if needed |
| **R-02** | Time overrun | Medium | Medium | Features 6+7 can be compressed |
| **R-03** | Unexpected bug during live demo | High | Low | Embrace it! Show debugging with AI |
| **R-04** | Audience skepticism | Medium | Medium | Emphasize process over product |
| **R-05** | WSL crash or environment issue | Low | High | Backup: pre-recorded video of critical segments |
| **R-06** | Network connectivity loss | Low | High | Claude Code works offline; pre-auth before demo |
| **R-07** | Projector font too small | Medium | Medium | Set terminal font size to 18pt+ during setup |
| **R-08** | Test failure during demo | Medium | High | This is actually good! Shows tests catch bugs. Fix live. |

### Technical Risks

| Risk ID | Risk Description | Probability | Impact | Mitigation Strategy |
|---------|------------------|-------------|--------|---------------------|
| **T-01** | Mutable state sneaks into domain | Medium | Medium | Code review during refactoring; explicit immutability checks |
| **T-02** | Test doubles not used correctly | Low | High | Port/Adapter pattern enforced in Feature 2 |
| **T-03** | Domain logic leaks into CLI | Medium | Medium | Strict separation: domain returns data, CLI presents |
| **T-04** | Over-engineering under time pressure | Low | Medium | YAGNI principle; minimal implementation |

---

## Stakeholder Analysis

### Stakeholder: Demo Presenter (Alex)

**Role**: Product Owner, Developer Facilitator
**Goals**:
- Deliver compelling 60-minute demonstration
- Hit all "wow moments"
- Manage time effectively
- Handle audience questions confidently

**Needs from Requirements**:
- Clear feature boundaries with time allocations
- Explicit "wow moment" triggers
- Risk mitigation strategies
- Backup plans for common failures

**Engagement Level**: Continuous (active driver of demo)

---

### Stakeholder: Software Crafters Audience

**Role**: Learners, Potential Adopters, Critics
**Goals**:
- Understand how to use Claude Code effectively
- See TDD and Clean Architecture in practice
- Evaluate if methodology is worth adopting
- Ask questions and challenge assumptions

**Needs from Requirements**:
- Visible proof of methodology (tests first, refactoring visible)
- Clear contrast: "what AI does wrong vs. how discipline fixes it"
- Reproducible example they can try themselves
- Honest discussion of trade-offs and limitations

**Engagement Level**: Observational (but critical for success measurement)

---

### Stakeholder: Claude Code (Developer Role)

**Role**: AI Coding Assistant, Developer
**Goals**:
- Follow TDD Outside-In methodology
- Produce clean, tested code
- Respond to refactoring guidance
- Complete features within time constraints

**Needs from Requirements**:
- Precise acceptance criteria in Given-When-Then format
- Clear architecture constraints (immutability, ports/adapters)
- Explicit test-first instructions
- Unambiguous success criteria

**Engagement Level**: Continuous (primary executor)

---

## Acceptance Test Strategy (ATDD)

### Test Pyramid Structure

```
        E2E (1-2 tests)
       /               \
      Integration (0 tests - not needed for demo)
     /                                            \
    Unit Tests (20-25 tests covering all domain logic)
```

**Rationale for No Integration Tests**: In this demo, "integration" is between simple domain objects. Unit tests + E2E provide sufficient coverage without middle layer complexity.

### Test Execution Order (Outside-In TDD)

1. **E2E Test First** (Walking Skeleton):
   ```gherkin
   Given two characters exist
   When they engage in combat
   Then initiative determines attack order
   And combat proceeds until one wins
   ```
   This test **will fail** initially - that's the point!

2. **Drill Down to Units**:
   - Character creation tests (with Agility)
   - Dice rolling tests
   - Initiative roll tests
   - Attack resolution tests
   - Combat round tests (attacker advantage)
   - Game loop tests
   - Victory condition tests

3. **E2E Test Passes**:
   Once all units work, E2E test turns green.

### Test Double Strategy

**Port**: `DiceRoller` interface
**Production Adapter**: `RandomDiceRoller`
**Test Adapter**: `FixedDiceRoller`

**No Mocking Libraries Required**: Test doubles are explicit implementations, not mocks. This demonstrates the Port/Adapter pattern clearly.

---

## Definition of Done

A feature is **Done** when:

- All acceptance criteria have passing tests (Given-When-Then)
- Code follows immutability and Clean Architecture principles
- No setters in domain objects
- Test coverage is 100% for new code
- Code is readable on projector (clear names, no abbreviations)
- Refactoring step completed (if applicable)
- Feature completes within allocated timeline

A **Demo is Done** when:

- All features 1-7 are completed
- E2E test passes
- CLI is playable
- Minimum 4 "wow moments" demonstrated
- Audience understands methodology, not just AI capability
- Q&A session leaves time for questions

---

## Handoff to DESIGN Wave

### Deliverables for solution-architect

This requirements document provides:

1. **Business Context**: Demo objectives, stakeholder goals, success criteria
2. **Combat Rules**: Clarified rules for attacker advantage, initiative, damage
3. **Domain Model**: Ubiquitous language, domain rules, business logic
4. **Feature Specifications**: 7 features with acceptance criteria in Given-When-Then
5. **Non-Functional Requirements**: Performance, quality, architecture constraints
6. **Risk Assessment**: Demo and technical risks with mitigations
7. **Test Strategy**: ATDD approach, test pyramid, test double strategy

### Architectural Constraints to Honor

- **Hexagonal Architecture** (Ports & Adapters)
- **Immutable Domain Models** (no setters)
- **Derived Stats** (Agility computed, not stored)
- **Dependency Injection** (ports injected into domain services)
- **Separation of Concerns** (domain vs. infrastructure vs. CLI)
- **Test-First Design** (architecture emerges from testability needs)

### Open Questions for Architecture Phase

1. **Language/Runtime**: TypeScript/Node.js vs. C#/.NET vs. Python? (Presenter preference)
2. **Test Framework**: Jest vs. Vitest vs. xUnit? (Language-dependent)
3. **CLI Framework**: Commander.js vs. raw args vs. Inquirer? (Simplicity for demo)
4. **Folder Structure**: Exact naming conventions for domain/infrastructure/application layers

### Recommended Next Steps

1. **DESIGN Wave**: solution-architect creates architecture diagrams and technical design
2. **DISTILL Wave**: acceptance-designer converts Given-When-Then into executable tests
3. **DEVELOP Wave**: developer-agent implements features via TDD Outside-In
4. **DELIVER Wave**: final validation, coverage report, demo rehearsal

---

## Appendix A: Wow Moments Reference

### Wow Moment 1: CLAUDE.md in Action (0:03)
**Trigger**: Show CLAUDE.md file at start
**Script**: "Watch how Claude follows these rules. I'm not writing code - I'm enforcing discipline."

### Wow Moment 2: Derived Agility Stat (0:15)
**Trigger**: Character creation with Agility
**Script**: "Agility isn't stored - it's computed from HP + Attack. As you take damage, you get slower!"

### Wow Moment 3: Test Double Emerges Naturally (0:25)
**Trigger**: Encounter untestable randomness in Feature 2
**Script**: "I can't test with random dice. Claude, how do we solve this?"
**Expected**: Claude proposes Port/Adapter pattern
**Payoff**: Hexagonal Architecture emerges from constraint, not upfront design

### Wow Moment 4: Immutability Enforced (0:40)
**Trigger**: Refactoring step in Feature 4
**Script**: "This setter bothers me. How do we make this immutable?"
**Expected**: Claude refactors to return new Character instance
**Payoff**: Audience sees functional programming preventing bugs

### Wow Moment 5: Attacker Advantage in Action (0:50)
**Trigger**: Combat round where attacker kills defender
**Script**: "Watch what happens when Thorin kills Goblin - no counter-attack!"
**Expected**: Goblin dies, no counter-attack happens
**Payoff**: Sequential resolution prevents unfair simultaneous death

### Wow Moment 6: E2E Test Turns Green (0:55)
**Trigger**: After Feature 6 completes
**Script**: "Remember that failing test from minute 3? Let's run it now."
**Expected**: E2E test passes
**Payoff**: TDD Outside-In success - we built exactly what the test specified

### Wow Moment 7: Live Combat Demo (0:56)
**Trigger**: Run CLI with real combat
**Script**: "Let's actually play the game."
**Expected**: Two characters fight, winner announced
**Payoff**: Working software, not just tests

### Wow Moment 8: Coverage Report (closing)
**Trigger**: Show coverage report
**Script**: "100% coverage, zero implementation mocks, clean architecture."
**Expected**: Coverage badge or report showing 100%
**Payoff**: Quality metrics prove rigor, not just vibes

---

## Appendix B: CLAUDE.md Configuration for Demo

**Recommended CLAUDE.md** (to be placed in project root):

```markdown
# Combat Simulator - Demo Development Rules

## Core Methodology
- **ALWAYS use TDD with Outside-In approach**
- Write ONE failing test before any implementation code
- Make the test pass with minimal code (no premature optimization)
- Refactor only when tests are green
- **NO CODE WITHOUT A FAILING TEST FIRST** (zero exceptions)

## Architecture Principles
- **Hexagonal Architecture**: Ports and Adapters pattern
- **Domain objects are immutable Value Objects** (no setters)
- Use factory methods or constructors, never expose setters
- Make illegal states unrepresentable via types
- Separate domain logic from infrastructure
- **Agility is DERIVED** (hp + attackPower), never stored

## Combat Rules
- **Attacker Advantage**: first attacker resolves, defender counter-attacks only if alive
- **Initiative**: rolled once at fight start using Agility + D6
- **Damage**: Attack Power + Die Roll (no caps, no armor)
- HP floors at 0

## Testing Standards
- Test behavior through public API only
- Use explicit test doubles (not mocking libraries)
- No mocking of internal implementation details
- E2E test as walking skeleton - start here first
- FixedDiceRoller injected via constructor

## Code Quality
- Favor immutability in all domain objects
- Small functions, single responsibility
- No comments explaining "what" (code should be self-documenting)
- Comments only for "why" if non-obvious
- Use type system to prevent bugs

## Demo Constraints
- Each feature has allocated time box
- Code must be readable on projector (clear names, no abbreviations)
- Show red-green-refactor cycle explicitly
- Explain architectural decisions as they emerge
```

---

**End of Requirements Specification**

**Document Version**: 2.0
**Status**: Ready for DESIGN Wave Handoff
**Next Agent**: solution-architect
**Estimated Architecture Phase**: 30 minutes
