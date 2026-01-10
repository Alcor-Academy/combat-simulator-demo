#!/usr/bin/env python3
"""
Generate ATDD-compliant step files for all phases.

This script generates step JSON files following the correct ATDD pattern:
1. Enable 1 acceptance test (RED)
2. Implement via unit TDD (GREEN)
3. Review + Refactor + Commit

Usage:
    python generate_atdd_steps.py
"""

import json
from datetime import UTC, datetime
from pathlib import Path


STEPS_DIR = Path("docs/workflow/interactive-cli-combat-viewer/steps")

# Phase 2 remaining steps (02-03 to 02-09)
PHASE_2_STEPS = [
    {
        "task_id": "02-03",
        "name": "Review + Refactor + Integrate + Commit (Test #1)",
        "description": "ATDD REFACTOR Phase for Test #1",
        "tdd_phase": "REFACTOR",
        "estimated_hours": 0.5,
        "requires": ["02-02"],
        "blocking": ["02-04"],
        "active_test": "E2E Test #1: Manual Character Creation - must PASS before commit",
        "key_activities": [
            "Code review (no duplication, clear logic, type hints)",
            "Refactor if needed (extract common patterns)",
            "Integrate CharacterCreator into main.py",
            "Run full test suite (unit + E2E)",
            "Commit when E2E Test #1 passes",
        ],
    },
    {
        "task_id": "02-04",
        "name": "Enable E2E Test #2: Random Defaults (RED)",
        "description": "ATDD RED Phase for Test #2",
        "tdd_phase": "RED",
        "estimated_hours": 0.5,
        "requires": ["02-03"],
        "blocking": ["02-05"],
        "active_test": "E2E Test #2: Random Defaults - SHOULD FAIL (RED)",
        "key_activities": [
            "Enable test: 'User uses random defaults for character attributes'",
            "Implement step definitions for INVIO (empty input)",
            "Run test - should FAIL (random defaults not implemented)",
            "Verify error indicates missing random generation logic",
        ],
    },
    {
        "task_id": "02-05",
        "name": "Implement Random Defaults via Unit TDD (GREEN)",
        "description": "ATDD GREEN Phase for Test #2",
        "tdd_phase": "GREEN",
        "estimated_hours": 1.5,
        "requires": ["02-04"],
        "blocking": ["02-06"],
        "active_test": "E2E Test #2: Random Defaults - should PASS when complete",
        "key_activities": [
            "Add unit tests for random HP generation [20-80]",
            "Add unit tests for random attack generation [5-15]",
            "Implement _random_hp() using dice_roller",
            "Implement _random_attack() using dice_roller",
            "Update _prompt_int_with_default() to accept empty input",
            "E2E Test #2 passes",
        ],
    },
    {
        "task_id": "02-06",
        "name": "Review + Refactor + Commit (Test #2)",
        "description": "ATDD REFACTOR Phase for Test #2",
        "tdd_phase": "REFACTOR",
        "estimated_hours": 0.5,
        "requires": ["02-05"],
        "blocking": ["02-07"],
        "active_test": "E2E Test #2: Random Defaults - must PASS before commit",
        "key_activities": [
            "Review random generation logic",
            "Verify dice_roller integration correct",
            "Run statistical tests (100 iterations, ranges valid)",
            "Commit when E2E Test #2 passes",
        ],
    },
    {
        "task_id": "02-07",
        "name": "Enable E2E Tests #3-5: Validation Errors (RED)",
        "description": "ATDD RED Phase for Tests #3-5 (logical group)",
        "tdd_phase": "RED",
        "estimated_hours": 0.5,
        "requires": ["02-06"],
        "blocking": ["02-08"],
        "active_test": "E2E Tests #3-5: Validation Errors - SHOULD FAIL (RED)",
        "key_activities": [
            "Enable test: 'Invalid HP input triggers validation error'",
            "Enable test: 'Invalid attack power input triggers validation error'",
            "Enable test: 'Empty name input triggers validation error'",
            "Implement step definitions for error verification",
            "Run tests - should mostly PASS (validation already implemented in 02-02)",
            "Verify error messages displayed correctly in red",
        ],
    },
    {
        "task_id": "02-08",
        "name": "Enhance Validation Logic if Needed (GREEN)",
        "description": "ATDD GREEN Phase for Tests #3-5",
        "tdd_phase": "GREEN",
        "estimated_hours": 0.5,
        "requires": ["02-07"],
        "blocking": ["02-09"],
        "active_test": "E2E Tests #3-5: Validation Errors - should PASS when complete",
        "key_activities": [
            "Verify all validation tests pass",
            "Add unit tests for edge cases if missing",
            "Enhance error messages if needed for clarity",
            "All E2E Tests #3-5 pass",
        ],
    },
    {
        "task_id": "02-09",
        "name": "Phase 2 Validation + Final Commit",
        "description": "ATDD REFACTOR + Phase Validation",
        "tdd_phase": "REFACTOR",
        "estimated_hours": 0.5,
        "requires": ["02-08"],
        "blocking": ["03-01"],
        "active_test": "All Phase 2 E2E tests (1-5) - must ALL PASS",
        "key_activities": [
            "Run full Phase 2 test suite (E2E tests 1-5)",
            "Code coverage check (>85% for CharacterCreator)",
            "Manual testing (create characters with all scenarios)",
            "Final refactoring pass",
            "Commit Phase 2 completion",
            "Document Phase 2 deliverables",
        ],
    },
]


