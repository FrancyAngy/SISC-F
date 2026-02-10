# SISC-F 32-bit CPU
# Copyright (c) 2026 Francesco Angeloni
#
# This source describes Open Hardware and is licensed under the CERN-OHL-W v2.
# You may redistribute and modify this source and make products using it 
# under the terms of the CERN-OHL-W v2 (https://cern.ch/cern-ohl).
#
# SPDX-License-Identifier: CERN-OHL-W-2.0

from amaranth import Module
from typing import Callable
from include.exceptions import *

instruction_opcodes = {}
instruction_names = {}
assembler_inst = {}

class OpcodeAlreadyExists(Exception):
    def __init__(self, opcode: int, instrName: str, addInfo = None):
        self.opcode = opcode
        self.instrName = instrName
        self.addInfo = addInfo

    def __str__(self) -> str:
        e: str = f"Tried assigining instruction {self.instrName} to opcode 0x{hex(self.opcode).upper()[2:]}, but it was already assigned to instruction {instruction_opcodes[self.opcode].name}. "
        if self.addInfo != None:
            e += f"Additional info are provided: {self.addInfo}"
        return e

class Instruction:
    """
    Create an instruction with an opcode, name, length and function
    """
    def execute(self, m: Module, core):
        self._executeFunc(m, core)

    def asmOverride(self, assembler, parameters: list[str] | None = None):
        if self._asmFunc != None:
            self._asmFunc(self, assembler, parameters)
            return True
        else:
            return False

    def __init__(self, opcode: int, name: str, execute: Callable, length: int = 0x01, asmFunc: Callable | None = None):
        self.opcode: int = opcode
        self.length: int = length
        self.name: str = name
        self._executeFunc: Callable = execute
        self._asmFunc: Callable | None = asmFunc
        if instruction_opcodes.get(self.opcode) != None:
            raise OpcodeAlreadyExists(self.opcode, self.name)
        if instruction_names.get(self.name) != None:
            raise InstructionNameAlreadyExists(self.name)
        if assembler_inst.get(self.name) != None:
            raise AssemblerInstructionAlreadyExists(self.name)
        instruction_opcodes[self.opcode] = self
        instruction_names[self.name] = self
        assembler_inst[self.name] = self

    def __str__(self) -> str:
        s = f"Instruction {self.name} with opcode 0x{hex(self.opcode).upper()[2:]} and length 0x{hex(self.length).upper()[2:]}."
        if self._asmFunc != None:
            s += "Overrides assembler standard instructions."

        return s

class PseudoInstruction:
    def __init__(self, name: str, execute: Callable):
        self.name: str = name
        self._executeAsm: Callable = execute
        if assembler_inst.get(self.name) != None:
            raise AssemblerInstructionAlreadyExists(self.name)
        assembler_inst[self.name] = self

    def execute(self, assembler, parameters: list[str] | None = None):
        self._executeAsm(self, assembler, parameters)
        return True

    def __str__(self) -> str:
        s = f"Pseudo-instruction {self.name}."
        return s