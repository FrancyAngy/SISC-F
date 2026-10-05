# SPDX-FileCopyrightText: 2026 Francesco Angeloni
# SPDX-License-Identifier: CERN-OHL-W-2.0

import importlib
import os
from typing import TYPE_CHECKING

from amaranth import Module

from ..include import alu_ops
from ..include.enums import Flags

for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith(".py") and file != "__init__.py":
        module_name = file[:-3]
        importlib.import_module(f"{__name__}.{module_name}")

if TYPE_CHECKING:
    from ..main import Core


def alu_handler(m: Module, core: "Core"):
    with m.If(core.alu_en):
        m.d.sync += core.flags.eq(0)
        with m.Switch(core.alu_op):
            for operation, implementation in alu_ops.alu_operations.items():
                with m.Case(operation):
                    implementation.execute(m, core)
            with m.Default():
                m.d.comb += core.alu_out.eq(0)
                m.d.sync += core.flags[Flags.ERROR].eq(1)
        m.d.comb += core.alu_en.eq(0)
