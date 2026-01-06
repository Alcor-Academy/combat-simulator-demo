# Combat Simulator Demo - Requirements Specification

**Project**: Combat Simulator CLI - Software Crafters Live Coding Demo
**Wave**: DISCUSS (Requirements Gathering)
**Date**: 2026-01-06
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

**Key Message**: *"AI amplifies your practices. Discipline → excellent code. No discipline → fast garbage."*

### Success Criteria

**Functional Success:**
- ✅ Playable combat simulator with two characters fighting to death
- ✅ All features implemented via TDD (red-green-refactor cycle visible)
- ✅ Clean Architecture patterns emerge naturally
- ✅ 100% test coverage achieved

**Demonstration Success:**
- ✅ Completed within 60-minute timeline
- ✅ Minimum 4 "wow moments" delivered (documented below)
- ✅ Audience understands methodology, not just the AI tool
- ✅ Code quality demonstrates professional software craftsmanship

### Business Value

**Primary Value**: Educational demonstration proving that AI coding assistants, when guided by disciplined practices, produce maintainable, tested, architecturally sound code.

**Secondary Value**: Reusable reference implementation for Software Crafters adopting AI-assisted development.

---

## Domain Analysis

### Ubiquitous Language

**Core Domain Terms:**

| Term | Definition | Usage Context |
|------|------------|---------------|
| **Character** | A combatant with name, hit points (HP), and attack power | Value Object (immutable) |
| **Hit Points (HP)** | Health of a character; 0 HP = death | Integer ≥ 0 |
| **Attack Power** | Base damage a character can inflict | Integer > 0 |
| **Dice Roll** | Random number generation simulating D&D dice | 1-6 for d6 dice |
| **Damage** | Total harm inflicted = Attack Power + Dice Roll | Calculated value |
| **Combat Round** | One turn where both combatants attack each other | Orchestration unit |
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

**DR-02: Combat Mechanics**
- Damage = Attacker's Attack Power + Dice Roll (1d6)
- HP reduction = Current HP - Damage
- Dead characters (HP ≤ 0) cannot attack

**DR-03: Victory Determination**
- Combat ends when one character reaches HP ≤ 0
- Surviving character is declared winner
- No draws (simplified ruleset)

**DR-04: Turn Order**
- Fixed alternating turns (no initiative system)
- Both characters attack once per round (if alive)
- Order: Character A attacks B, then B attacks A

**DR-05: Testability Requirement**
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
Then combat proceeds in rounds until one dies
And the winner is announced
And all combat actions are logged
```

---

### Feature 1: Character Creation (Timeline: 0:08-0:23, 15 minutes)

#### Business Value
Foundation for all combat mechanics. Demonstrates value object immutability and type-driven design.

#### User Story
```
As a player
I want to create a character with name, HP, and attack power
So that I can participate in combat simulations
```

#### Acceptance Criteria

**AC-1.1: Character Creation with Valid Attributes**
```gherkin
Given no character exists
When I create a character named "Thorin" with 20 HP and 5 Attack Power
Then the character's name is "Thorin"
And the character's HP is 20
And the character's Attack Power is 5
```

**AC-1.2: Character Liveness Check**
```gherkin
Given a character with 15 HP
When I check if the character is alive
Then the result is true

Given a character with 0 HP
When I check if the character is alive
Then the result is false

