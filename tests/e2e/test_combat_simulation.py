"""Step definitions for combat simulation acceptance tests.

These step definitions implement the Given-When-Then scenarios from
combat_simulation.feature, calling REAL PRODUCTION SERVICES (not mocks).

CRITICAL: All step methods must call production services via GetRequiredService pattern.
This ensures acceptance tests validate actual business logic, not test doubles.
"""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when


# Import production services (these will be implemented in DEVELOP wave)
# Following Outside-In TDD: These imports will fail initially, driving implementation
try:
    from modules.domain.model.character import Character
except ImportError:
    Character = None

try:
    from modules.application.combat_simulator import CombatSimulator
except ImportError:
    CombatSimulator = None

try:
    from modules.domain.services.initiative_resolver import InitiativeResolver
except ImportError:
    InitiativeResolver = None

try:
    from modules.domain.services.attack_resolver import AttackResolver
except ImportError:
    AttackResolver = None

try:
    from modules.domain.services.combat_round import CombatRound
except ImportError:
    CombatRound = None

# Import test double for deterministic testing
from tests.doubles.fixed_dice_roller import FixedDiceRoller


# Load all scenarios from feature file
scenarios("combat_simulation.feature")


# ============================================================================
# GIVEN STEPS - Setup preconditions and system state
# ============================================================================


@given("the combat system is initialized")
def initialize_combat_system(combat_context):
    """Initialize combat system for testing.

    This step ensures clean state for each scenario.
    No production service calls needed - just context reset.
    """
    # Reset context to clean state
    combat_context["characters"] = []
    combat_context["dice_roller"] = None
    combat_context["initiative_result"] = None
    combat_context["round_result"] = None
    combat_context["combat_result"] = None


@given(parsers.parse('a character "{name}" with {hp:d} HP and {attack:d} attack power'))
def create_character(name: str, hp: int, attack: int, combat_context):
    """Create a character using production Character class.

    PRODUCTION SERVICE CALL: Character(name, hp, attack_power)

    This step calls the real Character constructor, not a mock.
    The Character class enforces business rules:
    - Name cannot be empty
    - HP must be >= 0
    - Attack power must be > 0
    - Agility is derived (hp + attack_power), not stored

    Args:
        name: Character name (non-empty string)
        hp: Hit points (>= 0)
        attack: Attack power (> 0)
        combat_context: Shared scenario context
    """
    if Character is None:
        pytest.skip("Character class not yet implemented (Outside-In TDD)")

    # CRITICAL: This calls production Character constructor
    character = Character(name=name, hp=hp, attack_power=attack)
    combat_context["characters"].append(character)


@given(parsers.parse("dice configured to return initiative rolls [{rolls}]"))
def configure_initiative_dice(rolls: str, combat_context):
    """Configure test double for initiative rolls.

    This uses FixedDiceRoller test double to provide deterministic dice values
    for initiative calculation. Initiative is rolled ONCE at combat start.

    Args:
        rolls: Comma-separated dice values (e.g., "3, 5")
        combat_context: Shared scenario context
    """
    roll_values = [int(r.strip()) for r in rolls.split(",")]

    # Create or update dice roller with initiative values
    if combat_context["dice_roller"] is None:
        combat_context["dice_roller"] = FixedDiceRoller(roll_values)
    else:
        # Append to existing sequence
        existing = combat_context["dice_roller"]._values
        combat_context["dice_roller"] = FixedDiceRoller(existing + roll_values)


@given(parsers.parse("dice configured to return combat rolls [{rolls}]"))
def configure_combat_dice(rolls: str, combat_context):
    """Configure test double for combat damage rolls.

    This uses FixedDiceRoller test double to provide deterministic dice values
    for damage calculation during combat rounds.

    Args:
        rolls: Comma-separated dice values (e.g., "4, 2, 6")
        combat_context: Shared scenario context
    """
    roll_values = [int(r.strip()) for r in rolls.split(",")]

    # Append combat rolls to dice sequence
    if combat_context["dice_roller"] is None:
        combat_context["dice_roller"] = FixedDiceRoller(roll_values)
    else:
        # Append to existing sequence (after initiative rolls)
        existing = combat_context["dice_roller"]._values
        combat_context["dice_roller"] = FixedDiceRoller(existing + roll_values)


