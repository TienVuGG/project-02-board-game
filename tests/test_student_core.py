"""Correctness tests for the student Connect Four AI core."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
STARTER_DIR = PROJECT_DIR / "starter"
sys.path.insert(0, str(STARTER_DIR))

import game_engine as ge  # noqa: E402
import student_core as core  # noqa: E402


def board(*rows: str) -> ge.Board:
    return ge.board_from_rows(list(rows))


def test_evaluate_non_terminal_board_uses_heuristic():
    empty = ge.new_board()
    center = board(
        ".......",
        ".......",
        ".......",
        ".......",
        "...X...",
        ".......",
    )
    assert core.evaluate(empty, ge.PLAYER_X) == 0.0
    assert core.evaluate(center, ge.PLAYER_X) > core.evaluate(empty, ge.PLAYER_X)


def test_minimax_finds_immediate_winning_move():
    state = board(
        ".......",
        ".......",
        ".......",
        ".......",
        ".......",
        "XXX.OO.",
    )
    move, value = core.minimax(state, ge.PLAYER_X, depth=1, maximizing_player=ge.PLAYER_X)
    assert move == 3
    assert value == core.WIN_SCORE


def test_alphabeta_finds_immediate_winning_move():
    state = board(
        ".......",
        ".......",
        ".......",
        ".......",
        ".......",
        "XXX.OO.",
    )
    move, value = core.alphabeta(
        state, ge.PLAYER_X, depth=1, maximizing_player=ge.PLAYER_X
    )
    assert move == 3
    assert value == core.WIN_SCORE


def test_search_blocks_immediate_opponent_threat():
    state = board(
        ".......",
        ".......",
        ".......",
        ".......",
        "X......",
        "OOO.XX.",
    )
    minimax_move, _ = core.minimax(
        state, ge.PLAYER_X, depth=2, maximizing_player=ge.PLAYER_X
    )
    alphabeta_move, _ = core.alphabeta(
        state, ge.PLAYER_X, depth=2, maximizing_player=ge.PLAYER_X
    )
    assert minimax_move == 3
    assert alphabeta_move == 3


def test_terminal_board_returns_sentinel_column():
    state = board(
        ".......",
        ".......",
        ".......",
        ".......",
        ".......",
        "XXXX...",
    )
    expected = core.evaluate(state, ge.PLAYER_O)
    assert core.minimax(state, ge.PLAYER_O, 3, ge.PLAYER_O) == (-1, expected)
    assert core.alphabeta(state, ge.PLAYER_O, 3, ge.PLAYER_O) == (-1, expected)


def test_depth_zero_does_not_expand_and_returns_legal_fallback():
    state = ge.new_board()
    core.reset_node_counters()
    move, value = core.minimax(state, ge.PLAYER_X, 0, ge.PLAYER_X)
    minimax_nodes, _ = core.get_node_counters()
    assert move in ge.legal_moves(state)
    assert value == core.evaluate(state, ge.PLAYER_X)
    assert minimax_nodes == 1

    core.reset_node_counters()
    move, value = core.alphabeta(state, ge.PLAYER_X, 0, ge.PLAYER_X)
    _, alphabeta_nodes = core.get_node_counters()
    assert move in ge.legal_moves(state)
    assert value == core.evaluate(state, ge.PLAYER_X)
    assert alphabeta_nodes == 1


def test_full_column_is_never_returned():
    state = board(
        "...X...",
        "...O...",
        "...X...",
        "...O...",
        "...X...",
        "...O...",
    )
    legal = ge.legal_moves(state)
    assert 3 not in legal
    minimax_move, _ = core.minimax(state, ge.PLAYER_X, 2, ge.PLAYER_X)
    alphabeta_move, _ = core.alphabeta(state, ge.PLAYER_X, 2, ge.PLAYER_X)
    assert minimax_move in legal
    assert alphabeta_move in legal


def test_search_does_not_mutate_board():
    state = board(
        ".......",
        ".......",
        ".......",
        "....X..",
        "...XO..",
        "..XOXO.",
    )
    original = state
    core.minimax(state, ge.PLAYER_O, 3, ge.PLAYER_O)
    core.alphabeta(state, ge.PLAYER_O, 3, ge.PLAYER_O)
    assert state == original


def test_minimax_and_alphabeta_agree_on_benchmark_state():
    state = board(
        ".......",
        ".......",
        ".......",
        "....X..",
        "...XO..",
        "..XOXO.",
    )
    minimax_move, minimax_value = core.minimax(state, ge.PLAYER_O, 3, ge.PLAYER_O)
    alphabeta_move, alphabeta_value = core.alphabeta(state, ge.PLAYER_O, 3, ge.PLAYER_O)
    assert alphabeta_move == minimax_move
    assert alphabeta_value == minimax_value


def test_alpha_beta_expands_no_more_nodes_than_minimax():
    state = board(
        ".......",
        ".......",
        ".......",
        "....X..",
        "...XO..",
        "..XOXO.",
    )
    core.reset_node_counters()
    core.minimax(state, ge.PLAYER_O, 4, ge.PLAYER_O)
    minimax_nodes, _ = core.get_node_counters()
    core.reset_node_counters()
    core.alphabeta(state, ge.PLAYER_O, 4, ge.PLAYER_O)
    _, alphabeta_nodes = core.get_node_counters()
    assert minimax_nodes > 0
    assert alphabeta_nodes > 0
    assert alphabeta_nodes <= minimax_nodes


def test_sample_states_have_expected_search_safety_properties():
    with (STARTER_DIR / "sample_states.json").open(encoding="utf-8") as handle:
        states = json.load(handle)["states"]

    for sample in states:
        state = ge.board_from_rows(sample["board"])
        player = sample["to_move"]
        legal = ge.legal_moves(state)
        assert not ge.is_terminal(state), sample["id"]
        assert legal, sample["id"]
        minimax_move, _ = core.minimax(state, player, 1, player)
        alphabeta_move, _ = core.alphabeta(state, player, 1, player)
        assert minimax_move in legal, sample["id"]
        assert alphabeta_move in legal, sample["id"]


@pytest.mark.parametrize(
    ("algorithm", "depth"),
    [
        (core.minimax, -1),
        (core.alphabeta, -1),
    ],
)
def test_negative_depth_is_rejected(algorithm, depth):
    with pytest.raises(ValueError):
        algorithm(ge.new_board(), ge.PLAYER_X, depth, ge.PLAYER_X)


@pytest.mark.parametrize("algorithm", [core.evaluate])
def test_invalid_player_is_rejected_by_evaluate(algorithm):
    with pytest.raises(ValueError):
        algorithm(ge.new_board(), "Z")
