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
from include.enums import *

def _STI(m: Module, core, registry: Signal):
    with m.Switch(core.instr_state):
        with m.Case(1):
            core.advance_ip_goto_state(m, 2)
        with m.Case(2):
            m.d.sync += core.addr.eq(core.data_in)
            m.d.sync += core.RW.eq(0) 
            m.d.sync += core.data_out.eq(registry)
            m.d.sync += core.instr_state.eq(3)
        with m.Case(3):
            m.d.sync += core.RW.eq(1)
            m.d.sync += core.data_out.eq(0)
            core.end_instr(m, core.ip + 1)

def STA_exec(m: Module, core):
    _STI(m, core, core.ra)

def STB_exec(m: Module, core):
    _STI(m, core, core.rb)

def STX_exec(m: Module, core):
    _STI(m, core, core.rx)

Instruction(0x40, "STA", STA_exec, 0x3)
Instruction(0x41, "STB", STB_exec, 0x3)
Instruction(0x42, "STX", STX_exec, 0x3)