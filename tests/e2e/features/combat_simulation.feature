Feature: Combat Simulation
  As a Software Crafter
  I want to watch two characters fight in turn-based combat
  So that I can see disciplined TDD and Clean Architecture in action

  Background:
    Given the combat system is initialized

  Scenario: Full combat with attacker advantage enforcement
    Given a character "Thorin" with 20 HP and 5 attack power
    And a character "Goblin" with 10 HP and 3 attack power
    And dice configured to return initiative rolls [3, 5]
    And dice configured to return combat rolls [4, 2, 6]
    When the combat simulation runs
    Then one character wins the combat
    And the winner is "Thorin"
    And the loser has 0 HP
    And all combat rounds are recorded
    And the attacker advantage rule was enforced

  Scenario: Character with higher agility wins initiative
    Given a character "Thorin" with 20 HP and 5 attack power
    And a character "Goblin" with 10 HP and 3 attack power
    And dice configured to return initiative rolls [3, 5]
    When initiative is rolled
    Then "Thorin" wins initiative with total 28
    And "Goblin" has initiative total 18
    And "Thorin" is designated as attacker for all rounds

  Scenario: Attacker kills defender - no counter-attack occurs
    Given a character "Thorin" with 20 HP and 5 attack power
    And a character "Goblin" with 5 HP and 3 attack power
    And dice configured to return initiative rolls [3, 5]
    And dice configured to return combat rolls [6]
    When the combat simulation runs
    Then "Thorin" wins the combat
    And "Goblin" has 0 HP
    And the final round shows defender damage is 0
    And combat ended after attacker attack with no counter-attack

  Scenario: Defender survives and counter-attacks
    Given a character "Thorin" with 20 HP and 5 attack power
    And a character "Goblin" with 10 HP and 3 attack power
    And dice configured to return initiative rolls [3, 5]
    And dice configured to return combat rolls [4, 2]
    When one combat round executes
    Then "Goblin" survives the attacker strike with 1 HP
    And "Goblin" counter-attacks dealing 5 damage
    And "Thorin" has 15 HP after the round
    And combat has not ended

  Scenario: Character immutability during combat
    Given a character "Legolas" with 18 HP and 5 attack power
    And a character "Orc" with 15 HP and 4 attack power
    When combat damages "Legolas" by 5 HP
    Then a new character is created with 13 HP
    And the original character remains unchanged with 18 HP
    And both characters have the same name "Legolas"

  Scenario: Derived agility reflects current health
    Given a character "Warrior" with 20 HP and 5 attack power
    When the character receives 10 damage
    Then the original character has agility 25
    And the damaged character has agility 15
    And the agility decreased due to HP loss

  # ============================================================================
  # ERROR PATH SCENARIOS - Business rule violation handling
  # ============================================================================

  Scenario: Character creation fails with empty name
    When I attempt to create a character with empty name
    Then character creation fails with error "Name cannot be empty"

  Scenario: Dead character cannot initiate attack
    Given a character "Ghost" with 0 HP and 5 attack power
    And a character "Target" with 20 HP and 3 attack power
    When the dead character attempts to attack
    Then the attack is rejected
    And the target remains unharmed

  Scenario: Initiative tie resolved by first character rule
    Given a character "Elf" with 15 HP and 10 attack power
    And a character "Dwarf" with 20 HP and 5 attack power
    And dice configured to return initiative rolls [5, 5]
    When initiative is rolled
    Then "Elf" wins initiative by first character tie-breaker
    And both characters have initiative total 30
    And both characters have base agility 25
    And first character wins when all else is equal
