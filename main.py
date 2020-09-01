from core.chip8 import Chip8

import logging
import sys

logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) < 2:
    print("Usage: python main.py <rom file>")
    exit()

chip = Chip8()

chip.load(sys.argv[1])
chip.run()