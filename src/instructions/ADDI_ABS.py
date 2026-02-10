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

def _ADDI_ABS(m: Module, core: "Core", register: Signal):
    with m.If(core.instr_state == 1):
        core.advance_ip_goto_state(m, 2)
    with m.Else():
        m.d.comb += [
            core.alu_1.eq(register),
            core.alu_2.eq(core.data_in),
            core.alu_op.eq(AluOps.ADD),
            core.alu_en.eq(1)
        ]
        m.d.sync += register.eq(core.alu_out)
        core.end_instr(m, core.ip + 1)

def ADDA_ABS_exec(m: Module, core):
    _ADDI_ABS(m, core, core.ra)

def ADDB_ABS_exec(m: Module, core):
    _ADDI_ABS(m, core, core.rb)

def ADDX_ABS_exec(m: Module, core):
    _ADDI_ABS(m, core, core.rx)

Instruction(0x30, "ADDA_ABS", ADDA_ABS_exec, 0x2)
Instruction(0x31, "ADDB_ABS", ADDB_ABS_exec, 0x2)
Instruction(0x32, "ADDX_ABS", ADDX_ABS_exec, 0x2)