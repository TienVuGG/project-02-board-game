"""Pygame skeleton: Human vs random-agent Connect Four.

Run with (see README.md):

    python starter/app.py

This file is infrastructure only. It plays the human against
`random_agent.RandomAgent`. It does **not** call `student_core.minimax` /
`student_core.alphabeta` -- wire your AI in your own copy once the midterm
core is implemented.

`starter/game_engine.py` has no `pygame` import, so sanity tests do not need
pygame installed. This file needs pygame only to actually run the window.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from game_engine import (  # noqa: E402
    COLUMNS,
    ROWS,
    PLAYER_O,
    PLAYER_X,
    GameState,
    legal_moves,
)
from random_agent import RandomAgent  # noqa: E402

try:
    import pygame
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit(
        "pygame is required to run this app. Install it with "
        "`pip install -r requirements.txt`."
    ) from exc

CELL = 90
TOP_MARGIN = 1  # extra empty row of cells reserved for status text
WIDTH = COLUMNS * CELL
HEIGHT = (ROWS + TOP_MARGIN) * CELL
RADIUS = CELL // 2 - 10

# Shared quiet palette: X (human) = blue, O (opponent) = amber.
COLOR_BG = (51, 65, 85)          # slate board
COLOR_EMPTY = (15, 23, 42)       # dark empty cell
COLOR_X = (37, 99, 235)          # blue — player X
COLOR_O = (217, 119, 6)          # amber — player O
COLOR_TEXT = (248, 250, 252)     # near-white status text

HUMAN = PLAYER_X
AI = PLAYER_O

PLAYER_LABEL = {
    PLAYER_X: "X (blue)",
    PLAYER_O: "O (amber)",
}


def piece_color(token: str):
    if token == PLAYER_X:
        return COLOR_X
    if token == PLAYER_O:
        return COLOR_O
    return COLOR_EMPTY


def draw_board(screen, font, state: GameState, message: str) -> None:
    screen.fill(COLOR_BG)
    for row in range(ROWS):
        for col in range(COLUMNS):
            center = (col * CELL + CELL // 2, (row + TOP_MARGIN) * CELL + CELL // 2)
            pygame.draw.circle(screen, piece_color(state.board[row][col]), center, RADIUS)
    if message:
        text = font.render(message, True, COLOR_TEXT)
        screen.blit(text, (10, 5))
    pygame.display.flip()


def column_from_x(x: int) -> int:
    return max(0, min(COLUMNS - 1, x // CELL))


def status_message(state: GameState, base: str) -> str:
    if state.is_terminal():
        winner = state.winner()
        if winner:
            return f"{PLAYER_LABEL[winner]} wins! Press R to restart."
        return "Draw. Press R to restart."
    return base


def main() -> None:
    pygame.init()
    pygame.display.set_caption("AI Board Game Arena (Connect Four) — starter")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.SysFont(None, 26)
    clock = pygame.time.Clock()

    state = GameState.new(first_player=HUMAN)
    agent = RandomAgent(seed=None)
    base_message = (
        "Core not implemented. You are X (blue); opponent is O (amber). "
        "Press R to restart."
    )
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                state = GameState.new(first_player=HUMAN)
            elif (
                not state.is_terminal()
                and event.type == pygame.MOUSEBUTTONDOWN
                and state.to_move == HUMAN
            ):
                col = column_from_x(event.pos[0])
                if col in legal_moves(state.board):
                    state = state.apply(col)

        if not state.is_terminal() and state.to_move == AI:
            col = agent.choose_move(state.board)
            state = state.apply(col)

        draw_board(screen, font, state, status_message(state, base_message))
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