Given a character with -5 HP
When I check if the character is alive
Then the result is false
```

**AC-1.3: Immutability Enforcement**
```gherkin
Given a character "Legolas" with 18 HP
When the character receives 5 damage
Then a new character instance is returned
And the new character has 13 HP
And the original character instance remains unchanged with 18 HP
```

#### Technical Outcomes
- `Character` class as immutable value object
- Factory method or builder for creation
- `isAlive(): boolean` method
- `receiveDamage(amount: number): Character` method (returns new instance)
- Zero setters in public API
- 3-4 unit tests

#### Wow Moment
**"Value Object Immutability"** - Show how `receiveDamage()` returns a new `Character` instance instead of mutating state. Audience sees functional programming principles in action.

#### Risks & Mitigations
- **Risk**: Claude suggests mutable design with setters
- **Mitigation**: Explicitly guide toward immutable value object pattern

---

### Feature 2: Dice Rolling System (Timeline: 0:23-0:33, 10 minutes)

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

**AC-2.1: Random Dice Roll**
```gherkin
Given a 6-sided dice roller
When the dice is rolled
Then the result is between 1 and 6 inclusive
```

**AC-2.2: Deterministic Test Double**
```gherkin
Given a fixed dice roller configured to return 4
When the dice is rolled
Then the result is always 4

Given a fixed dice roller configured to return [3, 5, 2]
When the dice is rolled 3 times
Then the results are 3, 5, and 2 in sequence
```

**AC-2.3: Port/Adapter Contract**
```gherkin
Given a DiceRoller port interface
Then RandomDiceRoller implements the port for production use
And FixedDiceRoller implements the port for testing
And both adapters are interchangeable via dependency injection
```

#### Technical Outcomes
- `DiceRoller` interface (Port)
- `RandomDiceRoller` class (Adapter for production)
- `FixedDiceRoller` class (Test Double)
- Dependency injection ready
- 2-3 unit tests

#### Wow Moment
**"Hexagonal Architecture Emerges Naturally"** - Audience sees Port/Adapter pattern applied to something simple (dice). Demonstrates how architecture emerges from design constraints (testability).

#### Risks & Mitigations
- **Risk**: Claude uses `Math.random()` directly in domain logic
- **Mitigation**: Emphasize testability requirement, ask "How do we test this?"

---

### Feature 3: Attack Resolution (Timeline: 0:33-0:48, 15 minutes)

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

**AC-3.1: Damage Calculation**
```gherkin
Given an attacker with 5 Attack Power
And a dice roll of 3
When the attack is resolved
Then the total damage is 8 (5 + 3)
```

**AC-3.2: Damage Application**
```gherkin
Given a defender with 20 HP
And an incoming attack dealing 8 damage
When the damage is applied
Then the defender's new HP is 12

Given a defender with 5 HP
And an incoming attack dealing 8 damage
When the damage is applied
Then the defender's new HP is 0 (cannot go below zero)
```

**AC-3.3: Attack Result Structure**
```gherkin
Given an attack from "Thorin" to "Goblin"
And the dice roll is 4
And Thorin has 5 Attack Power
When the attack is resolved
Then the attack result contains:
  | Field          | Value     |
  | attacker       | "Thorin"  |
  | defender       | "Goblin"  |
  | diceRoll       | 4         |
  | attackPower    | 5         |
  | totalDamage    | 9         |
  | defenderNewHP  | <updated> |
