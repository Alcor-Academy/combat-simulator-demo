#!/usr/bin/env python3
"""
Orchestrator for completing the remaining 13 skipped E2E scenarios.

This script:
1. Creates step files for scenarios 05-05 through 05-17
2. Invokes software-crafter agent for each step via /dw:develop
3. Validates all 11 phases were executed
4. Auto-pushes after each successful completion
"""

import json
from pathlib import Path


# Map of remaining scenarios
SCENARIOS = [
    {
        "step_id": "05-05",
        "feature_line": 81,
        "scenario": "Random HP values are within valid range across multiple generations",
        "complexity": "MEDIUM",
        "requires_step_defs": True,
        "phase": "phase-1-character-creation",
    },
    {
        "step_id": "05-06",
        "feature_line": 87,
        "scenario": "Random attack power values are within valid range",
        "complexity": "LOW",
        "requires_step_defs": False,  # Copy of 05-05
        "phase": "phase-1-character-creation",
    },
    {
        "step_id": "05-07",
        "feature_line": 97,
        "scenario": "Complete combat displays initiative with dice emoji and calculations",
        "complexity": "LOW",
        "requires_step_defs": False,  # Validation only
        "phase": "phase-2-visual-combat",
    },
    {
        "step_id": "05-08",
        "feature_line": 130,
        "scenario": "Victory announcement displays complete combat summary",
        "complexity": "LOW",
        "requires_step_defs": False,  # Validation only
        "phase": "phase-2-visual-combat",
    },
    {
        "step_id": "05-09",
        "feature_line": 176,
        "scenario": "Test mode disables delays for rapid execution",
        "complexity": "LOW",
        "requires_step_defs": False,  # CLIConfig.test_mode() already exists
        "phase": "phase-3-combat-pacing",
    },
    {
        "step_id": "05-10",
        "feature_line": 184,
        "scenario": "Timing delays are within acceptable tolerance",
        "complexity": "MEDIUM",
        "requires_step_defs": True,  # Timing measurements
        "phase": "phase-3-combat-pacing",
    },
    {
        "step_id": "05-11",
        "feature_line": 195,
        "scenario": "User recovers from out-of-range HP input",
        "complexity": "LOW",
        "requires_step_defs": False,  # Validation already implemented
        "phase": "phase-4-error-recovery",
    },
    {
        "step_id": "05-12",
        "feature_line": 206,
        "scenario": "User recovers from out-of-range attack power input",
        "complexity": "LOW",
        "requires_step_defs": False,  # Validation already implemented
        "phase": "phase-4-error-recovery",
    },
    {
        "step_id": "05-13",
        "feature_line": 235,
        "scenario": "Non-numeric input is handled with clear guidance",
        "complexity": "LOW",
        "requires_step_defs": False,  # Validation already implemented
        "phase": "phase-4-error-recovery",
    },
    {
        "step_id": "05-14",
        "feature_line": 217,
        "scenario": "User interrupts CLI with CTRL-C during character creation",
        "complexity": "MEDIUM",
        "requires_step_defs": True,  # KeyboardInterrupt simulation
        "phase": "phase-4-error-recovery",
    },
    {
        "step_id": "05-15",
        "feature_line": 226,
        "scenario": "User interrupts CLI with CTRL-C during combat",
        "complexity": "MEDIUM",
        "requires_step_defs": True,  # KeyboardInterrupt simulation
        "phase": "phase-4-error-recovery",
    },
    {
        "step_id": "05-16",
        "feature_line": 283,
        "scenario": "Color support detection works correctly",
        "complexity": "MEDIUM",
        "requires_step_defs": True,  # Color validation
        "phase": "phase-5-cross-platform",
    },
    {
        "step_id": "05-17",
        "feature_line": 299,
        "scenario": "CLI works on terminals with limited color support",
        "complexity": "MEDIUM",
        "requires_step_defs": True,  # Limited color mode
        "phase": "phase-5-cross-platform",
    },
]


