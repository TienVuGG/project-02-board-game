"""Empty AI core stubs for Project 02 (AI Board Game Arena — Connect Four).

Implement Minimax, Alpha-Beta pruning, and an evaluation function here.
Every public function below raises `NotImplementedError` until you replace
its body with your own implementation. Do not call a hosted LLM to choose a
move: see the auto-zero note in the instructor rubric.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from game_engine import Board  # noqa: E402


def evaluate(board: Board, player: str) -> float:
    """Static evaluation of `board` from `player`'s perspective.

    Design your own features (e.g. open lines of 2/3, center-column
    control). Do not rely only on `check_winner` as the sole signal for
    non-terminal positions.
    """
    raise NotImplementedError("Implement evaluate() in student_core.py")


def minimax(
    board: Board,
    player: str,
    depth: int,
    maximizing_player: str,
) -> Tuple[int, float]:
    """Return `(best_column, value)` using plain Minimax to `depth` plies.

    `player` is whose turn it is to move at `board`. `maximizing_player`
    names the player whose score is being maximized throughout the tree.
    """
    raise NotImplementedError("Implement minimax() in student_core.py")


def alphabeta(
    board: Board,
    player: str,
    depth: int,
    maximizing_player: str,
    alpha: float = float("-inf"),
    beta: float = float("inf"),
) -> Tuple[int, float]:
    """Return `(best_column, value)` using Minimax with Alpha-Beta pruning.

    Also track how many nodes you expand (for example with a module-level
    counter you reset before each call, or an extra return value) so you can
    compare against plain `minimax()` in the required experiment.
    """
    raise NotImplementedError("Implement alphabeta() in student_core.py")
