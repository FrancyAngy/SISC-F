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
from amaranth import Module
from include.enums import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Core

def _execute(m: Module, core: "Core", flag: Flags, value: int):
    m.d.sync += core.flags[flag].eq(value)

def _SCF(m: Module, core):
    _execute(m, core, Flags.CARRY, 1)

def _CCF(m: Module, core):
    _execute(m, core, Flags.CARRY, 0)

def _SEF(m: Module, core):
    _execute(m, core, Flags.ERROR, 1)

def _CEF(m: Module, core):
    _execute(m, core, Flags.ERROR, 0)

Instruction(0xF0, "SCF", _SCF)
Instruction(0xF1, "CCF", _CCF)
Instruction(0xF2, "SEF", _SEF)
Instruction(0xF3, "CEF", _CEF)