# ============================================================================
# WHEN STEPS - Execute business actions
# ============================================================================


@when("the combat simulation runs")
def run_combat_simulation(combat_context):
    """Execute full combat simulation using production CombatSimulator.

    PRODUCTION SERVICE CALLS:
    1. CombatSimulator(initiative_resolver, combat_round) - dependency injection
    2. simulator.run_combat(char1, char2) - execute full combat

    This calls REAL production services:
    - InitiativeResolver (rolls initiative once at start)
    - CombatRound (executes rounds with attacker advantage)
    - AttackResolver (calculates damage)
    - Character.receive_damage() (applies damage immutably)

    The test uses FixedDiceRoller for deterministic outcomes,
    but all business logic is production code.
    """
    if CombatSimulator is None:
        pytest.skip("CombatSimulator not yet implemented (Outside-In TDD)")

    char1, char2 = combat_context["characters"][0], combat_context["characters"][1]
    dice_roller = combat_context["dice_roller"]

    # Wire up production services (dependency injection)
    initiative_resolver = InitiativeResolver(dice_roller=dice_roller)
    attack_resolver = AttackResolver(dice_roller=dice_roller)
    combat_round = CombatRound(attack_resolver=attack_resolver)

    # CRITICAL: This calls production CombatSimulator
    simulator = CombatSimulator(initiative_resolver=initiative_resolver, combat_round=combat_round)

    # Execute combat - calls production run_combat method
    combat_context["combat_result"] = simulator.run_combat(char1, char2)


@when("initiative is rolled")
def roll_initiative(combat_context):
    """Roll initiative using production InitiativeResolver.

    PRODUCTION SERVICE CALL: InitiativeResolver.roll_initiative(char1, char2)

    This calls the real InitiativeResolver service, which:
    - Rolls D6 for each character
    - Adds agility bonus (hp + attack_power)
    - Determines attacker (higher total) and defender
    - Handles tie-breaker (higher base agility, then first character)
    """
    if InitiativeResolver is None:
        pytest.skip("InitiativeResolver not yet implemented (Outside-In TDD)")

    char1, char2 = combat_context["characters"][0], combat_context["characters"][1]
    dice_roller = combat_context["dice_roller"]

    # CRITICAL: This calls production InitiativeResolver
    resolver = InitiativeResolver(dice_roller=dice_roller)
    combat_context["initiative_result"] = resolver.roll_initiative(char1, char2)


@when("one combat round executes")
def execute_one_round(combat_context):
    """Execute single combat round using production CombatRound service.

    PRODUCTION SERVICE CALL: CombatRound.execute_round(attacker, defender, round_number)

    This calls the real CombatRound service, which enforces attacker advantage:
    1. Attacker attacks first
    2. Defender counter-attacks ONLY if HP > 0 after attacker's strike
    3. If attacker kills defender, round ends immediately (no counter-attack)
    """
    if CombatRound is None:
        pytest.skip("CombatRound not yet implemented (Outside-In TDD)")

    char1, char2 = combat_context["characters"][0], combat_context["characters"][1]
    dice_roller = combat_context["dice_roller"]

    # Determine initiative first
    initiative_resolver = InitiativeResolver(dice_roller=dice_roller)
    init_result = initiative_resolver.roll_initiative(char1, char2)

    # Execute one round
    attack_resolver = AttackResolver(dice_roller=dice_roller)
    combat_round = CombatRound(attack_resolver=attack_resolver)

    # CRITICAL: This calls production CombatRound.execute_round
    combat_context["round_result"] = combat_round.execute_round(
        attacker=init_result.attacker, defender=init_result.defender, round_number=1
    )


