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
from amaranth import Module, Signal

_length = 0x2

def _LDI(m: Module, core, register: Signal):
    with m.Switch(core.instr_state):
        with m.Case(1):
            core.advance_ip_goto_state(m, 2)
        with m.Case(2):
            m.d.sync += [
                core.addr.eq(core.data_in),
                core.instr_state.eq(3)
            ]
        with m.Case(3):
            m.d.sync += [
                register.eq(core.data_in),
                core.flags[Flags.NEGATIVE].eq(core.data_in < 0),
                core.flags[Flags.ZERO].eq(core.data_in == 0),
            ]
            core.end_instr(m, core.ip + 1)

def LDA_exec(m: Module, core):
    _LDI(m, core, core.ra)
def LDB_exec(m: Module, core):
    _LDI(m, core, core.rb)
def LDX_exec(m: Module, core):
    _LDI(m, core, core.rx)

Instruction(0xD0, "LDA", LDA_exec, _length)
Instruction(0xD1, "LDB", LDB_exec, _length)
Instruction(0xD2, "LDX", LDX_exec, _length)