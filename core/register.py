class Register:
    def __init__(self, size, value=0x0):
        self._size = size
        self._value = value
        self._value_mask = (0x1 << self._size) - 1

    def get(self):
        return self._value

    def set(self, value):
        # Prevent overflow of register
        self._value = value & self._value_mask

    def __repr__(self):
        return f"Register(0x{self._value:0>2x})"