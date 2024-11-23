"""
Forked from original source code at https://github.com/RadoTheProgrammer/tetris
- Moved the game and its pieces into their own classes

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
from game.TetrisGame import TetrisGame

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
