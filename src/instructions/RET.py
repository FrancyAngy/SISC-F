# SISC-F 32-bit CPU
# Copyright (c) 2026 Francesco Angeloni
#
# This source describes Open Hardware and is licensed under the CERN-OHL-W v2.
# You may redistribute and modify this source and make products using it
# under the terms of the CERN-OHL-W v2 (https://cern.ch/cern-ohl).
#
# SPDX-License-Identifier: CERN-OHL-W-2.0

from include.instruction import *
from include.enums import *
from amaranth import Module, Signal, Const, signed
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Core

def _exec(m: Module, core: "Core"):
    with m.Switch(core.instr_state):
        with m.Case(1):
            m.d.comb += [
                core.stack_op.eq(StackOps.POP),
                core.stack_en.eq(1),
            ]
            m.d.sync += core.instr_state.eq(2)
        with m.Case(2):
            core.end_instr(m, core.data_in)

Instruction(0xB5, "RET", _exec, 0x1)