from include import exceptions
from include.instruction import *
from amaranth import Module

def NOP_exec(m: Module, core):
    core.end_instr(m, core.ip + 1)

NOP = Instruction(0x01, "NOP", NOP_exec)