import pygame
import pygame.display
import pygame.draw

class Display:
    def __init__(self, width, height, scaling=10):
        self._width     = width
        self._height    = height
        self._scaling   = scaling

        self._screen = [[0] * height for _ in range(0, width)]

        self._surface = pygame.display.set_mode(
            size=(self._width * self._scaling, self._height * self._scaling),
            flags=pygame.HWSURFACE | pygame.DOUBLEBUF
        )

    def draw(self, x, y, bytes):
        collided = False

        for line in range(len(bytes)):
            for col in range(8):
                state = (bytes[line] & (1 << (7 - col))) >> (7 - col)

                collided |= self._draw_pixel(x + col, y + line, state)

        return collided

    def clear(self):
        for x in range(self._width):
            for y in range(self._height):
                self._screen[x][y] = 0

    def render(self):
        self._surface.fill((0, 0, 0))

        for x in range(self._width):
            for y in range(self._height):
                if self._screen[x][y]:
                    pygame.draw.rect(
                        self._surface,
                        (255, 255, 255),
                        (
                            (x * self._scaling, y * self._scaling),
                            (self._scaling, self._scaling)
                        )
                    )

        pygame.display.flip()

    def _draw_pixel(self, x, y, state):
        x_wrap = x % self._width
        y_wrap = y % self._height

        collided = not (state ^ self._screen[x_wrap][y_wrap])

        self._screen[x_wrap][y_wrap] ^= state

        return collided
