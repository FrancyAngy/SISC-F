# SISC-F 32-bit CPU
# Copyright (c) 2026 Francesco Angeloni
#
# This source describes Open Hardware and is licensed under the CERN-OHL-W v2.
# You may redistribute and modify this source and make products using it
# under the terms of the CERN-OHL-W v2 (https://cern.ch/cern-ohl).
#
# SPDX-License-Identifier: CERN-OHL-W-2.0

from include import exceptions
from include.instruction import *
from amaranth import Module, Signal, Cat
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Core

def JMP_exec(m: Module, core:"Core"):
    with m.Switch(core.instr_state):
        with m.Case(2):
            core.end_instr(m, core.data_in)
        with m.Default():
            core.advance_ip_goto_state(m, 2)

Instruction(0x10, "JMP", JMP_exec, 0x3)