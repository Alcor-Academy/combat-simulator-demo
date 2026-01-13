#!/usr/bin/env python3
"""
Manual test script for Combat Simulator
Demonstrates the walking skeleton with visual output
"""

from src.application.combat_simulator import CombatSimulator
from src.domain.model.character import Character
from src.domain.model.combat_result import CombatResult
from src.domain.model.round_result import RoundResult
from src.domain.services.attack_resolver import AttackResolver
from src.domain.services.combat_round import CombatRound
from src.domain.services.initiative_resolver import InitiativeResolver
from src.infrastructure.random_dice_roller import RandomDiceRoller


def print_separator(title: str):
    """Print a visual separator"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def display_character(char: Character, label: str):
    """Display character stats"""
    print(f"{label}:")
    print(f"  Name: {char.name}")
    print(f"  HP: {char.hp}")
    print(f"  Attack Power: {char.attack_power}")
    print(f"  Agility: {char.agility} (derived = HP + Attack)")
    print()


def display_round(round_result: RoundResult, round_num: int):
    """Display a single combat round"""
    print(f"--- Round {round_num} ---")
    print(f"  Attacker: {round_result.attacker.name} (HP: {round_result.attacker.hp})")
    print(f"  Defender: {round_result.defender.name} (HP: {round_result.defender.hp})")

    # Extract damage values from tuple
    # Get damage values directly from RoundResult fields

    print(f"  Attacker deals: {round_result.attacker_damage} damage")
    print(f"  Defender HP after: {round_result.defender_hp_after}")

    if round_result.defender_damage > 0:
        print(f"  Defender counter-attacks: {round_result.defender_damage} damage")
        print(f"  Attacker HP after: {round_result.attacker_hp_after}")
    else:
        print("  Defender DIES - no counter-attack (Attacker Advantage)")

    print()


def display_combat_result(result: CombatResult):
    """Display complete combat result"""
    print_separator("COMBAT RESULT")

    print(f"Winner: {result.winner.name} (HP: {result.winner.hp})")
    print(f"Loser: {result.loser.name} (HP: {result.loser.hp})")
    print(f"Total Rounds: {result.total_rounds}")
    print()

    print("Round History:")
    for i, round_result in enumerate(result.rounds, 1):
        display_round(round_result, i)

    print_separator("END OF COMBAT")


def main():
    """Run manual combat test"""

    print_separator("COMBAT SIMULATOR - MANUAL TEST")

    # Create characters
    hero = Character(name="Hero", hp=50, attack_power=10)

    villain = Character(name="Villain", hp=40, attack_power=8)

    # Display initial stats
    print("Initial Character Stats:\n")
    display_character(hero, "HERO")
    display_character(villain, "VILLAIN")

    # Setup combat simulator with dependency injection
    dice_roller = RandomDiceRoller()
    initiative_resolver = InitiativeResolver(dice_roller)
    attack_resolver = AttackResolver(dice_roller)
    combat_round_service = CombatRound(attack_resolver)

    simulator = CombatSimulator(initiative_resolver, combat_round_service)

    print_separator("COMBAT BEGIN")
    print("Rolling initiative...")
    print()

    # Run combat
    result = simulator.run_combat(hero, villain)

    # Display results
    display_combat_result(result)

    # Verify immutability
    print_separator("VERIFICATION")
    print(f"✓ Result type: {type(result.rounds)}")
    print(f"✓ Rounds are immutable tuple: {isinstance(result.rounds, tuple)}")
    print("✓ All tests should pass: pytest tests/e2e/ -v")


if __name__ == "__main__":
    main()
