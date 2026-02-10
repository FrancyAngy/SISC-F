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

def _exec(m: Module, core: "Core", register: Signal):
    m.d.comb += [
        core.alu_1.eq(register),
        core.alu_op.eq(AluOps.INC),
        core.alu_en.eq(1)
    ]
    m.d.sync += register.eq(core.alu_out)
    core.end_instr(m, core.ip + 1)

def _exec_INCA(m: Module, core: "Core"):
    _exec(m, core, core.ra)

def _exec_INCB(m: Module, core: "Core"):
    _exec(m, core, core.rb)

def _exec_INCX(m: Module, core: "Core"):
    _exec(m, core, core.rx)

Instruction(0x36, "INCA", _exec_INCA)
Instruction(0x37, "INCB", _exec_INCB)
Instruction(0x38, "INCX", _exec_INCX)