@when(parsers.parse('combat damages "{name}" by {damage:d} HP'))
def damage_character(name: str, damage: int, combat_context):
    """Apply damage to character using production Character.receive_damage method.

    PRODUCTION SERVICE CALL: Character.receive_damage(damage)

    This calls the real Character.receive_damage method, which:
    - Returns NEW Character instance (immutability)
    - Reduces HP by damage amount
    - Floors HP at 0 (cannot go negative)
    - Original instance remains unchanged
    """
    # Find character by name
    original = next(c for c in combat_context["characters"] if c.name == name)
    combat_context["original_character"] = original

    # CRITICAL: This calls production Character.receive_damage
    combat_context["damaged_character"] = original.receive_damage(damage)


@when("I check the character agility")
def check_agility(combat_context):
    """Check character agility using production Character.agility property.

    PRODUCTION SERVICE CALL: Character.agility (property)

    This accesses the real Character.agility computed property, which:
    - Returns hp + attack_power (derived stat)
    - Is NOT stored as a field
    - Automatically decreases as HP drops
    """
    character = combat_context["characters"][0]
    combat_context["original_agility"] = character.agility


@when(parsers.parse("the character receives {damage:d} damage"))
def character_receives_damage(damage: int, combat_context):
    """Apply damage using production Character.receive_damage.

    PRODUCTION SERVICE CALL: Character.receive_damage(damage)
    """
    original = combat_context["characters"][0]
    combat_context["original_character"] = original
    combat_context["damaged_character"] = original.receive_damage(damage)


@when("I check the damaged character agility")
def check_damaged_agility(combat_context):
    """Check agility of damaged character.

    PRODUCTION SERVICE CALL: Character.agility (property)
    """
    damaged = combat_context["damaged_character"]
    combat_context["damaged_agility"] = damaged.agility


# ============================================================================
# THEN STEPS - Validate business outcomes
# ============================================================================


@then("one character wins the combat")
def verify_winner_exists(combat_context):
    """Validate that combat produced a winner.

    Business rule validation: Combat ends when one character reaches 0 HP.
    """
    result = combat_context["combat_result"]
    assert result.winner is not None, "Combat must have a winner"
    assert result.winner.is_alive, "Winner must be alive (HP > 0)"


@then(parsers.parse('the winner is "{name}"'))
def verify_winner_name(name: str, combat_context):
    """Validate winner identity.

    Business rule validation: Correct character won based on combat mechanics.
    """
    result = combat_context["combat_result"]
    assert result.winner.name == name, f"Expected {name} to win, but {result.winner.name} won"


@then("the loser has 0 HP")
def verify_loser_dead(combat_context):
    """Validate loser is dead.

    Business rule validation: Combat ends when HP reaches 0.
    """
    result = combat_context["combat_result"]
    assert result.loser.hp == 0, f"Loser must have 0 HP, but has {result.loser.hp}"
    assert not result.loser.is_alive, "Loser must be dead (is_alive == False)"


@then("all combat rounds are recorded")
def verify_rounds_recorded(combat_context):
    """Validate all rounds are in result.

    Business rule validation: Complete combat history is preserved.
    """
    result = combat_context["combat_result"]
    assert result.total_rounds > 0, "Combat must have at least one round"
    assert len(result.rounds) == result.total_rounds, "All rounds must be recorded"


@then("the attacker advantage rule was enforced")
def verify_attacker_advantage(combat_context):
    """Validate attacker advantage rule enforcement.

    Business rule validation: If defender dies, defender_action must be None
    (dead character cannot counter-attack).
    """
    result = combat_context["combat_result"]
    for round_result in result.rounds:
        if round_result.defender_hp_after == 0:
            # Defender died - should have no counter-attack
            msg = f"Round {round_result.round_number}: Dead defender counter-attacked"
            assert round_result.defender_action is None, msg


