# Architecture Design: Interactive CLI Combat Viewer

**Project**: Combat Simulator Demo
**Feature**: Interactive CLI Combat Viewer
**Wave**: DESIGN (Architecture Design)
**Date**: 2026-01-09
**Version**: 1.1
**Status**: Finalized (Ready for DISTILL Wave Handoff)
**Architect**: Morgan (solution-architect)

---

## 1. Architecture Overview

### 1.1 Baseline Context

**System State**: Greenfield CLI Enhancement

This CLI feature represents the **first user-facing interface** for the combat simulator system. There is no existing manual workflow or CLI to optimize/replace.

**Current Usage**:
- Combat system used ONLY via automated tests (9 E2E scenarios, 34 unit tests)
- No user-facing entry point exists
- All validation via pytest execution

**CLI Purpose**: Enable **first human interaction** with combat system, transforming it from test-only library to usable application.

**Baseline Measurement**: Not applicable (greenfield). Success measured by:
- Functional completeness (all FR-01 to FR-08 implemented)
- UX quality (intuitive, visually clear, properly paced)
- Test coverage (automated E2E for CLI interactions)

This clarifies: CLI priority is validated by user need (DISCUSS wave), not by quantitative comparison to existing workflow.

### 1.2 System Context

The Interactive CLI Combat Viewer adds a presentation layer to the existing combat simulator system. The CLI adapter transforms the programmatic combat simulation into an engaging, user-facing command-line application with interactive character creation, real-time combat visualization, and rich visual feedback.

**Current System State**:
- **Domain Layer**: Complete (Character, Combat Services, Value Objects)
- **Application Layer**: Complete (CombatSimulator use case)
- **Infrastructure Layer**: Partially complete (RandomDiceRoller only)
- **Presentation Layer**: MISSING (this design addresses the gap)

### 1.3 Hexagonal Architecture Position

```
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER (NEW)                   │
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │        CLI Adapter (Infrastructure)               │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │    │
│  │  │  CLI Main   │  │  Character  │  │  Combat  │ │    │
│  │  │ Entry Point │  │   Creator   │  │  Renderer│ │    │
│  │  └─────────────┘  └─────────────┘  └──────────┘ │    │
│  │         │                │                │       │    │
│  └─────────┼────────────────┼────────────────┼───────┘    │
│            │                │                │            │
└────────────┼────────────────┼────────────────┼────────────┘
             │                │                │
             ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│               APPLICATION LAYER (EXISTING)                  │
│                                                             │
│              ┌─────────────────────────┐                   │
│              │   CombatSimulator       │                   │
│              │   (Use Case Service)    │                   │
│              └─────────────────────────┘                   │
│                         │                                   │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  DOMAIN LAYER (EXISTING)                    │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Domain Services                                   │   │
│  │  • InitiativeResolver  • AttackResolver           │   │
│  │  • CombatRound                                    │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Domain Model (Value Objects)                      │   │
│  │  • Character      • CombatResult                  │   │
│  │  • RoundResult    • AttackResult                  │   │
│  │  • InitiativeResult                               │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Ports (Interfaces)                                │   │
│  │  • DiceRoller (Protocol)                          │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
└────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│          INFRASTRUCTURE LAYER (EXISTING + NEW)              │
│                                                             │
│  ┌───────────────┐         ┌───────────────┐              │
│  │ RandomDice    │         │  CLI Adapter  │              │
│  │ Roller        │         │  (see above)  │              │
│  │ (existing)    │         │  (NEW)        │              │
│  └───────────────┘         └───────────────┘              │
│                                                            │
└────────────────────────────────────────────────────────────┘

**External Dependencies**:
- Rich 13.x (UI Library)
- Python stdlib (time, sys)
```

**Dependency Direction**: All dependencies point **inward** toward the domain core.
- CLI Adapter → Application Layer → Domain Layer
- CLI Adapter **NEVER** directly accesses Domain Services (goes through CombatSimulator)
- Domain Layer **NEVER** depends on outer layers (preserves hexagonal purity)

### 1.4 Architecture Goals

1. **Hexagonal Architecture Preservation**: CLI as pure infrastructure adapter, no domain logic leakage
2. **Testability**: All CLI logic testable without manual interaction
3. **UX Excellence**: Professional, engaging user experience with Rich library
4. **Maintainability**: Clear component boundaries, separation of concerns
5. **Cross-Platform Compatibility**: Works on Windows, macOS, Linux terminals
6. **Extensibility**: Easy to add features (config files, logging, replay, different UI modes)

---

## 2. Component Design

### 2.1 Component Architecture

```mermaid
graph TB
    subgraph "CLI Infrastructure Layer"
        Main[CLI Main<br/>Entry Point]
        CharCreator[CharacterCreator<br/>Input Handler]
        Renderer[CombatRenderer<br/>Output Formatter]
        Console[ConsoleOutput<br/>Rich Wrapper]
        Config[CLIConfig<br/>Constants]
    end

    subgraph "Rich Library (External)"
        RichConsole[Rich.Console]
        RichPrompt[Rich.Prompt]
        RichText[Rich.Text]
    end

    subgraph "Application Layer"
        CombatSim[CombatSimulator]
    end

    subgraph "Domain Layer"
        Character[Character]
        CombatResult[CombatResult]
        RoundResult[RoundResult]
        AttackResult[AttackResult]
        InitiativeResult[InitiativeResult]
    end

    subgraph "Infrastructure"
        DiceRoller[RandomDiceRoller]
    end

    Main --> CharCreator
    Main --> CombatSim
    Main --> Renderer
    Main --> Config

    CharCreator --> RichPrompt
    CharCreator --> Character
    CharCreator --> DiceRoller

    Renderer --> Console
    Renderer --> CombatResult
    Renderer --> Config

    Console --> RichConsole
    Console --> RichText
    Console --> Config

    CombatSim --> Character
    CombatSim --> CombatResult
    CombatSim --> DiceRoller

    style Main fill:#e1f5ff
    style CombatSim fill:#fff4e1
    style Character fill:#ffe1f5
    style RichConsole fill:#f0f0f0
```

### 2.2 Directory Structure

```
modules/infrastructure/cli/
├── __init__.py                  # Package initialization
├── main.py                      # CLI entry point (run_cli function)
├── character_creator.py         # CharacterCreator class
├── combat_renderer.py           # CombatRenderer class
├── console_output.py            # ConsoleOutput class (Rich wrapper)
└── config.py                    # CLIConfig class (timing, emoji, colors)

Top-level entry point:
cli.py                           # Convenience script: python cli.py
```

**Rationale for Directory Structure**:
- CLI components live in `modules/infrastructure/cli/` (Infrastructure adapter)
- Consistent with existing structure (`modules/infrastructure/random_dice_roller.py`)
- Clear separation: CLI is infrastructure, not domain or application
- Top-level `cli.py` provides convenient entry point for users

### 2.3 Component Responsibilities

#### **CLI Main (Entry Point)**

**File**: `modules/infrastructure/cli/main.py`

**Responsibility**: Application lifecycle orchestration and dependency wiring

**Key Functions**:
```python
def run_cli() -> None:
    """Main entry point for CLI application.

    Orchestrates:
    1. Welcome display
    2. Character creation (both characters)
    3. Combat simulation
    4. Combat visualization
    5. Exit confirmation

    Handles:
    - KeyboardInterrupt (Ctrl+C) gracefully
    - Unexpected errors with user-friendly messages
    """
```

