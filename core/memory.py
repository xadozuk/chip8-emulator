class Memory:
    def __init__(self, size, cell_bit_size = 8):
        self._max_size = size
        self._buffer = [0x0] * size
        self._value_mask = (1 << cell_bit_size) - 1

    def __getitem__(self, index):
        self._assert_in_bounds(index)

        return self._buffer[index]

    def __setitem__(self, index, value):
        self._assert_in_bounds(index)
        self._assert_value_size(value)

        self._buffer[index] = value

    def __len__(self):
        return self._max_size

    def _assert_in_bounds(self, index):
        if index < 0 or index >= self._max_size:
            raise IndexError(index)

    def _assert_value_size(self, value):
        if value & self._value_mask != value:
            raise OverflowError(value)