```

**AC-3.4: Dead Characters Cannot Attack**
```gherkin
Given a character with 0 HP (dead)
When attempting to perform an attack
Then the attack fails
And an appropriate message is returned (e.g., "Dead characters cannot attack")
```

#### Technical Outcomes
- `AttackResult` value object
- `AttackResolver` or `CombatService` domain service
- `Character.receiveDamage()` returns new instance
- 4-5 unit tests

#### Wow Moment
**"Immutability in Practice"** - Character state updates return new instances. Audience sees how immutability prevents bugs and makes reasoning easier.

#### Risks & Mitigations
- **Risk**: Mutable state sneaks in under time pressure
- **Mitigation**: Refactoring step explicitly enforces immutability

---

### Feature 4: Combat Round Orchestration (Timeline: 0:48-0:58, 10 minutes)

#### Business Value
Completes the walking skeleton. Full E2E functionality demonstrating TDD success.

#### User Story
```
As a player
I want to execute a combat round where both characters attack each other
So that I can see the progression of battle and determine the winner
```

#### Acceptance Criteria

**AC-4.1: Full Combat Round**
```gherkin
Given "Thorin" with 20 HP and 5 Attack Power
And "Goblin" with 10 HP and 3 Attack Power
And dice rolls are [4, 2] (for Thorin's attack, then Goblin's attack)
When a combat round is executed
Then Thorin deals 9 damage (5 + 4) to Goblin
And Goblin deals 5 damage (3 + 2) to Thorin
And Goblin's HP becomes 1
And Thorin's HP becomes 15
And both characters' new states are returned
```

**AC-4.2: Dead Character Cannot Attack**
```gherkin
Given "Thorin" with 10 HP and 5 Attack Power
And "Goblin" with 0 HP and 3 Attack Power (already dead)
And dice roll is 4
When a combat round is executed
Then only Thorin attacks
And Goblin does not attack (is dead)
And the round result indicates Goblin could not attack
```

**AC-4.3: Round Result Output**
```gherkin
Given a combat round is executed
Then the round result contains:
  - Attacker 1 action (attack details)
  - Attacker 2 action (attack details or "cannot attack")
  - Updated character states
  - Round number
  - Combat status (ongoing or finished)
```

**AC-4.4: Combat Log (Non-Print Output)**
```gherkin
Given a combat round is executed
Then the results are returned as structured data (not console prints)
And the data includes all attacks, damage, and state changes
And the output can be consumed by CLI presenter or test assertions
```

#### Technical Outcomes
- `CombatRound` orchestrator class
- `RoundResult` or `CombatLog` value object
- Walking skeleton CLI functional (main.ts)
- E2E test passing
- 3-4 unit tests + 1 E2E test

#### Wow Moment
**"It Works End-to-End!"** - Run the CLI, see a full combat. Audience witnesses that rigorous TDD produces working software, not just tests.

#### Risks & Mitigations
- **Risk**: Time pressure leads to `console.log` in domain logic
- **Mitigation**: Emphasize separation of concerns - domain returns data, CLI handles presentation

---

### Feature 5: Victory Condition (Timeline: 0:58-1:00, 2 minutes buffer/bonus)

#### Business Value
Completes the game loop. Demonstrates finishing touches under time constraints.

#### User Story
```
As a player
I want to know when combat ends and who won
So that I can see the final outcome
```

#### Acceptance Criteria

**AC-5.1: Victory Detection**
```gherkin
Given a combat in progress
When one character reaches 0 HP
Then the combat ends
And the other character is declared the winner
```

**AC-5.2: Combat Result Structure**
```gherkin
Given combat has ended
Then the combat result contains:
  - Winner name
  - Winner's remaining HP
  - Loser name
  - Total rounds fought
```

#### Technical Outcomes
- `CombatResult` value object
- `CombatSimulator` use case with game loop
- Victory condition enforcement
- 1-2 tests

#### Wow Moment
**"Complete Game Logic"** - If time allows, show the full game loop with victory announcement.

#### Risks & Mitigations
- **Risk**: Running out of time
- **Mitigation**: This feature is optional buffer. Core demo succeeds without it.

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
**Requirement**: All features must be completable within 60-minute window with 5-minute buffer.
**Rationale**: Conference session time constraint.
**Validation**: Timed rehearsal.

---

## Risk Assessment

### Demo Execution Risks

| Risk ID | Risk Description | Probability | Impact | Mitigation Strategy |
|---------|------------------|-------------|--------|---------------------|
| **R-01** | Claude Code goes off methodology | Medium | High | CLAUDE.md with strict rules; manual interruption if needed |
| **R-02** | Time overrun | Medium | Medium | Feature 5 is sacrificial buffer; rehearse timing |
| **R-03** | Unexpected bug during live demo | High | Low | Embrace it! Show debugging with AI as bonus content |
| **R-04** | Audience skepticism | Medium | Medium | Emphasize process over product; show tests first, not code first |
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
    Unit Tests (15-20 tests covering all domain logic)
```

