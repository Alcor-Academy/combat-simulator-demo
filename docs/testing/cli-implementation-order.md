# CLI Implementation Order: One E2E Test at a Time

**Project**: Combat Simulator Demo
**Feature**: Interactive CLI Combat Viewer
**Wave**: DISTILL → DEVELOP Handoff
**Strategy**: Outside-In TDD with Sequential Test Enabling
**Date**: 2026-01-09

---

## Critical Implementation Principle

**ONE E2E TEST AT A TIME**: Enable and implement tests sequentially to prevent commit blocks and maintain focus on single business scenario.

### Why One-at-a-Time?

1. **Prevents Commit Blocks**: Multiple failing tests block commits, breaking TDD flow
2. **Maintains Focus**: Single scenario focuses development effort
3. **Enables Incremental Delivery**: Each passing test represents shippable increment
4. **Natural Test Progression**: Tests pass when sufficient implementation exists
5. **Outside-In TDD Workflow**: Acceptance test drives inner-loop unit tests

---

## Test Enablement Strategy

### Initial State (All Tests Ignored)

```python
# Mark all scenarios as ignored initially
pytestmark = pytest.mark.skip(reason="Temporarily disabled - enabling one at a time")
```

### Progressive Enablement

1. **Remove skip marker** from ONE scenario
2. **Implement through Outside-In TDD** until test passes
3. **Commit working implementation**
4. **Remove skip marker** from NEXT scenario
5. **Repeat cycle**

---

## Phase 1: Baseline - Minimum Viable CLI

**Goal**: Prove integration works end-to-end with hardcoded characters

**Duration**: 2-4 hours

### Test 1.1: Hardcoded Combat Execution (MVP)

**Scenario**: CLI runs combat with hardcoded characters and displays winner

**Implementation Order**:
1. Create CLI entry point (`modules/infrastructure/cli/main.py`)
2. Wire CombatSimulator with domain services
3. Create two hardcoded Characters
4. Call `CombatSimulator.run_combat()`
5. Display winner name (plain text, no formatting)

**Success Criteria**:
- CLI executes without errors
- Combat completes
- Winner name displayed
- Program exits cleanly

**Test File**:
```python
@pytest.mark.skip(reason="PHASE 1: Enable first")
def test_cli_runs_hardcoded_combat():
    """Baseline: CLI executes combat with hardcoded characters."""
    # Run CLI with hardcoded Hero (50 HP, 10 ATK) vs Villain (40 HP, 8 ATK)
    # Assert winner displayed
    # Assert clean exit
```

**Dependencies**: None (uses existing CombatSimulator)

**Deliverable**: Working CLI that produces correct combat result

---

## Phase 2: Interactive Input with Validation

**Goal**: Robust user input handling with validation and random defaults

**Duration**: 6-10 hours

### Test 2.1: Manual Character Creation

**Scenario**: User creates both characters with manual input

**Feature File**:
```gherkin
Scenario: User creates both characters with manual input
  When I enter "Hero" for character 1 name
  And I enter "50" for character 1 HP
  And I enter "10" for character 1 attack power
  And I enter "Villain" for character 2 name
  And I enter "40" for character 2 HP
  And I enter "8" for character 2 attack power
  Then both characters are created successfully
```

**Implementation Order**:
1. Create CharacterCreator class
2. Implement name prompt with Rich.Prompt
3. Implement HP prompt with Rich.IntPrompt
4. Implement attack power prompt with Rich.IntPrompt
5. Create Character domain objects from inputs
6. Display character confirmation cards

**Success Criteria**:
- All three prompts accept valid input
- Character objects created correctly
- Agility calculated automatically
- Confirmation cards displayed

**Dependencies**: Rich library integration

---

### Test 2.2: Invalid HP Input Recovery

**Scenario**: Invalid HP input triggers validation error and re-prompt

**Feature File**:
```gherkin
Scenario: Invalid HP input triggers validation error and re-prompt
  When I enter "Hero" for character 1 name
  And I enter "150" for character 1 HP
  Then validation error is displayed in red
  And error message contains "HP must be between 1 and 999"
  When I enter "50" for character 1 HP
  Then character creation continues successfully
```

