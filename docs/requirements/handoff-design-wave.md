# DISCUSS -> DESIGN Wave Handoff Package

**From**: product-owner (Riley - Requirements Analyst)
**To**: solution-architect (Architecture & Design Agent)
**Date**: 2026-01-07
**Wave Transition**: DISCUSS -> DESIGN

---

## Handoff Summary

### Requirements Gathering Status: COMPLETE

All requirements gathering activities are complete and validated. The combat simulator demo project is ready for architectural design phase.

**Quality Gate Status**: PASSED
- Business context documented
- Stakeholder analysis complete
- User stories with acceptance criteria defined (7 stories, 27 ACs)
- Domain language established (including new combat rules)
- Risk assessment performed
- Non-functional requirements specified
- ATDD compliance verified

---

## Combat Rules Summary (CRITICAL)

These clarified rules govern all combat mechanics and must be reflected in architecture:

### Death Rule: Attacker Advantage
- First attacker resolves their attack fully
- Defender counter-attacks **only if they survive** (HP > 0)
- If attacker kills defender, round ends immediately - no counter-attack
- Ties are **impossible** due to sequential resolution

### Attack Order: Initiative Roll
- Initiative is rolled **once at fight start** (not every round)
- Each character rolls D6 + Agility (Attack Power + HP)
- Higher total wins initiative, attacks first **every round** for entire combat
- Winner = "attacker", Loser = "defender"

### Derived Stat: Agility
- **Agility = Attack Power + Current HP**
- Derived stat (computed property), not stored
- Represents fatigue: as you take damage, HP drops, so Agility drops
- Used for initiative calculation at fight start

### Dice Boundaries
- All dice return values in **[1, 6] inclusive**
- Never returns 0, never returns 7
- Same DiceRoller port for combat AND character stat generation

### Damage Calculation
- **Total Damage = Attack Power + Die Roll**
- No caps, no floors, no armor, no critical hits
- HP cannot go below 0 (floor at 0)

---

## Deliverables

### Primary Documents

1. **Requirements Specification**
   - **Location**: `docs/requirements/requirements.md`
   - **Content**: Comprehensive requirements document with business context, combat rules, domain analysis, feature breakdown, NFRs, risk assessment
   - **Status**: Complete and validated

2. **User Stories Catalog**
   - **Location**: `docs/requirements/user-stories.md`
   - **Content**: 7 user stories (US-01 to US-07) with detailed acceptance criteria in Given-When-Then format
   - **Status**: Complete and demo-optimized

3. **Acceptance Criteria Reference**
   - **Location**: `docs/requirements/acceptance-criteria.md`
   - **Content**: 27 testable acceptance criteria with implementation guidance
   - **Status**: Complete and ready for test automation

---

## Key Information for Architecture Phase

### Business Context (Meta-Level)

This is a **live coding demonstration** project, not a traditional product development effort. The requirements are optimized for:

1. **60-minute timeline** (tight time constraints)
2. **Educational value** (demonstrate methodology to Software Crafters audience)
3. **Multiple "wow moments"** (architecture emergence, immutability, attacker advantage)
4. **Production-ready quality** (100% test coverage, Clean Architecture)

**Critical**: Architecture must support rapid development while maintaining quality standards.

---

### Architectural Constraints (Non-Negotiable)

#### AC-1: Hexagonal Architecture (Ports & Adapters)
**Requirement**: System must demonstrate Hexagonal Architecture pattern clearly.
**Rationale**: Educational goal - show Clean Architecture in practice.
**Implementation**:
- Domain logic isolated from infrastructure
- Ports (interfaces) for external dependencies
- Adapters (implementations) for production and testing

#### AC-2: Immutable Domain Models
**Requirement**: All domain objects must be immutable value objects.
**Rationale**: Demonstrate functional programming principles and bug prevention.
**Implementation**:
- No public setters
- State changes return new instances
- Constructor or factory methods only

#### AC-3: Derived Stats (Agility)
**Requirement**: Agility must be computed, not stored.
**Rationale**: Demonstrates derived properties pattern, keeps HP change logic simple.
**Implementation**:
- `get agility() { return this.hp + this.attackPower }`
- Never a field in Character

#### AC-4: Dependency Injection Ready
**Requirement**: All dependencies must be injectable.
**Rationale**: Enable test doubles (FixedDiceRoller) without framework magic.
**Implementation**:
- Constructor injection preferred
- Explicit dependency passing (no service locators or global state)

