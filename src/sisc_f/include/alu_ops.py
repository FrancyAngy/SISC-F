# SISC-F 32-bit CPU
# Copyright (c) 2026 Francesco Angeloni
#
# This source describes Open Hardware and is licensed under the CERN-OHL-W v2.
# You may redistribute and modify this source and make products using it
# under the terms of the CERN-OHL-W v2 (https://cern.ch/cern-ohl).
#
# SPDX-License-Identifier: CERN-OHL-W-2.0

from collections.abc import Callable
from typing import Any

from .enums import AluOps
from .exceptions import *

alu_operations: dict[AluOps, Any] = {}


class AluOperation:

    def __init__(self, Operation: AluOps, execute: Callable):
        if Operation in alu_operations:
            raise AluOperationAlreadyImplemented

        self._execute = execute
        alu_operations[Operation] = self

    def execute(self, m, core):
        self._execute(m, core)
