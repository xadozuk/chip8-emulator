from core.cpu import Cpu
from core.memory import Memory
from core.display import Display
from core.timer import Timer
from core.sound import Sound

from datetime import datetime

import random
import time
import logging
import pygame
import pygame.time
import pygame.event

class Chip8:
    STARTING_ADDRESS = 0x200

    HEX_SPRITES = [
        [0xF0, 0x90, 0x90, 0x90, 0xF0], # 0
        [0x20, 0x60, 0x20, 0x20, 0x70], # 1
        [0xF0, 0x10, 0xF0, 0x80, 0xF0], # 2
        [0xF0, 0x10, 0xF0, 0x10, 0xF0], # 3
        [0x90, 0x90, 0xF0, 0x10, 0x10], # 4
        [0xF0, 0x80, 0xF0, 0x10, 0xF0], # 5
        [0xF0, 0x80, 0xF0, 0x90, 0xF0], # 6
        [0xF0, 0x10, 0x20, 0x40, 0x40], # 7
        [0xF0, 0x90, 0xF0, 0x90, 0xF0], # 8
        [0xF0, 0x90, 0xF0, 0x10, 0xF0], # 9
        [0xF0, 0x90, 0xF0, 0x90, 0x90], # A
        [0xE0, 0x90, 0xE0, 0x90, 0xE0], # B
        [0xF0, 0x80, 0x80, 0x80, 0xF0], # C
        [0xE0, 0x90, 0x90, 0x90, 0xE0], # D
        [0xF0, 0x80, 0xF0, 0x80, 0xF0], # E
        [0xF0, 0x80, 0xF0, 0x80, 0x80] # F
    ]

    def __init__(self):
        self._memory  = Memory(0x1000)
        self._display = Display(64, 32)
        self._delay_timer = Timer(freq=60)
        self._sound_timer = Timer(freq=60)

        self._sound   = Sound(self._sound_timer)
        self._cpu     = Cpu(self._memory, self._display, delay_timer=self._delay_timer, sound_timer=self._sound_timer)

        self._fps_time = datetime.now()

        pygame.init()

    def load(self, file):
        logging.info(f"Loading ROM [{file}] into memory (starting at 0x{self.STARTING_ADDRESS:x})")

        with open(file, 'rb') as f:
            i = self.STARTING_ADDRESS

            while byte := f.read(1):
                self._memory[i] = byte[0]
                i += 1

            logging.info(f"ROM loaded (0x{i:x} bytes read)")

    def run(self):
        self._reset()

        running = True

        while running:
            self._cpu.tick()

            logging.debug(self._cpu)
            logging.info(f"FPS: {self._fps()}")

            self._delay_timer.tick()
            self._sound_timer.tick()

            self._display.render()
            self._sound.play()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False

            pygame.time.wait(15)            

    def _reset(self):
        # TODO: self._cpu.reset()
        # TODO: self._display.reset()
        self._cpu.set_starting_address(self.STARTING_ADDRESS)
        random.seed()

        self._load_sprites_in_memory()

    def _load_sprites_in_memory(self):
        i = 0
        for font in self.HEX_SPRITES:
            for byte in font:
                self._memory[i] = byte
                i += 1

    def _fps(self):
        now = datetime.now()
        d = now - self._fps_time

        self._fps_time = now

        return 1.0 / d.total_seconds()