class UnknownOpcodeError(Exception):
    def __init__(self, opcode):
        self.opcode = opcode

    def __str__(self):
        return f"Unknown opcode 0x{self.opcode:x}"