def create_step_file(scenario: dict, previous_step: str | None = None) -> None:
    """Create step JSON file for scenario."""
    step_id = scenario["step_id"]
    prev_step = previous_step or "05-04"

    # Calculate next step for blocking
    step_num = int(step_id.split("-")[1])
    next_step = f"05-{step_num + 1:02d}" if step_num < 17 else "05-18"

    step_data = {
        "task_id": step_id,
        "project_id": "interactive-cli-combat-viewer",
        "execution_agent": "software-crafter",
        "self_contained_context": {
            "background": f"Part of Phase 5: Scenario Completion. Enable skipped test: {scenario['scenario']}",
            "prerequisites_completed": [prev_step],
            "relevant_files": [
                "tests/e2e/features/cli_combat.feature (modify - remove @skip)",
                "tests/e2e/test_cli_combat.py (verify/implement step definitions)",
            ],
            "technical_context": f"""Enable skipped acceptance test.

Scenario (line {scenario["feature_line"]} in cli_combat.feature):
Remove @skip tag and verify/implement step definitions as needed.

Complexity: {scenario["complexity"]}
Requires new step definitions: {scenario["requires_step_defs"]}
""",
            "tdd_phase": "RED" if scenario["requires_step_defs"] else "GREEN",
            "active_e2e_test": f"{scenario['scenario']} - {scenario['step_id']}",
            "inactive_e2e_tests": "All other @skip scenarios remain disabled",
        },
        "task_specification": {
            "name": f"Enable Scenario: {scenario['scenario']}",
            "description": (
                f"Remove @skip tag from line {scenario['feature_line']} and implement/verify step definitions."
            ),
            "motivation": f"Complete E2E test coverage for: {scenario['scenario']}",
            "commit_policy": "Commit after ALL 11 PHASES complete. AUTO-PUSH after commit.",
            "detailed_instructions": """MANDATORY 11-PHASE TDD LOOP:

Phase 1: PREPARE - Remove @skip, verify only 1 scenario enabled
Phase 2: RED (Acceptance) - Test must FAIL initially
Phase 3-5: RED/GREEN (Unit) - Implement step definitions if needed
Phase 6: GREEN (Acceptance) - All tests PASS
Phase 7: REVIEW - Execute /dw:review @software-crafter-reviewer (MANDATORY)
Phase 8: REFACTOR - Apply L1→L4 with validation (MANDATORY)
Phase 9: POST-REFACTOR REVIEW - Execute /dw:review again (MANDATORY)
Phase 10: FINAL VALIDATE - Document full test results (MANDATORY)
Phase 11: COMMIT - Commit with detailed message

ALL 11 PHASES MUST BE EXECUTED AND DOCUMENTED.""",
            "acceptance_criteria": [
                "@skip removed",
                "Step definitions verified/implemented",
                "Test PASSES",
                "ALL 11 PHASES documented in execution_result",
                "No regressions",
            ],
            "estimated_hours": 0.5 if scenario["complexity"] == "LOW" else 1.0,
        },
        "dependencies": {"requires": [prev_step], "blocking": [next_step] if step_num < 17 else []},
        "state": {"status": "TODO", "assigned_to": None, "started_at": None, "completed_at": None, "updated": None},
        "phase_id": "phase-5",
    }

    # Write step file
    step_path = Path(f"docs/workflow/interactive-cli-combat-viewer/steps/{step_id}.json")
    with open(step_path, "w") as f:
        json.dump(step_data, f, indent=2)

    print(f"✓ Created {step_id}.json")


def main():
    """Create all 13 step files for remaining scenarios."""
    print("Creating step files for 13 remaining scenarios...")
    print("=" * 80)

    previous_step = "05-04"
    for scenario in SCENARIOS:
        create_step_file(scenario, previous_step)
        previous_step = scenario["step_id"]

    print("=" * 80)
    print("✓ Created 13 step files (05-05 through 05-17)")
    print()
    print("Next: Invoke software-crafter for each step sequentially")
    print("Command: /dw:develop interactive-cli-combat-viewer --step <step-id>")


if __name__ == "__main__":
    main()