#### AC-5: Testability First
**Requirement**: Architecture must enable 100% test coverage without mocking internal implementation.
**Rationale**: TDD Outside-In requires testable design.
**Implementation**:
- Domain returns data, doesn't produce side effects (prints, file I/O)
- Randomness abstracted behind port (DiceRoller)
- Clear separation of concerns

#### AC-6: Demo-Friendly Structure
**Requirement**: Code must be projector-readable during live demo.
**Rationale**: Audience must understand architecture visually.
**Implementation**:
- Clear folder structure (domain/, infrastructure/, application/, cli/)
- Descriptive class and method names (no abbreviations)
- Minimal nesting depth

---

### Domain Model

#### Core Entities and Value Objects

**Character** (Value Object - Immutable)
- Properties: name (string), hp (number >= 0), attackPower (number > 0)
- Derived: `agility` (computed: hp + attackPower)
- Methods:
  - `isAlive(): boolean`
  - `receiveDamage(amount: number): Character` (returns new instance)
  - Factory method using DiceRoller for creation

**InitiativeResult** (Value Object)
- Properties: attacker (Character), defender (Character), attackerRoll (number), defenderRoll (number)
- Purpose: Stores combat order for entire fight

**AttackResult** (Value Object)
- Properties: attacker (string), defender (string), diceRoll (number), attackPower (number), totalDamage (number), defenderOldHP (number), defenderNewHP (number)

**RoundResult** (Value Object)
- Properties: roundNumber (number), attacker (Character), defender (Character), attackerRoll (number), defenderRoll (number), attackerDamage (number), defenderDamage (number), attackerHPAfter (number), defenderHPAfter (number), combatEnded (boolean), winner (Character | null)

**CombatResult** (Value Object)
- Properties: winner (Character), loser (Character), totalRounds (number), rounds (RoundResult[])

#### Domain Services

**InitiativeResolver**
- Responsibility: Roll initiative and determine attacker/defender
- Dependencies: DiceRoller (port)
- Methods: `rollInitiative(char1: Character, char2: Character): InitiativeResult`

**AttackResolver** or **CombatService**
- Responsibility: Orchestrate attack resolution (damage calculation + application)
- Dependencies: DiceRoller (port)
- Methods: `resolveAttack(attacker: Character, defender: Character): AttackResult`

**CombatRound**
- Responsibility: Orchestrate one round of combat (attacker advantage enforcement)
- Dependencies: AttackResolver
- Methods: `executeRound(attacker: Character, defender: Character, roundNumber: number): RoundResult`
- Key Logic: Defender only counter-attacks if HP > 0 after attacker's attack

**CombatSimulator** (Use Case)
- Responsibility: Full game loop until victory
- Dependencies: InitiativeResolver, CombatRound
- Methods: `runCombat(char1: Character, char2: Character): CombatResult`

#### Ports (Interfaces)

**DiceRoller** (Port)
- Method: `roll(): number` (returns [1, 6])

#### Adapters (Implementations)

**RandomDiceRoller** (Adapter - Production)
- Implements: DiceRoller
- Implementation: Uses `Math.random()` or equivalent

**FixedDiceRoller** (Adapter - Test Double)
- Implements: DiceRoller
- Implementation: Returns pre-configured values (single value or sequence)

---

### Domain Rules Summary

| Rule ID | Description | Enforcement |
|---------|-------------|-------------|
| DR-01 | Characters are immutable value objects | Type system + no setters |
| DR-02 | Damage = Attack Power + Dice Roll (1d6) | Domain logic |
| DR-03 | HP cannot go below 0 | Character.receiveDamage() logic |
| DR-04 | Initiative rolled once at fight start | CombatSimulator calls InitiativeResolver once |
| DR-05 | Initiative = Agility + D6 | InitiativeResolver calculation |
| DR-06 | Attacker advantage: defender only counter-attacks if alive | CombatRound orchestration |
| DR-07 | Combat ends immediately when character reaches 0 HP | CombatRound / CombatSimulator |
| DR-08 | Agility = Attack Power + HP (derived) | Character computed property |
| DR-09 | Dice boundaries: [1, 6] inclusive | DiceRoller contract |
| DR-10 | All randomness must be injectable | DiceRoller port abstraction |

---

### Non-Functional Requirements Summary

| NFR ID | Requirement | Priority | Validation Method |
|--------|-------------|----------|-------------------|
| NFR-1 | Combat round < 10ms | Medium | Qualitative (demo responsiveness) |
| NFR-2 | 100% test coverage (domain) | Critical | Coverage report |
| NFR-3 | Projector-readable code | Critical | Font size, clear naming |
| NFR-4 | Hexagonal Architecture visible | Critical | Code review, folder structure |
| NFR-5 | Immutability enforced | Critical | Code review, no setters |
| NFR-6 | Complete in 60 minutes | Critical | Timed rehearsal |

