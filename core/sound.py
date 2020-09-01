import pygame
import pygame.mixer
import pygame.sndarray
import math
import numpy

class Sound:
    def __init__(self, timer):
        self._timer = timer

        pygame.mixer.pre_init(frequency=44100, channels=1)
        pygame.mixer.init()

        self._sound = pygame.sndarray.make_sound(self.build_samples())

    def play(self):
        if self._timer.get() > 0:
            self._sound.play(-1)
        else:
            self._sound.stop()

    def build_samples(self):
        return numpy.array([
            4096 * math.sin(2.0 * math.pi * 440 * t / 44100) for t in range(44100)
        ]).astype(numpy.int16)