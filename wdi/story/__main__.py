"""`python -m wdi.story [E1.1 ...] [--seeds ...]`: run the storyline experiments (see wdi/story/__init__.py)."""
import sys

from wdi.story import main

main(sys.argv[1:])
