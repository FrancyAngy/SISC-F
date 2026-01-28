from enum import IntEnum, auto

class AluOps(IntEnum):
    NONE = 0
    ADD = auto()
    SUB = auto()
    MUL = auto()
    INC = auto()
    DEC = auto()

class Flags(IntEnum):
    ZERO = 0
    CARRY = 1
    NEGATIVE = 2
    ERROR = 3
    OVERFLOW = 4