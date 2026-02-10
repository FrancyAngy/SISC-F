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

def _exec(m: Module, core: "Core", register: Signal):
    with m.Switch(core.instr_state):
        with m.Case(1):
            m.d.comb += [
                core.stack_data.eq(register),
                core.stack_op.eq(StackOps.PUSH),
                core.stack_en.eq(1)
            ]
            m.d.sync += core.instr_state.eq(2)
        with m.Case(2):
            m.d.sync += [
                core.RW.eq(1),
                core.data_out.eq(0)
            ]
            core.end_instr(m, core.ip + 1)

def _exec_PUSHA(m: Module, core: "Core"):
    _exec(m, core, core.ra)

def _exec_PUSHB(m: Module, core: "Core"):
    _exec(m, core, core.rb)

def _exec_PUSHX(m: Module, core: "Core"):
    _exec(m, core, core.rx)

Instruction(0xA1, "PUSHA", _exec_PUSHA)
Instruction(0xA2, "PUSHB", _exec_PUSHB)
Instruction(0xA3, "PUSHX", _exec_PUSHX)