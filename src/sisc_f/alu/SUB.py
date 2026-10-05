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


def _exec(m: Module, core: "Core"):
    m.d.comb += [
        core.alu_out.eq(core.alu_1 - core.alu_2),
        core.alu_33.eq(core.alu_1.as_unsigned() - core.alu_2.as_unsigned()),
    ]
    m.d.sync += [
        core.flags[Flags.ZERO].eq(core.alu_out == 0),
        core.flags[Flags.NEGATIVE].eq(core.alu_out < 0),
        core.flags[Flags.OVERFLOW].eq(
            (core.alu_1[31] != core.alu_2[31]) & (core.alu_1[31] != core.alu_out[31])
        ),
        core.flags[Flags.CARRY].eq(core.alu_33[32]),
    ]


AluOperation(AluOps.SUB, _exec)
