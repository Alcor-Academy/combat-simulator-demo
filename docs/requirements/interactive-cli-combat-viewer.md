# Requirements Specification: Interactive CLI Combat Viewer

**Project**: Combat Simulator Demo
**Feature**: Interactive CLI Combat Viewer
**Wave**: DISCUSS (Requirements Gathering and Analysis)
**Date**: 2026-01-09
**Version**: 1.0
**Status**: Ready for DESIGN Wave Handoff

---

## 1. Executive Summary

### 1.1 Feature Overview

The Interactive CLI Combat Viewer transforms the existing combat simulator from a purely programmatic system into an engaging, user-facing command-line application. Users will interactively create two characters and watch them battle in turn-based combat, displayed with visual enhancements (colors, emoji) and carefully paced output for optimal comprehension.

### 1.2 Business Value

**Primary Value**:
- Demonstrates practical application of hexagonal architecture principles
- Showcases clean separation between domain logic and presentation layer
- Provides tangible, engaging demonstration of TDD-developed combat system

**User Impact**:
- Transforms abstract combat system into interactive, entertaining experience
- Provides clear visual feedback on combat mechanics
- Educational tool for understanding turn-based combat logic

**Stakeholder Value**:
- **End Users** (developers, students): Engaging way to see combat system in action
- **Software Crafters/Educators**: Teaching tool for hexagonal architecture and ATDD
- **QA/Testers**: Testable CLI adapter demonstrating test strategy for interactive applications
- **Project Contributors**: Foundation for future enhancements (config files, replay, logging)

### 1.3 Scope

**In Scope**:
- Interactive character creation via sequential prompts
- Real-time combat visualization with emoji and colors
- Configurable pacing with user-controlled skip capability
- Comprehensive combat event logging (initiative, attacks, HP changes, victory)
- Input validation with clear error messages

**Out of Scope**:
- Multi-combat sessions (single run executes one combat)
- Character persistence/save system
- Graphical user interface
- Network/multiplayer functionality
- Character class system or special abilities
- Accessibility features for screen readers (deferred to future enhancement - documented in NFR-06)

---

## 2. Technical Context

### 2.1 Existing System Architecture

**Architecture Pattern**: Hexagonal (Ports & Adapters)

**Existing Layers**:

1. **Domain Layer** (Core Business Logic):
   - `Character` (name, hp, attack_power, agility)
   - `AttackResult`, `RoundResult`, `CombatResult`, `InitiativeResult`
   - Domain Services: `InitiativeResolver`, `AttackResolver`, `CombatRound`

2. **Application Layer** (Use Cases):
   - `CombatSimulator` - orchestrates complete combat from initiative to victory

3. **Infrastructure Layer** (External Adapters):
   - `RandomDiceRoller` - implements `DiceRoller` port with `random.randint(1, 6)`

**Test Coverage**:
- 9/9 E2E acceptance tests PASSING (Gherkin scenarios)
- 34/34 unit tests PASSING
- Domain immutability validated
- Business rules enforced (attacker advantage, initiative tie-breaker, dead character rejection)

### 2.2 New Layer Integration

**CLI Presentation Layer** (Infrastructure - User Interface Adapter):

```
┌─────────────────────────────────────┐
│   CLI Adapter (NEW)                 │
│   - CharacterCreator                │
│   - CombatVisualizer                │
│   - CLI Entry Point                 │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Application Layer                 │
│   - CombatSimulator                 │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Domain Layer                      │
│   - Character, Services, Models     │
└─────────────────────────────────────┘
```

**Dependency Direction**: CLI → Application → Domain (dependencies point inward)

**Technology Decisions**:
- **UI Library**: Rich (modern Python CLI library with colors, emoji, layouts, progress bars)
- **Input Mechanism**: `Rich.prompt()` with validators for sequential, guided input
- **Output Mechanism**: `Rich.Console()` for colored, emoji-enhanced text streaming
- **Timing Control**: `time.sleep()` with configurable delay, optional skip via ENTER (non-blocking input)

---

## 3. Functional Requirements

### FR-01: CLI Entry Point and Application Lifecycle

**Description**: The application must provide a command-line executable entry point that initializes the combat system and manages the complete combat session lifecycle.

**Detailed Requirements**:

1. **Entry Point**:
   - Executable via `python -m combat_simulator.cli` or similar command
   - Application initializes Rich console, CombatSimulator, and RandomDiceRoller

2. **Welcome Screen**:
   - Display application title with emoji header (e.g., "⚔️  COMBAT SIMULATOR  ⚔️")
   - Brief instruction: "Create two characters and watch them battle!"

3. **Lifecycle Flow**:
   ```
   Start → Welcome → Create Character 1 → Create Character 2
         → Display Character Summary → Run Combat → Display Victory
         → Exit
   ```

4. **Exit Behavior**:
   - After combat completion and victory announcement, application terminates
   - Graceful handling of Ctrl+C interruption (display "Combat interrupted" message)

**Acceptance Criteria**:
- AC-01.1: Application starts with welcome message and instructions
- AC-01.2: Application executes full lifecycle from start to exit
- AC-01.3: Ctrl+C displays interruption message and exits cleanly

---

### FR-02: Interactive Character Creation Flow

**Description**: Users must be able to create two characters through sequential, guided prompts with clear instructions and visual feedback.

**Detailed Requirements**:

### Input Fields (3 total)

1. **Name** (string)
   - Required, no default
   - Validation: non-empty, no whitespace-only
   - Prompt: `Nome personaggio: `

2. **HP** (int)
   - Range: 1-100
   - Default: random [20-80] if INVIO pressed
   - Prompt: `HP [1-100, INVIO=random 20-80]: `
   - Validation: must be integer in range

3. **Attack Power** (int)
   - Range: 1-20
   - Default: random [5-15] if INVIO pressed
   - Prompt: `Potere d'attacco [1-20, INVIO=random 5-15]: `
   - Validation: must be integer in range

### Derived Attributes (read-only, calculated)

4. **Agility** (int, non-input)
   - Formula: `hp + attack_power` (existing domain logic)
   - Displayed as info after character creation
   - Used internally for initiative calculation
   - Example display: `🏃 Agility: 60 (calcolata automaticamente)`

### Random Default Behavior

- **Randomness source**: Use `RandomDiceRoller` (same PRNG as combat)
- **User interaction**:
  - Empty input (INVIO) → generate random value in default range
  - Typed number → use that value (validate range)
- **Range rationale**:
  - HP [20-80]: Avoids too-fragile (< 20) or too-tanky (> 80) characters
  - Attack [5-15]: Balanced damage output, avoids one-shot kills
- **Varianza**: Combined random ranges create diverse character profiles

### Validation Behavior

- Invalid input displays colored error message (red text)
- Error message specifies the constraint (e.g., "HP must be between 1 and 100")
- Prompt re-appears immediately after error for re-entry
- No limit on retry attempts

### Character Confirmation

