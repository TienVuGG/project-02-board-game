"""Random baseline agent for Connect Four.

Used as a comparison baseline in the required experiment (automated matches
across AI configurations). It performs no search and no evaluation.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from game_engine import Board, legal_moves  # noqa: E402


class RandomAgent:
    """Picks a uniformly random legal column."""

    def __init__(self, seed: Optional[int] = None):
        self._rng = random.Random(seed)

    def choose_move(self, board: Board) -> int:
        moves = legal_moves(board)
        if not moves:
            raise ValueError("No legal moves available")
        return self._rng.choice(moves)