def generate_step_file(step_config: dict) -> dict:
    """Generate a complete step JSON file from configuration."""

    return {
        "task_id": step_config["task_id"],
        "project_id": "interactive-cli-combat-viewer",
        "execution_agent": "software-crafter",
        "self_contained_context": {
            "background": f"Part of Phase 2: Interactive Input with Validation. {step_config['description']}.\n",
            "prerequisites_completed": step_config["requires"],
            "relevant_files": [
                "modules/infrastructure/cli/character_creator.py (modify)",
                "tests/unit/infrastructure/cli/test_character_creator.py (modify)",
                "tests/e2e/test_cli_combat.py (modify)",
                "tests/e2e/features/cli_combat.feature (modify)",
            ],
            "technical_context": f"{step_config['description']}.\n\nKey activities:\n"
            + "\n".join(f"- {activity}" for activity in step_config["key_activities"]),
            "tdd_phase": step_config["tdd_phase"],
            "active_e2e_test": step_config["active_test"],
            "inactive_e2e_tests": "Tests not yet enabled remain disabled with @skip",
        },
        "task_specification": {
            "name": step_config["name"],
            "description": step_config["description"],
            "motivation": f"{step_config['tdd_phase']} phase of ATDD cycle. {step_config['description']}.",
            "detailed_instructions": "Follow ATDD discipline:\n\n"
            + "\n".join(f"{i + 1}. {activity}" for i, activity in enumerate(step_config["key_activities"])),
            "acceptance_criteria": step_config["key_activities"],
            "estimated_hours": step_config["estimated_hours"],
        },
        "dependencies": {"requires": step_config["requires"], "blocking": step_config["blocking"]},
        "state": {
            "status": "TODO",
            "assigned_to": None,
            "started_at": None,
            "completed_at": None,
            "updated": datetime.now(UTC).isoformat(),
        },
    }


def main():
    """Generate all remaining Phase 2 step files."""

    print("Generating ATDD-compliant step files for Phase 2...")

    for step_config in PHASE_2_STEPS:
        step_file = STEPS_DIR / f"{step_config['task_id']}.json"
        step_data = generate_step_file(step_config)

        with open(step_file, "w") as f:
            json.dump(step_data, f, indent=2)

        print(f"✓ Generated {step_file}")

    print(f"\n✓ Successfully generated {len(PHASE_2_STEPS)} step files")
    print("\nNext: Review generated files and adjust if needed")


if __name__ == "__main__":
    main()