- After all inputs, display character summary card:
  ```
  ╭─────────────────────╮
  │ 🧙 Thorin           │
  │ ❤️  HP: 20          │
  │ ⚔️  Attack: 5       │
  │ ⚡ Agility: 25      │
  ╰─────────────────────╯
  ```
- Display summary for both characters side-by-side before combat starts

### Character Instantiation

- Create `Character` domain objects using validated inputs
- Handle domain validation errors (e.g., empty name after trim) with user-friendly message

**Acceptance Criteria**:
- AC-02.1: User creates Character 1 via three sequential prompts
- AC-02.2: User creates Character 2 via three sequential prompts
- AC-02.3: Invalid inputs display error messages and re-prompt
- AC-02.4: Valid characters display confirmation summary cards
- AC-02.5: Domain validation errors are caught and displayed with user-friendly messages

---

### FR-03: Initiative Resolution Display

**Description**: The application must clearly display which character won initiative and will attack first throughout the combat.

**Detailed Requirements**:

1. **Initiative Roll Display**:
   - Header: "🎲 Rolling Initiative..."
   - Line 1: "{Character1 name}: Base agility {agility} + 🎲 {roll} = {total}"
   - Line 2: "{Character2 name}: Base agility {agility} + 🎲 {roll} = {total}"
   - Pause: 1.0 second after displaying rolls

2. **Initiative Winner Announcement**:
   - Visual: "⚡ {Winner name} wins initiative and attacks first!"
   - Color: Winner name in bold/bright color
   - Pause: 1.5 seconds before starting combat

3. **Tie-Breaker Transparency**:
   - If initiative totals equal, display: "Initiative tied! {Winner} wins by tie-breaker rule."
   - Explain tie-breaker: "(Higher agility, or first character if agility equal)"

**Acceptance Criteria**:
- AC-03.1: Initiative rolls displayed with dice emoji and calculations
- AC-03.2: Winner announced with clear visual indicator
- AC-03.3: Tie-breaker logic explained when applicable
- AC-03.4: Appropriate pauses for comprehension

---

### FR-04: Combat Round Visualization

**Description**: Each combat round must be displayed with complete detail, showing all attack actions, damage calculations, and HP changes in a clear, visually engaging format.

**Detailed Requirements**:

1. **Round Header**:
   ```
   ═══════════════════════════════════
   ⚔️  ROUND {number}
   ═══════════════════════════════════
   ```
   - Pause: 0.5 seconds after header

2. **Attacker Strike Display**:
   - Format: "⚔️  {Attacker name} attacks!"
   - Details: "   🎲 Roll: {dice} + ⚔️  Power: {attack_power} = 💥 {total_damage} damage"
   - HP Change: "   {Defender name}: {old_hp} HP → {new_hp} HP"
   - Color: Damage numbers in red/orange, HP in color gradient (green→yellow→red based on remaining %)
   - Pause: 1.5 seconds after attacker strike

3. **Defender Counter-Attack Display** (if defender survives):
   - Format: "🛡️  {Defender name} counter-attacks!"
   - Details: "   🎲 Roll: {dice} + ⚔️  Power: {attack_power} = 💥 {total_damage} damage"
   - HP Change: "   {Attacker name}: {old_hp} HP → {new_hp} HP"
   - Pause: 1.5 seconds after counter-attack

4. **Death Announcement** (if character dies during round):
   - Format: "☠️  {Character name} has been defeated!"
   - Color: Dim/grey for defeated character
   - Pause: 2.0 seconds before victory announcement

5. **Round End** (both characters alive):
   - Separator line: "---"
   - Pause: 0.5 seconds before next round

6. **Comprehensive Logging** (all rounds, regardless of length):
   - Every round follows same format
   - No summarization or abbreviation for long combats
   - Consistent detail level maintained throughout

**Acceptance Criteria**:
- AC-04.1: Round number displayed with visual separator
- AC-04.2: Attacker action shows dice roll, attack power, total damage, HP change
- AC-04.3: Defender action shows same details (if defender survives)
- AC-04.4: Death events clearly announced with emoji
- AC-04.5: All rounds logged with same detail level (no adaptive summarization)
- AC-04.6: Appropriate pauses between events for comprehension

---

### FR-05: Victory Announcement and Combat Summary

**Description**: When combat ends, the application must display a clear victory announcement and provide a summary of the combat outcome.

**Detailed Requirements**:

1. **Victory Banner**:
   ```
   ╔═══════════════════════════════════╗
   ║     🏆  {WINNER NAME} WINS!  🏆   ║
   ╚═══════════════════════════════════╝
   ```
   - Winner name in large, bold, bright color
   - Celebratory emoji (🏆, 🎉)

2. **Combat Statistics**:
   - Total rounds: "Combat lasted {total_rounds} rounds"
   - Final HP: "{Winner name}: {hp} HP remaining"
   - Final HP: "{Loser name}: 0 HP (defeated)"

3. **Closing Message**:
   - "Thanks for playing! Exiting..."
   - Pause: 2.0 seconds before exit

**Acceptance Criteria**:
- AC-05.1: Victory banner displayed with winner's name
- AC-05.2: Combat statistics show total rounds and final HP
- AC-05.3: Closing message displayed before exit
- AC-05.4: Application exits cleanly after display

---

### FR-06: Timing and Pacing Control

**Description**: Combat visualization must be paced appropriately for user comprehension, with configurable delays and user-controlled skip capability.

**Detailed Requirements**:

1. **Default Timing Configuration**:
   - Initiative display: 1.0s after rolls, 1.5s after winner announcement
   - Round header: 0.5s pause
   - After each attack: 1.5s pause
   - After death: 2.0s pause
   - Before exit: 2.0s pause

2. **Skip Mechanism**:
   - User can press ENTER to skip current pause and advance immediately
   - Skip detection: Non-blocking input check during sleep periods
   - Visual hint: "(Press ENTER to skip)" displayed during long pauses (>1.0s)

3. **Configuration Future-Proofing**:
   - Timing values stored as configurable constants
   - Easy to adjust globally (preparation for future config file support)

**Acceptance Criteria**:
- AC-06.1: Default delays provide comfortable comprehension pacing
- AC-06.2: User can press ENTER to skip any pause
- AC-06.3: Skip hint displayed during longer pauses
- AC-06.4: Timing configuration centralized for future adjustments

---

### FR-07: Input Validation and Error Handling

**Description**: All user inputs must be validated, with clear, actionable error messages displayed for invalid entries.

**Detailed Requirements**:

1. **Character Name Validation**:
   - Rules: Non-empty after trimming whitespace, 1-50 characters
   - Error Messages:
     - Empty input: "❌ Name cannot be empty. Please enter a name."
     - Too long: "❌ Name too long (max 50 characters). Please try again."

2. **HP Validation**:
   - Rules: Integer, range 1-999
   - Error Messages:
     - Non-integer: "❌ HP must be a whole number. Please try again."
     - Out of range: "❌ HP must be between 1 and 999. Please try again."

