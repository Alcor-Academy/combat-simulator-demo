# DISCUSS → DESIGN Wave Handoff Package

**From**: product-owner (Riley - Requirements Analyst)
**To**: solution-architect (Architecture & Design Agent)
**Date**: 2026-01-06
**Wave Transition**: DISCUSS → DESIGN

---

## Handoff Summary

### Requirements Gathering Status: ✅ COMPLETE

All requirements gathering activities are complete and validated. The combat simulator demo project is ready for architectural design phase.

**Quality Gate Status**: PASSED
- ✅ Business context documented
- ✅ Stakeholder analysis complete
- ✅ User stories with acceptance criteria defined
- ✅ Domain language established
- ✅ Risk assessment performed
- ✅ Non-functional requirements specified
- ✅ ATDD compliance verified

---

## Deliverables

### Primary Documents

1. **Requirements Specification**
   - **Location**: `docs/requirements/requirements.md`
   - **Content**: Comprehensive requirements document with business context, domain analysis, feature breakdown, NFRs, risk assessment
   - **Status**: Complete and validated

2. **User Stories Catalog**
   - **Location**: `docs/requirements/user-stories.md`
   - **Content**: 5 user stories (US-01 to US-05) with detailed acceptance criteria in Given-When-Then format
   - **Status**: Complete and demo-optimized

3. **Acceptance Criteria Reference**
   - **Location**: `docs/requirements/acceptance-criteria.md`
   - **Content**: 22 testable acceptance criteria with implementation guidance
   - **Status**: Complete and ready for test automation

---

## Key Information for Architecture Phase

### Business Context (Meta-Level)

This is a **live coding demonstration** project, not a traditional product development effort. The requirements are optimized for:

1. **60-minute timeline** (tight time constraints)
2. **Educational value** (demonstrate methodology to Software Crafters audience)
3. **Multiple "wow moments"** (architecture emergence, immutability, TDD success)
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

#### AC-3: Dependency Injection Ready
**Requirement**: All dependencies must be injectable.
**Rationale**: Enable test doubles (FixedDiceRoller) without framework magic.
**Implementation**:
- Constructor injection preferred
- Explicit dependency passing (no service locators or global state)

#### AC-4: Testability First
**Requirement**: Architecture must enable 100% test coverage without mocking internal implementation.
**Rationale**: TDD Outside-In requires testable design.
**Implementation**:
- Domain returns data, doesn't produce side effects (prints, file I/O)
- Randomness abstracted behind port (DiceRoller)
- Clear separation of concerns

#### AC-5: Demo-Friendly Structure
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
- Properties: name (string), hp (number ≥ 0), attackPower (number > 0)
- Methods:
  - `isAlive(): boolean`
  - `receiveDamage(amount: number): Character` (returns new instance)
  - `performAttack(target: Character, diceRoll: number): AttackResult` (or delegate to service)

**AttackResult** (Value Object)
- Properties: attacker (string), defender (string), diceRoll (number), attackPower (number), totalDamage (number), defenderOldHP (number), defenderNewHP (number)

**RoundResult** (Value Object)
- Properties: roundNumber (number), attackerActions (AttackResult[]), updatedCharacters (Character[]), combatStatus (enum: ONGOING | FINISHED)

**CombatResult** (Value Object - Optional Feature 5)
- Properties: winner (string), winnerHP (number), loser (string), totalRounds (number)

#### Domain Services

**AttackResolver** or **CombatService**
- Responsibility: Orchestrate attack resolution (damage calculation + application)
- Dependencies: DiceRoller (port)
- Methods: `resolveAttack(attacker: Character, defender: Character): AttackResult`

**CombatRound**
- Responsibility: Orchestrate one round of combat (both characters attack if alive)
- Dependencies: AttackResolver or CombatService
- Methods: `executeRound(char1: Character, char2: Character, roundNumber: number): RoundResult`

**CombatSimulator** (Use Case - Optional Feature 5)
- Responsibility: Full game loop until victory
- Dependencies: CombatRound
- Methods: `runCombat(char1: Character, char2: Character): CombatResult`

#### Ports (Interfaces)

**DiceRoller** (Port)
- Method: `roll(): number` (returns 1-6)

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
| DR-04 | Dead characters (HP ≤ 0) cannot attack | AttackResolver validation |
| DR-05 | Combat rounds: A attacks B, then B attacks A | CombatRound orchestration |
| DR-06 | Combat ends when one character reaches 0 HP | CombatSimulator (Feature 5) |
| DR-07 | All randomness must be injectable | DiceRoller port abstraction |

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
| Feature 1: Character Creation | 0:08-0:23 | 15 min | CRITICAL |
| Feature 2: Dice Rolling | 0:23-0:33 | 10 min | CRITICAL |
| Feature 3: Attack Resolution | 0:33-0:48 | 15 min | CRITICAL |
| Feature 4: Combat Round | 0:48-0:58 | 10 min | CRITICAL |
| Feature 5: Victory Condition | 0:58-1:00 | 2 min | OPTIONAL |
| **Total Development Time** | | **52 min** | **5 min buffer** |