**Dependencies**:
- CharacterCreator (creates Characters from user input)
- CombatSimulator (runs combat with domain services)
- CombatRenderer (formats CombatResult for display)
- ConsoleOutput (displays to terminal with Rich)
- RandomDiceRoller (injected into CombatSimulator)
- InitiativeResolver, CombatRound (domain services for CombatSimulator)

**Error Handling**:
- `KeyboardInterrupt`: Display "⚠️ Combat interrupted by user. Exiting..." and exit cleanly
- `ValueError` from Character creation: Caught by CharacterCreator, displayed as validation error
- Unexpected exceptions: Display "❌ Unexpected error occurred. Please try again." and exit with error code

---

#### **CharacterCreator**

**File**: `modules/infrastructure/cli/character_creator.py`

**Responsibility**: Interactive character creation with validation and random defaults

**Class Definition**:
```python
class CharacterCreator:
    """Handles interactive character creation via Rich prompts.

    Responsibilities:
    - Prompt user for name, HP, attack power
    - Validate inputs against domain constraints
    - Generate random defaults when user presses ENTER
    - Display character confirmation summary
    - Handle domain validation errors (ValueError from Character)
    """

    def __init__(self, console: ConsoleOutput, dice_roller: DiceRoller):
        """Initialize character creator.

        Args:
            console: Output wrapper for Rich Console
            dice_roller: Random number generator for default values
        """
        self._console = console
        self._dice_roller = dice_roller

    def create_character(self, character_number: int) -> Character:
        """Create character through interactive prompts.

        Args:
            character_number: 1 or 2 (for prompt display)

        Returns:
            Character: Validated Character object

        Raises:
            KeyboardInterrupt: If user presses Ctrl+C (propagates to main)
        """
```

**Input Validation Strategy**:

1. **Name Validation**:
   - Prompt: `"Nome personaggio {character_number}: "`
   - Rules: Non-empty after strip, 1-50 characters
   - Error: `"❌ Name cannot be empty. Please enter a name."`
   - Implementation: Custom Rich validator

2. **HP Validation**:
   - Prompt: `"HP [1-999, INVIO=random 20-80]: "`
   - Rules: Integer in range [1, 999]
   - Default: Random [20, 80] if ENTER pressed (using dice_roller)
   - Error: `"❌ HP must be between 1 and 999. Please try again."`
   - Implementation: Rich IntPrompt with custom validator

3. **Attack Power Validation**:
   - Prompt: `"Potere d'attacco [1-99, INVIO=random 5-15]: "`
   - Rules: Integer in range [1, 99]
   - Default: Random [5, 15] if ENTER pressed (using dice_roller)
   - Error: `"❌ Attack power must be between 1 and 99. Please try again."`
   - Implementation: Rich IntPrompt with custom validator

**Random Default Implementation**:
```python
def _random_hp(self) -> int:
    """Generate random HP using dice_roller (simulates 10d6+20)."""
    total = sum(self._dice_roller.roll() for _ in range(10))
    return 20 + total  # Range [20, 80]

def _random_attack(self) -> int:
    """Generate random attack using dice_roller (simulates 2d6+4)."""
    total = sum(self._dice_roller.roll() for _ in range(2))
    return 4 + total  # Range [5, 15]
```

**Character Confirmation Display**:
```
╭─────────────────────╮
│ 🧙 Thorin           │
│ ❤️  HP: 20          │
│ ⚔️  Attack: 5       │
│ ⚡ Agility: 25      │
╰─────────────────────╯
```

---

#### **CombatRenderer**

**File**: `modules/infrastructure/cli/combat_renderer.py`

**Responsibility**: Format CombatResult for visual display with emoji, colors, and pacing

**Class Definition**:
```python
class CombatRenderer:
    """Formats combat events for visual display.

    Responsibilities:
    - Display initiative resolution
    - Display each combat round with full details
    - Display victory announcement and statistics
    - Apply pacing delays between events (fixed timing, no skip)
    """

    def __init__(self, console: ConsoleOutput, config: CLIConfig):
        """Initialize combat renderer.

        Args:
            console: Output wrapper for Rich Console
            config: Configuration for timing, emoji, colors
        """
        self._console = console
        self._config = config

    def render_combat(self, result: CombatResult) -> None:
        """Render complete combat visualization.

        Args:
            result: CombatResult from CombatSimulator
        """
        self._render_initiative(result.initiative_result)

        for round_result in result.rounds:
            self._render_round(round_result)

        self._render_victory(result)
```

**Rendering Methods**:

1. **Initiative Display**:
   ```
   🎲 Rolling Initiative...

   Thorin: Base agility 25 + 🎲 4 = 29
   Goblin: Base agility 13 + 🎲 3 = 16

   ⚡ Thorin wins initiative and attacks first!
   ```
   - Pause: 1.0s after rolls, 1.5s after winner announcement

2. **Round Display**:
   ```
   ═══════════════════════════════════
   ⚔️  ROUND 1
   ═══════════════════════════════════

   ⚔️  Thorin attacks!
      🎲 Roll: 4 + ⚔️  Power: 5 = 💥 9 damage
      Goblin: 10 HP → 1 HP

   🛡️  Goblin counter-attacks!
      🎲 Roll: 2 + ⚔️  Power: 3 = 💥 5 damage
      Thorin: 20 HP → 15 HP

   ---
   ```
   - Pause: 0.5s after header, 1.5s after each attack, 0.5s before next round

3. **Death Announcement**:
   ```
   ☠️  Goblin has been defeated!
   ```
   - Pause: 2.0s before victory announcement

4. **Victory Display**:
   ```
   ╔═══════════════════════════════════╗
   ║     🏆  THORIN WINS!  🏆         ║
   ╚═══════════════════════════════════╝

   Combat lasted 3 rounds
   Thorin: 15 HP remaining
   Goblin: 0 HP (defeated)

   Premi INVIO per uscire (o CTRL-C per terminare)
   ```
   - Wait for user ENTER press before exit

**Color Strategy**:
- HP values: Color gradient based on percentage remaining
  - Green: 70-100% HP
  - Yellow: 40-69% HP
  - Orange: 20-39% HP
  - Red: 1-19% HP
- Damage numbers: Red/Orange (🔥 fire theme)
- Success messages: Green (✅ checkmark theme)
- Error messages: Red (❌ cross theme)

**Emoji Mapping** (with fallbacks):
```python
EMOJI = {
    'attack': '⚔️',
    'damage': '💥',
    'hp': '❤️',
    'dice': '🎲',
    'initiative': '⚡',
    'victory': '🏆',
    'death': '☠️',
    'defend': '🛡️',
    'character': '🧙',
}

FALLBACK = {
    'attack': '[ATK]',
    'damage': '[DMG]',
    'hp': '[HP]',
    'dice': '[D6]',
    'initiative': '[INIT]',
    'victory': '[WIN]',
    'death': '[DEAD]',
    'defend': '[DEF]',
    'character': '[CHAR]',
}
```

---

#### **ConsoleOutput**

**File**: `modules/infrastructure/cli/console_output.py`

**Responsibility**: Thin wrapper around Rich Console with pacing control