**Implementation Order**:
1. Create HP validation rules (range [1-999])
2. Implement error message display (red color)
3. Implement re-prompt logic
4. Test validation boundary conditions

**Success Criteria**:
- Out-of-range HP rejected
- Error message clear and specific
- Re-prompt appears automatically
- Valid input accepted after error

**Dependencies**: CharacterCreator validation

---

### Test 2.3: Random Defaults with INVIO

**Scenario**: User uses random defaults for character attributes

**Feature File**:
```gherkin
Scenario: User uses random defaults for character attributes
  When I enter "Hero" for character 1 name
  And I press INVIO for character 1 HP
  And I press INVIO for character 1 attack power
  Then character 1 HP is randomly generated in range [20-80]
  And character 1 attack power is randomly generated in range [5-15]
```

**Implementation Order**:
1. Integrate RandomDiceRoller for random generation
2. Implement empty input detection (INVIO press)
3. Generate random HP: 10d6+20 (range [20-80])
4. Generate random attack: 2d6+4 (range [5-15])
5. Display generated values for confirmation

**Success Criteria**:
- Empty input triggers random generation
- Values within specified ranges
- Generated values displayed
- Agility calculated from random values

**Dependencies**: CharacterCreator + RandomDiceRoller

---

### Test 2.4: Empty Name Validation

**Scenario**: Empty name input triggers validation error

**Feature File**:
```gherkin
Scenario: Empty name input triggers validation error
  When I enter "" for character 1 name
  Then validation error is displayed
  And error message contains "Name cannot be empty"
```

**Implementation Order**:
1. Implement name validation (non-empty after trim)
2. Add length validation (1-50 characters)
3. Display validation error
4. Re-prompt for name

**Success Criteria**:
- Empty names rejected
- Whitespace-only names rejected
- Clear error message
- Re-prompt works

**Dependencies**: CharacterCreator validation

---

### Test 2.5: Invalid Attack Power Validation

**Scenario**: Invalid attack power input triggers validation error

**Feature File**:
```gherkin
Scenario: Invalid attack power input triggers validation error
  When I enter "Hero" for character 1 name
  And I enter "50" for character 1 HP
  And I enter "0" for character 1 attack power
  Then validation error is displayed
```

**Implementation Order**:
1. Implement attack power validation (range [1-99])
2. Test boundary conditions (0, 100)
3. Display error message
4. Re-prompt

**Success Criteria**:
- Zero attack power rejected
- Out-of-range values rejected
- Re-prompt works

**Dependencies**: CharacterCreator validation

---

## Phase 3: Visual Enhancement

**Goal**: Engaging, readable combat visualization with emoji, colors, and pacing

**Duration**: 8-12 hours

### Test 3.1: Initiative Display with Emoji and Calculations

**Scenario**: Complete combat displays initiative with dice emoji and calculations

**Feature File**:
```gherkin
Scenario: Complete combat displays initiative with dice emoji and calculations
  Given two characters are created: Hero (HP 50, attack 10) and Villain (HP 40, attack 8)
  When combat starts
  Then initiative roll is displayed with 🎲 emoji
  And initiative shows both characters' agility values
  And initiative shows dice rolls for each character
```

**Implementation Order**:
1. Create CombatRenderer class
2. Implement `_render_initiative()` method
3. Format initiative with emoji (🎲, ⚡)
4. Display agility values
5. Display dice rolls and totals
6. Announce initiative winner

**Success Criteria**:
- Initiative formatted with emoji
- Calculations transparent
- Winner announcement clear

**Dependencies**: CombatRenderer + ConsoleOutput

---

### Test 3.2: Combat Round Display with All Event Details

**Scenario**: Combat round displays all event details with emoji

**Feature File**:
```gherkin
Scenario: Combat round displays all event details with emoji
  When combat starts
  Then each combat round displays round number
  And attacker action shows ⚔️ emoji
  And attack details show dice roll with 🎲 emoji
  And damage dealt shows 💥 emoji
  And HP change shows ❤️ emoji
```

