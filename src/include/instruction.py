from amaranth import Module
from typing import Callable

instruction_opcodes = {}

class OpcodeAlreadyExists(Exception):
    def __init__(self, opcode: int, instrName: str, addInfo = None):
        self.opcode = opcode
        self.instrName = instrName
        self.addInfo = addInfo

    def __str__(self) -> str:
        e: str = f"Tried assigining instruction {self.instrName} to opcode {self.opcode}, but it was already assigned to instruction {instruction_opcodes[self.opcode].name}. "
        if self.addInfo != None:
            e += f"Additional info are provided: {self.addInfo}"
        return e

class Instruction:
    """
    Create an instruction with an opcode, name, length and function
    """
    def execute(self, m: Module, core):
        self.executeFunc(m, core)

    def __init__(self, opcode: int, name: str, execute: Callable, length: int = 0x01):
        self.opcode: int = opcode
        self.length: int = length
        self.name: str = name
        self.executeFunc: Callable = execute
        if instruction_opcodes.get(self.opcode) != None:
            raise OpcodeAlreadyExists(opcode, name)
        instruction_opcodes[self.opcode] = self

    def __str__(self) -> str:
        return f"Instruction {self.name} with opcode {self.opcode} and length {self.length}"