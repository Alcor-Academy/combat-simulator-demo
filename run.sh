#!/bin/bash
# Combat Simulator - Linux/macOS Launch Script

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Combat Simulator - Launch Script${NC}"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo "Please install Python 3.8 or higher to run this game."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python $PYTHON_VERSION detected.${NC}"
    echo "Python 3.8 or higher is required."
    exit 1
fi

echo -e "${GREEN}Python $PYTHON_VERSION detected${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Warning: No virtual environment detected.${NC}"
    echo "It's recommended to run this in a virtual environment."
    echo ""
fi

# Check if dependencies are installed
if ! python3 -c "import rich" 2>/dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
    echo ""
fi

# Launch the game
echo -e "${GREEN}Launching Combat Simulator...${NC}"
echo ""
python3 cli.py
