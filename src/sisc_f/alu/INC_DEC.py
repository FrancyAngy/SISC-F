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

from ..include.alu_ops import *
from ..include.enums import *

if TYPE_CHECKING:
    from ..main import Core


def _exec_inc(m: Module, core: "Core"):
    m.d.comb += core.alu_out.eq(core.alu_1 + 1)

    m.d.sync += [
        core.flags[Flags.ZERO].eq(core.alu_out == 0),
        core.flags[Flags.NEGATIVE].eq(core.alu_out < 0),
        core.flags[Flags.OVERFLOW].eq(
            core.alu_out.as_signed() < core.alu_1.as_signed()
        ),
        core.flags[Flags.CARRY].eq(0),
    ]


def _exec_dec(m: Module, core: "Core"):
    m.d.comb += core.alu_out.eq(core.alu_1 - 1)

    m.d.sync += [
        core.flags[Flags.ZERO].eq(core.alu_out == 0),
        core.flags[Flags.NEGATIVE].eq(core.alu_out < 0),
        core.flags[Flags.OVERFLOW].eq(
            core.alu_out.as_signed() > core.alu_1.as_signed()
        ),
        core.flags[Flags.CARRY].eq(0),
    ]


AluOperation(AluOps.INC, _exec_inc)
AluOperation(AluOps.DEC, _exec_dec)