3. **Attack Power Validation**:
   - Rules: Integer, range 1-99
   - Error Messages:
     - Non-integer: "❌ Attack power must be a whole number. Please try again."
     - Out of range: "❌ Attack power must be between 1 and 99. Please try again."

4. **Rich Validators**:
   - Utilize Rich's built-in prompt validators for type checking
   - Custom validators for range constraints
   - Validation occurs immediately on input submission

5. **Error Display Format**:
   - Errors displayed in red color
   - Emoji indicator (❌) for visibility
   - Clear instruction on valid format
   - Prompt re-appears immediately after error

**Acceptance Criteria**:
- AC-07.1: Invalid name inputs display specific error and re-prompt
- AC-07.2: Invalid HP inputs display specific error and re-prompt
- AC-07.3: Invalid attack power inputs display specific error and re-prompt
- AC-07.4: Errors are color-coded and include emoji indicators
- AC-07.5: Error messages specify the constraint and provide guidance

---

### FR-08: Exit Confirmation

**Description**: Wait for user confirmation before exiting after combat ends.

**Detailed Requirements**:

1. **Exit Flow**:
   - Combat completes with victory announcement
   - Display full result summary (winner, loser, rounds, stats)
   - Show exit prompt: `Premi INVIO per uscire (o CTRL-C per terminare)`
   - Wait for user keypress (blocking input)
   - Exit program cleanly

2. **Rationale**:
   - Prevents abrupt termination
   - User can review results at their own pace
   - Professional UX (no rushed reading)
   - CTRL-C always available for immediate exit

3. **Technical Implementation**:
   - Use Rich `Console().input()` for blocking wait
   - Handle KeyboardInterrupt (CTRL-C) gracefully
   - Exit code 0 on normal INVIO, exit code 130 on CTRL-C (Unix convention)

**Acceptance Criteria**:
- AC-08.1: After victory announcement, program waits for user input
- AC-08.2: Exit prompt is clearly displayed
- AC-08.3: INVIO press exits program cleanly (exit code 0)
- AC-08.4: CTRL-C exits program with appropriate message (exit code 130)

---

## 4. Non-Functional Requirements

### NFR-01: User Experience

**Description**: The application must provide an intuitive, visually engaging, and easy-to-understand user experience.

**Specific Requirements**:

1. **Visual Clarity**:
   - Clear visual hierarchy with headers, separators, spacing
   - Consistent emoji usage (same emoji for same concept throughout)
   - Color-coded information (damage in red, HP in health-gradient, success in green)

2. **Cognitive Load**:
   - One question/action at a time (sequential flow)
   - Sufficient pauses for reading and comprehension
   - Clear instructions at each step

3. **Feedback Responsiveness**:
   - Immediate validation feedback on input errors
   - Visible progress through combat (round numbers, HP changes)
   - Clear indication of completion (victory banner, exit message)

4. **Entertainment Value**:
   - Emoji enhance engagement and visual appeal
   - Combat narration feels dynamic and exciting
   - Victory celebration feels rewarding

5. **Pacing Validation** (addressing "comfortable" comprehension):
   - Default timing (1.5-2s delays) must allow reading without rushing
   - Measured through user observation: Can users explain what happened in previous round?
   - Quantifiable metric: 80%+ of test users comprehend combat flow without replay/questions
   - Validation: Informal user testing with 5+ developers from target audience

6. **Input Defaults and Variability**:
   - Support both rapid character creation (random) and precise control (manual input)
   - Random generation completes in < 1 second
   - Generated values create diverse character profiles (no clustering around single archetype)
   - Manual input validation response < 100ms
   - Validation: Generate 100 random characters, verify distribution across HP/attack ranges

**Validation Method**: User acceptance testing with target audience (developers, students learning TDD/architecture)

**Success Criteria**:
- Users understand combat flow without external documentation (80%+ success rate)
- Users can identify why/how characters won or lost (explained correctly)
- Users describe experience as "clear", "intuitive", "engaging" (qualitative feedback)
- No user reports feeling "rushed" or unable to read outputs (zero complaints)

---

### NFR-02: Performance

**Description**: The application must be responsive with no perceptible lag in input handling or output display.

**Specific Requirements**:

1. **Input Response Time**:
   - Validation and error display: < 100ms from input submission
   - Next prompt appearance: < 50ms after valid input

2. **Output Rendering**:
   - Text output rendering: Instantaneous (no chunking/streaming delays)
   - Rich console rendering: < 50ms for any single element

3. **Pause Accuracy**:
   - Configured delays accurate to ±50ms
   - Skip mechanism responsive within 100ms of ENTER press

4. **Startup Time**:
   - Application launch to welcome screen: < 500ms

**Measurement Method**: Timing instrumentation during development testing (no formal benchmark required for MVP)

**Success Criteria**:
- No user-perceptible delay in interactions
- Pauses feel natural, not laggy or rushed
- Skip mechanism feels responsive

---

### NFR-03: Cross-Platform Compatibility

**Description**: The application must work consistently across Windows, macOS, and Linux terminals.

**Specific Requirements**:

1. **Emoji Support**:
   - All emoji render correctly on major platforms
   - Test emoji: ⚔️ 💥 ❤️ 🎲 ⚡ 🏆 ☠️ 🛡️ 🧙
   - **Fallback Behavior** (if emoji unsupported):

| Emoji | Fallback Text | Usage |
|-------|---------------|-------|
| ⚔️ | `[ATK]` | Attack action |
| 💥 | `[DMG]` | Damage dealt |
| ❤️ | `[HP]` | Hit points |
| 🎲 | `[D6]` | Dice roll |
| ⚡ | `[INIT]` | Initiative |
| 🏆 | `[WIN]` | Victory |
| ☠️ | `[DEAD]` | Defeated |
| 🛡️ | `[DEF]` | Defense/counter |
| 🧙 | `[CHAR]` | Character |

2. **Color Support**:
   - Rich library handles color capability detection automatically
   - **Graceful degradation**:
     - 256-color terminals: Full color palette
     - 16-color terminals: Basic color set (red, green, yellow, blue)
     - No-color terminals: Plain text with emoji/fallback symbols for distinction
   - No functionality loss when colors unavailable (symbols provide visual cues)

3. **Terminal Compatibility**:
   - Works in common terminals: Windows Terminal, PowerShell, CMD, macOS Terminal, iTerm2, GNOME Terminal, Konsole
   - Minimum terminal width: 80 characters (standard default)
   - No assumptions about terminal height (scrolling supported)

4. **Character Encoding**:
   - UTF-8 encoding for all output
   - Handle potential encoding errors gracefully (replace with ASCII alternatives from fallback table)

**Validation Method**:
- Manual testing on Windows, macOS, Linux
- Automated CI/CD testing (limited to text output validation, emoji display manual)

**Success Criteria**:
- Application runs without errors on all three platforms
- Emoji and colors display correctly or degrade gracefully per fallback table
- No character encoding errors

