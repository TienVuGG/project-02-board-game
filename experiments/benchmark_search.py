"""Benchmark Minimax and Alpha-Beta search calls.

This module measures one root search call at a time. It intentionally does
not run a tournament; tournament orchestration belongs to T07.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Callable, Iterable

PROJECT_DIR = Path(__file__).resolve().parents[1]
STARTER_DIR = PROJECT_DIR / "starter"
if str(STARTER_DIR) not in sys.path:
    sys.path.insert(0, str(STARTER_DIR))

import game_engine as ge  # noqa: E402
import student_core as core  # noqa: E402


SearchFunction = Callable[..., tuple[int, float]]


def measure_search(
    board: ge.Board,
    player: str,
    depth: int,
    algorithm: str,
) -> dict[str, object]:
    """Measure one deterministic search call and return a serializable record."""
    searches: dict[str, SearchFunction] = {
        "minimax": core.minimax,
        "alphabeta": core.alphabeta,
    }
    try:
        search = searches[algorithm]
    except KeyError as exc:
        raise ValueError(
            f"Unknown algorithm {algorithm!r}; expected 'minimax' or 'alphabeta'"
        ) from exc

    core.reset_node_counters()
    started = time.perf_counter()
    best_column, value = search(
        board,
        player,
        depth=depth,
        maximizing_player=player,
    )
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    minimax_nodes, alphabeta_nodes = core.get_node_counters()
    nodes = minimax_nodes if algorithm == "minimax" else alphabeta_nodes

    if not ge.is_terminal(board) and best_column not in ge.legal_moves(board):
        raise ValueError(
            f"{algorithm} returned illegal column {best_column} for board"
        )

    return {
        "algorithm": algorithm,
        "depth": depth,
        "player": player,
        "best_column": best_column,
        "value": value,
        "nodes_expanded": nodes,
        "elapsed_ms": elapsed_ms,
    }


def load_sample_state(state_id: str) -> tuple[ge.Board, str]:
    """Load one benchmark board and its side to move from sample_states.json."""
    path = STARTER_DIR / "sample_states.json"
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    for state in data["states"]:
        if state["id"] == state_id:
            return ge.board_from_rows(state["board"]), state["to_move"]
    raise ValueError(f"Unknown sample state: {state_id}")


def benchmark_cases(
    state_id: str = "B3_alphabeta_reduction",
    depths: Iterable[int] = (2, 3, 4),
) -> list[dict[str, object]]:
    """Measure both algorithms for each requested depth on one sample state."""
    board, player = load_sample_state(state_id)
    records: list[dict[str, object]] = []
    for depth in depths:
        for algorithm in ("minimax", "alphabeta"):
            records.append(measure_search(board, player, depth, algorithm))
    return records


def write_csv(records: Iterable[dict[str, object]], output: Path) -> None:
    """Write benchmark records with a stable, analysis-friendly schema."""
    fieldnames = [
        "algorithm",
        "depth",
        "player",
        "best_column",
        "value",
        "nodes_expanded",
        "elapsed_ms",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", default="B3_alphabeta_reduction")
    parser.add_argument("--depths", nargs="+", type=int, default=[2, 3, 4])
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_DIR / "experiments" / "search_benchmark.csv",
    )
    args = parser.parse_args()

    records = benchmark_cases(args.state, args.depths)
    write_csv(records, args.output)
    for record in records:
        print(
            f"{record['algorithm']:9} depth={record['depth']} "
            f"nodes={record['nodes_expanded']} "
            f"time_ms={record['elapsed_ms']:.3f} "
            f"move={record['best_column']} value={record['value']}"
        )
    print(f"Wrote {len(records)} records to {args.output}")


if __name__ == "__main__":
    main()
