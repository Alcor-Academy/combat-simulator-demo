# Combat Simulator Demo - Software Crafters Event

## Demo Objective

Demonstrate how Claude Code + disciplined framework (Outside-In TDD, ATDD, Clean Architecture) produces production-ready code, not "AI-generated spaghetti."

**Key message:** AI amplifies your practices. If you have discipline, you get excellent code. If not, you get garbage quickly.

---

## Combat Rules (Clarified)

These rules govern all combat mechanics. They are explicit to prevent implementation ambiguity.

### Death Rule: Attacker Advantage

- First attacker resolves their attack fully
- Defender counter-attacks **only if they survive** (HP > 0)
- If attacker kills defender, round ends immediately - no counter-attack
- Ties are **impossible** due to sequential resolution

### Attack Order: Initiative Roll

- Initiative is rolled **once at fight start** (not every round)
- Each character rolls a D6 and adds their **Agility bonus**
- Higher total wins initiative and attacks first **every round** for the entire combat
- Winner of initiative is called the "attacker", loser is "defender"

### Derived Stat: Agility

- **Agility = Attack Power + Current HP**
- This is a derived stat, not stored separately
- Represents fatigue: as you take damage, HP drops, so Agility drops
- Used only for initiative calculation at fight start (uses starting HP)

### Dice Boundaries

- All dice are D6: returns value in range **[1, 6] inclusive**
- Never returns 0, never returns 7
- Same DiceRoller port used for combat rolls AND character stat generation

### Damage Calculation

- **Total Damage = Attack Power + Die Roll**
- No caps, no floors, no armor, no critical hits (simplified D&D)
- HP cannot go below 0 (floor at 0)

---

## Functional Requirements

### Epic: Combat Simulator CLI

Two characters face off in simplified D&D-style turn-based combat. Combat is fully automated with detailed round-by-round output.

---

### Feature 1: Character Creation (15 min)

**User Story:**
> As a player, I want to create a character with randomly generated stats, so I can participate in combat with unique characters.

**Acceptance Criteria:**

```gherkin
Scenario: Create character with random stats
  Given a DiceRoller that returns [4, 3] for HP rolls and [2] for Attack roll
  When I create a character named "Thorin"
  Then the character has name "Thorin"
  And the character has HP calculated from dice rolls (e.g., 4+3 = 7 base, scaled)
  And the character has Attack Power from dice roll
  And the character has Agility = Attack Power + HP (derived, not stored)

Scenario: Create character with fixed stats for testing
  Given a FixedDiceRoller configured for predictable values
  When I create a character "Thorin" resulting in 20 HP and 5 Attack
  Then the character has name "Thorin"
  And the character has 20 HP
  And the character has 5 Attack Power
  And the character has Agility of 25 (20 + 5)

Scenario: Check if character is alive
  Given a character with HP > 0
  When I check if it's alive
  Then it returns true

Scenario: Check if character is dead
  Given a character with HP = 0
  When I check if it's alive
  Then it returns false

Scenario: Character name cannot be empty
  Given I attempt to create a character with name ""
  Then creation fails with ValidationError "Name cannot be empty"
```

**Expected Outcome:**

- `Character` immutable value object with: name, hp, attackPower
- `agility` is a computed property: `get agility() { return this.hp + this.attackPower }`
- Factory method using DiceRoller for random generation
- FixedDiceRoller for deterministic tests
- No setters, illegal state not representable
- 4-5 unit tests

**Wow moment:** Show how Claude proposes a constructor with validation, you guide toward immutable Value Object with derived Agility.

---

### Feature 2: Dice Rolling System (10 min)

**User Story:**
> As a combat system, I need to generate random numbers to simulate dice, while keeping the system testable.

**Acceptance Criteria:**

```gherkin
Scenario: Roll a D6 returns valid range
  Given a 6-sided die (D6)
  When it is rolled
  Then it returns a value in range [1, 6] inclusive
  And it never returns 0
  And it never returns 7

Scenario: Deterministic dice for testing
  Given a FixedDiceRoller configured with sequence [4, 2, 6]
  When rolled three times
  Then it returns 4, then 2, then 6 in order

Scenario: Fixed single value for simple tests
  Given a FixedDiceRoller configured to always return 4
  When rolled any number of times
  Then it always returns 4
```