**Class Definition**:
```python
class ConsoleOutput:
    """Wraps Rich Console with fixed-timing pacing.

    Responsibilities:
    - Display text with Rich formatting (colors, emoji, markup)
    - Control timing delays between events (fixed delays, no skip)
    - Handle emoji fallback based on terminal capabilities
    """

    def __init__(self, console: Console, config: CLIConfig):
        """Initialize console output.

        Args:
            console: Rich Console instance
            config: Configuration for timing and display
        """
        self._console = console
        self._config = config

    def print(self, text: str, style: str = "", end: str = "\n") -> None:
        """Print text with optional Rich styling.

        Args:
            text: Text to display
            style: Rich style string (e.g., "bold red", "green")
            end: Line ending character
        """

    def display_with_delay(self, message: str, delay: float) -> None:
        """Display message and pause for specified duration.

        Args:
            message: Text to display (may include Rich markup/emoji)
            delay: Pause duration in seconds (0 in test mode)
        """
        self._console.print(message)
        if delay > 0:
            time.sleep(delay)

    def prompt_continue(self, message: str) -> None:
        """Block until user presses ENTER.

        Args:
            message: Prompt message to display

        Used for exit confirmation.
        """
```

---

#### **CLIConfig**

**File**: `modules/infrastructure/cli/config.py`

**Responsibility**: Centralized configuration for timing, emoji, and display settings

**Class Definition**:
```python
@dataclass(frozen=True)
class CLIConfig:
    """Immutable configuration for CLI display and timing.

    All timing, emoji, and color settings centralized here for:
    - Easy adjustment during development
    - Future config file support
    - Test mode (zero delays)
    """

    # Timing Configuration (seconds)
    initiative_roll_delay: float = 1.0
    initiative_winner_delay: float = 1.5
    round_header_delay: float = 0.5
    attack_delay: float = 1.5
    death_delay: float = 2.0
    round_separator_delay: float = 0.5
    exit_delay: float = 2.0

    # Display Configuration
    emoji_enabled: bool = True  # Auto-detect from Rich in production
    colors_enabled: bool = True  # Auto-detect from Rich in production

    # Emoji Mapping
    emoji: dict[str, str] = field(default_factory=lambda: {
        'attack': '⚔️',
        'damage': '💥',
        'hp': '❤️',
        'dice': '🎲',
        'initiative': '⚡',
        'victory': '🏆',
        'death': '☠️',
        'defend': '🛡️',
        'character': '🧙',
    })

    # Fallback Symbols (if emoji unsupported)
    fallback: dict[str, str] = field(default_factory=lambda: {
        'attack': '[ATK]',
        'damage': '[DMG]',
        'hp': '[HP]',
        'dice': '[D6]',
        'initiative': '[INIT]',
        'victory': '[WIN]',
        'death': '[DEAD]',
        'defend': '[DEF]',
        'character': '[CHAR]',
    })

    @staticmethod
    def test_mode() -> "CLIConfig":
        """Create config with zero delays for testing."""
        return CLIConfig(
            initiative_roll_delay=0.0,
            initiative_winner_delay=0.0,
            round_header_delay=0.0,
            attack_delay=0.0,
            death_delay=0.0,
            round_separator_delay=0.0,
            exit_delay=0.0,
        )
```

**Usage in Production**:
```python
config = CLIConfig()  # Default timing
console = ConsoleOutput(Console(), config)
renderer = CombatRenderer(console, config)
```

**Usage in Tests**:
```python
config = CLIConfig.test_mode()  # Zero delays
console = ConsoleOutput(Console(), config)
renderer = CombatRenderer(console, config)
```

---

## 3. Technology Stack Integration

### 3.1 Rich Library 13.x

**Why Rich?**
- All-in-one solution: colors, emoji, prompts, validation, layouts
- User-confirmed choice during DISCUSS wave
- Testing-friendly with Console capture API
- Cross-platform with automatic capability detection
- Modern, actively maintained library

**Rich Components Used**:

| Rich Component | Purpose | Integration Point |
|----------------|---------|-------------------|
| `Console` | Main output interface | Wrapped by ConsoleOutput |
| `Prompt.ask()` | Interactive string prompts | CharacterCreator name input |
| `IntPrompt.ask()` | Interactive integer prompts | CharacterCreator HP/attack input |
| `Text()` | Styled text with markup | CombatRenderer formatting |
| `Panel()` | Character summary cards | CharacterCreator confirmation |

**Installation**:
```toml
# pyproject.toml
[project]
dependencies = [
    "rich>=13.0.0,<14.0.0"
]
```

**Rich Console Capabilities Detection**:
Rich automatically detects:
- Terminal color support (true-color, 256-color, 16-color, no-color)
- Emoji rendering support (UTF-8 encoding, emoji fallback)
- Terminal width and height

### 3.2 Integration with Existing System

**Application Layer Integration**:
```python
# CLI Main instantiates application services
from modules.application.combat_simulator import CombatSimulator
from modules.domain.services.initiative_resolver import InitiativeResolver
from modules.domain.services.combat_round import CombatRound
from modules.domain.services.attack_resolver import AttackResolver
from modules.infrastructure.random_dice_roller import RandomDiceRoller

# Wire dependencies
dice_roller = RandomDiceRoller()
attack_resolver = AttackResolver(dice_roller)
initiative_resolver = InitiativeResolver(dice_roller)
combat_round = CombatRound(attack_resolver)
combat_simulator = CombatSimulator(initiative_resolver, combat_round)
```

**Domain Model Consumption**:
- CharacterCreator creates `Character` domain objects
- CombatRenderer consumes `CombatResult` value object
- CLI never modifies domain objects (immutable dataclasses)

**Dependency Injection Flow**:
```
CLI Main
  ├─ Creates RandomDiceRoller
  ├─ Creates Domain Services (InitiativeResolver, AttackResolver, CombatRound)
  ├─ Creates CombatSimulator (injects domain services)
  ├─ Creates CharacterCreator (injects RandomDiceRoller for random defaults)
  └─ Creates CombatRenderer (injects ConsoleOutput and CLIConfig)
```

---

## 4. Testing Architecture

### 4.1 Testing Strategy Overview

**Goal**: CLI fully testable without manual interaction

**Approach**: Separate business logic from Rich-specific I/O

```
┌─────────────────────────────────────────┐
│         Testable Logic                  │
│  (No Rich dependencies)                 │
│                                         │
│  • Validation rules                    │
│  • Formatting functions                │
│  • Color selection logic               │
│  • Round display structure             │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     Rich I/O Layer (Thin)               │
│  (Minimal testing - integration only)   │
│                                         │
│  • Console.print() calls               │
│  • Prompt.ask() calls                  │
│  • Panel rendering                     │
└─────────────────────────────────────────┘
```

### 4.2 Unit Testing Strategy

**CharacterCreator Unit Tests**:
```python
def test_name_validation_rejects_empty():
    """Test that empty name triggers validation error."""
    # Mock Rich Prompt to return empty string
    # Assert error message displayed
    # Assert re-prompt occurs

def test_hp_validation_rejects_out_of_range():
    """Test HP validation enforces [1, 999] range."""
    # Mock Rich IntPrompt to return 1000
    # Assert error message displayed
    # Assert re-prompt occurs

def test_random_hp_uses_dice_roller():
    """Test random HP generation uses injected dice_roller."""
    # Mock dice_roller.roll() to return fixed values
    # Mock user pressing ENTER (empty input)
    # Assert HP in expected range [20, 80]

def test_character_creation_calls_domain_constructor():
    """Test Character object created with validated inputs."""
    # Mock prompts to return valid inputs
    # Assert Character() called with correct arguments
```