**Architecture Implication**: Design must support incremental development. Each feature builds on previous without requiring refactoring of earlier code.

---

### Risk Assessment for Architecture

| Risk ID | Architectural Consideration | Mitigation |
|---------|----------------------------|------------|
| R-01 | Mutable state sneaks in under time pressure | Make immutability explicit in class design |
| R-02 | Domain logic leaks into CLI layer | Strict layering: domain returns data, CLI presents |
| R-03 | Test doubles not used correctly | Port/Adapter pattern enforced in Feature 2 |
| R-04 | Over-engineering (time waste) | YAGNI - minimal implementation, no speculative features |
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
  ├── domain/          # Business logic (pure, no dependencies)
  │   ├── Character.ts
  │   ├── AttackResult.ts
  │   ├── RoundResult.ts
  │   ├── CombatRound.ts
  │   └── ports/
  │       └── DiceRoller.ts
  ├── infrastructure/  # Adapters (external dependencies)
  │   └── RandomDiceRoller.ts
  ├── application/     # Use cases
  │   └── CombatSimulator.ts
  └── cli/             # Presentation layer
      └── main.ts

  test/
  ├── domain/
  ├── doubles/
  │   └── FixedDiceRoller.ts
  └── e2e/
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

✅ **Technical stack decided** (language, framework, test runner)
✅ **Folder structure defined** (Hexagonal Architecture visible)
✅ **Class diagram created** (showing domain entities, services, ports, adapters)
✅ **Sequence diagrams for key flows** (attack resolution, combat round)
✅ **Dependency injection strategy defined** (how ports are injected)
✅ **Test strategy documented** (unit test structure, E2E approach, test double usage)
✅ **Architecture Decision Records (ADRs)** for key choices (if time allows, optional)

### Quality Gates

- ✅ Architecture supports all 22 acceptance criteria
- ✅ Hexagonal Architecture pattern clearly visible
- ✅ Immutability enforced by design (no setters in class diagrams)
- ✅ All external dependencies behind ports
- ✅ Clear separation of concerns (domain/infrastructure/application/CLI)
- ✅ Architecture can be implemented in 50-minute timeline

---

## Recommended Next Steps for solution-architect

### Phase 1: Technical Stack Decision (5 minutes)
1. Confirm language/runtime with presenter (TypeScript/Node.js recommended)
2. Select test framework (Jest recommended)
3. Select CLI approach (raw args or Commander.js)

### Phase 2: High-Level Architecture (10 minutes)
1. Create Hexagonal Architecture diagram (hexagon with ports/adapters)
2. Define folder structure matching architecture
3. Document dependency flow (CLI → Application → Domain, Infrastructure → Domain Ports)

### Phase 3: Detailed Design (15 minutes)
1. Create class diagram for domain layer (Character, AttackResult, RoundResult, services)
2. Define port interfaces (DiceRoller)
3. Define adapter implementations (RandomDiceRoller, FixedDiceRoller)
4. Create sequence diagram for attack resolution flow
5. Create sequence diagram for combat round flow

### Phase 4: Test Strategy (5 minutes)
1. Document unit test structure (one test file per class)
2. Document E2E test approach (walking skeleton)
3. Document test double strategy (FixedDiceRoller usage)

### Phase 5: Handoff Package for DISTILL Wave (5 minutes)
1. Compile all diagrams and design documents
2. Create DESIGN → DISTILL handoff document
3. Validate architecture against all acceptance criteria

**Total Estimated Time**: 40 minutes

---

## Stakeholder Alignment

### Demo Presenter (Alex)
**Needs from Architecture**:
- Clear visual diagrams for projection
- Architecture that supports "wow moments" (Hexagonal emergence, immutability)
- Confidence that design can be completed in timeline

**Engagement**: Review architecture diagrams before proceeding to DISTILL wave

### Software Crafters Audience
**Needs from Architecture**:
- Visible demonstration of Clean Architecture principles
- Clear separation between domain and infrastructure
- Understandable diagrams (not overly complex)

**Engagement**: Diagrams should be presentation-ready

### Claude Code (Developer)
**Needs from Architecture**:
- Clear class interfaces to implement
- Unambiguous dependency injection patterns
- Test structure guidance

**Engagement**: Architecture artifacts become implementation blueprint

---

## Appendix: Requirements Traceability

All requirements from DISCUSS wave are traceable forward to DESIGN wave:

| Requirement | Design Artifact |
|-------------|-----------------|
| Domain Language | Class diagram with domain terms |
| Immutability Constraint | Class design (no setters, return new instances) |
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

**Handoff Status**: ✅ APPROVED - Ready for DESIGN Wave

**Next Agent**: solution-architect
**Expected DESIGN Completion**: 30-40 minutes
**Next Handoff**: DESIGN → DISTILL Wave (Acceptance Test Creation)

---

**Document Version**: 1.0
**Last Updated**: 2026-01-06
**Approved By**: product-owner (Riley - Requirements Analyst)