**Expected Outcome:**

- `DiceRoller` as Port (interface) with `roll(): number`
- `RandomDiceRoller` adapter for production
- `FixedDiceRoller` test double with constructor injection: `new FixedDiceRoller([4, 2, 6])` or `new FixedDiceRoller(4)`
- Dependency Injection via constructor for all consumers

**Wow moment:** Hexagonal Architecture emerges naturally. The audience sees the Port/Adapter pattern applied to something simple.

---

### Feature 3: Initiative Roll (5 min)

**User Story:**
> As the combat system, I need to determine who attacks first based on an initiative roll at the start of combat.

**Acceptance Criteria:**

```gherkin
Scenario: Determine initiative at combat start
  Given "Thorin" with Agility 25 (HP 20 + Attack 5)
  And "Goblin" with Agility 13 (HP 10 + Attack 3)
  And dice configured for [3, 5] (Thorin rolls 3, Goblin rolls 5)
  When initiative is rolled
  Then Thorin's initiative = 25 + 3 = 28
  And Goblin's initiative = 13 + 5 = 18
  And Thorin wins initiative (28 > 18)
  And Thorin is designated as "attacker" for all rounds

Scenario: Initiative tie-breaker
  Given two characters with equal initiative totals
  When initiative is rolled
  Then the character with higher base Agility wins
  Or if still tied, first character in order wins (deterministic)
```

**Expected Outcome:**

- `InitiativeResult` value object with attacker and defender
- Initiative calculated once, stored for combat duration
- Clear winner determination with tie-breaker rules

---

### Feature 4: Attack Resolution (15 min)

**User Story:**
> As a player, I want to attack an enemy and see the damage calculated based on the die roll and my attack power.

**Acceptance Criteria:**

```gherkin
Scenario: Calculate attack damage
  Given attacker with Attack Power 5
  And a die that returns 3
  When attack is resolved
  Then the total damage is 8 (5 + 3)

Scenario: Apply damage to defender (immutability)
  Given defender "Goblin" with 20 HP
  And inflicted damage of 8
  When the damage is applied
  Then a NEW Character instance is returned with 12 HP
  And the original Goblin still has 20 HP (immutable)

Scenario: Damage floors at 0 HP
  Given defender with 5 HP
  And inflicted damage of 10
  When the damage is applied
  Then the defender has 0 HP (not -5)
```

**Expected Outcome:**

- `AttackResult` value object with: attacker, defender, dieRoll, damage, defenderAfter
- `Character.receiveDamage(amount)` returns new Character instance (immutability)
- 4-5 unit tests

**Wow moment:** Character.receiveDamage() returns new Character, doesn't mutate. Audience sees immutability in practice.

---

### Feature 5: Combat Round (15 min)

**User Story:**
> As a player, I want to execute a combat round where the attacker strikes first, and the defender counter-attacks only if they survive.

**Acceptance Criteria:**

```gherkin
Scenario: Both characters attack in single round (no death)
  Given "Thorin" (attacker) with 20 HP and 5 Attack Power
  And "Goblin" (defender) with 10 HP and 3 Attack Power
  And dice configured for [4, 2] (Thorin's attack roll, Goblin's counter-attack roll)
  When I execute a combat round
  Then Thorin's attack resolves FIRST: deals 9 damage (5+4) to Goblin
  And Goblin survives with 1 HP (10-9)
  And Goblin's counter-attack resolves SECOND: deals 5 damage (3+2) to Thorin
  And Thorin has 15 HP remaining
  And round result shows both attacks in sequence

Scenario: Attacker kills defender - no counter-attack (Attacker Advantage)
  Given "Thorin" (attacker) with 20 HP and 5 Attack Power
  And "Goblin" (defender) with 5 HP and 3 Attack Power
  And dice configured for [6] (only one roll needed - Goblin dies)
  When I execute a combat round
  Then Thorin's attack resolves: deals 11 damage (5+6) to Goblin
  And Goblin reaches 0 HP and is dead
  And Goblin does NOT get to counter-attack
  And round ends immediately
  And victory condition is met

Scenario: Round result output format
  Given a completed combat round
  When RoundResult is created
  Then it contains:
    | Field | Description |
    | attacker | Character who attacked first |
    | defender | Character who defended |
    | attackerRoll | Die roll for attacker |
    | defenderRoll | Die roll for defender (0 if dead) |
    | attackerDamage | Damage dealt by attacker |
    | defenderDamage | Damage dealt by defender (0 if dead) |
    | attackerHPAfter | Attacker HP after round |
    | defenderHPAfter | Defender HP after round |
    | combatEnded | Boolean - true if someone died |
    | winner | Character or null |
```