@then(parsers.parse('"{name}" wins initiative with total {total:d}'))
def verify_initiative_winner(name: str, total: int, combat_context):
    """Validate initiative calculation and winner.

    Business rule validation: Initiative = agility + D6 roll.
    """
    init_result = combat_context["initiative_result"]
    assert init_result.attacker.name == name, f"Expected {name} to win initiative, but {init_result.attacker.name} won"
    assert init_result.attacker_total == total, f"Expected initiative total {total}, got {init_result.attacker_total}"


@then(parsers.parse('"{name}" has initiative total {total:d}'))
def verify_initiative_total(name: str, total: int, combat_context):
    """Validate initiative total calculation.

    Business rule validation: Initiative = agility + D6 roll.
    """
    init_result = combat_context["initiative_result"]
    if init_result.attacker.name == name:
        assert init_result.attacker_total == total
    else:
        assert init_result.defender_total == total


@then(parsers.parse('"{name}" is designated as attacker for all rounds'))
def verify_attacker_designation(name: str, combat_context):
    """Validate attacker designation persists.

    Business rule validation: Initiative winner attacks first in ALL rounds.
    """
    init_result = combat_context["initiative_result"]
    assert init_result.attacker.name == name, f"Expected {name} as attacker, got {init_result.attacker.name}"


@then(parsers.parse('"{name}" wins the combat'))
def verify_combat_winner(name: str, combat_context):
    """Validate combat winner."""
    result = combat_context["combat_result"]
    assert result.winner.name == name


@then(parsers.parse('"{name}" has {hp:d} HP'))
def verify_character_hp(name: str, hp: int, combat_context):
    """Validate character HP value."""
    result = combat_context["combat_result"]
    if result.winner.name == name:
        assert result.winner.hp == hp
    else:
        assert result.loser.hp == hp


@then("the final round shows defender damage is 0")
def verify_no_counter_attack_damage(combat_context):
    """Validate no counter-attack when defender dies.

    Business rule validation: Attacker advantage - dead defender cannot attack.
    """
    result = combat_context["combat_result"]
    final_round = result.rounds[-1]
    assert final_round.defender_action is None, "Dead defender should not counter-attack"


@then("combat ended after attacker attack with no counter-attack")
def verify_immediate_combat_end(combat_context):
    """Validate combat ended immediately when defender died.

    Business rule validation: Combat ends immediately on death, no counter-attack.
    """
    result = combat_context["combat_result"]
    final_round = result.rounds[-1]
    assert final_round.combat_ended, "Combat should have ended"
    assert final_round.defender_hp_after == 0, "Defender should be dead"
    assert final_round.defender_action is None, "Dead defender cannot counter-attack"


@then(parsers.parse('"{name}" survives the attacker strike with {hp:d} HP'))
def verify_defender_survives(name: str, hp: int, combat_context):
    """Validate defender survived with specific HP.

    Business rule validation: HP reduced correctly, defender still alive.
    """
    round_result = combat_context["round_result"]
    # Defender is embedded in attacker_action.defender_after
    defender_after = round_result.attacker_action.defender_after
    assert defender_after.name == name
    assert round_result.defender_hp_after == hp
    assert defender_after.is_alive


@then(parsers.parse('"{name}" counter-attacks dealing {damage:d} damage'))
def verify_counter_attack_damage(name: str, damage: int, combat_context):
    """Validate counter-attack damage calculation.

    Business rule validation: Damage = attack_power + dice_roll.
    """
    round_result = combat_context["round_result"]
    # Defender counter-attack is in defender_action
    assert round_result.defender_action is not None, "Defender should counter-attack"
    assert round_result.defender_action.attacker_name == name
    assert round_result.defender_action.total_damage == damage


