# SPDX-FileCopyrightText: 2026 Francesco Angeloni
# SPDX-License-Identifier: CERN-OHL-W-2.0

import os
import importlib

for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith(".py") and file != "__init__.py":
        module_name = file[:-3]
        importlib.import_module(f"pseudo_instructions.{module_name}")