---

### NFR-04: Testability

**Description**: The CLI application must be testable through automated tests, covering both interactive input and visual output.

**Specific Requirements**:

1. **Separation of Concerns**:
   - Character creation logic separated from Rich-specific UI code
   - Combat visualization logic separated from Rich-specific rendering
   - Testable components accept abstracted I/O (not hardcoded to Rich Console)

2. **Test Strategies**:
   - **Unit Tests**: Test character creation validation logic, combat event formatting logic
   - **Integration Tests**: Test CLI adapter integration with CombatSimulator
   - **Snapshot Tests**: Capture and compare text output for visual regression detection
   - **Mock Input Tests**: Simulate user input sequences using mocked input streams

3. **Testable Interfaces**:
   - `CharacterCreator` accepts `Console` abstraction (allows test doubles)
   - `CombatVisualizer` accepts `Console` abstraction and `CombatResult`
   - Timing controlled via injectable delay strategy (allows zero-delay test mode)

4. **Test Fixtures and Data Management**:
   - Test fixtures for character creation input sequences (valid/invalid patterns)
   - Snapshot file management strategy (golden files in `tests/snapshots/`)
   - Test data catalog for deterministic combat scenarios
   - Mock dice roll configurations for predictable outcomes

5. **CI/CD Integration**:
   - All tests run in CI pipeline without requiring interactive terminal
   - Emoji/color rendering not required for tests (content validation only)

**Validation Method**: Automated test suite execution in CI/CD

**Success Criteria**:
- Unit test coverage > 80% for CLI adapter logic
- Integration tests validate end-to-end flow with CombatSimulator
- Test fixtures cover all validation scenarios
- Snapshot tests detect visual regressions
- Tests pass consistently in CI/CD environment
- No manual testing required for logic validation (only for visual QA)

---

### NFR-05: Maintainability

**Description**: The CLI code must be well-structured, documented, and easy to modify or extend.

**Specific Requirements**:

1. **Code Structure**:
   - CLI adapter code located in `modules/infrastructure/cli/` (or similar)
   - Separate modules for character creation, combat visualization, main entry point
   - No business logic in CLI layer (only presentation/input handling)

2. **Configuration Management**:
   - Timing constants defined in single location
   - Emoji/symbol choices defined in constants/config
   - Easy to modify visual elements without code changes (future: config file)

3. **Documentation**:
   - Docstrings for all public classes and functions
   - README section explaining how to run CLI application
   - Architecture documentation showing CLI adapter placement in hexagonal structure

4. **Extensibility**:
   - Easy to add new output formats (e.g., JSON log file)
   - Easy to add new input sources (e.g., config file for character creation)
   - Rich library abstraction allows future GUI migration

**Validation Method**: Code review during DESIGN and DEVELOP waves

**Success Criteria**:
- CLI code follows project coding standards
- New developers can understand CLI structure from documentation
- Visual tweaks (timing, emoji, colors) achievable without architectural changes

---

### NFR-06: Accessibility

**Description**: Accessibility considerations for users with disabilities.

**Specific Requirements**:

1. **Current Scope (MVP)**:
   - Accessibility features explicitly OUT OF SCOPE for MVP
   - Focus on visual, emoji-heavy design for standard terminal users
   - Screen reader compatibility NOT required for initial release

2. **Known Limitations**:
   - Heavy emoji usage may create barriers for screen reader users
   - Color-coded information may be inaccessible to colorblind users
   - Visual formatting assumes sighted users

3. **Future Enhancement Path**:
   - Audio cues for combat events (future consideration)
   - Text-only mode without emoji (future enhancement)
   - Screen reader-friendly output format (deferred)
   - Alternative color schemes for colorblind users (deferred)

**Rationale**: This is an educational/demonstration project for learning TDD and hexagonal architecture. Target audience is developers working in standard terminal environments. Accessibility features would significantly expand scope without adding educational value for primary use case.

**Validation Method**: Explicit documentation that accessibility is deferred

**Success Criteria**:
- Accessibility limitations documented transparently
- Future enhancement path identified for consideration
- Target audience clearly defined (developers with standard terminal access)

---

## 5. User Stories with Acceptance Criteria

### US-01: Interactive Character Creation

**As a** user
**I want** to create two characters through guided prompts
**So that** I can quickly set up a combat scenario without writing code

**Acceptance Criteria** (Gherkin Format):

```gherkin
Scenario: Successful character creation for both combatants
  Given the CLI application is started
  When I enter "Thorin" for Character 1 name
  And I enter "20" for Character 1 HP
  And I enter "5" for Character 1 attack power
  And I enter "Goblin" for Character 2 name
  And I enter "10" for Character 2 HP
  And I enter "3" for Character 2 attack power
  Then I see confirmation "Character created: Thorin (❤️ 20 HP, ⚔️ 5 ATK)"
  And I see confirmation "Character created: Goblin (❤️ 10 HP, ⚔️ 3 ATK)"
  And both character summary cards are displayed
```

```gherkin
Scenario: Invalid HP input with re-prompt
  Given the CLI application is started
  And I have entered "Hero" for Character 1 name
  When I enter "abc" for Character 1 HP
  Then I see error message "❌ HP must be a whole number"
  And the HP prompt appears again
  When I enter "25" for Character 1 HP
  Then the HP is accepted
  And the attack power prompt appears
```

```gherkin
Scenario: Empty character name validation
  Given the CLI application is started
  When I enter "" (empty string) for Character 1 name
  Then I see error message "❌ Name cannot be empty"
  And the name prompt appears again
  When I enter "Warrior" for Character 1 name
  Then the name is accepted
  And the HP prompt appears
```

```gherkin
Scenario: Random defaults work as expected
  Given the CLI application is started
  And I have entered "Hero" for Character 1 name
  When I press INVIO at HP prompt
  Then HP value is generated in range [20-80]
  And value is displayed for confirmation
  And the attack power prompt appears
```

```gherkin
Scenario: Manual input overrides random
  Given the CLI application is started
  And I have entered "Hero" for Character 1 name
  When I enter "50" at HP prompt
  Then HP is exactly 50 (not random)
  And the attack power prompt appears
```

---

### US-02: Visual Combat Progress Display

**As a** user
**I want** to see each combat round with detailed attack information, damage, and HP changes
**So that** I can understand how the combat progresses and why one character won

**Acceptance Criteria** (Gherkin Format):

```gherkin
Scenario: Complete round visualization with attacker and defender actions
  Given two characters "Thorin" (20 HP, 5 ATK) and "Goblin" (10 HP, 3 ATK)
  And "Thorin" won initiative
  When combat round 1 executes
  Then I see round header "⚔️ ROUND 1"
  And I see "⚔️ Thorin attacks!"
  And I see attack details showing dice roll, attack power, total damage
  And I see HP change "Goblin: 10 HP → 7 HP" (example with 3 damage)
  And I see "🛡️ Goblin counter-attacks!"
  And I see counter-attack details showing dice roll, attack power, total damage
  And I see HP change "Thorin: 20 HP → 15 HP" (example with 5 damage)
```

