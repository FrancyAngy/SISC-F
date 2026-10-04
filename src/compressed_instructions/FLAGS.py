# SISC-F 32-bit CPU
# Copyright (c) 2026 Francesco Angeloni
#
# This source describes Open Hardware and is licensed under the CERN-OHL-W v2.
# You may redistribute and modify this source and make products using it
# under the terms of the CERN-OHL-W v2 (https://cern.ch/cern-ohl).
#
# SPDX-License-Identifier: CERN-OHL-W-2.0

from typing import TYPE_CHECKING

from amaranth import Module

from include.enums import *
from include.instruction import *

if TYPE_CHECKING:
    from main import Core


def _exec_set(m: Module, core: "Core"):
    with m.Switch(core.ir[:16]):
        for flag in Flags:
            with m.Case(flag.value):
                m.d.sync += core.flags[flag].eq(1)
        with m.Default():
            m.d.sync += core.flags[Flags.ERROR].eq(1)
    core.end_instr(m, core.ip + 1)


def _exec_clear(m: Module, core: "Core"):
    with m.Switch(core.ir[:16]):
        for flag in Flags:
            with m.Case(flag.value):
                m.d.sync += core.flags[flag].eq(0)
        with m.Case(0xFFFF):
            m.d.sync += core.flags.eq(0)
        with m.Default():
            m.d.sync += core.flags[Flags.ERROR].eq(1)
    core.end_instr(m, core.ip + 1)


CompressedInstruction(0x0020, "SF", _exec_set)
CompressedInstruction(0x0021, "CF", _exec_clear)