**CLI Output Format:**

```
Round 1:
  Thorin attacks Goblin for 9 damage!
  Goblin (1 HP) counter-attacks Thorin for 5 damage!
  Status: Thorin 15 HP | Goblin 1 HP
```

**Expected Outcome:**

- `CombatRound` orchestrator that enforces attacker advantage rule
- `RoundResult` value object with all fields above
- DiceRoller injected via constructor
- Working CLI walking skeleton

**Wow moment:** The game works E2E! The audience sees something playable born from rigorous TDD.

---

### Feature 6: Game Loop (10 min)

**User Story:**
> As a player, I want combat to run automatically through multiple rounds until one character dies, seeing each round's action unfold.

**Acceptance Criteria:**

```gherkin
Scenario: Fully automated combat to victory
  Given "Thorin" with 20 HP, 5 Attack
  And "Goblin" with 10 HP, 3 Attack
  And Thorin wins initiative
  When I execute "fight"
  Then combat runs automatically round by round
  And each round displays attacker action and defender reaction
  And combat continues until one character has 0 HP
  And winner is declared with victory message

Scenario: Combat output shows progression
  Given combat between Thorin and Goblin
  When combat executes
  Then output shows:
    | Round 1: Thorin attacks... Goblin counter-attacks... |
    | Round 2: Thorin attacks... Goblin counter-attacks... |
    | ... |
    | VICTORY: Thorin wins! Goblin has been defeated. |

Scenario: Combat ends immediately on death
  Given combat in progress
  When a character reaches 0 HP mid-round
  Then combat ends immediately (attacker advantage)
  And no further rounds execute
  And survivor is declared winner
```

**Expected Outcome:**

- `CombatSimulator` use case that orchestrates full combat
- Outputs detailed round-by-round log
- Victory message clearly identifies winner
- Fully automated - no user interaction during combat

---

### Feature 7: Victory Condition (5 min) - REQUIRED

**User Story:**
> As a player, I want to know when combat is over and who won.

**Acceptance Criteria:**

```gherkin
Scenario: Victory when opponent dies
  Given combat in progress
  When a character reaches 0 HP
  Then combat ends immediately
  And the surviving character is declared winner
  And victory message displays: "[Winner] wins! [Loser] has been defeated."

Scenario: Victory message format
  Given Thorin defeats Goblin
  When victory is declared
  Then output shows:
    | ================================== |
    | VICTORY! Thorin wins!              |
    | Goblin has been defeated.          |
    | Final HP: Thorin 15 | Goblin 0     |
    | ================================== |
```

**Expected Outcome:**

- `CombatResult` value object with winner, loser, final states
- Clear, formatted victory message for audience readability

---

## Detailed Timeline

| Phase | Time | Activity | Presenter Notes |
| ----- | ---- | -------- | --------------- |
| **Setup** | 0:00-0:03 | Show CLAUDE.md, explain the framework | "Here are the rules Claude must follow" |
| **Walking Skeleton** | 0:03-0:08 | Failing E2E test, base structure | First wow: Claude understands outside-in |
| **Feature 1** | 0:08-0:20 | Character with TDD + Agility | Show red-green-refactor cycle |
| **Feature 2** | 0:20-0:28 | DiceRoller + Port/Adapter | Wow: Hexagonal emerges |
| **Feature 3** | 0:28-0:33 | Initiative Roll | Quick win, sets up combat order |
| **Feature 4** | 0:33-0:43 | Attack with immutability | Wow: no mutations |
| **Feature 5** | 0:43-0:53 | Combat Round with Attacker Advantage | Core mechanic demo |
| **Feature 6+7** | 0:53-0:58 | Game Loop + Victory | Grand finale: it works! |
| **Q&A** | 0:58-1:00 | Questions | |