```gherkin
Scenario: Defender death prevents counter-attack
  Given two characters "Thorin" (20 HP, 5 ATK) and "Goblin" (5 HP, 3 ATK)
  And "Thorin" won initiative
  And the dice roll will result in lethal damage to Goblin
  When combat round 1 executes
  Then I see "⚔️ Thorin attacks!"
  And I see "Goblin: 5 HP → 0 HP"
  And I see "☠️ Goblin has been defeated!"
  And I do NOT see "Goblin counter-attacks"
```

```gherkin
Scenario: Initiative roll display shows calculations with agility info
  Given two characters "Elf" (15 HP, 10 ATK) and "Dwarf" (20 HP, 5 ATK)
  When initiative is rolled
  Then I see "🎲 Rolling Initiative..."
  And I see "Elf: Base agility 25 + 🎲 {roll1} = {total1}"
  And I see "Dwarf: Base agility 25 + 🎲 {roll2} = {total2}"
  And I see "⚡ {Winner} wins initiative and attacks first!"
  And agility values are clearly displayed
  And dice rolls for each character are shown
  And initiative totals are calculated and displayed
  And first attacker is announced
```

---

### US-03: Combat Pacing Control

**As a** user
**I want** combat events to be displayed with appropriate delays
**So that** I can read and comprehend what's happening without feeling rushed

**Acceptance Criteria** (Gherkin Format):

```gherkin
Scenario: Default pacing provides reading time
  Given combat is in progress
  When an attack is displayed
  Then there is a 1.5 second pause after the attack details (±0.1s tolerance)
  And the next action does not appear until the pause completes or user skips
```

```gherkin
Scenario: User skips delay with ENTER key
  Given combat is in progress
  And an attack has been displayed with a 1.5s pause
  When I press ENTER during the pause
  Then the pause ends within 200ms of keypress
  And the next action appears without further delay
```

```gherkin
Scenario: Skip hint displayed during long pauses
  Given combat is in progress
  When a pause longer than 1 second begins
  Then I see hint "(Press ENTER to skip)" displayed
```

---

### US-04: Clear Error Recovery

**As a** user
**I want** clear error messages when I enter invalid input
**So that** I understand what went wrong and how to fix it

**Acceptance Criteria** (Gherkin Format):

```gherkin
Scenario: Out-of-range HP value with guidance
  Given I am creating a character
  When I enter "1000" for HP (exceeds max of 999)
  Then I see error "❌ HP must be between 1 and 999. Please try again."
  And the HP prompt appears again
  When I enter "50" for HP
  Then the HP is accepted
```

```gherkin
Scenario: Non-numeric attack power with clear instruction
  Given I am creating a character
  And I have entered valid name and HP
  When I enter "strong" for attack power
  Then I see error "❌ Attack power must be a whole number. Please try again."
  And the attack power prompt appears again
  When I enter "8" for attack power
  Then the attack power is accepted
```

---

### US-05: Victory Announcement

**As a** user
**I want** a clear, celebratory victory announcement when combat ends
**So that** I feel a sense of completion and understand the outcome

**Acceptance Criteria** (Gherkin Format):

```gherkin
Scenario: Victory banner displayed with combat statistics
  Given combat is complete
  And "Thorin" won with 12 HP remaining
  And combat lasted 3 rounds
  When the final round ends
  Then I see victory banner with "🏆 THORIN WINS! 🏆"
  And I see "Combat lasted 3 rounds"
  And I see "Thorin: 12 HP remaining"
  And I see "Goblin: 0 HP (defeated)"
  And I see "Thanks for playing! Exiting..."
  And the application exits after 2 seconds
```

---

### US-06: Graceful Interruption

**As a** user
**I want** to cancel combat with Ctrl+C gracefully
**So that** I can exit without seeing error messages

**Acceptance Criteria** (Gherkin Format):

```gherkin
Scenario: Ctrl+C during character creation
  Given I am at the character creation prompt
  When I press Ctrl+C
  Then I see "⚠️ Combat interrupted by user. Exiting..."
  And the application exits cleanly
  And no stack trace is displayed
```

```gherkin
Scenario: Ctrl+C during combat visualization
  Given combat is in progress
  And combat round 2 is being displayed
  When I press Ctrl+C
  Then I see "⚠️ Combat interrupted by user. Exiting..."
  And the application exits cleanly
  And no stack trace is displayed
```

---

## 6. Domain Model Integration

### 6.1 Existing Domain Objects (CLI Adapter Consumes)

**Character**:
- Properties: `name: str`, `hp: int`, `attack_power: int`, `agility: int` (derived), `is_alive: bool` (derived)
- Immutable dataclass

**CombatResult**:
- Properties: `winner: Character`, `loser: Character`, `total_rounds: int`, `rounds: tuple[RoundResult, ...]`, `initiative_result: InitiativeResult`
- Contains complete combat history

**RoundResult**:
- Properties: `round_number`, `attacker_action`, `defender_action`, `attacker_hp_before`, `attacker_hp_after`, `defender_hp_before`, `defender_hp_after`, `combat_ended`, `winner`
- Full round state including both actions

**AttackResult**:
- Properties: `attacker_name`, `defender_name`, `dice_roll`, `attack_power`, `total_damage`, `defender_old_hp`, `defender_new_hp`, `defender_after`
- Complete attack details for visualization

**InitiativeResult**:
- Properties: `attacker`, `defender`, `attacker_roll`, `defender_roll`, `attacker_total`, `defender_total`
- Initiative calculation transparency

### 6.2 CLI Adapter Responsibilities

**CharacterCreator** (CLI Component):
- Prompt user for name, HP, attack power
- Validate inputs against constraints
- Create `Character` domain objects
- Handle domain validation errors (e.g., `ValueError` from empty name)

**CombatVisualizer** (CLI Component):
- Accept `CombatResult` from `CombatSimulator`
- Display `InitiativeResult` with roll details
- Iterate through `rounds` tuple and display each `RoundResult`
- Format `AttackResult` details for visual output
- Display victory announcement from `CombatResult.winner`

**CLI Entry Point** (Main Script):
- Initialize Rich `Console`
- Initialize `CombatSimulator` with `RandomDiceRoller`
- Orchestrate CharacterCreator → CombatSimulator → CombatVisualizer flow
- Handle `KeyboardInterrupt` for graceful exit

---

## 7. Technical Constraints and Decisions

### 7.1 Technology Stack

**UI Library Selection Analysis**:

