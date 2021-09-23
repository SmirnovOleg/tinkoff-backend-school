from __future__ import annotations

import random
from enum import Enum
from typing import Optional

from PlayingArea import PlayingArea, CellState


class TicTacToe:
    def __init__(self, width: int = 3, height: int = 3):
        self.area = PlayingArea(width, height)
        self.state = States.USER_TURN
        self.prev_turn = None

    def refresh(self):
        self.area.clear()
        self.prev_turn = None
        self.state = States.USER_TURN

    def user_turn(self):
        if self.area.is_empty_cell(self.area.cursor.i, self.area.cursor.j):
            self.area.set_symbol(CellState.X, self.area.cursor.i, self.area.cursor.j)
            self.prev_turn = CellState.X
        else:
            raise FailedTurnError('This cell has been already occupied.')

    def ai_turn(self):
        if len(self.area.empty_cells) == 0:
            raise FailedTurnError('All the cells have been already occupied.')
        i, j = random.choice(tuple(self.area.empty_cells))
        self.area.set_symbol(CellState.O, i, j)
        self.prev_turn = CellState.O

    def find_winner(self) -> Optional[str]:
        return self.area.find_winner()


class States(Enum):
    USER_TURN = 1
    AI_TURN = 2
    WINNER_CHECKING = 3
    X_WIN = 4
    O_WIN = 5
    DRAW = 6
    CONTINUE = 7


class FailedTurnError(Exception):
    pass