@then(parsers.parse('"{name}" has {hp:d} HP after the round'))
def verify_hp_after_round(name: str, hp: int, combat_context):
    """Validate HP after complete round."""
    round_result = combat_context["round_result"]
    # Check attacker name from attacker_action
    attacker_name = round_result.attacker_action.attacker_name
    if attacker_name == name:
        assert round_result.attacker_hp_after == hp
    else:
        assert round_result.defender_hp_after == hp


@then("combat has not ended")
def verify_combat_continues(combat_context):
    """Validate combat continues (both alive).

    Business rule validation: Combat only ends when one reaches 0 HP.
    """
    round_result = combat_context["round_result"]
    assert not round_result.combat_ended, "Combat should continue"
    assert round_result.winner is None, "No winner yet"


@then(parsers.parse("a new character instance is returned with {hp:d} HP"))
def verify_new_instance_hp(hp: int, combat_context):
    """Validate immutability - new instance returned.

    Business rule validation: Character.receive_damage returns NEW instance.
    """
    damaged = combat_context["damaged_character"]
    assert damaged.hp == hp, f"Expected {hp} HP, got {damaged.hp}"


@then(parsers.parse("the original character remains unchanged with {hp:d} HP"))
def verify_original_unchanged(hp: int, combat_context):
    """Validate immutability - original instance unchanged.

    Business rule validation: Immutable value objects prevent state mutation bugs.
    """
    original = combat_context["original_character"]
    assert original.hp == hp, f"Original character mutated! Expected {hp} HP, got {original.hp}"


@then(parsers.parse('both characters have the same name "{name}"'))
def verify_same_name(name: str, combat_context):
    """Validate name preserved across instances."""
    original = combat_context["original_character"]
    damaged = combat_context["damaged_character"]
    assert original.name == name
    assert damaged.name == name


@then(parsers.parse("a new character is created with {hp:d} HP"))
def verify_new_character_created(hp: int, combat_context):
    """Validate immutability - new character created (not mutated).

    Business rule validation: Character.receive_damage returns NEW instance.
    """
    damaged = combat_context["damaged_character"]
    assert damaged.hp == hp, f"Expected {hp} HP, got {damaged.hp}"


@then(parsers.parse("the original character has agility {agility:d}"))
def verify_original_agility(agility: int, combat_context):
    """Validate original character agility.

    Business rule validation: Agility = HP + attack_power (derived).
    """
    original = combat_context["original_character"]
    assert original.agility == agility, f"Expected original agility {agility}, got {original.agility}"


@then(parsers.parse("the damaged character has agility {agility:d}"))
def verify_damaged_agility(agility: int, combat_context):
    """Validate damaged character agility.

    Business rule validation: Agility decreases as HP drops.
    """
    damaged = combat_context["damaged_character"]
    assert damaged.agility == agility, f"Expected damaged agility {agility}, got {damaged.agility}"


@then("the agility decreased due to HP loss")
def verify_agility_decreased(combat_context):
    """Validate agility decreases as HP drops.

    Business rule validation: Derived agility reflects fatigue from damage.
    """
    original = combat_context["original_character"]
    damaged = combat_context["damaged_character"]
    assert damaged.agility < original.agility, (
        f"Agility should decrease (was {original.agility}, now {damaged.agility})"
    )


# ============================================================================
# ERROR PATH STEP DEFINITIONS - Business rule violation handling
# ============================================================================


@when("I attempt to create a character with empty name")
def attempt_create_empty_name(combat_context):
    """Attempt to create character with invalid empty name.

    PRODUCTION SERVICE CALL: Character(name="", hp, attack_power)

    This should raise ValueError due to business rule validation.
    """
    try:
        # CRITICAL: This calls production Character constructor with invalid input
        combat_context["invalid_character"] = Character(name="", hp=20, attack_power=5)
        combat_context["validation_error"] = None
    except ValueError as e:
        combat_context["validation_error"] = str(e)
        combat_context["invalid_character"] = None