| Criterion | Rich 13.x | Click | prompt_toolkit | curses | Decision |
|-----------|-----------|-------|----------------|--------|----------|
| **Emoji Support** | Native, automatic fallback | Limited, manual handling | Good, requires config | Poor, ASCII-focused | ✅ Rich |
| **Color Support** | Auto-detection, 256-color | Basic, 16-color | Excellent, true-color | Good, 256-color | ✅ Rich |
| **Input Validation** | Built-in validators | Manual validation | Built-in, complex | Manual validation | ✅ Rich |
| **Layout/Formatting** | Tables, panels, columns | Basic text | Advanced TUI widgets | Full TUI control | ✅ Rich (simplicity) |
| **Learning Curve** | Low (declarative API) | Low (decorator-based) | Medium (event-driven) | High (low-level) | ✅ Rich |
| **Cross-Platform** | Excellent (Windows+Unix) | Good | Excellent | Good (Unix better) | ✅ Rich |
| **Testing Support** | Console capture API | Standard output capture | Complex (async) | Terminal emulation required | ✅ Rich |
| **Maintenance** | Active (2025+) | Active | Active | Stdlib (stable) | All good |

**Selection Rationale**: Rich selected for:

1. **All-in-one solution** - emoji, colors, validation, layouts in single library
2. **User decision confirmation** - User explicitly chose Rich during requirements gathering
3. **Simplicity for educational project** - Low learning curve, declarative API suitable for TDD demonstration
4. **Testing-friendly** - Built-in console capture simplifies automated testing
5. **Modern aesthetics** - Best emoji/color support for engaging user experience

**Alternatives Considered**:

- **Click**: Good for CLI arguments/commands, but lacks rich formatting for our visualization needs
- **prompt_toolkit**: Powerful for complex TUI, overkill for linear sequential prompts
- **curses**: Low-level, high complexity, harder to test, less suitable for educational context

**Final Technology Stack**:

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **UI Library** | Rich 13.x | Selected per analysis above. Modern, all-in-one, user-confirmed. |
| **Input Handling** | `Rich.prompt()` with validators | Built-in validation, type coercion, error handling. Clean API for sequential prompts. |
| **Output Rendering** | `Rich.Console()` | Powerful console abstraction with color, emoji, markup support. Cross-platform compatible. |
| **Timing/Delays** | `time.sleep()` + non-blocking input | Simple, reliable delay mechanism. Non-blocking input check for skip functionality. |
| **Character Encoding** | UTF-8 | Standard for modern terminals. Rich handles encoding detection. |

### 7.2 Architectural Placement

**Layer**: Infrastructure (User Interface Adapter)

**Directory Structure** (Proposed):
```
modules/infrastructure/cli/
├── __init__.py
├── character_creator.py       # CharacterCreator class
├── combat_visualizer.py       # CombatVisualizer class
├── config.py                  # Timing constants, emoji config
└── main.py                    # CLI entry point
```

**Dependency Flow**:
```
CLI Adapter → Application (CombatSimulator) → Domain (Services, Models)
```

**Hexagonal Architecture Compliance**:
- CLI is an **Adapter** (infrastructure), not core domain
- CLI depends on Application layer (`CombatSimulator`)
- CLI never directly accesses domain services (goes through `CombatSimulator`)
- Domain remains independent of presentation layer

### 7.3 Library Dependencies

**New Dependencies** (to be added to `pyproject.toml` or `requirements.txt`):
- `rich>=13.0.0` - CLI UI library

**Existing Dependencies** (unchanged):
- `pytest`, `pytest-bdd` - Testing framework
- Python 3.12+ - Language version

### 7.4 Cross-Platform Considerations

**Emoji Compatibility**:
- Rich handles emoji rendering automatically
- Fallback strategy: If emoji unsupported, Rich displays box or ASCII
- Testing required on Windows (historically worst emoji support)

**Color Compatibility**:
- Rich detects terminal color capabilities (`COLORTERM`, terminal type)
- Automatic degradation to 16-color, 8-color, or no-color modes
- No special handling required in CLI code

**Terminal Width**:
- Assume minimum 80 characters width (standard)
- Combat visualization fits within 80 columns
- Character summary cards: ~30 characters wide (side-by-side within 80)

### 7.5 Testing Strategy

**Unit Tests** (CharacterCreator, CombatVisualizer logic):
- Test validation logic with various inputs
- Test formatting functions (attack display, HP gradient color selection)
- Mock Rich Console to capture output
- Zero-delay mode for timing tests

**Integration Tests** (CLI → CombatSimulator):
- Test full flow with mocked input stream (name, HP, attack for both characters)
- Verify `CombatSimulator.run_combat()` called with correct `Character` objects
- Verify `CombatResult` consumed and displayed correctly

**Snapshot Tests** (Visual Regression):
- Capture text output of complete combat session
- Compare against golden snapshot files
- Detect unintended visual changes

**Manual Tests** (required for emoji/color validation):
- Run CLI on Windows, macOS, Linux
- Verify emoji display correctly
- Verify colors render appropriately
- Verify timing feels natural

---

## 8. Open Questions and Risks

### 8.1 Open Questions

| ID | Question | Priority | Status | Owner |
|----|----------|----------|--------|-------|
| Q-01 | Should we support configuration file for timing adjustments (e.g., `~/.combat-sim-config.yaml`)? | Low | Deferred to future enhancement | Product Owner |
| Q-02 | Should we add combat replay functionality (re-run same characters)? | Medium | Deferred - violates "single combat per run" decision | Product Owner |
| Q-03 | Should we log combat results to a file for post-analysis? | Low | Deferred to future enhancement | Product Owner |
| Q-04 | Should we support non-interactive mode (e.g., `--char1 "Thorin,20,5"`)? | Low | Deferred to future enhancement | Product Owner |

### 8.2 Identified Risks

| ID | Risk | Severity | Probability | Mitigation Strategy | Status |
|----|------|----------|-------------|---------------------|--------|
| R-01 | Emoji rendering issues on Windows terminals | Medium | Medium | Rich library handles fallbacks automatically. Manual testing on Windows required. | Accepted |
| R-02 | Testing interactive CLI in CI/CD challenging | Medium | High | Separate logic from Rich UI. Use mocked input streams. Snapshot tests for output validation. | Mitigated |
| R-03 | Non-blocking input for skip mechanism complex | Low | Medium | Use `select` (Unix) or `msvcrt.kbhit()` (Windows) or Rich's built-in input handling. Research during DESIGN. | Under Investigation |
| R-04 | Timing variations on different systems | Low | Low | Timing accuracy not critical (±100ms acceptable). Configurable constants allow adjustment. | Accepted |
| R-05 | UTF-8 encoding issues on legacy terminals | Low | Low | Rich handles encoding detection. Target modern terminals only (document minimum requirements). | Accepted |
| R-06 | Character creation takes too long for repeat testing | Low | Medium | Future enhancement: config file or non-interactive mode for developers. Not MVP blocker. | Accepted |

---

## 9. Development Strategy: Outside-In TDD with Incremental Phases

### Philosophy

Deliver testable business value incrementally. Each phase is:
- **Releasable**: Functional end-to-end, no broken states
- **Testable**: E2E acceptance tests validate business value
- **Incremental**: Builds on previous phase without rework