**Implementation Order**:
1. Implement `_render_round()` method
2. Format round header with separator
3. Display attacker action (⚔️)
4. Show dice roll (🎲)
5. Show damage (💥)
6. Show HP change (❤️ Old HP → New HP)
7. Display defender counter-attack (🛡️) if alive
8. Display death announcement (☠️) if character dies

**Success Criteria**:
- All events displayed with emoji
- Information complete and clear
- Counter-attack conditional (only if defender survives)

**Dependencies**: CombatRenderer

---

### Test 3.3: Fixed Timing Delays Between Rounds

**Scenario**: Combat uses fixed timing delays between rounds

**Feature File**:
```gherkin
Scenario: Combat uses fixed timing delays between rounds
  When combat executes with default timing configuration
  Then delay between rounds is approximately 1.5-2 seconds
  And delays are consistent across all rounds
```

**Implementation Order**:
1. Create CLIConfig dataclass
2. Define timing constants (1.5s attack delay, etc.)
3. Implement ConsoleOutput.display_with_delay()
4. Apply delays in CombatRenderer
5. Create CLIConfig.test_mode() for zero delays

**Success Criteria**:
- Production delays: 1.5-2s between major events
- Test mode delays: 0s (fast execution)
- Timing consistent across rounds

**Dependencies**: CLIConfig + ConsoleOutput

---

### Test 3.4: HP Tracking Accuracy

**Scenario**: HP tracking accuracy throughout combat

**Feature File**:
```gherkin
Scenario: HP tracking accuracy throughout combat
  Given Hero starts with HP 50
  When Hero attacks and deals 14 damage
  Then Villain HP changes from 40 to 26
  And display shows "Villain: 40 HP → 26 HP"
```

**Implementation Order**:
1. Display old HP before attack
2. Calculate new HP after damage
3. Format HP change: "Old HP → New HP"
4. Color-code HP based on percentage remaining

**Success Criteria**:
- HP calculations accurate
- HP change format clear
- Color gradient applied (green→yellow→red)

**Dependencies**: CombatRenderer formatting

---

## Phase 4: Polish and Edge Cases

**Goal**: Production-ready refinements with exit confirmation and error handling

**Duration**: 4-6 hours

### Test 4.1: Victory Celebration Complete Information

**Scenario**: Victory celebration shows all required information

**Feature File**:
```gherkin
Scenario: Victory celebration shows all required information
  Given combat completes with Hero winning after 3 rounds
  Then victory banner includes winner name "Hero"
  And victory banner includes 🏆 emoji
  And combat statistics show "3 rounds"
  And winner final HP is displayed
```

**Implementation Order**:
1. Implement `_render_victory()` method
2. Create victory banner with borders
3. Display winner name with 🏆 emoji
4. Show combat statistics (rounds, final HP)
5. Show loser with ☠️ emoji

**Success Criteria**:
- Victory banner visually distinct
- All statistics present
- Emoji enhance celebration

**Dependencies**: CombatRenderer

---

### Test 4.2: Exit Confirmation Wait

**Scenario**: Exit confirmation waits for user keypress

**Feature File**:
```gherkin
Scenario: Exit confirmation waits for user keypress
  When victory banner is displayed
  Then program shows "Premi INVIO per uscire"
  And program waits for user keypress
  When I press INVIO
  Then program exits with code 0
```

**Implementation Order**:
1. Implement ConsoleOutput.prompt_continue()
2. Display exit message after victory
3. Block until user presses INVIO
4. Exit cleanly

**Success Criteria**:
- Program waits (no auto-exit)
- Exit message clear
- Clean exit on INVIO

**Dependencies**: ConsoleOutput

---

### Test 4.3: CTRL-C Graceful Exit

**Scenario**: User interrupts CLI with CTRL-C

**Feature File**:
```gherkin
Scenario: User interrupts CLI with CTRL-C during character creation
  When I press CTRL-C
  Then program exits gracefully
  And interruption message is displayed
  And exit code is 130
```

