# Combat Simulator

An interactive CLI-based combat simulator built with Python, featuring turn-based combat mechanics with visual feedback.

## Features

- **Interactive Character Creation**: Create characters with custom names, HP, and attack power
- **Random Generation**: Press ENTER for random character attributes
- **Turn-Based Combat**: Watch characters battle with initiative rolls and strategic combat
- **Visual Feedback**: Rich CLI interface with emoji, colors, and formatted output
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd combat-simulator-demo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Game

#### Linux/macOS
```bash
./run.sh
```

#### Windows
```cmd
run.bat
```

#### Manual Launch
```bash
python3 cli.py  # Linux/macOS
python cli.py   # Windows
```

## How to Play

1. **Create Character 1**: Enter name, HP (1-999), and attack power (1-99)
2. **Create Character 2**: Enter name, HP, and attack power
3. **Watch Combat**: The simulator automatically runs the battle
4. **View Results**: See the winner and combat statistics

### Tips

- Press **ENTER** without input to generate random HP (20-80) or attack power (5-15)
- Press **CTRL-C** at any time to exit
- Characters with higher agility (HP + attack power) have better initiative

## Combat Mechanics

- **Initiative**: Roll d6 + agility to determine who attacks first
- **Attack**: Roll d6 + attack power = total damage
- **Turns**: Attacker strikes, then defender counter-attacks (if alive)
- **Victory**: Combat ends when one character reaches 0 HP

## Development

### Project Structure

```
combat-simulator-demo/
├── modules/
│   ├── domain/           # Business logic (Character, Combat services)
│   ├── application/      # Use cases (CombatSimulator)
│   └── infrastructure/   # CLI, rendering, dice rolling
├── tests/
│   ├── unit/            # Unit tests
│   └── e2e/             # End-to-end acceptance tests
├── cli.py               # Main entry point
├── run.sh               # Linux/macOS launch script
└── run.bat              # Windows launch script
```

### Running Tests

```bash
# Run all tests
pytest

# Run only E2E tests
pytest tests/e2e/

# Run with coverage
pytest --cov=modules
```

### Architecture

The project follows **Hexagonal Architecture** principles:
- **Domain Layer**: Core business logic (zero dependencies)
- **Application Layer**: Use case orchestration
- **Infrastructure Layer**: CLI, adapters, external integrations

## Development Approach

Built using **Outside-In TDD** and **BDD** with:
- pytest-bdd for acceptance tests
- Gherkin scenarios for feature specifications
- RED-GREEN-REFACTOR cycle for implementation

## License

[Specify your license here]

## Contributing

[Specify contribution guidelines here]