### Phase 1: Baseline - Minimum Viable CLI (MVP)

**Goal**: Prove integration works end-to-end

**Scope**:
- CLI entry point (`python -m cli` or similar)
- Hardcoded character creation (fixed values, no prompts)
- Call `CombatSimulator.run_combat()`
- Plain text output (no colors, no emoji)
- Display winner

**E2E Scenario**:
```gherkin
Scenario: Baseline CLI runs combat
  Given CLI is invoked with hardcoded characters
  When combat executes
  Then winner is displayed
  And program exits successfully
```

**Business Value**: Validates hexagonal architecture wiring (CLI → Application → Domain)

**Deliverable**: Working CLI that produces correct combat result

---

### Phase 2: Interactive Input with Validation

**Goal**: Robust user input handling

**Scope**:
- Replace hardcoded values with Rich.prompt()
- Implement 3 input fields (name, hp, attack_power)
- Live validation with re-prompting
- Random defaults (INVIO behavior)
- Display created characters before combat

**E2E Scenarios**:
```gherkin
Scenario: Valid character creation
  Given user provides valid inputs
  When characters are created
  Then combat proceeds with those characters

Scenario: Invalid input recovery
  Given user provides invalid HP (e.g., 150)
  When validation fails
  Then error message shown
  And user re-prompted
  And combat eventually succeeds with valid input
```

**Business Value**: Professional input UX, prevents garbage data

**Deliverable**: Fully interactive character creation with bulletproof validation

---

### Phase 3: Visual Enhancement (Emoji, Colors, Pacing)

**Goal**: Engaging, readable combat visualization

**Scope**:
- Add emoji to all events (⚔️, 💥, ❤️, 🎲, 🏆, ☠️)
- Color-code output (Rich styling)
- Implement pacing delays (1.5-2s between rounds)
- Format HP changes clearly
- Initiative announcement with visual flair

**E2E Scenarios**:
```gherkin
Scenario: Combat visualization completeness
  Given two characters created
  When combat runs
  Then initiative shown with emoji
  And each attack shows: attacker, dice roll, damage, HP change
  And pacing allows comprehension
  And victory banner displayed

Scenario: Cross-platform emoji support
  Given CLI runs on [Windows|Linux|macOS]
  When combat visualized
  Then emoji display correctly OR fallback to [ATK]/[HP] text
```

**Business Value**: Demo-quality UX, showcases Rich library capabilities

**Deliverable**: Visually polished combat display

---

### Phase 4: Polish (Exit Confirmation, Edge Cases)

**Goal**: Production-ready refinements

**Scope**:
- Exit confirmation (INVIO to quit)
- Graceful CTRL-C handling
- Edge case testing (1-round combat, 20+ round combat)
- Help text (`--help` flag)
- Error messages for unexpected failures

**E2E Scenarios**:
```gherkin
Scenario: Exit confirmation prevents abrupt termination
  Given combat completed successfully
  When victory shown
  Then program waits for user confirmation
  And exits only after INVIO pressed

Scenario: Graceful interrupt handling
  Given combat in progress
  When user presses CTRL-C
  Then program exits cleanly with message
  And exit code is 130
```

**Business Value**: Professional finish, handles real-world usage

**Deliverable**: Production-ready CLI suitable for distribution

---

### Phase Transition Criteria

Each phase must meet these gates before proceeding:

1. **All E2E scenarios for that phase PASS**
2. **Unit tests for new components PASS**
3. **Manual smoke test successful**
4. **Code review approval**
5. **No regressions in previous phases**

### Why This Sequence?

1. **Basic First**: Proves architecture before investing in UX
2. **Validation Second**: Robustness before beauty (avoid polishing broken input)
3. **Visual Third**: Enhances working foundation (safe to experiment)
4. **Polish Last**: Refines proven system (low-risk improvements)

This order minimizes rework and delivers value at each checkpoint.

---

## 10. ATDD Foundation for DISTILL Wave

### 10.1 Testable Acceptance Criteria Summary

The user stories in Section 5 provide **Given-When-Then** scenarios that will translate directly to acceptance tests in the DISTILL wave. Key testable behaviors:

1. **Character Creation Flow**:
   - Valid input acceptance
   - Invalid input rejection with re-prompt
   - Domain validation error handling
   - Character summary display

2. **Combat Visualization**:
   - Initiative roll display with calculations
   - Round header and separator display
   - Attack action details (dice, power, damage, HP change)
   - Counter-attack conditional display (only if defender survives)
   - Death announcement
   - Victory banner and statistics

3. **Timing and Pacing**:
   - Delays occur with configured duration
   - Skip mechanism responsive to ENTER press
   - Skip hint display during long pauses

4. **Error Handling**:
   - Specific error messages for each validation failure
   - Error display format (color, emoji, message)
   - Prompt re-appearance after error

5. **Graceful Interruption**:
   - Ctrl+C handling at all stages
   - Clean exit message
   - No stack trace leakage

### 10.2 Edge Cases and Boundary Conditions

**Character Creation**:
- Minimum values: 1 HP, 1 attack power
- Maximum values: 999 HP, 99 attack power
- Boundary: Empty name (after trim), exactly 50 character name
- Special characters in name (Unicode, emoji in name input)

**Combat Visualization**:
- One-shot kill (defender dies in round 1, attacker action)
- Very long combat (20+ rounds) - no summarization
- Initiative tie (equal totals, equal agility, first character wins)

**Timing**:
- Very fast skip presses (multiple ENTER in quick succession)
- Skip pressed between events (timing edge cases)

**Interruption**:
- Ctrl+C during prompt input
- Ctrl+C during pause/delay
- Ctrl+C during Rich rendering

### 10.3 Test Data Strategy

**Acceptance Test Scenarios Will Use**:
- Predefined character pairs with known outcomes (borrowed from existing E2E tests)
- Mocked dice rolls for deterministic combat outcomes
- Captured output snapshots for visual regression

**Test Characters** (from existing E2E tests):
- Thorin (20 HP, 5 ATK) vs. Goblin (10 HP, 3 ATK) - standard combat
- Thorin (20 HP, 5 ATK) vs. Goblin (5 HP, 3 ATK) - one-shot kill
- Elf (15 HP, 10 ATK) vs. Dwarf (20 HP, 5 ATK) - initiative tie scenario

---

## 11. Handoff Package for DESIGN Wave

### 11.1 Deliverables Summary

This requirements document provides:

✅ **Functional Requirements**: 8 detailed FR specifications (FR-01 through FR-08)
✅ **Non-Functional Requirements**: 5 NFR specifications (NFR-01 through NFR-05)
✅ **User Stories**: 6 user stories with Gherkin acceptance criteria (US-01 through US-06)
✅ **Technical Constraints**: Technology stack, architectural placement, dependencies
✅ **Domain Model Integration**: Existing domain objects and CLI adapter responsibilities
✅ **Risk Assessment**: 6 identified risks with mitigation strategies
✅ **ATDD Foundation**: Testable scenarios, edge cases, test data strategy

