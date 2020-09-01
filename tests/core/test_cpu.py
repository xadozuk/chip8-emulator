import unittest
import random
from core.cpu import Cpu
from core.memory import Memory
from core.timer import Timer

class TestCpu(unittest.TestCase):
    def setUp(self):
        self.memory = Memory(0x1000)
        self.sound_timer = Timer(freq=60)
        self.delay_timer = Timer(freq=60)
        self.cpu = Cpu(self.memory, None, delay_timer=self.delay_timer, sound_timer=self.sound_timer)

    @unittest.skip("Not implemented")
    def test_clear_display(self):
        pass

    def test_ret(self):
        """
        Return from a subroutine.The interpreter sets the program counter to the address at the top of the stack,
        then subtracts 1 from the stack pointer.
        """

        # Add an address to the stack
        self.cpu._stack[0x0] = 0x1234
        self.cpu._sp = 1

        self.cpu._ret(None)

        self.assertEqual(0, self.cpu._sp)
        self.assertEqual(0x1234, self.cpu._pc)
        
    
    def test_jump_to_address(self):
        """
        1nnn - JP addr
        Jump to location nnn. The interpreter sets the program counter to nnn.
        """
        self.assertEqual(0, self.cpu._pc)

        self.cpu._jump_to_address(0x123)
        
        self.assertEqual(0x123, self.cpu._pc)

    def test_call_subroutine(self):
        """
        2nnn - CALL addr
        Call subroutine at nnn. The interpreter increments the stack pointer, then puts the current PC on the top
        of the stack. The PC is then set to nnn.
        """
        
        self.cpu._pc = 0x321
        self.cpu._call_subroutine(0x123)

        self.assertEqual(1, self.cpu._sp)
        self.assertEqual(0x123, self.cpu._pc)
        self.assertEqual(0x321, self.cpu._stack[0])


    def test_skip_if_reg_equal_const(self):
        """
        3xkk - SE Vx, byte
        Skip next instruction if Vx = kk. The interpreter compares register Vx to kk, and if they are equal,
        increments the program counter by 2.
        """
        
        self.cpu._pc = 0x100
        self.cpu._v[0x0].set(0x1)

        self.cpu._skip_if_reg_equal_const(0x000)

        self.assertEqual(0x100, self.cpu._pc)

        self.cpu._skip_if_reg_equal_const(0x001)

        self.assertEqual(0x100 + 2, self.cpu._pc)


    def test_skip_if_reg_not_equal_const(self):
        """
        4xkk - SNE Vx, byte
        Skip next instruction if Vx != kk. The interpreter compares register Vx to kk, and if they are not equal,
        increments the program counter by 2.
        """
        self.cpu._pc = 0x100
        self.cpu._v[0x0].set(0x1)

        self.cpu._skip_if_reg_not_equal_const(0x001)

        self.assertEqual(0x100, self.cpu._pc)

        self.cpu._skip_if_reg_not_equal_const(0x000)

        self.assertEqual(0x100 + 2, self.cpu._pc)

    def test_skip_if_reg_equal_reg(self):
        """
        5xy0 - SE Vx, Vy
        Skip next instruction if Vx = Vy. The interpreter compares register Vx to register Vy, and if they are equal,
        increments the program counter by 2.
        """

        self.cpu._pc = 0x100
        self.cpu._v[0x0].set(0x50)
        self.cpu._v[0x1].set(0x50)
        self.cpu._v[0x2].set(0x40)

        self.cpu._skip_if_reg_equal_reg(0x020)
        self.assertEqual(0x100, self.cpu._pc)

        self.cpu._skip_if_reg_equal_reg(0x010)
        self.assertEqual(0x100 + 2, self.cpu._pc)

    def test_set_reg_to_const(self):
        """
        6xkk - LD Vx, byte
        Set Vx = kk. The interpreter puts the value kk into register Vx
        """

        self.cpu._v[0x0].set(0x0)

        self.cpu._set_reg_to_const(0x050)
        self.assertEqual(0x50, self.cpu._v[0x0].get())

    def test_add_const_to_reg(self):
        """
        7xkk - ADD Vx, byte
        Set Vx = Vx + kk. Adds the value kk to the value of register Vx, then stores the result in Vx.
        """

        self.cpu._v[0x0].set(0x10)
        self.cpu._add_const_to_reg(0x00F)

        self.assertEqual(0x1F, self.cpu._v[0x0].get())

    def test_skip_if_reg_not_equal_reg(self):
        """
        9xy0 - SNE Vx, Vy
        Skip next instruction if Vx != Vy. The values of Vx and Vy are compared, and if they are not equal, the
        program counter is increased by 2.
        """

        self.cpu._pc = 0x100
        self.cpu._v[0x0].set(0x50)
        self.cpu._v[0x1].set(0x50)
        self.cpu._v[0x2].set(0x40)

        self.cpu._skip_if_reg_not_equal_reg(0x010)
        self.assertEqual(0x100, self.cpu._pc)

        self.cpu._skip_if_reg_not_equal_reg(0x020)
        self.assertEqual(0x100 + 2, self.cpu._pc)

    def test_set_i_to_address(self):
        """
        Annn - LD I, addr
        Set I = nnn. The value of register I is set to nnn.
        """
        
        self.cpu._i.set(0x0)
        self.cpu._set_i_to_address(0x123)

        self.assertEqual(0x123, self.cpu._i.get())

    def test_jump_to_address_plus_v0(self):
        """
        Bnnn - JP V0, addr
        Jump to location nnn + V0. The program counter is set to nnn plus the value of V0.
        """
        
        self.cpu._pc = 0x0
        self.cpu._v[0x0].set(0xFF)
        self.cpu._jump_to_address_plus_v0(0x100)

        self.assertEqual(0x1FF, self.cpu._pc)

    def test_set_reg_to_xor_rand_and_const(self):
        """
        Cxkk - RND Vx, byte
        Set Vx = random byte AND kk. The interpreter generates a random number from 0 to 255, which is then
        ANDed with the value kk. The results are stored in Vx. See instruction 8xy2 for more information on AND.
        """
        
        self.cpu._v[0x0].set(0x0)
        random.seed(0x0)
        n = random.randint(0, 255) # n = 197

        random.seed(0x0)
        self.cpu._set_reg_to_xor_rand_and_const(n) # 0x0kk

        self.assertEqual(n, self.cpu._v[0x0].get())

    @unittest.skip("Not implemented")
    def test_draw_sprite(self):
        pass

    @unittest.skip("Not implemented")
    def test_skip_on_key_press_event(self):
        pass

    def test_mov_reg_to_reg(self):
        """
        8xy0 - LD Vx, Vy
        Set Vx = Vy. Stores the value of register Vy in register Vx
        """
        
        self.cpu._v[0x0].set(0x0)
        self.cpu._v[0x1].set(0x10)

        self.cpu._mov_reg_to_reg(0x010)

        self.assertEqual(0x10, self.cpu._v[0x1].get())

    def test_bitwise_or(self):
        """
        8xy1 - OR Vx, Vy
        Set Vx = Vx OR Vy. Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx. A
        bitwise OR compares the corresponding bits from two values, and if either bit is 1, then the same bit in the
        result is also 1. Otherwise, it is 0.
        """

        self.cpu._v[0x0].set(0xF0)
        self.cpu._v[0x1].set(0x0F)

        self.cpu._bitwise_or(0x011)

        self.assertEqual(0xFF, self.cpu._v[0x0].get()) 

    def test_bitwise_and(self):
        """
        8xy2 - AND Vx, Vy
        Set Vx = Vx AND Vy. Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx.
        A bitwise AND compares the corresponding bits from two values, and if both bits are 1, then the same bit
        in the result is also 1. Otherwise, it is 0.
        """
        self.cpu._v[0x0].set(0xFF)
        self.cpu._v[0x1].set(0x0F)

        self.cpu._bitwise_and(0x012)

        self.assertEqual(0x0F, self.cpu._v[0x0].get()) 

    def test_bitwise_xor(self):
        """
        8xy3 - XOR Vx, Vy
        Set Vx = Vx XOR Vy. Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result
        in Vx. An exclusive OR compares the corresponding bits from two values, and if the bits are not both the
        same, then the corresponding bit in the result is set to 1. Otherwise, it is 0.
        """

        self.cpu._v[0x0].set(0xF8)  #   1111 1000
        self.cpu._v[0x1].set(0x1F)  # ^ 0001 1111
                                    # = 1110 0111 (E7)

        self.cpu._bitwise_xor(0x013)

        self.assertEqual(0xE7, self.cpu._v[0x0].get()) 

    def test_add_reg_to_reg(self):
        """
        8xy4 - ADD Vx, Vy
        Set Vx = Vx + Vy, set VF = carry. The values of Vx and Vy are added together. If the result is greater
        than 8 bits (i.e., ¿ 255,) VF is set to 1, otherwise 0. Only the lowest 8 bits of the result are kept, and stored
        in Vx.
        """

        self.cpu._v[0x0].set(0x0)
        self.cpu._v[0x1].set(0x10)
        self.cpu._v[0xF].set(0x0)

        self.cpu._add_reg_to_reg(0x014)

        self.assertEqual(0x10, self.cpu._v[0x0].get())
        self.assertEqual(0x0, self.cpu._v[0xF].get())

        self.cpu._v[0x2].set(0xFF)
        self.cpu._v[0x3].set(0x1)

        self.cpu._add_reg_to_reg(0x234)

        self.assertEqual(0x0, self.cpu._v[0x2].get())
        self.assertEqual(0x1, self.cpu._v[0xF].get())

    def test_sub_reg_to_reg(self):
        """
        8xy5 - SUB Vx, Vy
        Set Vx = Vx - Vy, set VF = NOT borrow.

        If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted from Vx, and the results stored in Vx.
        """
        
        self.cpu._v[0x0].set(0x11)
        self.cpu._v[0x1].set(0x01)

        self.cpu._sub_reg_to_reg(0x015)

        self.assertEqual(0x10, self.cpu._v[0x0].get())
        self.assertEqual(0x01, self.cpu._v[0xF].get())

        self.cpu._v[0x2].set(0x0)
        self.cpu._v[0x3].set(0x1)

        self.cpu._sub_reg_to_reg(0x235)

        self.assertEqual(0xFF, self.cpu._v[0x2].get())
        self.assertEqual(0x00, self.cpu._v[0xF].get())

    def test_left_shift(self):
        """
        8xyE - SHL Vx {, Vy}
        Set Vx = Vx SHL 1. If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is
        multiplied by 2.
        """

        self.cpu._v[0x0].set(0x01)

        self.cpu._left_shift(0x00E)

        self.assertEqual(0x0, self.cpu._v[0xF].get())
        self.assertEqual(0x2, self.cpu._v[0x0].get())

        self.cpu._v[0x1].set(0x80) # 0b1000 0000
        
        self.cpu._left_shift(0x11E)

        self.assertEqual(0x1, self.cpu._v[0xF].get())
        self.assertEqual(0x0, self.cpu._v[0x1].get())

    def test_sub_reg_to_reg_inv(self):
        """
        8xy7 - SUBN Vx, Vy
        Set Vx = Vy - Vx, set VF = NOT borrow.

        If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results stored in Vx.
        """

        self.cpu._v[0x0].set(0x01)
        self.cpu._v[0x1].set(0x11)

        self.cpu._sub_reg_to_reg_inv(0x017)

        self.assertEqual(0x10, self.cpu._v[0x0].get())
        self.assertEqual(0x1, self.cpu._v[0xF].get())

        self.cpu._v[0x2].set(0x1)
        self.cpu._v[0x3].set(0x0)

        self.cpu._sub_reg_to_reg_inv(0x237)

        self.assertEqual(0xFF, self.cpu._v[0x2].get())
        self.assertEqual(0x0, self.cpu._v[0xF].get())

    def test_right_shift(self):
        """
        8xy6 - SHR Vx {, Vy}
        Set Vx = Vx SHR 1.

        If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is divided by 2.
        """

        self.cpu._v[0x0].set(0x01)

        self.cpu._right_shift(0x00E)

        self.assertEqual(0x1, self.cpu._v[0xF].get())
        self.assertEqual(0x0, self.cpu._v[0x0].get())

        self.cpu._v[0x1].set(0x2) # 0b0000 0010
        
        self.cpu._right_shift(0x11E)

        self.assertEqual(0x0, self.cpu._v[0xF].get())
        self.assertEqual(0x1, self.cpu._v[0x1].get())

    def test_mov_delay_to_reg(self):
        """
        Fx07 - LD Vx, DT
        Set Vx = delay timer value. The value of DT is placed into Vx.
        """

        self.delay_timer._countdown = 0x10

        self.cpu._mov_delay_to_reg(0x007)

        self.assertEqual(0x10, self.cpu._v[0x0].get())

    def test_set_delay_to_reg(self):
        """
        Fx15 - LD DT, Vx
        Set delay timer = Vx.

        DT is set equal to the value of Vx.
        """

        self.cpu._v[0x0].set(0x10)

        self.cpu._set_delay_to_reg(0x015)

        self.assertEqual(0x10, self.delay_timer._countdown)


    def test_set_sound_to_reg(self):
        """
        Fx18 - LD ST, Vx
        Set sound timer = Vx.

        ST is set equal to the value of Vx.
        """
        
        self.cpu._v[0x0].set(0x10)

        self.cpu._set_sound_to_reg(0x018)

        self.assertEqual(0x10, self.sound_timer._countdown)

    def test_add_reg_to_i(self):
        """
        Fx1E - ADD I, Vx
        Set I = I + Vx. The values of I and Vx are added, and the results are stored in I.
        """

        self.cpu._i.set(0x100)
        self.cpu._v[0x0].set(0x10)

        self.cpu._add_reg_to_i(0x01E)

        self.assertEqual(0x110, self.cpu._i.get())

    @unittest.skip("Not implemented")
    def test_mov_reg_sprite_addr_to_i(self):
        pass

    def test_mov_reg_to_bcd(self):
        """
        Fx33 - LD B, Vx
        Store BCD representation of Vx in memory locations I, I+1, and I+2. The interpreter takes the decimal
        value of Vx, and places the hundreds digit in memory at location in I, the tens digit at location I+1, and
        the ones digit at location I+2.
        """

        self.cpu._v[0x0].set(0x7B) # 123
        self.cpu._i.set(0x100)

        self.cpu._mov_reg_to_bcd(0x033)

        self.assertEqual(1, self.memory[0x100])
        self.assertEqual(2, self.memory[0x101])
        self.assertEqual(3, self.memory[0x102])

    def test_dump_regs(self):
        """
        Fx55 - LD [I], Vx
        Stores V0 to VX in memory starting at address I. I is then set to I + x + 1.
        """

        self.cpu._i.set(0x100)

        for i in range(0x0, 0xF + 1):
            self.cpu._v[i].set(i)

        self.cpu._dump_regs(0xF55)

        for i in range(0x0, 0xF + 1):
            self.assertEqual(i, self.memory[0x100 + i], f"memory[0x100 + 0x{i:x}]")

        self.assertEqual(0x110, self.cpu._i.get()) # 0x100 + 0xF + 0x1


    def test_load_regs(self):
        """
        Fx65 - LD Vx, [I]
        Fills V0 to VX with values from memory starting at address I. I is then set to I + x + 1.
        """

        self.cpu._i.set(0x100)

        for i in range(0x0, 0xF + 1):
            self.memory[0x100 + i] = i

        self.cpu._load_regs(0xF65)

        for i in range(0x0, 0xF + 1):
            self.assertEqual(i, self.cpu._v[i].get())

        self.assertEqual(0x110, self.cpu._i.get())