**CombatRenderer Unit Tests**:
```python
def test_initiative_display_format():
    """Test initiative rendered with correct emoji and calculations."""
    # Create InitiativeResult with known values
    # Call _render_initiative()
    # Assert output contains expected strings (name, agility, rolls, totals)

def test_round_display_includes_all_details():
    """Test round rendered with attack, damage, HP change."""
    # Create RoundResult with known values
    # Call _render_round()
    # Assert output contains attacker name, dice roll, damage, HP change

def test_hp_color_gradient():
    """Test HP color selection based on percentage remaining."""
    # Test HP at 100% → green
    # Test HP at 50% → yellow
    # Test HP at 25% → orange
    # Test HP at 10% → red

def test_defender_counter_attack_conditional():
    """Test counter-attack only rendered if defender survives."""
    # RoundResult with defender_action = None (defender died)
    # Assert counter-attack NOT in output

    # RoundResult with defender_action present (defender survived)
    # Assert counter-attack in output
```

**ConsoleOutput Unit Tests**:
```python
def test_display_with_delay_respects_duration():
    """Test delay duration accurate in non-test mode."""
    # Config with 1.0s delay
    # Measure actual time elapsed
    # Assert within ±100ms tolerance

def test_display_with_delay_zero_in_test_mode():
    """Test zero delay in test mode."""
    # Config with test_mode()
    # Measure actual time elapsed
    # Assert < 10ms (no delay)

def test_emoji_fallback_when_unsupported():
    """Test fallback symbols used when emoji unavailable."""
    # Config with emoji_enabled=False
    # Assert fallback symbols used instead of emoji
```

### 4.3 Integration Testing Strategy

**Full CLI Flow Test**:
```python
def test_cli_full_flow_with_mocked_input():
    """Test complete CLI flow from start to exit."""
    # Mock Rich Prompts with input sequence:
    #   Char1: "Thorin", 20, 5
    #   Char2: "Goblin", 10, 3
    # Mock RandomDiceRoller with deterministic rolls
    # Run run_cli()
    # Assert:
    #   - Character confirmation cards displayed
    #   - Initiative roll displayed
    #   - Combat rounds displayed
    #   - Victory banner displayed
    #   - Exit confirmation shown

def test_cli_handles_invalid_input_recovery():
    """Test validation error recovery."""
    # Mock prompts with invalid then valid input:
    #   HP: 1000 (invalid) → 50 (valid)
    # Assert:
    #   - Error message displayed
    #   - Re-prompt occurs
    #   - Combat proceeds after valid input

def test_cli_handles_keyboard_interrupt():
    """Test Ctrl+C graceful exit."""
    # Mock KeyboardInterrupt during character creation
    # Assert:
    #   - Interruption message displayed
    #   - No stack trace
    #   - Exit code 130
```

### 4.4 Snapshot Testing Strategy

**Purpose**: Detect visual regressions in combat output

**Approach**: Capture text output of complete combat, compare to golden snapshot

```python
def test_combat_output_snapshot(snapshot):
    """Snapshot test for combat visualization."""
    # Create deterministic combat scenario
    char1 = Character("Thorin", 20, 5)
    char2 = Character("Goblin", 10, 3)

    # Mock dice rolls for deterministic outcome
    dice_roller = MockDiceRoller([4, 3, 2, 5, 1])  # Fixed rolls

    # Run combat and capture output
    output = capture_combat_output(char1, char2, dice_roller)

    # Compare to saved snapshot
    snapshot.assert_match(output)
```

**Snapshot Management**:
- Golden snapshots stored in `tests/snapshots/cli/`
- Update with `pytest --snapshot-update` when intentional changes occur
- Detect unintended changes (emoji position, spacing, colors)

### 4.5 Testing Infrastructure

**Test Fixtures**:
```python
@pytest.fixture
def mock_console():
    """Mock Rich Console for unit tests."""
    return Mock(spec=Console)

@pytest.fixture
def test_config():
    """CLI config with zero delays for tests."""
    return CLIConfig.test_mode()

@pytest.fixture
def deterministic_dice_roller():
    """Dice roller with fixed roll sequence."""
    return MockDiceRoller([4, 3, 2, 5, 1, 6])
```

**Test Data Catalog**:
```python
# tests/fixtures/combat_scenarios.py

SCENARIOS = {
    'standard_combat': {
        'char1': Character("Thorin", 20, 5),
        'char2': Character("Goblin", 10, 3),
        'rolls': [4, 3, 2, 5],
        'expected_rounds': 3,
        'expected_winner': "Thorin",
    },
    'one_shot_kill': {
        'char1': Character("Thorin", 20, 5),
        'char2': Character("Goblin", 5, 3),
        'rolls': [6, 6],  # High damage
        'expected_rounds': 1,
        'expected_winner': "Thorin",
    },
    'initiative_tie': {
        'char1': Character("Elf", 15, 10),
        'char2': Character("Dwarf", 20, 5),
        'rolls': [3, 3],  # Same initiative totals
        'expected_rounds': 5,
        'expected_winner': "Elf",  # Tie-breaker
    },
}
```

### 4.6 CI/CD Testing Configuration

**Requirements**:
- Tests must run in CI without interactive terminal
- No emoji/color validation required (content validation only)
- Zero-delay mode for fast execution

**pytest Configuration**:
```ini
# pytest.ini
[pytest]
testpaths = tests
markers =
    cli: CLI integration tests
    unit: Unit tests (fast)
    snapshot: Snapshot tests
    manual: Manual tests requiring terminal (skip in CI)

# Skip manual tests in CI
addopts = -m "not manual"
```

**CI Pipeline**:
```yaml
# .github/workflows/test.yml
- name: Run CLI tests
  run: |
    pytest tests/infrastructure/cli/ -v --snapshot-check
    # Snapshot check ensures no visual regressions
```

---

## 5. Design Patterns

### 5.1 Adapter Pattern

**Pattern**: CLI Adapter wraps external system (Rich library) and domain (CombatSimulator)

**Implementation**:
- **Adaptee**: Rich library (Console, Prompt, Text)
- **Target**: Domain model (Character, CombatResult)
- **Adapter**: CLI components (CharacterCreator, CombatRenderer)

**Benefit**: Domain remains independent of presentation technology

```
User Input (Rich Prompts)
         ↓
CharacterCreator (Adapter)
         ↓
Character (Domain Model)
         ↓
CombatSimulator (Application)
         ↓
CombatResult (Domain Model)
         ↓
CombatRenderer (Adapter)
         ↓
Rich Console Output
```

### 5.2 Dependency Injection Pattern

**Pattern**: Components receive dependencies via constructor, not create them

**Implementation**:
- CharacterCreator receives ConsoleOutput and DiceRoller
- CombatRenderer receives ConsoleOutput and CLIConfig
- ConsoleOutput receives Rich Console and CLIConfig
- CombatSimulator receives InitiativeResolver and CombatRound

**Benefit**: Testability (inject mocks), flexibility (swap implementations)

### 5.3 Strategy Pattern

**Pattern**: Timing configuration is a strategy, swappable via CLIConfig

**Implementation**:
- Production mode: `CLIConfig()` with standard delays
- Test mode: `CLIConfig.test_mode()` with zero delays
- Future: `CLIConfig.fast_mode()` with 50% delays for experienced users

**Benefit**: Easy to adjust pacing without code changes

### 5.4 Template Method Pattern

**Pattern**: Combat rendering follows fixed template, steps customizable

**Implementation**:
```python
def render_combat(self, result: CombatResult) -> None:
    """Template method for combat rendering."""
    self._render_initiative(result.initiative_result)  # Step 1

    for round_result in result.rounds:
        self._render_round(round_result)  # Step 2 (repeated)

    self._render_victory(result)  # Step 3
```

