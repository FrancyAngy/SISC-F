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
from include.enums import *
from amaranth import Module, Signal

_length = 0x2

def _LDI_ABS(m: Module, core, register: Signal):
    with m.If(core.instr_state == 1):
        core.advance_ip_goto_state(m, 2)
    with m.Else():
        m.d.sync += [
            register.eq(core.data_in),
            core.flags[Flags.NEGATIVE].eq(core.data_in < 0),
            core.flags[Flags.ZERO].eq(core.data_in == 0),
        ]
        core.end_instr(m, core.ip + 1)

def LDA_ABS_exec(m: Module, core):
    _LDI_ABS(m, core, core.ra)
def LDB_ABS_exec(m: Module, core):
    _LDI_ABS(m, core, core.rb)
def LDX_ABS_exec(m: Module, core):
    _LDI_ABS(m, core, core.rx)

Instruction(0x20, "LDA_ABS", LDA_ABS_exec, _length)
Instruction(0x21, "LDB_ABS", LDB_ABS_exec, _length)
Instruction(0x22, "LDX_ABS", LDX_ABS_exec, _length)