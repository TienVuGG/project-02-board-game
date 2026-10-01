"""Sanity tests for Project 02 (AI Board Game Arena — Connect Four).

These tests check the game engine (including win detection), the random
baseline agent, and that the starter does NOT ship a working Minimax /
Alpha-Beta core. They do not grade the student's AI. None of this file
imports pygame: game_engine.py, random_agent.py, and student_core.py must
be importable without it.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
STARTER_DIR = PROJECT_DIR / "starter"

sys.path.insert(0, str(STARTER_DIR))

import game_engine as ge  # noqa: E402
import random_agent as ra  # noqa: E402


def _load_module(name: str, path: Path):
    """Load a module under a unique name so `starter/student_core.py`
    (which also exists in project-01) never collides via `sys.modules`
    when both projects' sanity tests run in the same pytest session."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


student_core = _load_module("project02_student_core", STARTER_DIR / "student_core.py")


# ---------------------------------------------------------------------------
# Engine basics
# ---------------------------------------------------------------------------


def test_new_board_is_empty_and_shaped_correctly():
    board = ge.new_board()
    assert len(board) == ge.ROWS
    assert all(len(row) == ge.COLUMNS for row in board)
    assert all(cell == ge.EMPTY for row in board for cell in row)


def test_legal_moves_all_columns_open_on_empty_board():
    board = ge.new_board()
    assert ge.legal_moves(board) == list(range(ge.COLUMNS))


def test_apply_move_lands_on_bottom_row_first():
    board = ge.new_board()
    board = ge.apply_move(board, 3, ge.PLAYER_X)
    assert board[ge.ROWS - 1][3] == ge.PLAYER_X
    board = ge.apply_move(board, 3, ge.PLAYER_O)
    assert board[ge.ROWS - 2][3] == ge.PLAYER_O


def test_apply_move_out_of_range_raises():
    board = ge.new_board()
    with pytest.raises(ValueError):
        ge.apply_move(board, -1, ge.PLAYER_X)
    with pytest.raises(ValueError):
        ge.apply_move(board, ge.COLUMNS, ge.PLAYER_X)


def test_apply_move_unknown_player_raises():
    board = ge.new_board()
    with pytest.raises(ValueError):
        ge.apply_move(board, 0, "Z")


def test_apply_move_full_column_raises():
    board = ge.new_board()
    for i in range(ge.ROWS):
        board = ge.apply_move(board, 0, ge.PLAYER_X if i % 2 == 0 else ge.PLAYER_O)
    assert 0 not in ge.legal_moves(board)
    with pytest.raises(ValueError):
        ge.apply_move(board, 0, ge.PLAYER_X)


# ---------------------------------------------------------------------------
# Win detection (mandatory: horizontal, vertical, diagonal, draw)
# ---------------------------------------------------------------------------


def test_horizontal_win_detected():
    rows = [
        ".......",
        ".......",
        ".......",
        ".......",
        ".......",
        "XXXX...",
    ]
    board = ge.board_from_rows(rows)
    assert ge.check_winner(board) == ge.PLAYER_X
    assert ge.is_terminal(board) is True
    assert ge.result_label(board) == ge.PLAYER_X


def test_vertical_win_detected():
    rows = [
        ".......",
        ".......",
        "O......",
        "O......",
        "O......",
        "O......",
    ]
    board = ge.board_from_rows(rows)
    assert ge.check_winner(board) == ge.PLAYER_O
    assert ge.result_label(board) == ge.PLAYER_O


def test_diagonal_down_left_win_detected():
    rows = [
        ".......",
        ".......",
        "...X...",
        "..XO...",
        ".XOO...",
        "XOOO...",
    ]
    board = ge.board_from_rows(rows)
    assert ge.check_winner(board) == ge.PLAYER_X


def test_diagonal_down_right_win_the_other_way():
    rows = [
        ".......",
        ".......",
        ".X.....",
        "..X....",
        "...X...",
        "....X..",
    ]
    board = ge.board_from_rows(rows)
    assert ge.check_winner(board) == ge.PLAYER_X


def test_no_winner_on_empty_board():
    assert ge.check_winner(ge.new_board()) is None
    assert ge.is_terminal(ge.new_board()) is False
    assert ge.result_label(ge.new_board()) is None