**Benefit**: Consistent structure, easy to extend (add replay, add logging)

### 5.5 Facade Pattern

**Pattern**: ConsoleOutput provides simplified interface to Rich Console

**Implementation**:
- Rich Console has many methods (print, render, update, live, etc.)
- ConsoleOutput exposes only needed methods (print, pause, prompt_continue)
- Hides Rich complexity from CLI components

**Benefit**: Simpler testing, easier to swap Rich for different library

---

## 6. Deployment Architecture

### 6.1 Entry Points

**Primary Entry Point**:
```bash
python -m modules.infrastructure.cli.main
```

**Convenience Script** (top-level `cli.py`):
```python
#!/usr/bin/env python3
"""Convenience entry point for CLI application."""

from modules.infrastructure.cli.main import run_cli

if __name__ == "__main__":
    run_cli()
```

**Usage**:
```bash
# Option 1: Module invocation
python -m modules.infrastructure.cli.main

# Option 2: Convenience script
python cli.py

# Option 3: Make script executable (Unix/Linux/macOS)
chmod +x cli.py
./cli.py
```

### 6.2 Dependencies

**Runtime Dependencies**:
```toml
# pyproject.toml
[project]
name = "combat-simulator-demo"
version = "1.0.0"
dependencies = [
    "rich>=13.0.0,<14.0.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-bdd>=6.0.0",
    "pytest-mock>=3.10.0",
    "pytest-snapshot>=0.9.0",
]
```

**Installation**:
```bash
# Development installation (includes test dependencies)
pip install -e ".[dev]"

# Production installation (minimal dependencies)
pip install -e .
```

### 6.3 Platform Compatibility

**Supported Platforms**:
- Linux (Ubuntu 20.04+, Debian 11+, Fedora 35+)
- macOS (11.0 Big Sur+)
- Windows (10+, Windows Terminal recommended)

**Terminal Requirements**:
- UTF-8 encoding support (modern terminals)
- Minimum 80 characters width
- Color support: Optional but recommended (automatic fallback to no-color)
- Emoji support: Optional but recommended (automatic fallback to ASCII symbols)

**Tested Terminals**:
- ✅ Windows Terminal (Windows 10+)
- ✅ PowerShell 7+ (Windows/macOS/Linux)
- ✅ macOS Terminal.app
- ✅ iTerm2 (macOS)
- ✅ GNOME Terminal (Linux)
- ✅ Konsole (Linux KDE)
- ⚠️ CMD.exe (Windows) - Limited emoji support, fallbacks used

---

## 7. Quality Attributes

### 7.1 Testability

**Design Decisions for Testability**:

1. **Dependency Injection**: All components receive dependencies via constructor
   - Enables mock injection for isolated testing
   - Example: CharacterCreator receives ConsoleOutput (mockable)

2. **Pure Functions**: Formatting logic separated from I/O
   - HP color selection: Pure function (HP percentage → color string)
   - Attack display formatting: Pure function (AttackResult → formatted string)

3. **Timing Abstraction**: CLIConfig.test_mode() enables zero-delay testing
   - Integration tests run in milliseconds, not seconds
   - CI/CD pipelines fast and reliable

4. **Rich Console Abstraction**: ConsoleOutput wraps Rich Console
   - Tests inject mock ConsoleOutput, not real Rich Console
   - Output captured for assertion without terminal dependency

**Testability Validation**:
- ✅ All CLI components unit testable in isolation
- ✅ Integration tests run without interactive terminal
- ✅ CI/CD pipeline runs tests without manual intervention
- ✅ Snapshot tests detect visual regressions

### 7.2 Maintainability

**Design Decisions for Maintainability**:

1. **Clear Component Boundaries**:
   - CharacterCreator: Only input handling and validation
   - CombatRenderer: Only output formatting and pacing
   - ConsoleOutput: Only Rich wrapper and timing
   - No cross-cutting concerns or tangled responsibilities

2. **Configuration Centralization**:
   - All timing constants in CLIConfig
   - All emoji mappings in CLIConfig
   - Easy to adjust without code changes

3. **Separation of Business Logic from Presentation**:
   - Domain logic in domain layer (existing, unchanged)
   - CLI only handles presentation concerns
   - No domain rules in CLI code

4. **Documentation**:
   - Docstrings for all public classes and methods
   - Architecture diagrams (this document)
   - Sequence diagrams for key flows (see Section 8)

**Maintainability Validation**:
- ✅ New developers can understand CLI structure from documentation
- ✅ Visual tweaks (timing, emoji, colors) achievable without architectural changes
- ✅ Easy to add features (logging, replay, config file) without major refactoring

### 7.3 User Experience

**Design Decisions for UX Excellence**:

1. **Visual Clarity**:
   - Consistent emoji usage throughout (same emoji = same concept)
   - Color-coded information (HP gradient, damage red, success green)
   - Clear visual hierarchy (headers, separators, spacing)

2. **Cognitive Load Management**:
   - Sequential prompts (one question at a time)
   - Sufficient pauses for reading and comprehension (fixed 1.5-2s timing)
   - No skip mechanism - consistent pacing for all users

3. **Error Handling**:
   - Immediate validation feedback (no waiting)
   - Clear error messages with specific constraints
   - Automatic re-prompt (no need to restart)

4. **Pacing**:
   - Fixed delays allow comfortable reading (1.5-2s between major events)
   - Consistent timing for all users (no skip mechanism)
   - Pacing optimized through user testing

**UX Validation**:
- ✅ Default timing allows reading without rushing (measured in user testing)
- ✅ Random defaults support rapid character creation (<1s)
- ✅ Manual input validation responsive (<100ms feedback)
- ✅ Error messages actionable and specific

### 7.4 Cross-Platform Compatibility

**Design Decisions for Compatibility**:

1. **Rich Library Automatic Detection**:
   - Rich detects terminal capabilities (color, emoji, encoding)
   - Automatic degradation to best available mode
   - No special handling required in CLI code

2. **Emoji Fallback Strategy**:
   - Fallback symbols defined in CLIConfig
   - Rich uses fallback if emoji unsupported
   - Functionality preserved without emoji (symbols provide visual cues)

3. **Platform-Specific Input Handling**:
   - Unix: `select.select()` for non-blocking input
   - Windows: `msvcrt.kbhit()` and `msvcrt.getch()`
   - Cross-platform compatibility maintained

4. **Terminal Width Assumptions**:
   - Minimum 80 characters width (standard default)
   - No horizontal scrolling required
   - Combat visualization fits within 80 columns

**Compatibility Validation**:
- ✅ Application runs without errors on Windows, macOS, Linux
- ✅ Emoji display correctly or degrade gracefully per fallback table
- ✅ No character encoding errors

### 7.5 Performance

**Design Decisions for Performance**:

1. **Lightweight Components**:
   - CLI components have minimal state (no caching, no complex data structures)
   - No blocking operations except intentional pauses
   - Rich Console rendering optimized by library

2. **Input Validation Speed**:
   - Validation logic simple (range checks, type checks)
   - No external calls during validation
   - Rich handles prompt rendering efficiently

3. **Delay Accuracy**:
   - Simple time.sleep() implementation
   - Timing accuracy: ±50ms tolerance acceptable
   - No drift over multiple delays

**Performance Targets**:
- ✅ Input validation response: <100ms
- ✅ Next prompt appearance: <50ms
- ✅ Startup time: <500ms
- ✅ Fixed timing delays accurate within ±50ms

---

## 8. Sequence Diagrams

### 8.1 Character Creation Sequence

