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

def _exec(m: Module, core: "Core", flag, invert: bool = False):
    if invert:
        flag = ~flag

    with m.If(flag):
        with m.Switch(core.instr_state):
            with m.Case(2):
                core.end_instr(m, core.data_in)
            with m.Default():
                core.advance_ip_goto_state(m, 2)
    with m.Else():
        core.end_instr(m, core.ip + 3)

def _JIZ_exec(m: Module, core: "Core"):
    _exec(m, core, core.flags[Flags.ZERO])

def _JNZ_exec(m: Module, core: "Core"):
    _exec(m, core, core.flags[Flags.ZERO], True)

def _JIC_exec(m: Module, core: "Core"):
    _exec(m, core, core.flags[Flags.CARRY])

def _JNC_exec(m: Module, core: "Core"):
    _exec(m, core, core.flags[Flags.CARRY], True)

def _JIE_exec(m: Module, core: "Core"):
    _exec(m, core, core.flags[Flags.ERROR])
 
def _JNE_exec(m: Module, core: "Core"):
    _exec(m, core, core.flags[Flags.ERROR], True)


Instruction(0x11, "JIZ", _JIZ_exec, 0x03)
Instruction(0x12, "JNZ", _JNZ_exec, 0x03)
Instruction(0x13, "JIC", _JIC_exec, 0x03)
Instruction(0x14, "JNC", _JNC_exec, 0x03)
Instruction(0x15, "JIE", _JIE_exec, 0x03)
Instruction(0x16, "JNE", _JNE_exec, 0x03)