from core.memory import Memory
from core.register import Register
from core.exceptions import UnknownOpcodeError

import random
import logging

class Cpu:
    def __init__(self, memory, display, delay_timer, sound_timer):
        self._memory    = memory
        self._display   = display

        self._delay_timer = delay_timer
        self._sound_timer = sound_timer

        self._v = [Register(8) for i in range(0, 0x10)] # 0xF + 1
        self._i = Register(16)
        self._pc = 0x0

        self._stack = Memory(12, cell_bit_size=16)
        self._sp    = 0

        self._standard_ops = {
            0x1: self._jump_to_address,
            0x2: self._call_subroutine,
            0x3: self._skip_if_reg_equal_const,
            0x4: self._skip_if_reg_not_equal_const,
            0x5: self._skip_if_reg_equal_reg,
            0x6: self._set_reg_to_const,
            0x7: self._add_const_to_reg,
            0x9: self._skip_if_reg_not_equal_reg,
            0xA: self._set_i_to_address,
            0xB: self._jump_to_address_plus_v0,
            0xC: self._set_reg_to_xor_rand_and_const,
            0xD: self._draw_sprite,
            0xE: self._skip_on_key_press_event,
        }

        self._extended_ops_decode = {
            0x0: self._decode_0_ops,
            0x8: self._decode_8_ops,
            0xF: self._decode_F_ops
        }

        self._8_ops = {
            0x0: self._mov_reg_to_reg,
            0x1: self._bitwise_or,
            0x2: self._bitwise_and,
            0x3: self._bitwise_xor,
            0x4: self._add_reg_to_reg,
            0x5: self._sub_reg_to_reg,
            0x6: self._right_shift,
            0x7: self._sub_reg_to_reg_inv,
            0xE: self._left_shift,
        }

        self._F_ops = {
            0x07: self._mov_delay_to_reg,
            0x0A: self._set_delay_to_reg,
            0x15: self._set_sound_to_reg,
            0x1E: self._add_reg_to_i,
            0x29: self._mov_reg_sprite_addr_to_i,
            0x33: self._mov_reg_to_bcd,
            0x55: self._dump_regs,
            0x65: self._load_regs
        }

    def set_starting_address(self, address):
        if address > len(self._memory):
            raise OverflowError(address, len(self._memory))

        self._pc = address

    def tick(self):
        instruction = self._fetch()
        opcode, operands = self._decode(instruction)

        self._execute(opcode, operands)

    def __repr__(self):
        registers = [
            "   ".join([
                f"V{c * 4 + i:X}: 0x{self._v[c*4+i].get():0>2x}"
                for i in range(0, 4)
            ])
            for c in range(0, 4)
        ]

        return "\n".join([
            "CPU state",
            "--- Registers ---",
            "\n".join(registers),
            "",
            f"I: 0x{self._i.get():0>12x}     PC: 0x{self._pc:0>12x}",
            ""
        ])

    def _fetch(self):
        instruction = self._memory[self._pc] << 8 | self._memory[self._pc + 1]
        self._pc += 2

        logging.debug(f"Instruction fetched at [0x{self._pc:0>12x}] : 0x{instruction:0>4x}")

        return instruction

    def _decode(self, instruction):
        opcode = (instruction & 0xF000) >> 12
        operands = instruction & 0x0FFF

        if opcode in self._standard_ops:
            return self._standard_ops[opcode], operands

        if opcode in self._extended_ops_decode:
            decoded = self._extended_ops_decode[opcode](operands)

        if decoded == None:
            raise UnknownOpcodeError(instruction)

        return decoded

    def _execute(self, opcode, operands):
        logging.debug(f"Executing <{opcode.__name__}>(0x{operands:3>x})")
        opcode(operands)

    def _skip_next_instruction(self):
        self._pc += 2

    def _decode_0_ops(self, operands):
        if operands == 0x0E0:
            return (self._clear_display, 0x000)
        elif operands == 0x0EE:
            return (self._ret, 0x000)

    def _decode_8_ops(self, operands):
        op = operands & 0x00F

        if op in self._8_ops:
            return self._8_ops[op], operands

    def _decode_F_ops(self, operands):
        op = operands & 0xFF

        if op in self._F_ops:
            return self._F_ops[op], operands

    def _clear_display(self, operands):
        self._display.clear()

    def _ret(self, operands):
        """
        Return from a subroutine.The interpreter sets the program counter to the address at the top of the stack,
        then subtracts 1 from the stack pointer.
        """

        self._sp -= 1
        self._pc = self._stack[self._sp]
    
    def _jump_to_address(self, operands):
        """
        1nnn - JP addr
        Jump to location nnn. The interpreter sets the program counter to nnn.
        """

        self._pc = operands

    def _call_subroutine(self, operands):
        """
        2nnn - CALL addr
        Call subroutine at nnn. The interpreter increments the stack pointer, then puts the current PC on the top
        of the stack. The PC is then set to nnn.
        """

        self._stack[self._sp] = self._pc
        self._sp += 1
        self._pc = operands

    def _skip_if_reg_equal_const(self, operands):
        """
        3xkk - SE Vx, byte
        Skip next instruction if Vx = kk. The interpreter compares register Vx to kk, and if they are equal,
        increments the program counter by 2.
        """

        register = (operands & 0xF00) >> 8
        const    = operands & 0x0FF

        if self._v[register].get() == const:
            self._skip_next_instruction()

    def _skip_if_reg_not_equal_const(self, operands):
        """
        4xkk - SNE Vx, byte
        Skip next instruction if Vx != kk. The interpreter compares register Vx to kk, and if they are not equal,
        increments the program counter by 2.
        """

        register = (operands & 0xF00) >> 8
        const    = operands & 0x0FF

        if self._v[register].get() != const:
            self._skip_next_instruction()

    def _skip_if_reg_equal_reg(self, operands):
        """
        5xy0 - SE Vx, Vy
        Skip next instruction if Vx = Vy. The interpreter compares register Vx to register Vy, and if they are equal,
        increments the program counter by 2.
        """

        reg1 = (operands & 0xF00) >> 8
        reg2 = (operands & 0x0F0) >> 4

        if self._v[reg1].get() == self._v[reg2].get():
            self._skip_next_instruction()


    def _set_reg_to_const(self, operands):
        """
        6xkk - LD Vx, byte
        Set Vx = kk. The interpreter puts the value kk into register Vx
        """

        reg     = (operands & 0xF00) >> 8
        value   = (operands & 0x0FF)

        self._v[reg].set(value)

    def _add_const_to_reg(self, operands):
        """
        7xkk - ADD Vx, byte
        Set Vx = Vx + kk. Adds the value kk to the value of register Vx, then stores the result in Vx.
        """
        
        register = (operands & 0xF00) >> 8
        const    = operands & 0x0FF

        self._v[register].set(self._v[register].get() + const)

    def _skip_if_reg_not_equal_reg(self, operands):
        """
        9xy0 - SNE Vx, Vy
        Skip next instruction if Vx != Vy. The values of Vx and Vy are compared, and if they are not equal, the
        program counter is increased by 2.
        """

        reg1 = (operands & 0xF00) >> 8
        reg2 = (operands & 0x0F0) >> 4

        if self._v[reg1].get() != self._v[reg2].get():
            self._skip_next_instruction()


    def _set_i_to_address(self, operands):
        """
        Annn - LD I, addr
        Set I = nnn. The value of register I is set to nnn.
        """

        self._i.set(operands)

    def _jump_to_address_plus_v0(self, operands):
        """
        Bnnn - JP V0, addr
        Jump to location nnn + V0. The program counter is set to nnn plus the value of V0.
        """

        self._pc = operands + self._v[0x0].get()

    def _set_reg_to_xor_rand_and_const(self, operands):
        """
        Cxkk - RND Vx, byte
        Set Vx = random byte AND kk. The interpreter generates a random number from 0 to 255, which is then
        ANDed with the value kk. The results are stored in Vx. See instruction 8xy2 for more information on AND.
        """

        reg     = (operands & 0xF00) >> 8
        value   = (operands & 0x0FF)
        r       = random.randint(0x0, 0xFF)

        self._v[reg].set(r & value)

    def _draw_sprite(self, operands):
        """
        Dxyn - DRW Vx, Vy, nibble
        Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.

        The interpreter reads n bytes from memory, starting at the address stored in I. 
        These bytes are then displayed as sprites on screen at coordinates (Vx, Vy). 
        Sprites are XORed onto the existing screen. If this causes any pixels to be erased, 
        VF is set to 1, otherwise it is set to 0. If the sprite is positioned so part of 
        it is outside the coordinates of the display, it wraps around to the opposite side 
        of the screen. 
        See instruction 8xy3 for more information on XOR, and section 2.4, Display, 
        for more information on the Chip-8 screen and sprites.
        """

        vx = (operands & 0xF00) >> 8
        vy = (operands & 0x0F0) >> 4
        n = (operands & 0x00F)

        x, y = self._v[vx].get(), self._v[vy].get()

        b = [self._memory[self._i.get() + i] for i in range(0, n)]

        collided = self._display.draw(x, y, b)
        self._v[0xF].set(int(collided))

    def _skip_on_key_press_event(self, operands):
        raise NotImplementedError

    def _mov_reg_to_reg(self, operands):
        """
        8xy0 - LD Vx, Vy
        Set Vx = Vy. Stores the value of register Vy in register Vx
        """

        reg1 = (operands & 0xF00) >> 8
        reg2 = (operands & 0x0F0) >> 4

        self._v[reg1].set(self._v[reg2].get())

    def _bitwise_or(self, operands):
        """
        8xy1 - OR Vx, Vy
        Set Vx = Vx OR Vy. Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx. A
        bitwise OR compares the corresponding bits from two values, and if either bit is 1, then the same bit in the
        result is also 1. Otherwise, it is 0.
        """

        reg1 = (operands & 0xF00) >> 8
        reg2 = (operands & 0x0F0) >> 4

        # Reg auto-mask value to the right size
        self._v[reg1].set(
            self._v[reg1].get() | self._v[reg2].get()
        )


    def _bitwise_and(self, operands):
        """
        8xy2 - AND Vx, Vy
        Set Vx = Vx AND Vy. Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx.
        A bitwise AND compares the corresponding bits from two values, and if both bits are 1, then the same bit
        in the result is also 1. Otherwise, it is 0.
        """

        reg1 = (operands & 0xF00) >> 8
        reg2 = (operands & 0x0F0) >> 4

        # Reg auto-mask value to the right size
        self._v[reg1].set(
            self._v[reg1].get() & self._v[reg2].get()
        )

    def _bitwise_xor(self, operands):
        """
        8xy3 - XOR Vx, Vy
        Set Vx = Vx XOR Vy. Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result
        in Vx. An exclusive OR compares the corresponding bits from two values, and if the bits are not both the
        same, then the corresponding bit in the result is set to 1. Otherwise, it is 0.
        """

        reg1 = (operands & 0xF00) >> 8
        reg2 = (operands & 0x0F0) >> 4

        # Reg auto-mask value to the right size
        self._v[reg1].set(
            self._v[reg1].get() ^ self._v[reg2].get()
        )

    def _add_reg_to_reg(self, operands):
        """
        8xy4 - ADD Vx, Vy
        Set Vx = Vx + Vy, set VF = carry. The values of Vx and Vy are added together. If the result is greater
        than 8 bits (i.e., ¿ 255,) VF is set to 1, otherwise 0. Only the lowest 8 bits of the result are kept, and stored
        in Vx.
        """
        
        reg1 = (operands & 0xF00) >> 8
        reg2 = (operands & 0x0F0) >> 4

        value = self._v[reg1].get() + self._v[reg2].get()

        self._v[0xF].set(value > 0xFF)

        # Reg auto-mask value to the right size
        self._v[reg1].set(value)


    def _sub_reg_to_reg(self, operands):
        """
        8xy5 - SUB Vx, Vy
        Set Vx = Vx - Vy, set VF = NOT borrow.

        If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted from Vx, and the results stored in Vx.
        """

        reg1 = (operands & 0xF00) >> 8
        reg2 = (operands & 0x0F0) >> 4

        vx = self._v[reg1]
        vy = self._v[reg2]

        self._v[0xF].set(vx.get() > vy.get())
        vx.set((vx.get() - vy.get()) % 0x100)

    def _left_shift(self, operands):
        """
        8xyE - SHL Vx {, Vy}
        Set Vx = Vx SHL 1. If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is
        multiplied by 2.
        """

        reg1 = (operands & 0xF00) >> 8
        reg2 = (operands & 0x0F0) >> 4

        flag = (self._v[reg1].get() & 0x80) >> 7 # 0x80 = 0b1000.0000

        self._v[0xF].set(flag)
        self._v[reg2].set(self._v[reg1].get() << 1)

    def _sub_reg_to_reg_inv(self, operands):
        """
        8xy7 - SUBN Vx, Vy
        Set Vx = Vy - Vx, set VF = NOT borrow.

        If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results stored in Vx.
        """

        reg1 = (operands & 0xF00) >> 8
        reg2 = (operands & 0x0F0) >> 4

        vx = self._v[reg1]
        vy = self._v[reg2]

        self._v[0xF].set(vy.get() > vx.get())
        vx.set((vy.get() - vx.get()) % 0x100)

    def _right_shift(self, operands):
        """
        8xy6 - SHR Vx {, Vy}
        Set Vx = Vx SHR 1.

        If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is divided by 2.
        """

        reg1 = (operands & 0xF00) >> 8
        reg2 = (operands & 0x0F0) >> 4
        flag = (self._v[reg1].get() & 0x01)

        self._v[0xF].set(flag)
        self._v[reg2].set(self._v[reg1].get() >> 1)

    def _mov_delay_to_reg(self, operands):
        """
        Fx07 - LD Vx, DT
        Set Vx = delay timer value. The value of DT is placed into Vx.
        """

        reg = (operands & 0xF00) >> 8

        self._v[reg].set(self._delay_timer.get())

    def _set_delay_to_reg(self, operands):
        """
        Fx15 - LD DT, Vx
        Set delay timer = Vx.

        DT is set equal to the value of Vx.
        """

        reg = (operands & 0xF00) >> 8

        self._delay_timer.set(self._v[reg].get())

    def _set_sound_to_reg(self, operands):
        """
        Fx18 - LD ST, Vx
        Set sound timer = Vx.

        ST is set equal to the value of Vx.
        """

        reg = (operands & 0xF00) >> 8

        self._sound_timer.set(self._v[reg].get())

    def _add_reg_to_i(self, operands):
        """
        Fx1E - ADD I, Vx
        Set I = I + Vx. The values of I and Vx are added, and the results are stored in I.
        """

        reg = (operands & 0xF00) >> 8

        self._i.set(self._i.get() + self._v[reg].get())

    def _mov_reg_sprite_addr_to_i(self, operands):
        """
        Fx29 - LD F, Vx
        Set I = location of sprite for digit Vx.

        The value of I is set to the location for the hexadecimal sprite corresponding 
        to the value of Vx. See section 2.4, Display, for more information on the Chip-8 hexadecimal font.
        """

        reg   = (operands & 0xF00) >> 8
        value = self._v[reg].get()

        # TODO: what if value > 0
        self._i.set(value * 5)

    def _mov_reg_to_bcd(self, operands):
        """
        Fx33 - LD B, Vx
        Store BCD representation of Vx in memory locations I, I+1, and I+2. The interpreter takes the decimal
        value of Vx, and places the hundreds digit in memory at location in I, the tens digit at location I+1, and
        the ones digit at location I+2.
        """

        reg = (operands & 0xF00) >> 8
        value = self._v[reg].get()

        for i in reversed(range(0, 3)):
            self._memory[self._i.get() + i] = value % 10
            value //= 10


    def _dump_regs(self, operands):
        """
        Fx55 - LD [I], Vx
        Stores V0 to VX in memory starting at address I. I is then set to I + x + 1.
        """

        end_register = (operands & 0xF00) >> 8

        for i in range(0x0, end_register + 1):
            self._memory[self._i.get() + i] = self._v[i].get()

        # TODO: self._i.add(end_register + 1)
        self._i.set(self._i.get() + end_register + 1)

    def _load_regs(self, operands):
        """
        Fx65 - LD Vx, [I]
        Fills V0 to VX with values from memory starting at address I. I is then set to I + x + 1.
        """

        end_register = (operands & 0xF00) >> 8

        for i in range(0x0, end_register + 1):
            self._v[i].set(self._memory[self._i.get() + i])

        self._i.set(self._i.get() + end_register + 1)