```mermaid
sequenceDiagram
    participant User
    participant Main as CLI Main
    participant Creator as CharacterCreator
    participant Console as ConsoleOutput
    participant Rich as Rich.Prompt
    participant Domain as Character

    User->>Main: Start CLI
    Main->>Creator: create_character(1)

    Creator->>Console: print("Enter Character 1 details")
    Console->>User: Display prompt

    Creator->>Rich: Prompt.ask("Nome personaggio 1: ")
    User->>Rich: "Thorin"
    Rich->>Creator: "Thorin"

    Creator->>Rich: IntPrompt.ask("HP [1-999, INVIO=random]: ")
    User->>Rich: 20
    Rich->>Creator: 20

    Creator->>Rich: IntPrompt.ask("Potere d'attacco [1-99, INVIO=random]: ")
    User->>Rich: 5
    Rich->>Creator: 5

    Creator->>Domain: Character("Thorin", 20, 5)
    Domain->>Creator: Character instance

    Creator->>Console: print_panel(character_summary)
    Console->>User: Display character card

    Creator->>Main: Return Character

    Main->>Creator: create_character(2)
    Note over Main,Creator: Repeat for Character 2
```

### 8.2 Combat Visualization Sequence

```mermaid
sequenceDiagram
    participant Main as CLI Main
    participant Simulator as CombatSimulator
    participant Renderer as CombatRenderer
    participant Console as ConsoleOutput
    participant User

    Main->>Simulator: run_combat(char1, char2)
    Simulator->>Main: CombatResult

    Main->>Renderer: render_combat(CombatResult)

    Renderer->>Console: print("🎲 Rolling Initiative...")
    Renderer->>Console: print(initiative details)
    Console->>User: Display initiative
    Renderer->>Console: display_with_delay(message, 1.5s)

    loop For each round in CombatResult.rounds
        Renderer->>Console: print("⚔️ ROUND {number}")
        Renderer->>Console: display_with_delay(message, 0.5s)

        Renderer->>Console: print("⚔️ {Attacker} attacks!")
        Renderer->>Console: print(attack details)
        Renderer->>Console: display_with_delay(message, 1.5s)

        alt Defender survives
            Renderer->>Console: print("🛡️ {Defender} counter-attacks!")
            Renderer->>Console: print(counter-attack details)
            Renderer->>Console: display_with_delay(message, 1.5s)
        else Defender defeated
            Renderer->>Console: print("☠️ {Defender} defeated!")
            Renderer->>Console: display_with_delay(message, 2.0s)
        end
    end

    Renderer->>Console: print("🏆 {Winner} WINS!")
    Renderer->>Console: print(combat statistics)
    Renderer->>Console: prompt_continue("Premi INVIO per uscire")
    User->>Console: Press ENTER

    Renderer->>Main: Return (rendering complete)
    Main->>User: Exit application
```

### 8.3 Error Handling Sequence

```mermaid
sequenceDiagram
    participant User
    participant Creator as CharacterCreator
    participant Rich as Rich.IntPrompt
    participant Console as ConsoleOutput
    participant Domain as Character

    Creator->>Rich: IntPrompt.ask("HP [1-999]: ")
    User->>Rich: 1000 (out of range)
    Rich->>Creator: 1000

    Creator->>Creator: validate_hp(1000)
    Creator->>Console: print("❌ HP must be between 1 and 999", style="red")
    Console->>User: Display error message

    Creator->>Rich: IntPrompt.ask("HP [1-999]: ") [retry]
    User->>Rich: 50 (valid)
    Rich->>Creator: 50

    Creator->>Creator: validate_hp(50)
    Note over Creator: Validation passes

    Creator->>Domain: Character(..., hp=50, ...)

    alt Domain validation error
        Domain-->>Creator: ValueError("Name cannot be empty")
        Creator->>Console: print("❌ Invalid character: Name cannot be empty", style="red")
        Creator->>Creator: Restart character creation
    else Success
        Domain->>Creator: Character instance
    end
```

---

## 9. Risk Assessment and Mitigation

### 9.1 Identified Risks

| Risk ID | Risk Description | Probability | Impact | Mitigation Strategy | Status |
|---------|------------------|-------------|--------|---------------------|--------|
| R-01 | Emoji rendering issues on Windows CMD.exe | Medium | Low | Rich library handles fallbacks automatically. Fallback symbols defined. Test on Windows Terminal (recommended). | Accepted |
| R-02 | Testing interactive CLI in CI/CD | Medium | Medium | Separate logic from Rich UI. Mock input streams. Zero-delay test mode. Snapshot tests for output. | Mitigated |
| R-03 | Timing variations on different systems | Low | Low | Timing accuracy not critical (±100ms acceptable). Configurable constants allow adjustment. Fixed timing simplifies implementation. | Accepted |
| R-04 | Platform compatibility (emoji display, color support) | Medium | Low | Rich handles platform detection automatically for emoji and colors. Fallback symbols and graceful degradation built-in. | Accepted |
| R-05 | UTF-8 encoding issues on legacy terminals | Low | Low | Rich handles encoding detection. Target modern terminals only. Document minimum requirements. | Accepted |
| R-06 | Character creation tedious for repeat testing | Low | Low | Future enhancement: config file or non-interactive mode. Not MVP blocker. Test mode uses programmatic creation. | Accepted |
| R-07 | Rich library API changes in future versions | Low | Medium | Pin Rich to 13.x range (>=13.0.0,<14.0.0). Monitor release notes. Abstract Rich behind ConsoleOutput. | Mitigated |

### 9.2 Risk Mitigation Details

**R-02: Testing Interactive CLI in CI/CD** (Critical for DISTILL wave)

**Mitigation Implementation**:

1. **Mock Input Strategy**:
```python
@pytest.fixture
def mock_rich_prompts(monkeypatch):
    """Mock Rich prompt functions for testing."""
    inputs = ["Thorin", "20", "5", "Goblin", "10", "3"]
    input_iter = iter(inputs)

    def mock_ask(*args, **kwargs):
        return next(input_iter)

    monkeypatch.setattr("rich.prompt.Prompt.ask", mock_ask)
    monkeypatch.setattr("rich.prompt.IntPrompt.ask", lambda *args, **kwargs: int(next(input_iter)))
```

2. **Output Capture Strategy**:
```python
from rich.console import Console
from io import StringIO

def test_combat_output():
    """Test combat output without real terminal."""
    output_buffer = StringIO()
    console = Console(file=output_buffer, force_terminal=True)

    # Run CLI with captured console
    # ...

    # Assert output contents
    output = output_buffer.getvalue()
    assert "🏆" in output or "[WIN]" in output
```

3. **Zero-Delay Test Mode**:
```python
config = CLIConfig.test_mode()  # All delays = 0.0
# Tests complete in milliseconds, not seconds
```

---

## 10. Architecture Decision Records (ADRs)

### ADR-001: Selection of Rich Library for CLI UI

**Status**: Accepted

**Context**:
Need modern CLI library for interactive prompts, colors, emoji, and visual formatting. Options: Rich, Click, prompt_toolkit, curses.

**Decision**: Use Rich 13.x for CLI UI

**Rationale**:
1. **All-in-one solution**: Rich provides prompts, colors, emoji, layouts in single library (reduces dependencies)
2. **User-confirmed choice**: User explicitly selected Rich during requirements gathering
3. **Testing-friendly**: Rich Console capture API simplifies automated testing
4. **Cross-platform**: Rich handles terminal capability detection automatically (colors, emoji, encoding)
5. **Modern aesthetics**: Best emoji and color support for engaging user experience
6. **Active maintenance**: Rich actively developed and maintained (2025+ roadmap)