**Implementation Order**:
1. Add KeyboardInterrupt handler in CLI Main
2. Display interruption message
3. Exit with code 130 (Unix SIGINT convention)
4. No stack trace displayed

**Success Criteria**:
- CTRL-C caught at all stages
- Clean exit message
- Correct exit code

**Dependencies**: CLI Main error handling

---

### Test 4.4: Extended Combat Consistent Formatting

**Scenario**: Extended combat displays all rounds with consistent formatting

**Feature File**:
```gherkin
Scenario: Extended combat displays all rounds with consistent formatting
  Given two balanced characters are created
  When combat runs for 7 rounds
  Then all 7 rounds are displayed
  And no output is truncated
```

**Implementation Order**:
1. Test long combat (20+ rounds)
2. Verify no output truncation
3. Verify consistent formatting
4. Verify all events logged

**Success Criteria**:
- Long combats fully displayed
- No summarization or abbreviation
- Consistent detail level throughout

**Dependencies**: CombatRenderer completeness

---

## Phase 5: Cross-Platform Compatibility

**Goal**: Emoji fallback and terminal compatibility validation

**Duration**: 2-4 hours

### Test 5.1: Emoji Display on Unicode Terminals

**Scenario**: Emoji display correctly on Unicode-capable terminals

**Feature File**:
```gherkin
Scenario: Emoji display correctly on Unicode-capable terminals
  Given terminal supports Unicode emoji
  When combat runs
  Then emoji are rendered correctly: ⚔️ 💥 ❤️ 🎲 🏆 ☠️ 🛡️
```

**Implementation Order**:
1. Configure Rich for emoji rendering
2. Test on Unicode-capable terminal
3. Verify emoji display correctly
4. Verify no broken characters

**Success Criteria**:
- All emoji render correctly
- No placeholder boxes
- Line formatting intact

**Dependencies**: Rich emoji detection

---

### Test 5.2: Emoji Fallback for Limited Terminals

**Scenario**: Graceful degradation for terminals without emoji support

**Feature File**:
```gherkin
Scenario: CLI works on terminals without emoji support
  Given terminal does not support emoji
  When CLI runs
  Then emoji fallback to text equivalents
  And combat remains fully functional
```

**Implementation Order**:
1. Define fallback symbols in CLIConfig
2. Detect emoji support via Rich
3. Use fallbacks when emoji unsupported
4. Test on limited terminal (TERM=dumb)

**Success Criteria**:
- Fallback symbols used
- Full functionality preserved
- Information conveyed via text

**Dependencies**: CLIConfig fallback table

---

## Implementation Summary

### Total Tests: 18 Scenarios

**Phase 1 (Baseline)**: 1 test
**Phase 2 (Input/Validation)**: 5 tests
**Phase 3 (Visual Enhancement)**: 4 tests
**Phase 4 (Polish)**: 4 tests
**Phase 5 (Cross-Platform)**: 2 tests
**Additional Edge Cases**: 2 tests

### Estimated Timeline

- **Phase 1**: 2-4 hours (baseline integration)
- **Phase 2**: 6-10 hours (input handling and validation)
- **Phase 3**: 8-12 hours (visual formatting and pacing)
- **Phase 4**: 4-6 hours (polish and edge cases)
- **Phase 5**: 2-4 hours (cross-platform testing)

**Total**: 22-36 hours (approximately 3-5 days of focused development)

---

## Commit Strategy

### Commit After Each Passing Test

```bash
# Example commit messages (following Co-Authored-By convention)
git commit -m "feat: Add baseline CLI with hardcoded combat execution

Implements Phase 1.1: CLI entry point that executes combat
with hardcoded characters and displays winner.

- Create CLI Main entry point
- Wire CombatSimulator with domain services
- Display combat result (plain text)
- Clean exit after completion

Test: test_cli_runs_hardcoded_combat PASSES

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Commit Frequency

- **Minimum**: One commit per passing E2E test
- **Preferred**: Multiple commits per test (TDD inner loop)
- **Quality Gate**: All tests (existing + new) must pass before commit

---

## Test Data Management

### Deterministic Combat Scenarios

```python
# Fixture for deterministic dice rolls
@pytest.fixture
def deterministic_dice_roller():
    """Fixed seed for predictable combat outcomes."""
    return RandomDiceRoller(seed=42)

