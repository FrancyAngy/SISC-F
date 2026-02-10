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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Core

def _ADDI(m: Module, core: "Core", register: Signal):
    with m.Switch(core.instr_state):
        with m.Case(1):
            core.advance_ip_goto_state(m, 2)
        with m.Case(2):
            m.d.sync += [
                core.addr.eq(core.data_in),
                core.instr_state.eq(3)
            ]
        with m.Case(3):
            m.d.comb += [
                core.alu_1.eq(register),
                core.alu_2.eq(core.data_in),
                core.alu_op.eq(AluOps.ADD),
                core.alu_en.eq(1)
            ]
            m.d.sync += register.eq(core.alu_out)
            core.end_instr(m, core.ip + 1)

def ADDA_exec(m: Module, core):
    _ADDI(m, core, core.ra)

def ADDB_exec(m: Module, core):
    _ADDI(m, core, core.rb)

def ADDX_exec(m: Module, core):
    _ADDI(m, core, core.rx)

Instruction(0xE0, "ADDA", ADDA_exec, 0x2)
Instruction(0xE1, "ADDB", ADDB_exec, 0x2)
Instruction(0xE2, "ADDX", ADDX_exec, 0x2)