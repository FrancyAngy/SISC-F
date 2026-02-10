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
            m.d.sync += [
                core.tmp32.eq(core.data_in),
            ]
            core.advance_ip_goto_state(m, 3)
        with m.Case(3):
            m.d.sync += [
                core.addr.eq(core.data_in),
                core.data_out.eq(core.tmp32),
                core.instr_state.eq(4),
                core.RW.eq(0),
            ]
        with m.Case(4):
            m.d.sync += [
                core.RW.eq(1),
                core.tmp32.eq(0),
                core.data_out.eq(0)
            ]
            core.end_instr(m, core.ip + 1)

Instruction(0xB0, "POP", _exec, 0x2)