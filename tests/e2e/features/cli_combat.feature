# language: en
Feature: Interactive CLI Combat Viewer
  As a user of the combat simulator
  I want to interactively create characters and watch them battle
  So that I can see the combat system in action with engaging visual feedback

  Background:
    Given the CLI is launched

  # ============================================================================
  # BASELINE: Minimum Viable CLI (Phase 1)
  # ============================================================================

  Scenario: Baseline CLI runs hardcoded combat
    Given two characters are created: Hero (HP 50, attack 10) and Villain (HP 40, attack 8)
    When combat starts
    Then combat executes
    And combat ends after attacker action
    And exit code is 0

  # ============================================================================
  # US-01: Interactive Character Creation
  # ============================================================================

  Scenario: User creates both characters with manual input
    When I enter "Hero" for character 1 name
    And I enter "50" for character 1 HP
    And I enter "10" for character 1 attack power
    And I enter "Villain" for character 2 name
    And I enter "40" for character 2 HP
    And I enter "8" for character 2 attack power
    Then both characters are created successfully
    And character 1 has name "Hero", HP 50, attack power 10, agility 60
    And character 2 has name "Villain", HP 40, attack power 8, agility 48
    And both character summary cards are displayed

  @skip
  Scenario: User uses random defaults for character attributes
    When I enter "Hero" for character 1 name
    And I press INVIO for character 1 HP
    And I press INVIO for character 1 attack power
    Then character 1 HP is randomly generated in range [20-80]
    And character 1 attack power is randomly generated in range [5-15]
    And character 1 agility is calculated as HP plus attack power

  @skip
  Scenario: Invalid HP input triggers validation error and re-prompt
    When I enter "Hero" for character 1 name
    And I enter "150" for character 1 HP
    Then validation error is displayed in red
    And error message contains "HP must be between 1 and 999"
    And I am re-prompted for character 1 HP
    When I enter "50" for character 1 HP
    Then character creation continues successfully

  @skip
  Scenario: Invalid attack power input triggers validation error
    When I enter "Hero" for character 1 name
    And I enter "50" for character 1 HP
    And I enter "0" for character 1 attack power
    Then validation error is displayed in red
    And error message contains "Attack power must be between 1 and 99"
    And I am re-prompted for character 1 attack power
    When I enter "10" for character 1 attack power
    Then character creation continues successfully

  @skip
  Scenario: Empty name input triggers validation error
    When I enter "" for character 1 name
    Then validation error is displayed
    And error message contains "Name cannot be empty"
    And I am re-prompted for character 1 name
    When I enter "Hero" for character 1 name
    Then character creation continues successfully

  @skip
  Scenario: Non-numeric HP input triggers validation error
    When I enter "Hero" for character 1 name
    And I enter "abc" for character 1 HP
    Then validation error is displayed
    And error message contains "must be a whole number"
    And I am re-prompted for character 1 HP

  @skip
  Scenario: Random HP values are within valid range across multiple generations
    When I create 10 characters using random HP defaults
    Then all random HP values are in range [20-80]
    And no random HP value is outside specified bounds

  @skip
  Scenario: Random attack power values are within valid range
    When I create 10 characters using random attack defaults
    Then all random attack power values are in range [5-15]
    And no random attack value is outside specified bounds

  # ============================================================================
  # US-02: Visual Combat Progress Display
  # ============================================================================

  @skip
  Scenario: Complete combat displays initiative with dice emoji and calculations
    Given two characters are created: Hero (HP 50, attack 10) and Villain (HP 40, attack 8)
    When combat starts
    Then initiative roll is displayed with 🎲 emoji
    And initiative shows Hero agility value
    And initiative shows Villain agility value
    And initiative shows dice rolls for both characters
    And initiative shows calculated totals for both characters
    And initiative announces who attacks first with ⚡ emoji

  @skip
  Scenario: Combat round displays all event details with emoji
    Given two characters are created: Hero (HP 50, attack 10) and Villain (HP 40, attack 8)
    When combat starts
    Then each combat round displays round number
    And attacker action shows ⚔️ emoji
    And attack details show dice roll with 🎲 emoji
    And attack details show attack power
    And attack details show total damage with 💥 emoji
    And HP change shows old HP → new HP with ❤️ emoji
    And defender counter-attack shows 🛡️ emoji if defender survives
    And death announcement shows ☠️ emoji when character dies

  @skip
  Scenario: HP tracking accuracy throughout combat
    Given Hero starts with HP 50
    And Villain starts with HP 40
    When Hero attacks and deals 14 damage
    Then Villain HP changes from 40 to 26
    And display shows "Villain: 40 HP → 26 HP"
    When Villain counter-attacks and deals 12 damage
    Then Hero HP changes from 50 to 38
    And display shows "Hero: 50 HP → 38 HP"

  @skip
  Scenario: Victory announcement displays complete combat summary
    Given combat completes with Hero as winner
    Then victory banner is displayed with 🏆 emoji
    And winner name is shown in victory message
    And loser name is shown with ☠️ emoji
    And total rounds fought is displayed
    And winner final HP is displayed
    And loser final HP shows 0 HP

  @skip
  Scenario: Extended combat displays all rounds with consistent formatting
    Given two balanced characters are created
    When combat runs for 7 rounds
    Then all 7 rounds are displayed with consistent formatting
    And each round shows round number
    And no output is truncated or skipped
    And all combat events are shown in full detail

  @skip
  Scenario: Defender death prevents counter-attack display
    Given two characters are created: Hero (HP 50, attack 10) and Villain (HP 5, attack 8)
    And combat will result in lethal damage to Villain in round 1
    When combat starts
    Then Hero attack is displayed
    And Villain HP changes to 0
    And death announcement is displayed for Villain
    And Villain counter-attack is NOT displayed
    And combat ends after attacker action

  @skip
  Scenario: Initiative tie-breaker is transparently explained
    Given two characters with identical agility values
    When initiative is rolled with identical dice results
    Then tie-breaker message is displayed
    And tie-breaker rule explanation is shown
    And first character wins by tie-breaker rule

  # ============================================================================
  # US-03: Combat Pacing Control (Fixed Timing)
  # ============================================================================

  @skip
  Scenario: Combat uses fixed timing delays between rounds
    Given two characters are created
    When combat executes with default timing configuration
    Then delay between rounds is approximately 1.5-2 seconds
    And delays are consistent across all rounds
    And timing accuracy is within ±0.2 second tolerance

  @skip
  Scenario: Test mode disables delays for rapid execution
    Given CLI is launched in test mode
    When combat executes
    Then all delays are zero seconds
    And combat completes in less than 1 second total
    And output content is identical to normal mode

  @skip
  Scenario: Timing delays are within acceptable tolerance
    Given combat with 5 rounds
    When delays are measured during execution
    Then each delay is approximately 1.5 seconds with ±0.2s tolerance
    And total combat time is approximately 7.5-10 seconds

  # ============================================================================
  # US-04: Clear Error Recovery
  # ============================================================================

  @skip
  Scenario: User recovers from out-of-range HP input
    Given CLI is prompting for HP
    When I enter "999999" for HP
    Then validation error message is displayed
    And error specifies valid HP range [1-999]
    And I am re-prompted for HP
    When I enter "50" for HP
    Then HP input is accepted
    And character creation continues

  @skip
  Scenario: User recovers from out-of-range attack power input
    Given CLI is prompting for attack power
    When I enter "100" for attack power
    Then validation error message is displayed
    And error specifies valid attack power range [1-99]
    And I am re-prompted for attack power
    When I enter "10" for attack power
    Then attack power input is accepted
    And character creation continues

  @skip
  Scenario: User interrupts CLI with CTRL-C during character creation
    Given CLI is prompting for character input
    When I press CTRL-C
    Then program exits gracefully
    And interruption message is displayed
    And no stack trace is shown
    And exit code is 130

  @skip
  Scenario: User interrupts CLI with CTRL-C during combat
    Given combat is in progress
    When I press CTRL-C during combat visualization
    Then program exits gracefully
    And interruption message is displayed
    And no stack trace is shown
    And exit code is 130

  @skip
  Scenario: Non-numeric input is handled with clear guidance
    Given CLI is prompting for HP
    When I enter "strong" for HP
    Then validation error message is displayed
    And error message contains "must be a whole number"
    And I am re-prompted with format hint

  # ============================================================================
  # US-05: Victory Celebration
  # ============================================================================

  @skip
  Scenario: Victory celebration shows all required information
    Given combat completes with Hero winning after 3 rounds
    And Hero has 26 HP remaining
    And Villain has 0 HP
    Then victory banner includes winner name "Hero"
    And victory banner includes 🏆 emoji
    And combat statistics show "3 rounds"
    And winner final HP is displayed as "Hero: 26 HP remaining"
    And loser final HP is displayed as "Villain: 0 HP (defeated)"

  @skip
  Scenario: Exit confirmation waits for user keypress
    Given combat has completed successfully
    When victory banner is displayed
    Then program shows exit prompt "Premi INVIO per uscire (o CTRL-C per terminare)"
    And program waits for user keypress
    And program does not exit automatically
    When I press INVIO
    Then program exits with code 0

  @skip
  Scenario: CTRL-C during exit confirmation terminates program
    Given combat has completed and exit confirmation is shown
    When I press CTRL-C
    Then program exits immediately
    And exit code is 130

  # ============================================================================
  # US-06: Cross-Platform Experience
  # ============================================================================

  @skip
  Scenario: Emoji display correctly on Unicode-capable terminals
    Given terminal supports Unicode emoji
    When combat runs
    Then emoji are rendered correctly: ⚔️ 💥 ❤️ 🎲 🏆 ☠️ 🛡️
    And no placeholder characters appear
    And emoji do not break line formatting

  @skip
  Scenario: Color support detection works correctly
    Given terminal supports 256 colors
    When CLI runs
    Then colors are used for output styling
    And error messages display in red
    And HP values display with health-based color gradient
    And combat events use appropriate colors

  @skip
  Scenario: Graceful degradation for terminals without emoji support
    Given terminal does not support emoji
    When CLI runs
    Then emoji fallback to text equivalents
    And combat remains fully functional
    And all information is conveyed through text symbols

  @skip
  Scenario: CLI works on terminals with limited color support
    Given terminal supports only 16 colors
    When CLI runs
    Then basic color set is used
    And no functionality is lost
    And text remains readable

  @skip
  Scenario: Cross-platform emoji fallback mapping
    Given terminal does not support emoji
    When combat visualization displays events
    Then ⚔️ displays as "[ATK]"
    And 💥 displays as "[DMG]"
    And ❤️ displays as "[HP]"
    And 🎲 displays as "[D6]"
    And ⚡ displays as "[INIT]"
    And 🏆 displays as "[WIN]"
    And ☠️ displays as "[DEAD]"
    And 🛡️ displays as "[DEF]"
