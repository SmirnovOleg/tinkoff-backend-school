from enum import Enum
from functools import reduce
from typing import Optional, List


class CellState(str, Enum):
    X = 'X'
    O = 'O'
    EMPTY = '.'


class PlayingArea:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.winner_condition = min(width, height)
        self.area = [[CellState.EMPTY] * self.width for _ in range(self.height)]
        self.empty_cells = set((i, j) for i in range(height) for j in range(width))
        self.cursor = Cursor(width, height)

    def clear(self):
        self.area = [[CellState.EMPTY] * self.width for _ in range(self.height)]
        self.empty_cells = set([(i, j) for i in range(self.height) for j in range(self.width)])

    def set_symbol(self, symbol, i, j):
        self.area[i][j] = symbol
        self.empty_cells.remove((i, j))

    def get_symbol(self, i, j) -> str:
        return self.area[i][j]

    def is_empty_cell(self, i, j) -> bool:
        return self.area[i][j] == CellState.EMPTY

    def __repr__(self) -> str:
        return '\n'.join([''.join(row) for row in self.area])

    def find_winner(self) -> Optional[str]:
        cols = [[] for _ in range(self.width)]
        rows = [[] for _ in range(self.height)]
        main_diags = [[] for _ in range(self.width + self.height - 1)]
        anti_diags = [[] for _ in range(self.width + self.height - 1)]

        for i in range(self.height):
            for j in range(self.width):
                cols[j].append(self.area[i][j])
                rows[i].append(self.area[i][j])
                anti_diags[i + j].append(self.area[i][j])
                main_diags[j - i + self.winner_condition - 1].append(self.area[i][j])

        return reduce(lambda a, b: a or b,
                      [self.__find_winner_in_list(lst) for lst in cols + rows + main_diags + anti_diags],
                      None)

    def __find_winner_in_list(self, lst: List[str]) -> Optional[str]:
        max_X, max_O = 0, 0
        cur_X, cur_O = 0, 0
        if lst[0] == CellState.X:
            cur_X += 1
        elif lst[0] == CellState.O:
            cur_O += 1
        for i in range(1, len(lst)):
            if lst[i] == lst[i - 1] == CellState.X:
                cur_X += 1
            elif lst[i] == lst[i - 1] == CellState.O:
                cur_O += 1
            elif lst[i] == CellState.EMPTY:
                max_X = max(max_X, cur_X)
                max_O = max(max_O, cur_O)
                cur_X, cur_O = 0, 0
            elif lst[i] == CellState.X:
                max_O = max(max_O, cur_O)
                cur_O, cur_X = 0, 1
            elif lst[i] == CellState.O:
                max_X = max(max_X, cur_X)
                cur_X, cur_O = 0, 1
        max_X = max(max_X, cur_X)
        max_O = max(max_O, cur_O)
        if max_X == self.winner_condition:
            return CellState.X
        elif max_O == self.winner_condition:
            return CellState.O
        return None


class Cursor:
    def __init__(self, width_constraint, height_constraint):
        self.i = 0
        self.j = 0
        self.width_constraint = width_constraint
        self.height_constraint = height_constraint

    def move_up(self):
        if self.i > 0:
            self.i -= 1

    def move_down(self):
        if self.i < self.height_constraint - 1:
            self.i += 1

    def move_right(self):
        if self.j < self.width_constraint - 1:
            self.j += 1

    def move_left(self):
        if self.j > 0:
            self.j -= 1