# Test data catalog
COMBAT_SCENARIOS = {
    'quick_victory': {
        'char1': Character("Hero", 50, 10),
        'char2': Character("Weak", 10, 3),
        'expected_rounds': 1,
    },
    'balanced_fight': {
        'char1': Character("Warrior", 50, 8),
        'char2': Character("Knight", 50, 8),
        'expected_rounds': 7,
    },
    'initiative_tie': {
        'char1': Character("Twin1", 30, 10),
        'char2': Character("Twin2", 30, 10),
        'tie_breaker': 'Twin1',
    },
}
```

---

## Quality Gates

### Before Enabling Next Test

- [ ] Current test PASSES
- [ ] All previous tests still PASS
- [ ] No regressions in existing 9/9 E2E tests
- [ ] No regressions in existing 34/34 unit tests
- [ ] Code review completed
- [ ] Commit created with descriptive message

### Before Phase Completion

- [ ] All phase tests PASS
- [ ] Manual smoke test successful (run CLI interactively)
- [ ] Phase documentation updated
- [ ] Handoff notes prepared for next phase

---

## Risk Mitigation

### Common Pitfalls

1. **Multiple Failing Tests**: ONLY enable one test at a time
2. **Mock Overuse**: Use REAL services (CombatSimulator, Character), mock ONLY I/O
3. **Skipping Inner Loop**: Drop to unit tests when acceptance test fails
4. **Incomplete Implementation**: Resist urge to move on before test passes
5. **Commit Pressure**: Never commit with failing tests

### Recovery Strategies

**If Test Fails**:
1. Drop to inner loop (unit tests)
2. Implement missing components
3. Refactor if needed
4. Return to outer loop
5. Verify acceptance test passes

**If Stuck**:
1. Review architecture document
2. Check production service integration
3. Validate test data
4. Pair with reviewer
5. Consider simpler approach

---

## Handoff to DEVELOP Wave

### Deliverables

1. ✅ Complete Gherkin feature file (39 scenarios covering all 6 user stories)
2. ✅ Step definition templates with production service integration
3. ✅ Implementation order roadmap (this document)
4. ✅ Test data catalog and fixtures
5. ✅ Quality gates and commit strategy

### Next Steps for Developer

1. **Read architecture document** (`docs/architecture/interactive-cli-combat-viewer.md`)
2. **Review feature file** (`tests/e2e/features/cli_combat.feature`)
3. **Study step definitions** (`tests/e2e/test_cli_combat.py`)
4. **Start with Phase 1, Test 1.1** (baseline CLI)
5. **Follow Outside-In TDD**: Acceptance test → Unit tests → Implementation
6. **Commit after each passing test**
7. **Proceed sequentially through phases**

### Support Resources

- **Requirements**: `docs/requirements/interactive-cli-combat-viewer.md`
- **Architecture**: `docs/architecture/interactive-cli-combat-viewer.md`
- **Existing Tests**: `tests/e2e/features/combat_simulation.feature` (9 passing scenarios)
- **Domain Model**: `modules/domain/model/`
- **Application Service**: `modules/application/combat_simulator.py`

---

## Success Criteria

### DEVELOP Wave Complete When:

- [ ] All 18 core scenarios PASS
- [ ] All 8 functional requirements implemented (FR-01 to FR-08)
- [ ] All 6 user stories satisfied (US-01 to US-06)
- [ ] Manual testing confirms emoji/color display on Windows, macOS, Linux
- [ ] No regressions in existing tests (9/9 E2E + 34/34 unit)
- [ ] Code review approved
- [ ] Documentation updated

---

**Document Version**: 1.0
**Last Updated**: 2026-01-09
**Author**: Quinn (acceptance-designer)
**Status**: Ready for DEVELOP Wave Handoff
