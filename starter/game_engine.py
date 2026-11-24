"""Connect Four game engine: legal moves, board updates, and terminal/win detection.

Board convention: a 6x7 grid stored as a tuple of 6 rows, each row a tuple of
7 cells. Row index 0 is the TOP row; row index 5 (`ROWS - 1`) is the BOTTOM
row. A dropped piece always lands in the lowest empty row of its column
(gravity). Cell values are one of `EMPTY`, `PLAYER_X`, `PLAYER_O`.

This module implements only the mechanics of the game. It intentionally does
**not** implement Minimax, Alpha-Beta pruning, or any evaluation function --
that AI core is your own work in `student_core.py`. It does not import
`pygame`, so it can be imported and tested without a display or pygame
installed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

ROWS = 6
COLUMNS = 7
CONNECT = 4

EMPTY = "."
PLAYER_X = "X"
PLAYER_O = "O"

Board = Tuple[Tuple[str, ...], ...]


def set_board_config(rows: int, columns: int, connect: int) -> None:
    """Configure board dimensions for custom matches."""
    global ROWS, COLUMNS, CONNECT
    if not 7 <= columns <= 9:
        raise ValueError("columns must be in range 7..9")
    if not 6 <= rows <= 8:
        raise ValueError("rows must be in range 6..8")
    if not 4 <= connect <= 6:
        raise ValueError("connect must be in range 4..6")
    ROWS = rows
    COLUMNS = columns
    CONNECT = connect


def new_board() -> Board:
    """Return an empty ROWS x COLUMNS board."""
    return tuple(tuple(EMPTY for _ in range(COLUMNS)) for _ in range(ROWS))


def other_player(player: str) -> str:
    if player not in (PLAYER_X, PLAYER_O):
        raise ValueError(f"Unknown player token: {player!r}")
    return PLAYER_O if player == PLAYER_X else PLAYER_X


def legal_moves(board: Board) -> List[int]:
    """Return the list of column indices that are not full, left to right."""
    columns = len(board[0]) if board else COLUMNS
    return [col for col in range(columns) if board[0][col] == EMPTY]


def _landing_row(board: Board, column: int) -> Optional[int]:
    rows = len(board)
    for row in range(rows - 1, -1, -1):
        if board[row][column] == EMPTY:
            return row
    return None


def apply_move(board: Board, column: int, player: str) -> Board:
    """Return a new board with `player`'s piece dropped into `column`.

    Raises `ValueError` if the column is out of range or already full.
    """
    if player not in (PLAYER_X, PLAYER_O):
        raise ValueError(f"Unknown player token: {player!r}")
    columns = len(board[0]) if board else COLUMNS
    if column < 0 or column >= columns:
        raise ValueError(f"Column {column} is out of range 0..{columns - 1}")
    row = _landing_row(board, column)
    if row is None:
        raise ValueError(f"Column {column} is full")
    rows = [list(r) for r in board]
    rows[row][column] = player
    return tuple(tuple(r) for r in rows)


def _winning_line(board: Board, row: int, col: int, player: str) -> bool:
    rows = len(board)
    columns = len(board[0]) if board else COLUMNS
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for d_row, d_col in directions:
        count = 1
        for sign in (1, -1):
            r, c = row + d_row * sign, col + d_col * sign
            while 0 <= r < rows and 0 <= c < columns and board[r][c] == player:
                count += 1
                r += d_row * sign
                c += d_col * sign
        if count >= CONNECT:
            return True
    return False


def check_winner(board: Board) -> Optional[str]:
    """Return `PLAYER_X` or `PLAYER_O` if that player has 4 in a row, else `None`."""
    rows = len(board)
    columns = len(board[0]) if board else COLUMNS
    for row in range(rows):
        for col in range(columns):
            player = board[row][col]
            if player == EMPTY:
                continue
            if _winning_line(board, row, col, player):
                return player
    return None


def is_full(board: Board) -> bool:
    return all(cell != EMPTY for cell in board[0])


def is_terminal(board: Board) -> bool:
    return check_winner(board) is not None or is_full(board)


def result_label(board: Board) -> Optional[str]:
    """Return `'X'`, `'O'`, `'draw'`, or `None` (not terminal)."""
    winner = check_winner(board)
    if winner is not None:
        return winner
    if is_full(board):
        return "draw"
    return None


def render(board: Board) -> str:
    """Human-readable board rendering, top row first."""
    return "\n".join("|".join(row) for row in board)


def board_from_rows(rows: List[str]) -> Board:
    """Build a `Board` from a list of `ROWS` strings of length `COLUMNS`
    (top row first), as used in `sample_states.json`."""
    if len(rows) != ROWS:
        raise ValueError(f"Expected {ROWS} rows, got {len(rows)}")
    for row in rows:
        if len(row) != COLUMNS:
            raise ValueError(f"Expected each row to have {COLUMNS} columns, got {len(row)!r}")
    return tuple(tuple(row) for row in rows)


@dataclass
class GameState:
    """Convenience wrapper bundling a board with whose turn it is."""

    board: Board
    to_move: str

    @classmethod
    def new(cls, first_player: str = PLAYER_X) -> "GameState":
        return cls(board=new_board(), to_move=first_player)

    def legal_actions(self) -> List[int]:
        return legal_moves(self.board)

    def apply(self, column: int) -> "GameState":
        new_b = apply_move(self.board, column, self.to_move)
        return GameState(board=new_b, to_move=other_player(self.to_move))

    def is_terminal(self) -> bool:
        return is_terminal(self.board)

    def winner(self) -> Optional[str]:
        return check_winner(self.board)
