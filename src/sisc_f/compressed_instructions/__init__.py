# SPDX-FileCopyrightText: 2026 Francesco Angeloni
# SPDX-License-Identifier: CERN-OHL-W-2.0

import importlib
import os

from ..include.instruction import compressed_instruction_opcodes

__all__ = ["compressed_instruction_opcodes"]

for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith(".py") and file != "__init__.py":
        module_name = file[:-3]
        importlib.import_module(f"{__name__}.{module_name}")
