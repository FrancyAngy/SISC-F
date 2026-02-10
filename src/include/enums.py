# SISC-F 32-bit CPU
# Copyright (c) 2026 Francesco Angeloni
#
# This source describes Open Hardware and is licensed under the CERN-OHL-W v2.
# You may redistribute and modify this source and make products using it
# under the terms of the CERN-OHL-W v2 (https://cern.ch/cern-ohl).
#
# SPDX-License-Identifier: CERN-OHL-W-2.0

from enum import IntEnum, auto

class AluOps(IntEnum):
    NONE = 0
    ADD = auto()
    SUB = auto()
    MUL = auto()
    INC = auto()
    DEC = auto()

class StackOps(IntEnum):
    NONE = 0
    PUSH = auto()
    POP = auto()

class Flags(IntEnum):
    ZERO = 0
    CARRY = 1
    NEGATIVE = 2
    ERROR = 3
    OVERFLOW = 4