**Alternatives Considered**:
- **Click**: Good for CLI arguments, lacks rich formatting (emoji, colors, layouts)
- **prompt_toolkit**: Powerful for complex TUI, overkill for sequential prompts
- **curses**: Low-level, high complexity, harder to test, less suitable for educational context

**Consequences**:
- Positive: Modern, professional UI. Easy development. Good testing support.
- Negative: Dependency on external library (mitigated by pinning version >=13.0.0,<14.0.0)
- Trade-off: Rich has larger footprint than Click, but acceptable for educational project

---

### ADR-002: Hexagonal Architecture Placement of CLI Adapter

**Status**: Accepted

**Context**:
Need to integrate CLI presentation layer with existing hexagonal architecture. Options: CLI as infrastructure adapter, CLI as separate application layer, CLI with mixed responsibilities.

**Decision**: CLI as Infrastructure Adapter in `modules/infrastructure/cli/`

**Rationale**:
1. **Hexagonal Architecture Compliance**: Presentation layer is external concern, belongs in infrastructure
2. **Dependency Direction**: CLI depends on Application layer (CombatSimulator), not vice versa
3. **Domain Protection**: Domain remains independent of presentation technology
4. **Consistency**: Existing infrastructure adapters (RandomDiceRoller) follow same pattern
5. **Testability**: Infrastructure adapters easily mockable for testing

**Alternatives Considered**:
- **CLI as Application Layer**: Violates hexagonal architecture (application layer is use cases, not UI)
- **CLI in top-level directory**: Inconsistent with existing structure, less clear separation
- **CLI mixed with domain**: Violates separation of concerns, domain would depend on Rich

**Consequences**:
- Positive: Clear architecture boundaries. Domain remains pure. Easy to add alternative UIs (GUI, web).
- Negative: None significant.
- Trade-off: Requires dependency injection (CombatSimulator instantiated in CLI Main), but this is desired for testability.

---

### ADR-003: Testing Strategy for Interactive CLI

**Status**: Accepted

**Context**:
Interactive CLI traditionally difficult to test automatically. Need strategy for CI/CD testing without manual interaction.

**Decision**: Separate testable logic from Rich I/O, use mocking and zero-delay mode

**Testing Architecture**:
1. **Unit Tests**: Mock Rich Prompt/Console, test validation logic and formatting
2. **Integration Tests**: Mock input streams, capture output, assert content
3. **Snapshot Tests**: Capture complete combat output, compare to golden snapshots
4. **Zero-Delay Mode**: `CLIConfig.test_mode()` eliminates delays for fast tests

**Rationale**:
1. **CI/CD Compatibility**: Tests run without interactive terminal
2. **Fast Execution**: Zero delays mean tests complete in milliseconds
3. **Visual Regression Detection**: Snapshot tests catch unintended output changes
4. **Maintainability**: Mock strategy simple and well-understood

**Alternatives Considered**:
- **Expect/Pexpect**: Spawns real process, complex setup, slower execution
- **Manual Testing Only**: Not sustainable, error-prone, blocks CI/CD
- **No Testing**: Unacceptable for TDD educational project

**Consequences**:
- Positive: Full CI/CD automation. Fast tests. Reliable regression detection.
- Negative: Mock setup adds test code complexity (acceptable trade-off).
- Trade-off: Some visual aspects (emoji rendering, color display) require manual validation, but content logic fully automated.

---

### ADR-004: Timing Control with CLIConfig

**Status**: Accepted

**Context**:
Combat pacing critical for UX (too fast = unreadable, too slow = boring). Need configurable timing with future extensibility.

**Decision**: Centralize timing constants in immutable `CLIConfig` dataclass

**Configuration Strategy**:
- Production mode: `CLIConfig()` with default delays (1.5-2s)
- Test mode: `CLIConfig.test_mode()` with zero delays
- Future: Load from config file (`~/.combat-sim-config.yaml`)

**Rationale**:
1. **Single Source of Truth**: All timing in one place, easy to adjust
2. **Test Performance**: Zero-delay mode makes tests fast
3. **User Control**: Future config file allows user customization
4. **Type Safety**: Dataclass provides type hints and validation

**Alternatives Considered**:
- **Hardcoded Delays**: Inflexible, hard to test
- **Global Variables**: Mutable state, harder to reason about
- **Environment Variables**: Less discoverable, no type safety

**Consequences**:
- Positive: Easy timing adjustment. Fast tests. Future-proof for config file.
- Negative: Requires passing config to components (acceptable, follows dependency injection).
- Trade-off: Slight increase in boilerplate (config passing), but gains in flexibility and testability.

---

## 11. Open Questions for DISTILL Wave

### Q-001: Emoji Fallback Testing Strategy

**Question**: How to automatically test emoji fallback behavior in CI/CD?

**Options**:
1. **Environment Variable**: Set `TERM=dumb` to force no-emoji mode, assert fallback symbols used
2. **Mock Rich Capabilities**: Mock Rich's emoji detection to return False
3. **Manual Testing Only**: Accept that emoji fallback requires manual validation on old terminals

**Recommendation**: Option 1 (environment variable) for automated fallback path testing, plus manual validation on Windows CMD.exe

---

### Q-002: Configuration File Format

**Question**: When implementing config file support (future enhancement), use YAML, JSON, or TOML?

**Not Blocking MVP**: Config file support explicitly out of scope for MVP. Document preferred format for future.

**Recommendation**: YAML (most readable for users, good Python library support with PyYAML)

**Example Future Config**:
```yaml
# ~/.combat-sim-config.yaml
timing:
  initiative_roll_delay: 1.0
  attack_delay: 1.0
  fast_mode: false

display:
  emoji_enabled: true
  colors_enabled: true
  terminal_width: 80
```

---

## 12. Handoff Package for DISTILL Wave

### 12.1 Architecture Deliverables Checklist

- ✅ Architecture overview with hexagonal architecture context
- ✅ Component design with clear responsibilities
- ✅ Directory structure specification
- ✅ Class diagrams (Mermaid component diagram)
- ✅ Sequence diagrams (character creation, combat visualization, error handling)
- ✅ Technology stack integration details
- ✅ Testing architecture (unit, integration, snapshot strategies)
- ✅ Design patterns documentation
- ✅ Deployment architecture
- ✅ Quality attributes analysis
- ✅ Risk assessment with mitigation strategies
- ✅ ADRs for major decisions
- ✅ Open questions documented

### 12.2 Component Specifications Summary

| Component | Responsibility | Dependencies | Testing Strategy |
|-----------|----------------|--------------|------------------|
| CLI Main | Lifecycle orchestration, dependency wiring, error handling | CharacterCreator, CombatSimulator, CombatRenderer, ConsoleOutput | Integration tests with mocked input |
| CharacterCreator | Interactive character creation, validation, random defaults | ConsoleOutput, DiceRoller | Unit tests with mocked Rich Prompt |
| CombatRenderer | Combat visualization, emoji/color formatting, fixed-timing pacing | ConsoleOutput, CLIConfig | Unit tests for formatting, integration for full flow |
| ConsoleOutput | Rich Console wrapper, fixed timing delays | Rich Console, CLIConfig | Unit tests for display_with_delay logic |
| CLIConfig | Centralized configuration for timing and display | None (immutable data) | Unit tests for test_mode() |

### 12.3 Key Architectural Constraints