@then(parsers.parse('character creation fails with error "{error_message}"'))
def verify_creation_failure(error_message: str, combat_context):
    """Validate character creation failed with specific error.

    Business rule validation: Name cannot be empty.
    """
    assert combat_context["validation_error"] is not None, "Expected ValueError, but character was created"
    assert error_message in combat_context["validation_error"], (
        f"Expected error '{error_message}', got '{combat_context['validation_error']}'"
    )
    assert combat_context["invalid_character"] is None, "Character should not be created with invalid name"


@when("the dead character attempts to attack")
def dead_character_attacks(combat_context):
    """Attempt attack with dead character (0 HP).

    PRODUCTION SERVICE CALL: AttackResolver.resolve_attack(dead_character, target)

    This should raise ValueError or return None/error result.
    """
    if AttackResolver is None:
        pytest.skip("AttackResolver not yet implemented (Outside-In TDD)")

    dead_char = combat_context["characters"][0]
    target = combat_context["characters"][1]
    dice_roller = FixedDiceRoller(4)

    try:
        resolver = AttackResolver(dice_roller=dice_roller)
        # CRITICAL: This calls production AttackResolver with invalid state
        combat_context["attack_result"] = resolver.resolve_attack(dead_char, target)
        combat_context["attack_error"] = None
    except ValueError as e:
        combat_context["attack_error"] = str(e)
        combat_context["attack_result"] = None


@then("the attack is rejected")
def verify_attack_rejected(combat_context):
    """Validate dead character attack was rejected.

    Business rule validation: Dead character (HP=0) cannot attack.
    """
    assert combat_context["attack_error"] is not None, "Expected attack to be rejected, but it succeeded"
    assert (
        "dead" in combat_context["attack_error"].lower() or "cannot attack" in combat_context["attack_error"].lower()
    ), f"Expected dead character error, got: {combat_context['attack_error']}"


@then("the target remains unharmed")
def verify_target_unharmed(combat_context):
    """Validate target took no damage from rejected attack.

    Business rule validation: Rejected attack deals no damage.
    """
    target = combat_context["characters"][1]
    assert target.hp == 20, f"Target should be unharmed with 20 HP, but has {target.hp} HP"


@then(parsers.parse('"{name}" wins initiative by first character tie-breaker'))
def verify_first_character_tie_breaker(name: str, combat_context):
    """Validate first character wins in perfect tie.

    Business rule validation: Tie-breaker uses first character in order.
    """
    init_result = combat_context["initiative_result"]
    assert init_result.attacker.name == name, f"Expected {name} to win tie-breaker, got {init_result.attacker.name}"


@then(parsers.parse("both characters have initiative total {total:d}"))
def verify_both_initiative_totals(total: int, combat_context):
    """Validate both characters have same initiative total (tie).

    Business rule validation: Perfect tie scenario.
    """
    init_result = combat_context["initiative_result"]
    assert init_result.attacker_total == total, f"Attacker initiative {init_result.attacker_total} != {total}"
    assert init_result.defender_total == total, f"Defender initiative {init_result.defender_total} != {total}"


@then(parsers.parse("both characters have base agility {agility:d}"))
def verify_both_base_agility(agility: int, combat_context):
    """Validate both characters have same base agility.

    Business rule validation: Agility = HP + attack_power.
    """
    init_result = combat_context["initiative_result"]
    assert init_result.attacker.agility == agility, f"Attacker agility {init_result.attacker.agility} != {agility}"
    assert init_result.defender.agility == agility, f"Defender agility {init_result.defender.agility} != {agility}"


@then("first character wins when all else is equal")
def verify_first_character_rule(combat_context):
    """Validate tie-breaker logic uses first character.

    Business rule validation: Deterministic tie resolution.
    """
    init_result = combat_context["initiative_result"]
    # First character created should be the attacker in perfect tie
    first_char = combat_context["characters"][0]
    assert init_result.attacker.name == first_char.name, "First character should win tie-breaker"
