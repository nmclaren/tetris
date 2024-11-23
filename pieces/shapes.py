from .piece import Piece

class I(Piece):
    def __init__(self):
        super().__init__(((-1, 0), (0, 0), (1, 0), (2, 0)))

class O(Piece):
    def __init__(self):
        super().__init__(((0, 0), (0, 1), (1, 0), (1, 1)))

class S(Piece):
    def __init__(self):
        super().__init__(((0, 0), (0, 1), (1, 0), (-1, 1)))

class Z(Piece):
    def __init__(self):
        super().__init__(((0, 0), (0, 1), (-1, 0), (1, 1)))

class L(Piece):
    def __init__(self):
        super().__init__(((0, 0), (-1, 0), (1, 0), (-1, 1)))

class J(Piece):
    def __init__(self):
        super().__init__(((0, 0), (-1, 0), (1, 0), (1, 1)))

class T(Piece):
    def __init__(self):
        super().__init__(((0, 0), (-1, 0), (1, 0), (0, 1)))

PIECES = {
    1: I().coordinates,
    2: O().coordinates,
    3: S().coordinates,
    4: Z().coordinates,
    5: L().coordinates,
    6: J().coordinates,
    7: T().coordinates
}