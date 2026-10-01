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
from game_engine import (  # noqa: E402
    apply_move,
    COLUMNS,
    CONNECT,
    EMPTY,
    is_terminal,
    legal_moves,
    other_player,
    PLAYER_O,
    PLAYER_X,
    ROWS,
    Board,
    check_winner,
)


WIN_SCORE = 1_000_000.0
THREE_SCORE = 100.0
TWO_SCORE = 10.0
CENTER_SCORE = 3.0

_minimax_nodes_expanded = 0
_alphabeta_nodes_expanded = 0


def _validate_player(player: str) -> None:
    if player not in (PLAYER_X, PLAYER_O):
        raise ValueError(f"Unknown player token: {player!r}")


def _other_player(player: str) -> str:
    return PLAYER_O if player == PLAYER_X else PLAYER_X


def _score_window(window: tuple[str, ...], player: str) -> float:
    """Score one group of four cells from `player`'s perspective."""
    opponent = _other_player(player)
    player_count = window.count(player)
    opponent_count = window.count(opponent)
    empty_count = window.count(EMPTY)

    if player_count and opponent_count:
        return 0.0
    if player_count == CONNECT:
        return WIN_SCORE
    if opponent_count == CONNECT:
        return -WIN_SCORE
    if player_count == 3 and empty_count == 1:
        return THREE_SCORE
    if player_count == 2 and empty_count == 2:
        return TWO_SCORE
    if opponent_count == 3 and empty_count == 1:
        return -THREE_SCORE
    if opponent_count == 2 and empty_count == 2:
        return -TWO_SCORE
    return 0.0


def _iter_windows(board: Board):
    """Yield every horizontal, vertical, and diagonal window of four cells."""
    for row in range(ROWS):
        for col in range(COLUMNS - CONNECT + 1):
            yield tuple(board[row][col + offset] for offset in range(CONNECT))

    for row in range(ROWS - CONNECT + 1):
        for col in range(COLUMNS):
            yield tuple(board[row + offset][col] for offset in range(CONNECT))

    for row in range(ROWS - CONNECT + 1):
        for col in range(COLUMNS - CONNECT + 1):
            yield tuple(
                board[row + offset][col + offset] for offset in range(CONNECT)
            )

    for row in range(ROWS - CONNECT + 1):
        for col in range(CONNECT - 1, COLUMNS):
            yield tuple(
                board[row + offset][col - offset] for offset in range(CONNECT)
            )


def reset_node_counters() -> None:
    """Reset search-node counters before a benchmarked root call."""
    global _minimax_nodes_expanded, _alphabeta_nodes_expanded
    _minimax_nodes_expanded = 0
    _alphabeta_nodes_expanded = 0


def get_node_counters() -> tuple[int, int]:
    """Return `(minimax_nodes, alphabeta_nodes)` since the last reset."""
    return _minimax_nodes_expanded, _alphabeta_nodes_expanded


def evaluate(board: Board, player: str) -> float:
    """Static evaluation of `board` from `player`'s perspective.

    Design your own features (e.g. open lines of 2/3, center-column
    control). Do not rely only on `check_winner` as the sole signal for
    non-terminal positions.
    """
    _validate_player(player)

    winner = check_winner(board)
    if winner == player:
        return WIN_SCORE
    if winner == _other_player(player):
        return -WIN_SCORE
    if all(cell != EMPTY for cell in board[0]):
        return 0.0

    score = 0.0
    center_column = COLUMNS // 2
    center_count = sum(
        1 for row in range(ROWS) if board[row][center_column] == player
    )
    opponent_center_count = sum(
        1
        for row in range(ROWS)
        if board[row][center_column] == _other_player(player)
    )
    score += CENTER_SCORE * (center_count - opponent_center_count)

    for window in _iter_windows(board):
        score += _score_window(window, player)

    return score


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
    global _minimax_nodes_expanded
    _minimax_nodes_expanded += 1
    _validate_player(player)
    _validate_player(maximizing_player)
    if depth < 0:
        raise ValueError("depth must be non-negative")

    moves = legal_moves(board)
    if is_terminal(board) or not moves:
        return -1, evaluate(board, maximizing_player)

    if depth == 0:
        return moves[0], evaluate(board, maximizing_player)

    is_maximizing = player == maximizing_player
    best_column = moves[0]
    best_value = float("-inf") if is_maximizing else float("inf")

    for column in moves:
        child = apply_move(board, column, player)
        _, child_value = minimax(
            child,
            other_player(player),
            depth - 1,
            maximizing_player,
        )

        if is_maximizing:
            if child_value > best_value:
                best_value = child_value
                best_column = column
        elif child_value < best_value:
            best_value = child_value
            best_column = column

    return best_column, best_value


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
    global _alphabeta_nodes_expanded
    _alphabeta_nodes_expanded += 1
    _validate_player(player)
    _validate_player(maximizing_player)
    if depth < 0:
        raise ValueError("depth must be non-negative")

    moves = legal_moves(board)
    if is_terminal(board) or not moves:
        return -1, evaluate(board, maximizing_player)

    if depth == 0:
        return moves[0], evaluate(board, maximizing_player)

    is_maximizing = player == maximizing_player
    best_column = moves[0]

    if is_maximizing:
        best_value = float("-inf")
        for column in moves:
            child = apply_move(board, column, player)
            _, child_value = alphabeta(
                child,
                other_player(player),
                depth - 1,
                maximizing_player,
                alpha,
                beta,
            )
            if child_value > best_value:
                best_value = child_value
                best_column = column
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break
    else:
        best_value = float("inf")
        for column in moves:
            child = apply_move(board, column, player)
            _, child_value = alphabeta(
                child,
                other_player(player),
                depth - 1,
                maximizing_player,
                alpha,
                beta,
            )
            if child_value < best_value:
                best_value = child_value
                best_column = column
            beta = min(beta, best_value)
            if alpha >= beta:
                break

    return best_column, best_value
