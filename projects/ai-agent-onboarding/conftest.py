# This file adds the project root directory to Python's module search path. 
# This lets pytest find src when tests do from src.fetchers... import ....
# Without it, pytest doesn't know where to look for your src package.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

