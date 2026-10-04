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


def _exec(m: Module, core: "Core"):
    with m.Switch(core.instr_state):
        with m.Case(1), m.Switch(core.ir[:16]):
            for index, register in enumerate(core.reg_ids):
                with m.Case(index):
                    m.d.comb += core.stack_data.eq(register)
            with m.Default():
                m.d.comb += core.stack_data.eq(0)
                m.d.sync += core.flags[Flags.ERROR].eq(1)
            m.d.comb += [
                core.stack_op.eq(StackOps.PUSH),
                core.stack_en.eq(1),
            ]
            m.d.sync += core.instr_state.eq(2)
        with m.Case(2):
            m.d.sync += [core.RW.eq(1), core.data_out.eq(0)]
            core.end_instr(m, core.ip + 1)


CompressedInstruction(0x0011, "PUSHR", _exec)