---

## Expected Architecture

```text
src/
├── domain/
│   ├── Character.ts          # Value Object (name, hp, attackPower, agility)
│   ├── AttackResult.ts       # Value Object
│   ├── RoundResult.ts        # Value Object
│   ├── CombatResult.ts       # Value Object (victory)
│   ├── InitiativeResult.ts   # Value Object
│   └── ports/
│       └── DiceRoller.ts     # Port (interface)
├── infrastructure/
│   └── RandomDiceRoller.ts   # Adapter
├── application/
│   ├── CombatRound.ts        # Domain Service
│   └── CombatSimulator.ts    # Use Case (game loop)
└── cli/
    └── main.ts               # Entry point

test/
├── domain/
│   ├── Character.test.ts
│   ├── AttackResult.test.ts
│   └── InitiativeResult.test.ts
├── application/
│   ├── CombatRound.test.ts
│   └── CombatSimulator.test.ts
├── doubles/
│   └── FixedDiceRoller.ts    # Test Double
└── e2e/
    └── CombatSimulator.e2e.test.ts
```

---

## Wow Moments Not to Miss

1. **CLAUDE.md in action** (0:03)
   - "Watch, I tell it to do outside-in TDD and it starts from the E2E test"

2. **Derived Agility stat** (0:15)
   - "Agility isn't stored - it's computed from HP + Attack. As you take damage, you get slower!"

3. **Test Double emerges naturally** (0:25)
   - "I can't test with random dice. Claude, how do we solve this?"
   - Claude proposes Port/Adapter

4. **Forced immutability** (0:40)
   - "I don't like this setter. How do we make it immutable?"
   - Character.receiveDamage() → new Character

5. **Attacker Advantage in action** (0:50)
   - "Watch what happens when Thorin kills Goblin - no counter-attack!"

6. **The game works** (0:55)
   - CLI run, live combat with round-by-round output
   - "55 minutes, rigorous TDD, and we have a working game"

7. **Code coverage and design** (closing)
   - "100% coverage, zero implementation mocking, clean architecture"

---

## Risks and Mitigations

| Risk | Probability | Mitigation |
| ---- | ----------- | ---------- |
| Claude goes off track | Medium | Robust CLAUDE.md + manual interrupt |
| Time overrun | Medium | Features 6+7 can be compressed |
| Unexpected live bug | High | Embrace it! Show debugging with AI |
| Skeptical audience | Medium | Emphasize the process, not the product |
| WSL crashes | Low | Local backup ready |

---

## Suggested CLAUDE.md for the Demo

```markdown
# Combat Simulator - Demo Rules

## Development Methodology
- ALWAYS use TDD with Outside-In approach
- Write ONE failing test, then minimal code to pass
- Refactor only when tests are green
- No code without a failing test first

## Architecture
- Hexagonal Architecture: Ports and Adapters
- Domain objects are immutable Value Objects
- No setters, use factory methods or builders
- Make illegal states unrepresentable via types
- Agility is DERIVED (hp + attackPower), never stored

## Combat Rules
- Attacker Advantage: first attacker resolves, defender counter-attacks only if alive
- Initiative rolled once at fight start using Agility + D6
- Damage = Attack Power + Die Roll (no caps, no armor)
- HP floors at 0

## Testing
- Test behavior through public API only
- Use test doubles for external dependencies (randomness)
- No mocking of internal implementation
- E2E test as walking skeleton first
- FixedDiceRoller injected via constructor

## Code Style
- Favor immutability
- Small functions, single responsibility
- No comments that explain "what", only "why" if needed
- Types over runtime checks
```

---

## Pre-Demo Checklist

- [ ] CLAUDE.md configured and tested
- [ ] Empty repository ready
- [ ] Claude Code authenticated and working
- [ ] Terminal font size enlarged for projection
- [ ] WSL stable
- [ ] Timer visible
- [ ] Backup: pre-recorded video of critical parts
- [ ] Test FixedDiceRoller with known sequences

---

## Suggested Opening Line

> "Today I'm not showing you how good Claude is at generating code. I'm showing you how good it is at following rules. MY rules. OUR rules as software crafters."