---

### Timeline Constraints

| Feature | Timeline | Duration | Criticality |
|---------|----------|----------|-------------|
| Feature 1: Character Creation | 0:08-0:20 | 15 min | CRITICAL |
| Feature 2: Dice Rolling | 0:20-0:28 | 10 min | CRITICAL |
| Feature 3: Initiative Roll | 0:28-0:33 | 5 min | CRITICAL |
| Feature 4: Attack Resolution | 0:33-0:43 | 15 min | CRITICAL |
| Feature 5: Combat Round | 0:43-0:53 | 15 min | CRITICAL |
| Feature 6+7: Game Loop + Victory | 0:53-0:58 | 10 min | CRITICAL |
| **Total Development Time** | | **70 min** | **5 min buffer built into features** |

**Architecture Implication**: Design must support incremental development. Each feature builds on previous without requiring refactoring of earlier code.

---

### Risk Assessment for Architecture

| Risk ID | Architectural Consideration | Mitigation |
|---------|----------------------------|------------|
| R-01 | Mutable state sneaks in under time pressure | Make immutability explicit in class design |
| R-02 | Domain logic leaks into CLI layer | Strict layering: domain returns data, CLI presents |
| R-03 | Test doubles not used correctly | Port/Adapter pattern enforced in Feature 2 |
| R-04 | Over-engineering (time waste) | YAGNI - minimal implementation, no speculative features |
| R-05 | Attacker advantage not enforced | CombatRound must check defender.isAlive() before counter-attack |
| R-06 | Initiative re-rolled each round | InitiativeResult stored at combat start, reused each round |
| T-01 | Coupling between domain and infrastructure | Hexagonal Architecture with explicit ports |

---

## Open Questions for Architecture Phase

### Technical Stack (Needs Decision)

**Question 1**: Which language/runtime?
- **Options**: TypeScript/Node.js, C#/.NET, Python, Java
- **Recommendation**: TypeScript/Node.js (presenter familiarity, demo speed)
- **Decision Authority**: Demo presenter (Alex)

**Question 2**: Which test framework?
- **Options**: Jest, Vitest, xUnit, pytest (depends on language)
- **Recommendation**: Jest (if TypeScript) - mature, fast, good coverage reporting
- **Decision Authority**: solution-architect

**Question 3**: CLI framework?
- **Options**:
  - Raw command-line arguments (simplest)
  - Commander.js / Yargs (if Node.js)
  - Inquirer.js (interactive prompts)
- **Recommendation**: Raw args or Commander.js - keep it minimal
- **Decision Authority**: solution-architect

### Architectural Details (Needs Design)

**Question 4**: Exact folder structure?
- **Guideline**: Must visibly demonstrate Hexagonal Architecture
- **Suggestion**:
  ```
  src/
  +-- domain/          # Business logic (pure, no dependencies)
  |   +-- Character.ts
  |   +-- AttackResult.ts
  |   +-- RoundResult.ts
  |   +-- CombatResult.ts
  |   +-- InitiativeResult.ts
  |   +-- CombatRound.ts
  |   +-- ports/
  |       +-- DiceRoller.ts
  +-- infrastructure/  # Adapters (external dependencies)
  |   +-- RandomDiceRoller.ts
  +-- application/     # Use cases
  |   +-- CombatSimulator.ts
  +-- cli/             # Presentation layer
      +-- main.ts

  test/
  +-- domain/
  |   +-- Character.test.ts
  |   +-- AttackResult.test.ts
  |   +-- InitiativeResult.test.ts
  |   +-- CombatRound.test.ts
  +-- application/
  |   +-- CombatSimulator.test.ts
  +-- doubles/
  |   +-- FixedDiceRoller.ts
  +-- e2e/
      +-- CombatSimulator.e2e.test.ts
  ```
- **Decision Authority**: solution-architect

**Question 5**: Dependency injection mechanism?
- **Options**:
  - Manual DI (pass dependencies in constructors)
  - DI Container (InversifyJS, tsyringe, etc.)
- **Recommendation**: Manual DI - simpler for demo, no magic
- **Decision Authority**: solution-architect

**Question 6**: Error handling strategy?
- **Options**:
  - Exceptions
  - Result types (Either/Result monad)
  - Nullable returns
- **Recommendation**: Keep it simple - nullable returns or exceptions (language-dependent)
- **Decision Authority**: solution-architect

---

## Success Criteria for DESIGN Wave

### Architecture Design is Complete When:

- **Technical stack decided** (language, framework, test runner)
- **Folder structure defined** (Hexagonal Architecture visible)
- **Class diagram created** (showing domain entities, services, ports, adapters)
- **Sequence diagrams for key flows** (initiative roll, attack resolution, combat round with attacker advantage)
- **Dependency injection strategy defined** (how ports are injected)
- **Test strategy documented** (unit test structure, E2E approach, test double usage)
- **Architecture Decision Records (ADRs)** for key choices (if time allows, optional)

### Quality Gates

- Architecture supports all 27 acceptance criteria
- Hexagonal Architecture pattern clearly visible
- Immutability enforced by design (no setters in class diagrams)
- Derived Agility in Character (computed property, not field)
- Attacker advantage rule supported by CombatRound design
- Initiative rolled once, stored in InitiativeResult
- All external dependencies behind ports
- Clear separation of concerns (domain/infrastructure/application/CLI)
- Architecture can be implemented in 50-minute timeline

---

## Recommended Next Steps for solution-architect

### Phase 1: Technical Stack Decision (5 minutes)
1. Confirm language/runtime with presenter (TypeScript/Node.js recommended)
2. Select test framework (Jest recommended)
3. Select CLI approach (raw args or Commander.js)

### Phase 2: High-Level Architecture (10 minutes)
1. Create Hexagonal Architecture diagram (hexagon with ports/adapters)
2. Define folder structure matching architecture
3. Document dependency flow (CLI -> Application -> Domain, Infrastructure -> Domain Ports)

### Phase 3: Detailed Design (15 minutes)
1. Create class diagram for domain layer (Character with derived agility, InitiativeResult, AttackResult, RoundResult, CombatResult, services)
2. Define port interfaces (DiceRoller)
3. Define adapter implementations (RandomDiceRoller, FixedDiceRoller)
4. Create sequence diagram for initiative roll
5. Create sequence diagram for combat round (showing attacker advantage logic)
6. Create sequence diagram for full combat loop

### Phase 4: Test Strategy (5 minutes)
1. Document unit test structure (one test file per class)
2. Document E2E test approach (walking skeleton)
3. Document test double strategy (FixedDiceRoller usage)

### Phase 5: Handoff Package for DISTILL Wave (5 minutes)
1. Compile all diagrams and design documents
2. Create DESIGN -> DISTILL handoff document
3. Validate architecture against all acceptance criteria

**Total Estimated Time**: 40 minutes

---

## Stakeholder Alignment

### Demo Presenter (Alex)
**Needs from Architecture**:
- Clear visual diagrams for projection
- Architecture that supports "wow moments" (Hexagonal emergence, immutability, attacker advantage)
- Confidence that design can be completed in timeline

**Engagement**: Review architecture diagrams before proceeding to DISTILL wave

### Software Crafters Audience
**Needs from Architecture**:
- Visible demonstration of Clean Architecture principles
- Clear separation between domain and infrastructure
- Understandable diagrams (not overly complex)
- Attacker advantage rule visible in design

**Engagement**: Diagrams should be presentation-ready

### Claude Code (Developer)
**Needs from Architecture**:
- Clear class interfaces to implement
- Unambiguous dependency injection patterns
- Test structure guidance
- Combat rules clear in design

**Engagement**: Architecture artifacts become implementation blueprint

---

## Appendix: Requirements Traceability

All requirements from DISCUSS wave are traceable forward to DESIGN wave:

| Requirement | Design Artifact |
|-------------|-----------------|
| Domain Language | Class diagram with domain terms |
| Immutability Constraint | Class design (no setters, return new instances) |
| Derived Agility | Character class with computed property |
| Initiative System | InitiativeResult value object, InitiativeResolver service |
| Attacker Advantage | CombatRound orchestration logic |
| Hexagonal Architecture | Architecture diagram, folder structure |
| Test Doubles | DiceRoller port + FixedDiceRoller adapter |
| Acceptance Criteria | Validated against class responsibilities |

---

## Contact Information

**Questions During DESIGN Phase**:
- **Requirements Clarification**: Contact product-owner (Riley)
- **Technical Stack Decisions**: Demo presenter (Alex) approval needed
- **Architecture Review**: product-owner available for validation

---

**Handoff Status**: APPROVED - Ready for DESIGN Wave

**Next Agent**: solution-architect
**Expected DESIGN Completion**: 30-40 minutes
**Next Handoff**: DESIGN -> DISTILL Wave (Acceptance Test Creation)

---

**Document Version**: 2.0
**Last Updated**: 2026-01-07
**Approved By**: product-owner (Riley - Requirements Analyst)