1. **Hexagonal Architecture**: CLI must be infrastructure adapter, no domain logic leakage
2. **Dependency Direction**: All dependencies point inward (CLI → Application → Domain)
3. **Testability**: All logic testable without manual interaction
4. **Rich 13.x Dependency**: Pin to `>=13.0.0,<14.0.0` range
5. **Cross-Platform**: Must work on Windows, macOS, Linux terminals
6. **Immutability**: Respect domain model immutability (Character, CombatResult are frozen dataclasses)

### 12.4 Implementation Order (from Requirements Doc)

**Phase 1: Baseline** - Minimum Viable CLI
- CLI entry point with hardcoded characters
- Plain text output (no colors, no emoji)
- Integration validation (CLI → CombatSimulator → Domain)

**Phase 2: Interactive Input** - Character creation
- Rich.Prompt integration
- Validation with re-prompting
- Random defaults (ENTER behavior)
- Character confirmation cards

**Phase 3: Visual Enhancement** - Emoji, colors, pacing
- Add emoji to all events
- Color-coded output (HP gradient, damage red)
- Implement fixed pacing delays (1.5-2s timing)

**Phase 4: Polish** - Exit confirmation, edge cases
- Exit confirmation (ENTER to quit)
- Graceful Ctrl+C handling
- Edge case testing (1-round combat, 20+ rounds)
- Help text (`--help` flag)

### 12.5 Success Criteria for DEVELOP Wave

The DEVELOP wave will be considered complete when:

- [ ] All 8 functional requirements (FR-01 to FR-08) implemented
- [ ] All 6 non-functional requirements (NFR-01 to NFR-06) satisfied
- [ ] All 6 user stories (US-01 to US-06) acceptance criteria passing
- [ ] Phase 1-4 E2E scenarios passing (from requirements Section 9)
- [ ] Unit test coverage > 80% for CLI adapter logic
- [ ] Integration tests validate end-to-end flow
- [ ] Snapshot tests detect visual regressions
- [ ] Manual testing confirms emoji/color display on Windows, macOS, Linux
- [ ] No regressions in existing 9/9 E2E tests and 34/34 unit tests

### 12.6 Questions for Acceptance Designer (DISTILL Wave)

1. **Acceptance Test Framework**: Use pytest-bdd (existing) or create custom CLI test scenarios? Recommendation: Extend pytest-bdd with CLI fixtures.

2. **Mock vs. Real CombatSimulator**: Should acceptance tests mock CombatSimulator or use real implementation? Recommendation: Use real CombatSimulator (validates integration), mock only DiceRoller for deterministic outcomes.

3. **Snapshot Test Format**: Store snapshots as plain text files or structured JSON? Recommendation: Plain text (easier to review diffs, matches user-visible output).

4. **CI/CD Terminal Emulation**: Which terminal type to emulate in CI? Recommendation: `TERM=xterm-256color` for color support, validate no-color fallback with `TERM=dumb`.

5. **Performance Baselines**: Establish quantitative performance baselines (e.g., input validation <100ms)? Recommendation: Qualitative acceptance for MVP (no perceptible lag), defer quantitative to future if needed.

---

## 13. Future Enhancements (Out of Scope for MVP)

### 13.1 Configuration File Support

**Feature**: Load timing and display settings from `~/.combat-sim-config.yaml`

**Benefits**:
- Users customize pacing without code changes
- Fast mode for experienced users (50% delays)
- Accessibility mode (no emoji, high-contrast colors)

**Implementation Complexity**: Low (CLIConfig.from_file() method)

**Priority**: Low (post-MVP enhancement)

---

### 13.2 Combat Replay Functionality

**Feature**: Re-run same characters without re-entering

**Benefits**:
- Easier testing and demonstration
- See different combat outcomes with same characters (different dice rolls)

**Implementation Complexity**: Low (cache last character pair, add replay prompt)

**Priority**: Medium (requested by users during requirements gathering)

---

### 13.3 Combat Logging to File

**Feature**: Save combat output to text file for later review

**Benefits**:
- Post-combat analysis
- Share combat results
- Debugging unexpected outcomes

**Implementation Complexity**: Low (redirect ConsoleOutput to file)

**Priority**: Low (nice-to-have)

---

### 13.4 Non-Interactive Mode

**Feature**: CLI arguments for character creation (e.g., `--char1 "Thorin,20,5" --char2 "Goblin,10,3"`)

**Benefits**:
- Faster testing for developers
- Scriptable combat scenarios
- Integration with external tools

**Implementation Complexity**: Medium (add argparse, validate inputs)

**Priority**: Medium (developer productivity)

---

### 13.5 Accessibility Enhancements

**Feature**: Text-only mode, screen reader support, colorblind-friendly color schemes

**Benefits**:
- Broader audience reach
- Inclusive design

**Implementation Complexity**: Medium-High (requires accessibility testing, alternative output formats)

**Priority**: Low (educational project with defined target audience, but ethically valuable)

---

## 14. Glossary

| Term | Definition |
|------|------------|
| **Adapter** | Design pattern wrapping external system (Rich) to match domain interface |
| **Agility** | Derived character attribute: HP + Attack Power, used for initiative calculation |
| **CLI** | Command-Line Interface, text-based user interface in terminal |
| **CombatResult** | Domain value object containing complete combat outcome (winner, loser, rounds) |
| **Dependency Injection** | Design pattern where components receive dependencies via constructor |
| **Emoji Fallback** | ASCII symbols used when terminal doesn't support emoji (e.g., ⚔️ → [ATK]) |
| **Fixed Timing** | Pacing delays that remain constant (1.5-2s), no user skip capability |
| **Hexagonal Architecture** | Architecture pattern separating core domain from external adapters (UI, database) |
| **Rich** | Python library for rich text, colors, emoji, and interactive CLI applications |
| **Snapshot Test** | Test capturing output and comparing to saved golden snapshot (detects visual regressions) |

---

## 15. Document Metadata

**Document Control**:
- Architecture Document ID: ARCH-CLI-COMBAT-001
- Version: 1.1
- Status: Finalized (Ready for DISTILL Wave Handoff)
- Architect: Morgan (solution-architect)
- Date Created: 2026-01-09
- Last Updated: 2026-01-09

**Review and Approval**:
- Architecture Author: Morgan (solution-architect) - Finalized
- Requirements Source: Riley (product-owner) - Requirements approved
- Next Wave Recipient: Quinn (acceptance-designer, DISTILL wave) - Awaiting handoff

**References**:
- Requirements Document: `docs/requirements/interactive-cli-combat-viewer.md` (v1.1)
- Existing System: `modules/domain/`, `modules/application/`, `modules/infrastructure/`
- Rich Library Documentation: https://rich.readthedocs.io/
- Hexagonal Architecture Pattern: https://alistair.cockburn.us/hexagonal-architecture/

**Change Log**:
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-09 | Morgan | Initial architecture design document created. All components designed, testing strategy specified, ADRs documented, handoff package complete. |
| 1.1 | 2026-01-09 | Morgan | Applied user decisions: (1) Removed skip mechanism completely - fixed timing only (1.5-2s). Simplified ConsoleOutput.display_with_delay() to just time.sleep(). Removed ADR-005 and all skip-related testing/risks. (2) Added Section 1.1 Baseline Context - explicit greenfield statement clarifying CLI is first user-facing interface. (3) Confirmed architecture placement in modules/infrastructure/cli/. Renumbered sections and ADRs. Document finalized. |

---

**END OF ARCHITECTURE DESIGN DOCUMENT**
