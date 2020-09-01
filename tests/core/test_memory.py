import unittest
from core.exceptions import *
from core.memory import Memory

class TestMemory(unittest.TestCase):
    def test_memory_initialization(self):
        m = Memory(32)

        for i in range(0, 32):
            self.assertEqual(m[i], 0x0)

    def test_memory_setting_value(self):
        m = Memory(8)

        m[0] = 0xFF

        self.assertEqual(m[0], 0xFF)

    def test_memory_seeting_value_to_big(self):
        m = Memory(8, cell_bit_size=8)
        self.assertRaises(OverflowError, m.__setitem__, 0, 0xFFF)

    def test_memory_out_of_bounds(self):
        m = Memory(32)

        self.assertRaises(IndexError, m.__getitem__, 32)
        self.assertRaises(IndexError, m.__getitem__, -1)