### 11.2 Stakeholder Consensus

**User Requirements**:
- ✅ Interactive input flow confirmed (sequential prompts)
- ✅ Combat visualization format confirmed (scrolling text log with emoji)
- ✅ Timing/pacing confirmed (1.5-2s delays, ENTER skip)
- ✅ Detail level confirmed (show all events, no summarization)
- ✅ Single-combat scope confirmed (no multi-combat sessions)

**Technical Decisions**:
- ✅ Rich library selected for CLI UI
- ✅ Hexagonal architecture placement confirmed (Infrastructure adapter)
- ✅ Integration approach confirmed (CLI → CombatSimulator → Domain)

**Quality Attributes**:
- ✅ UX principles defined (clarity, intuitiveness, pacing)
- ✅ Cross-platform compatibility requirements specified
- ✅ Testability requirements established

### 11.3 Next Wave: DESIGN

**Solution Architect Responsibilities**:

1. **Architectural Design**:
   - Design CLI adapter class structure (CharacterCreator, CombatVisualizer, Main)
   - Define interfaces/abstractions for testability
   - Design timing control strategy (including skip mechanism)
   - Design error handling flow

2. **Component Specifications**:
   - CharacterCreator API specification
   - CombatVisualizer API specification
   - Configuration constants structure (timing, emoji, colors)

3. **Integration Design**:
   - Dependency injection strategy for CombatSimulator and RandomDiceRoller
   - Rich Console abstraction for testing
   - Mock input strategy for automated tests

4. **Testing Architecture**:
   - Unit test strategy for CLI components
   - Integration test strategy for CLI → Application flow
   - Snapshot test strategy for visual regression
   - CI/CD test execution plan (non-interactive mode)

5. **Sequence Diagrams**:
   - Character creation sequence
   - Combat visualization sequence
   - Error handling sequence

6. **ADRs (Architecture Decision Records)**:
   - ADR: Selection of Rich library over alternatives (click, prompt_toolkit)
   - ADR: Hexagonal architecture placement of CLI adapter
   - ADR: Testing strategy for interactive CLI

### 11.4 Success Criteria for DESIGN Wave

The DESIGN wave will be considered complete when:

- [ ] CLI adapter class structure designed and documented
- [ ] Interface specifications completed for CharacterCreator and CombatVisualizer
- [ ] Timing control and skip mechanism designed
- [ ] Error handling flow documented
- [ ] Testing architecture specified (unit, integration, snapshot)
- [ ] Sequence diagrams created for key flows
- [ ] ADRs documented for major decisions
- [ ] Design review completed and approved

### 11.5 Questions for Solution Architect

1. **Testing Strategy**: How should we abstract Rich Console to enable unit testing with test doubles? Custom interface or Rich's built-in testing utilities?

2. **Skip Mechanism**: What's the cleanest approach for non-blocking input during delays? Platform-specific solutions or Rich library capabilities?

3. **Configuration Management**: Should timing constants live in a dedicated config module or as class-level constants? Prepare for future config file support?

4. **Error Handling**: Should we create custom exception types for CLI-specific errors (e.g., `UserInterruptionError`) or rely on built-in exceptions?

5. **Dependency Injection**: How should we inject CombatSimulator and RandomDiceRoller into CLI entry point? Simple instantiation or formal DI container?

---

## 12. Appendix

### 12.1 Glossary

| Term | Definition |
|------|------------|
| **Agility** | Derived character attribute: HP + Attack Power. Used for initiative calculation. |
| **Attacker Advantage Rule** | Combat rule: character winning initiative attacks first every round. Defender counter-attacks only if survives. |
| **Character** | Combat participant with name, HP, attack power. Immutable domain object. |
| **Combat Round** | One complete cycle: attacker strikes, defender counter-attacks (if alive). |
| **Hexagonal Architecture** | Architecture pattern separating core domain from external adapters (UI, database, etc.). |
| **Initiative** | Roll determining which character attacks first. Calculated once at combat start. |
| **Rich** | Modern Python library for rich text, colors, and interactive CLI applications. |
| **Skip Mechanism** | User ability to press ENTER to bypass configured delays and advance immediately. |

### 12.2 References

**Existing System Documentation**:
- `tests/e2e/features/combat_simulation.feature` - Existing acceptance tests showing domain behavior
- `modules/domain/model/` - Domain object specifications (Character, CombatResult, RoundResult, AttackResult, InitiativeResult)
- `modules/application/combat_simulator.py` - Application use case service

**External Documentation**:
- [Rich Library Documentation](https://rich.readthedocs.io/) - UI library reference
- [Hexagonal Architecture Pattern](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)) - Architectural pattern reference

**User Decisions**:
- User requirement elicitation session (2026-01-09) - Captured interaction style, visualization format, timing, UI library selection

### 12.3 Requirements Traceability Matrix

| Business Objective | User Story | Functional Requirements | Acceptance Criteria |
|-------------------|------------|-------------------------|---------------------|
| Make combat simulator user-facing and interactive | US-01 | FR-01, FR-02, FR-07 | AC-01.*, AC-02.*, AC-07.* |
| Provide clear visualization of combat mechanics | US-02 | FR-03, FR-04 | AC-03.*, AC-04.* |
| Enable comfortable comprehension of combat flow | US-03 | FR-06 | AC-06.* |
| Ensure error recovery is clear and actionable | US-04 | FR-07 | AC-07.* |
| Celebrate victory with engaging conclusion | US-05 | FR-05 | AC-05.* |
| Handle user interruption gracefully | US-06 | FR-08 | AC-08.* |

---

## 13. Document Metadata

**Document Control**:
- Requirements Document ID: REQ-CLI-COMBAT-001
- Version: 1.1
- Status: Updated - Ready for DESIGN Wave Handoff
- Author: Riley (product-owner agent)
- Date Created: 2026-01-09
- Last Updated: 2026-01-09

**Review and Approval**:
- Requirements Author: Riley (product-owner) - Approved
- Stakeholder (User): Approved (decisions captured from feedback session)
- Next Wave Recipient: Solution Architect (DESIGN wave) - Pending

**Change Log**:
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-09 | Riley | Initial requirements document created. All functional requirements, NFRs, user stories, technical constraints, and handoff package completed. |
| 1.1 | 2026-01-09 | Riley | Updated based on user feedback: (1) FR-02: Added random default behavior for HP/attack with INVIO, clarified 3 input fields, agility as derived read-only attribute; (2) FR-08: Changed from interruption handling to exit confirmation with INVIO wait; (3) NFR-01: Added input defaults and variability subsection; (4) US-01: Added random defaults scenarios; (5) US-02: Clarified initiative display with agility info; (6) Added Section 9: Development Strategy with 4 incremental phases; (7) Renumbered subsequent sections (10-13). |

---

**END OF REQUIREMENTS SPECIFICATION**
