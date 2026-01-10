# ATDD Step Restructuring Plan

**Date**: 2026-01-10
**Purpose**: Restructure step files to follow proper Acceptance Test Driven Development (ATDD) pattern

## Problem Statement

Current step files violate ATDD principle: **enable one acceptance test at a time**.

### ATDD Pattern (Correct)

```
1. Enable 1 Acceptance Test (or tightly coupled logical group) → RED
2. Implement via Inner Loop Unit TDD → GREEN
3. Review + Refactor (if needed) → REFACTOR
4. Commit when test passes
5. Repeat for next acceptance test
```

### Current Violations

**Phase 2** (Interactive Input):
- 02-01: Acceptance criteria says "5 E2E tests enabled" (should be 1)
- 02-04: "Enable 3 additional E2E tests" (should be 1)
- Consequence: Tests not iterated one at a time

**Phase 3** (Visual Enhancement):
- 03-01: Correctly enables 1 test ✓
- Structure seems better, needs verification

**Phase 4** (Polish):
- 04-01: "Enable tests for victory celebration and exit" (3 tests - too many)

**Phase 5** (Cross-Platform):
- 05-01: "Enable tests for cross-platform emoji" (3 tests - too many)

## Acceptance Test Inventory

### Phase 1: Baseline (COMPLETE - no changes needed)
- 01-01 to 01-06: Already completed, validated

### Phase 2: Interactive Input with Validation
Acceptance tests (from step files):
1. "User creates both characters with manual input"
2. "User uses random defaults for character attributes"
3. "Invalid HP input triggers validation error and re-prompt"
4. "Invalid attack power input triggers validation error"
5. "Empty name input triggers validation error"

**Logical grouping**:
- TEST #1: Basic manual character creation (test 1)
- TEST #2: Random defaults (test 2)
- TESTS #3-5: Validation errors (tests 3-5 - tightly coupled, test same validation logic)

**Target structure**: 9 steps
```
02-01: Enable TEST #1 (manual input) → RED
02-02: Implement CharacterCreator base → GREEN (inner loop unit TDD)
02-03: Review + Refactor + Commit

02-04: Enable TEST #2 (random defaults) → RED
02-05: Enhance for random defaults → GREEN
02-06: Review + Refactor + Commit

02-07: Enable TESTS #3-5 (validation - logical group) → RED
02-08: Enhance validation logic → GREEN
02-09: Review + Refactor + Commit + Phase 2 validation checkpoint
```

### Phase 3: Visual Enhancement (Emoji, Colors, Pacing)
Acceptance tests (from step files):
1. "Combat round displays all event details with emoji"
2. (Need to identify other tests from remaining steps)

**Preliminary structure**: ~6-9 steps (needs verification)
```
03-01: Enable TEST #1 (emoji visualization) → RED
03-02: Add emoji configuration → GREEN (unit TDD)
03-03: Enhance renderer with emoji → GREEN
03-04: Review + Refactor + Commit

03-05: Enable TEST #2 (colors/pacing) → RED
03-06: Implement colors and pacing → GREEN
03-07: Review + Refactor + Commit + Phase 3 validation
```

### Phase 4: Polish (Exit, Errors, Edge Cases)
Acceptance tests (from step files):
1. "Victory celebration shows all required information"
2. "Exit confirmation waits for user keypress"
3. "CTRL-C during exit confirmation terminates program"

**Logical grouping**:
- TESTS #1-3: Exit and victory (tightly coupled - all about program termination)

**Target structure**: 3-6 steps
```
04-01: Enable TESTS #1-3 (victory + exit) → RED
04-02: Implement victory and exit handling → GREEN
04-03: Review + Refactor + Commit + Phase 4 validation
```

### Phase 5: Cross-Platform Compatibility
Acceptance tests (from step files):
1. "Emoji display correctly on Unicode-capable terminals"
2. "Graceful degradation for terminals without emoji support"
3. "Cross-platform emoji fallback mapping"

**Logical grouping**:
- TESTS #1-3: All test emoji fallback strategy (tightly coupled)

**Target structure**: 3 steps
```
05-01: Enable TESTS #1-3 (emoji fallback) → RED
05-02: Verify fallback logic (likely already implemented) → GREEN
05-03: Review + Manual cross-platform testing + Commit + Final validation
```

## Implementation Plan

### Step 1: Backup Current State ✓
- Current step files already in git

### Step 2: Restructure Phase 2 (02-01 to 02-09)
- Split current 6 steps into 9 steps
- Maintain atomic task granularity
- Update dependencies

### Step 3: Restructure Phase 3 (03-01 to 03-07)
- Verify acceptance test inventory
- Adjust step count if needed
- Update dependencies

### Step 4: Restructure Phase 4 (04-01 to 04-03)
- Consolidate related tests (victory + exit)
- Simplify to 3 steps

### Step 5: Restructure Phase 5 (05-01 to 05-03)
- Consolidate cross-platform tests
- Simplify to 3 steps

### Step 6: Validate Consistency
- Check all dependencies chain correctly
- Verify estimated hours are reasonable
- Ensure no gaps in coverage

## Validation Criteria

After restructuring, verify:
- [ ] Each step enables max 1 acceptance test (or tightly coupled logical group with clear justification)
- [ ] RED-GREEN-REFACTOR cycle is explicit in step sequence
- [ ] Commits happen AFTER tests pass (GREEN), not before
- [ ] Dependencies are sequential and logical
- [ ] Total estimated hours match roadmap (22-36 hours)
- [ ] All original acceptance tests are covered

## Notes

### Tightly Coupled Logical Groups - When Allowed

It's acceptable to enable multiple tests together ONLY when:
1. Tests validate the SAME feature from different angles
2. Implementation is the SAME code path (no separate work needed)
3. Tests cannot reasonably pass independently

**Example (VALID)**:
- "Invalid HP input shows error"
- "Invalid attack input shows error"
- "Empty name shows error"
→ All test the SAME validation method with different inputs

**Example (INVALID)**:
- "Manual character creation works"
- "Random defaults work"
- "Validation works"
→ These are DIFFERENT features requiring DIFFERENT implementation

### Review Step Purpose

Review steps should include:
- Code quality check
- Identify refactoring opportunities
- Verify acceptance criteria met
- Run full test suite
- Check for technical debt

Can invoke `/dw:review` command for adversarial validation.

### Commit Policy

NEVER commit with failing tests. Commit only when:
- Active acceptance test(s) PASS
- All unit tests PASS
- No regressions (Phase 1 tests still pass)
- Pre-commit hooks succeed

## Timeline

- Analysis and planning: 0.5h (DONE)
- Restructuring Phase 2: 0.5h
- Restructuring Phases 3-5: 0.5h
- Validation and testing: 0.5h
- **Total**: ~2 hours

## Success Criteria

Restructuring successful when:
1. All step files follow ATDD pattern
2. 02-01 execution_result correctly reflects "1 test enabled"
3. No acceptance criteria mention "5 tests" or "3 tests" (unless justified logical group)
4. Dependency chain is clean and sequential
5. Software-crafter agent can execute steps without confusion

---

**Status**: PLAN COMPLETE - Ready for implementation
**Next Action**: Begin restructuring Phase 2 step files (02-01 to 02-09)
