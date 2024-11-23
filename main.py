"""
Plan:
use numpy array to represent every square of cubes
the moving piece not in numpy array but added on
once there's sth under the moving piece, STOP
when it stop, moving piece added
then check if there's a line that can be cleared, SO CLEAR IT and move all lines
for each piece his color, color stored in dict, (e.g. {0:"yellow", 1:"red",2:"blue",3:"green", ...})
speed up in each level for dynamics

pieces:
- I
- O
- S
- Z
- L
- J
- T
Why this project:
I want to start freelancing but didn't code for 3 months, so I try to get back to coding

don't worry if it's not like the original, it would be even better !
"""


import pygame
import numpy as np
import random
import time
import sys
from pieces.shapes import PIECES as iPIECES

class TetrisGame:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TetrisGame, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        pygame.init()
        self.COLORS = {
            1: "blue",
            2: "red",
            3: "green",
            4: "yellow",
            5: "cyan",
            6: "magenta",
            7: "maroon"
        }

        self.PIECES = iPIECES
        self.NPIECES = tuple(self.PIECES.keys())
        self.GRID_CUBE_SIZE = (10, 20)  # x, y
        self.NUMBER_NEXT_PIECES = 3

        self.DELAY_CONTROL_H = 0.1  # to go left or right
        self.DELAY_CONTROL_V = 0.1  # to go down
        self.CLEAR_LINES_POINTS = {
            0: 0,
            1: 100,
            2: 300,
            3: 500,
            4: 800
        }
        self.LINES_CLEARED_BY_LEVEL = 10

        # DESIGN SETTINGS
        self.CUBE_SIZE = 30
        self.GRID_POS = (self.CUBE_SIZE * 4 + 20, 0)
        self.NEXT_POS = (self.GRID_CUBE_SIZE[0] * self.CUBE_SIZE + self.GRID_POS[0] + 10, 10)
        self.NEXT_BETWEEN_TEXT_PIECES = 20
        self.NEXT_BETWEEN_PIECES = 20
        self.HOLD_POS = (10, 10)
        self.HOLD_SPACE_TEXT_PIECES = 20
        self.HOLD_SPACE_PIECES = 20
        self.SCREEN_SIZE = ((self.GRID_CUBE_SIZE[0] + 8) * self.CUBE_SIZE + 40, self.GRID_CUBE_SIZE[1] * self.CUBE_SIZE)
        self.SCORE_POS = (10, self.SCREEN_SIZE[1] - 10)
        self.SCORE_SPACE_PIECES = 20

        self.SCREEN_COLOR = "darkgray"
        self.GRID_COLOR = "black"
        self.CUBES_LIMIT_COLOR = "white"
        self.NEXT_STYLE = pygame.font.Font(None, 24), True, "white"
        self.SCORE_STYLE = pygame.font.Font(None, 24), True, "white"
        self.HOLD_STYLE = pygame.font.Font(None, 24), True, "white"

        self.debug_mode = hasattr(sys, 'gettrace') and sys.gettrace()
        self.printd = print if self.debug_mode else lambda *x, **y: None

        self.grid = np.zeros(self.flip_coords(*self.GRID_CUBE_SIZE))
        self.cube_surfaces = {}
        self.pieces_surfaces = {}
        for piece_id, color in self.COLORS.items():
            cube_surface = pygame.Surface((self.CUBE_SIZE, self.CUBE_SIZE))
            cube_surface.fill(color)
            self.cube_surfaces[piece_id] = cube_surface

            piece_cubes = self.PIECES[piece_id]
            xs, ys = zip(*piece_cubes)
            min_x, min_y = min(xs), min(ys)
            x_dim, y_dim = max(xs) - min_x + 1, max(ys) - min_y + 1
            piece_cubes = tuple((x - min_x, y - min_y) for x, y in piece_cubes)
            piece_size = (self.CUBE_SIZE * x_dim, self.CUBE_SIZE * y_dim)
            piece_surface = pygame.Surface(piece_size, pygame.SRCALPHA)
            piece_surface.fill((0, 0, 0, 0))

            for cube in piece_cubes:
                piece_surface.blit(cube_surface, (cube[0] * self.CUBE_SIZE, cube[1] * self.CUBE_SIZE))
            self.pieces_surfaces[piece_id] = piece_surface

        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        self.clock = pygame.time.Clock()

        pygame.mixer.init()
        pygame.mixer.music.load("music.mp3")
        pygame.mixer.music.play(loops=-1)
        self.running = True
        self.next_pieces = [random.choice(self.NPIECES) for _ in range(self.NUMBER_NEXT_PIECES)]
        self.score = 0
        self.empty_line = np.zeros((1, self.GRID_CUBE_SIZE[0]))
        self.next_time_moving = time.time()
        self.next_time_moving_h = 0
        self.next_time_moving_v = 0
        self.moving_h = 0
        self.moving_v = 0
        self.holded_piece = 0
        self.lines = 0
        self.level_old = 0

        self.new_piece()
        self.next_time_moving += self.speed_moving

        self.grid_surface = pygame.Surface((self.GRID_CUBE_SIZE[0] * self.CUBE_SIZE, self.GRID_CUBE_SIZE[1] * self.CUBE_SIZE))
        self.grid_surface.fill(self.GRID_COLOR)
        for y in range(self.GRID_CUBE_SIZE[1]):
            pygame.draw.line(
                self.grid_surface,
                self.CUBES_LIMIT_COLOR,
                (0, y * self.CUBE_SIZE),
                (self.GRID_CUBE_SIZE[0] * self.CUBE_SIZE, y * self.CUBE_SIZE),
                1)
        for x in range(self.GRID_CUBE_SIZE[0]):
            pygame.draw.line(
                self.grid_surface,
                self.CUBES_LIMIT_COLOR,
                (x * self.CUBE_SIZE, 0),
                (x * self.CUBE_SIZE, self.GRID_CUBE_SIZE[1] * self.CUBE_SIZE),
                1)

    def flip_coords(self, x, y):
        """convert UI coords to numpy coords"""
        return y, x

    def update_speed_moving(self):
        if self.level <= 10:
            self.speed_moving = 1 - 0.1 * (self.level - 1)
        else:
            self.speed_moving = 0.05

    def new_piece(self, setup_cpiece_id=True):
        self.lines_cleared_piece = 0
        for nline in range(self.GRID_CUBE_SIZE[1]):
            if np.all(self.grid[nline]):
                self.grid = np.delete(self.grid, nline, axis=0)
                self.grid = np.vstack((self.empty_line, self.grid))
                self.lines_cleared_piece += 1

        self.lines += self.lines_cleared_piece
        self.level = self.lines // self.LINES_CLEARED_BY_LEVEL + 1
        if self.level != self.level_old:
            self.level_old = self.level
            self.printd("LEVEL UP")
            self.update_speed_moving()
        self.score += self.CLEAR_LINES_POINTS[self.lines_cleared_piece]

        if setup_cpiece_id:
            self.cpiece_id = self.next_pieces.pop(0)
            self.next_pieces.append(random.choice(self.NPIECES))
            self.holded_used = False
        self.cpiece_pos = [int(self.GRID_CUBE_SIZE[0]) // 2, 0]
        self.cpiece_cubes = self.PIECES[self.cpiece_id]
        self.holded_used = False

        while True:
            try:
                if self.add_cpiece_to_grid():
                    return
                else:
                    self.cpiece_pos[1] += 1
                    raise IndexError

            except IndexError:
                print("game over")
                pygame.quit()
                quit()

    def add_cpiece_to_grid(self):
        self.grid_w_cpiece_cache = self.grid.copy()
        for cube in self.cpiece_cubes:
            cube_pos = self.cpiece_pos[0] + cube[0], self.cpiece_pos[1] + cube[1]

            self.printd("condition", 0 <= cube_pos[0])
            self.printd("hello", cube_pos[0])
            if not (0 <= cube_pos[0] < self.GRID_CUBE_SIZE[0] and 0 <= cube_pos[1] < self.GRID_CUBE_SIZE[1]):
                return False
            if self.grid_w_cpiece_cache[self.flip_coords(*cube_pos)]:
                return False
            self.grid_w_cpiece_cache[self.flip_coords(*cube_pos)] = self.cpiece_id
        self.cubes_w_cpiece = self.grid_w_cpiece_cache
        return True

    def move_v(self, delta_v):
        self.cpiece_pos[1] += delta_v
        if not self.add_cpiece_to_grid():
            self.cpiece_pos[1] -= delta_v
            self.moving_v = 0
            self.grid = self.cubes_w_cpiece
            self.new_piece()
            return True

    def render(self, style, text):
        return style[0].render(text, *style[1:])

    def run(self):
        while self.running:
            self.screen.fill(self.SCREEN_COLOR)
            self.screen.blit(self.grid_surface, self.GRID_POS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.next_time_moving_h = time.time()
                        self.moving_h = -1
                    elif event.key == pygame.K_RIGHT:
                        self.next_time_moving_h = time.time()
                        self.moving_h = 1
                    elif event.key == pygame.K_DOWN:
                        self.next_time_moving_v = time.time()
                        self.moving_v = 1
                    elif event.key == pygame.K_UP:
                        self.cpiece_cubes_backup = self.cpiece_cubes
                        self.cpiece_cubes = tuple((cube[1], -cube[0]) for cube in self.cpiece_cubes)
                        if not self.add_cpiece_to_grid():
                            self.cpiece_cubes = self.cpiece_cubes_backup
                    elif event.unicode == "c":
                        if not self.holded_used:
                            if self.holded_piece:
                                self.cpiece_id, self.holded_piece = self.holded_piece, self.cpiece_id
                                self.new_piece(setup_cpiece_id=False)
                            else:
                                self.holded_piece = self.cpiece_id
                                self.new_piece()
                            self.holded_used = True
                    elif event.unicode == " ":
                        while not self.move_v(1):
                            self.score += 2

                elif event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        self.moving_h = 0
                    elif event.key == pygame.K_DOWN:
                        self.moving_v = 0

            if time.time() > self.next_time_moving:
                self.next_time_moving += self.speed_moving
                self.move_v(1)

            if self.moving_h and time.time() > self.next_time_moving_h:
                self.next_time_moving_h += self.DELAY_CONTROL_H
                self.cpiece_pos[0] += self.moving_h
                self.printd(self.cpiece_pos)
                if not self.add_cpiece_to_grid():
                    self.cpiece_pos[0] -= self.moving_h
                    self.moving_h = 0

            if self.moving_v and time.time() > self.next_time_moving_v:
                self.printd(self.next_time_moving_v)
                self.next_time_moving_v += self.DELAY_CONTROL_V
                self.move_v(self.moving_v)
                self.score += self.moving_v

            for y in range(self.GRID_CUBE_SIZE[1]):
                for x in range(self.GRID_CUBE_SIZE[0]):
                    piece_id = self.cubes_w_cpiece[self.flip_coords(x, y)]
                    if piece_id != 0:
                        cube_surface = self.cube_surfaces[piece_id]
                        self.screen.blit(cube_surface, (self.CUBE_SIZE * x + self.GRID_POS[0], self.CUBE_SIZE * y + self.GRID_POS[1]))

            surface_next = self.render(self.NEXT_STYLE, "Next")
            y = self.NEXT_POS[1]
            self.screen.blit(surface_next, self.NEXT_POS)
            y += surface_next.get_height() + self.NEXT_BETWEEN_TEXT_PIECES

            for next_piece in self.next_pieces:
                piece_surface = self.pieces_surfaces[next_piece]
                self.screen.blit(piece_surface, (self.NEXT_POS[0], y))
                y += self.CUBE_SIZE * 2 + self.NEXT_BETWEEN_PIECES

            surface_hold = self.render(self.SCORE_STYLE, "Hold")
            y = self.HOLD_POS[1]
            self.screen.blit(surface_hold, self.HOLD_POS)
            if self.holded_piece:
                y += surface_hold.get_height() + self.HOLD_SPACE_TEXT_PIECES
                piece_surface = self.pieces_surfaces[self.holded_piece]
                self.screen.blit(piece_surface, (10, y))

            y = self.SCORE_POS[1]
            self.printd(y)
            for text in (
                f"Level: {self.level}",
                f"Lines: {self.lines}",
                f"Score: {self.score}",
            ):
                surface = self.render(self.HOLD_STYLE, text)
                self.screen.blit(surface, surface.get_rect(bottomleft=(self.SCORE_POS[0], y)))
                y -= surface.get_height() + self.SCORE_SPACE_PIECES

            self.clock.tick(60)
            self.printd(self.next_pieces)
            pygame.display.flip()

        pygame.mixer.music.stop()
        pygame.quit()
        quit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