def test_draw_detected_when_board_full_without_winner():
    # A full board (produced by simulated legal play) with no 4-in-a-row
    # anywhere -- a pure checkerboard pattern is NOT safe here because its
    # diagonals are constant-color 4-in-a-rows.
    rows = [
        "OOXOXOX",
        "OXXXOXX",
        "OXOXOXO",
        "XOXOOOX",
        "XOOOXXO",
        "XXOXOXO",
    ]
    board = ge.board_from_rows(rows)
    assert ge.check_winner(board) is None
    assert ge.is_full(board) is True
    assert ge.is_terminal(board) is True
    assert ge.result_label(board) == "draw"


def test_game_state_apply_and_terminal():
    state = ge.GameState.new(first_player=ge.PLAYER_X)
    assert state.to_move == ge.PLAYER_X
    for col in [0, 1, 0, 1, 0, 1, 0]:
        if state.is_terminal():
            break
        state = state.apply(col)
    assert state.is_terminal()
    assert state.winner() == ge.PLAYER_X


# ---------------------------------------------------------------------------
# sample_states.json
# ---------------------------------------------------------------------------


def test_sample_states_file_covers_required_ids():
    with open(STARTER_DIR / "sample_states.json", encoding="utf-8") as fh:
        data = json.load(fh)
    ids = {s["id"] for s in data["states"]}
    for required_id in [
        "B1_open_start",
        "B2_depth_sensitive_block",
        "B3_alphabeta_reduction",
        "B4_full_column_failure",
    ]:
        assert required_id in ids, f"missing sample state id {required_id}"


def test_sample_states_are_valid_non_terminal_boards_with_consistent_turn():
    with open(STARTER_DIR / "sample_states.json", encoding="utf-8") as fh:
        data = json.load(fh)
    for s in data["states"]:
        board = ge.board_from_rows(s["board"])
        assert ge.check_winner(board) is None, f"{s['id']} must not already be won"
        x_count = sum(row.count("X") for row in board)
        o_count = sum(row.count("O") for row in board)
        if s["to_move"] == "X":
            assert x_count == o_count, f"{s['id']} bad turn parity for X to move"
        else:
            assert x_count == o_count + 1, f"{s['id']} bad turn parity for O to move"


def test_b4_full_column_state_matches_engine_failure_behavior():
    with open(STARTER_DIR / "sample_states.json", encoding="utf-8") as fh:
        data = json.load(fh)
    b4 = next(s for s in data["states"] if s["id"] == "B4_full_column_failure")
    board = ge.board_from_rows(b4["board"])
    assert 3 not in ge.legal_moves(board)
    with pytest.raises(ValueError):
        ge.apply_move(board, 3, ge.PLAYER_X)


# ---------------------------------------------------------------------------
# Random agent
# ---------------------------------------------------------------------------


def test_random_agent_chooses_legal_move():
    agent = ra.RandomAgent(seed=7)
    board = ge.new_board()
    move = agent.choose_move(board)
    assert move in ge.legal_moves(board)


def test_random_agent_raises_when_no_moves():
    agent = ra.RandomAgent(seed=1)
    board = ge.new_board()
    for col in range(ge.COLUMNS):
        for i in range(ge.ROWS):
            board = ge.apply_move(board, col, ge.PLAYER_X if i % 2 == 0 else ge.PLAYER_O)
    assert ge.legal_moves(board) == []
    with pytest.raises(ValueError):
        agent.choose_move(board)


# ---------------------------------------------------------------------------
# Starter core stubs (must be empty) and forbidden leaks
# ---------------------------------------------------------------------------


def test_student_core_stubs_raise_not_implemented():
    board = ge.new_board()
    with pytest.raises(NotImplementedError):
        student_core.evaluate(board, ge.PLAYER_X)
    with pytest.raises(NotImplementedError):
        student_core.minimax(board, ge.PLAYER_X, depth=2, maximizing_player=ge.PLAYER_X)
    with pytest.raises(NotImplementedError):
        student_core.alphabeta(board, ge.PLAYER_X, depth=2, maximizing_player=ge.PLAYER_X)


def test_game_engine_module_has_no_ai_core_functions():
    forbidden = {"minimax", "alphabeta", "evaluate"}
    defined = {name for name in dir(ge) if not name.startswith("_")}
    leaked = forbidden & defined
    assert not leaked, f"starter/game_engine.py must not define AI core functions: {leaked}"


def test_game_engine_importable_without_pygame():
    assert "pygame" not in sys.modules, (
        "importing game_engine must not require pygame; "
        "pygame should only be imported by app.py"
    )