**Rationale for No Integration Tests**: In this demo, "integration" is between simple domain objects. Unit tests + E2E provide sufficient coverage without middle layer complexity.

### Test Execution Order (Outside-In TDD)

1. **E2E Test First** (Walking Skeleton):
   ```gherkin
   Given two characters exist
   When they engage in combat
   Then combat proceeds until one wins
   ```
   This test **will fail** initially - that's the point!

2. **Drill Down to Units**:
   - Character creation tests
   - Dice rolling tests
   - Attack resolution tests
   - Combat round tests

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

- ✅ All acceptance criteria have passing tests (Given-When-Then)
- ✅ Code follows immutability and Clean Architecture principles
- ✅ No setters in domain objects
- ✅ Test coverage is 100% for new code
- ✅ Code is readable on projector (clear names, no abbreviations)
- ✅ Refactoring step completed (if applicable)
- ✅ Feature completes within allocated timeline

A **Demo is Done** when:

- ✅ All features 1-4 are completed (Feature 5 is optional)
- ✅ E2E test passes
- ✅ CLI is playable
- ✅ Minimum 4 "wow moments" demonstrated
- ✅ Audience understands methodology, not just AI capability
- ✅ Q&A session leaves time for questions

---

## Handoff to DESIGN Wave

### Deliverables for solution-architect

This requirements document provides:

1. **Business Context**: Demo objectives, stakeholder goals, success criteria
2. **Domain Model**: Ubiquitous language, domain rules, business logic
3. **Feature Specifications**: 5 features with acceptance criteria in Given-When-Then
4. **Non-Functional Requirements**: Performance, quality, architecture constraints
5. **Risk Assessment**: Demo and technical risks with mitigations
6. **Test Strategy**: ATDD approach, test pyramid, test double strategy

### Architectural Constraints to Honor

- **Hexagonal Architecture** (Ports & Adapters)
- **Immutable Domain Models** (no setters)
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

### Wow Moment 2: Test Double Emerges Naturally (0:25)
**Trigger**: Encounter untestable randomness in Feature 2
**Script**: "I can't test with random dice. Claude, how do we solve this?"
**Expected**: Claude proposes Port/Adapter pattern
**Payoff**: Hexagonal Architecture emerges from constraint, not upfront design

### Wow Moment 3: Immutability Enforced (0:40)
**Trigger**: Refactoring step in Feature 3
**Script**: "This setter bothers me. How do we make this immutable?"
**Expected**: Claude refactors to return new Character instance
**Payoff**: Audience sees functional programming preventing bugs

### Wow Moment 4: E2E Test Turns Green (0:55)
**Trigger**: After Feature 4 completes
**Script**: "Remember that failing test from minute 3? Let's run it now."
**Expected**: E2E test passes
**Payoff**: TDD Outside-In success - we built exactly what the test specified

### Wow Moment 5: Live Combat Demo (0:56)
**Trigger**: Run CLI with real combat
**Script**: "Let's actually play the game."
**Expected**: Two characters fight, winner announced
**Payoff**: Working software, not just tests

### Wow Moment 6: Coverage Report (closing)
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

## Testing Standards
- Test behavior through public API only
- Use explicit test doubles (not mocking libraries)
- No mocking of internal implementation details
- E2E test as walking skeleton - start here first

## Code Quality
- Favor immutability in all domain objects
- Small functions, single responsibility
- No comments explaining "what" (code should be self-documenting)
- Comments only for "why" if non-obvious
- Use type system to prevent bugs

## Demo Constraints
- Each feature has 10-15 minute time box
- Code must be readable on projector (clear names, no abbreviations)
- Show red-green-refactor cycle explicitly
- Explain architectural decisions as they emerge
```

---

**End of Requirements Specification**

**Document Version**: 1.0
**Status**: Ready for DESIGN Wave Handoff
**Next Agent**: solution-architect
**Estimated Architecture Phase**: 30 minutes
