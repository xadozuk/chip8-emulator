import unittest
from core.register import Register

class TestRegister(unittest.TestCase):
    def test_register_overflow(self):
        r = Register(8)

        r.set(0xFFF)
        self.assertEqual(r.get(), 0xFF)