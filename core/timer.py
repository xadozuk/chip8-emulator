from datetime import datetime

class Timer:
    def __init__(self, freq):
        self._countdown   = 0
        self._accumulator = 0
        self._last_tick   = datetime.now()
        self._freq        = freq
        self._interval    = 1000.0 / freq

    def tick(self):
        if self._countdown == 0:
            return

        self._accumulator += (datetime.now() - self._last_tick).total_seconds() * 1000

        self._countdown -= int(self._accumulator / self._interval)
        self._accumulator //= self._interval

        if self._countdown < 0:
            self._countdown = 0

    def set(self, value):
        self._countdown = value
        self._last_tick = datetime.now()

    def get(self):
        return self._countdown
