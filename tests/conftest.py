"""Root pytest configuration.

Ensures the project root is in the Python path so modules can be imported.
"""

import sys
from pathlib import Path


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
