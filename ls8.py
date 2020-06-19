#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()
try:
    filename = sys.argv[1]
except (IndexError, FileNotFoundError):
    print("Please provide a valid filename!")
    exit(1)

cpu.load(filename)
cpu.run()
