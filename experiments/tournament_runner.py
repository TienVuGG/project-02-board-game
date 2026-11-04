"""Run reproducible Connect Four agent tournaments.

Examples:
    python experiments/tournament_runner.py --first random --second minimax:2 --games 50
    python experiments/tournament_runner.py --first minimax:3 --second alphabeta:3 --games 50
    python experiments/tournament_runner.py --first alphabeta:2 --second alphabeta:2 --games 50
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from dataclasses import dataclass
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
STARTER_DIR = PROJECT_DIR / "starter"
if str(STARTER_DIR) not in sys.path:
    sys.path.insert(0, str(STARTER_DIR))

import game_engine as ge  # noqa: E402
import random_agent  # noqa: E402
import student_core as core  # noqa: E402


@dataclass(frozen=True)
class AgentSpec:
    name: str
    algorithm: str
    depth: int | None = None


@dataclass
class AgentStats:
    moves: int = 0
    nodes: int = 0
    elapsed_ms: float = 0.0


def parse_agent_spec(spec: str) -> AgentSpec:
    """Parse `random`, `minimax:N`, or `alphabeta:N`."""
    parts = spec.strip().lower().split(":")
    if parts[0] == "random" and len(parts) == 1:
        return AgentSpec(name=spec, algorithm="random")
    if parts[0] in {"minimax", "alphabeta"} and len(parts) == 2:
        try:
            depth = int(parts[1])
        except ValueError as exc:
            raise ValueError(f"Invalid depth in agent spec: {spec!r}") from exc
        if depth < 1:
            raise ValueError("Search depth must be at least 1")
        return AgentSpec(name=spec, algorithm=parts[0], depth=depth)
    raise ValueError(
        f"Invalid agent spec {spec!r}; use random, minimax:N, or alphabeta:N"
    )


def choose_move(
    board: ge.Board,
    player: str,
    spec: AgentSpec,
    random_agent_instance: random_agent.RandomAgent | None,
) -> tuple[int, int, float]:
    """Return `(column, nodes, elapsed_ms)` for one agent move."""
    started = time.perf_counter()
    if spec.algorithm == "random":
        if random_agent_instance is None:
            raise ValueError("Random agent instance is required")
        column = random_agent_instance.choose_move(board)
        nodes = 0
    else:
        core.reset_node_counters()
        if spec.algorithm == "minimax":
            column, _ = core.minimax(
                board, player, spec.depth or 1, maximizing_player=player
            )
            nodes, _ = core.get_node_counters()
        else:
            column, _ = core.alphabeta(
                board, player, spec.depth or 1, maximizing_player=player
            )
            _, nodes = core.get_node_counters()
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    if column not in ge.legal_moves(board):
        raise ValueError(f"{spec.name} returned illegal column {column}")
    return column, nodes, elapsed_ms


def play_game(
    first_agent: AgentSpec,
    second_agent: AgentSpec,
    game_number: int,
    seed: int,
) -> dict[str, object]:
    """Play one game, alternating which configured agent receives X."""
    first_is_x = game_number % 2 == 1
    x_spec = first_agent if first_is_x else second_agent
    o_spec = second_agent if first_is_x else first_agent
    x_random = random_agent.RandomAgent(seed=seed * 2 + 1)
    o_random = random_agent.RandomAgent(seed=seed * 2 + 2)
    stats = {"X": AgentStats(), "O": AgentStats()}
    state = ge.GameState.new(first_player=ge.PLAYER_X)
    turns = 0

    while not state.is_terminal():
        player = state.to_move
        spec = x_spec if player == ge.PLAYER_X else o_spec
        rng = x_random if player == ge.PLAYER_X else o_random
        column, nodes, elapsed_ms = choose_move(state.board, player, spec, rng)
        state = state.apply(column)
        agent_stats = stats[player]
        agent_stats.moves += 1
        agent_stats.nodes += nodes
        agent_stats.elapsed_ms += elapsed_ms
        turns += 1

    winner = state.winner()
    winner_agent = None
    if winner is not None:
        winner_agent = (x_spec if winner == ge.PLAYER_X else o_spec).name
    first_won = winner is not None and (
        (first_is_x and winner == ge.PLAYER_X)
        or (not first_is_x and winner == ge.PLAYER_O)
    )
    first_result = "draw" if winner is None else ("win" if first_won else "loss")
    first_stats = stats["X"] if first_is_x else stats["O"]
    second_stats = stats["O"] if first_is_x else stats["X"]
    return {
        "game": game_number,
        "first_agent": first_agent.name,
        "second_agent": second_agent.name,
        "x_agent": x_spec.name,
        "o_agent": o_spec.name,
        "winner": winner or "draw",
        "winner_agent": winner_agent or "draw",
        "first_agent_result": first_result,
        "turns": turns,
        "first_moves": first_stats.moves,
        "first_nodes": first_stats.nodes,
        "first_time_ms": first_stats.elapsed_ms,
        "second_moves": second_stats.moves,
        "second_nodes": second_stats.nodes,
        "second_time_ms": second_stats.elapsed_ms,
    }


def run_tournament(
    first_agent: AgentSpec,
    second_agent: AgentSpec,
    games: int,
    seed: int,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Run games and return per-game records plus one summary record."""
    if games < 1:
        raise ValueError("games must be at least 1")
    records = [
        play_game(first_agent, second_agent, number, seed + number - 1)
        for number in range(1, games + 1)
    ]
    wins = sum(record["first_agent_result"] == "win" for record in records)
    losses = sum(record["first_agent_result"] == "loss" for record in records)
    draws = games - wins - losses
    summary = {
        "first_agent": first_agent.name,
        "second_agent": second_agent.name,
        "games": games,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "win_rate": wins / games,
        "draw_rate": draws / games,
        "loss_rate": losses / games,
        "avg_turns": sum(r["turns"] for r in records) / games,
        "avg_first_nodes_per_move": sum(r["first_nodes"] for r in records)
        / sum(r["first_moves"] for r in records),
        "avg_second_nodes_per_move": sum(r["second_nodes"] for r in records)
        / sum(r["second_moves"] for r in records),
        "avg_first_time_ms_per_move": sum(r["first_time_ms"] for r in records)
        / sum(r["first_moves"] for r in records),
        "avg_second_time_ms_per_move": sum(r["second_time_ms"] for r in records)
        / sum(r["second_moves"] for r in records),
    }
    return records, summary


def write_csv(records: list[dict[str, object]], summary: dict[str, object], output: Path) -> None:
    """Write per-game records and the summary using two CSV files."""
    output.parent.mkdir(parents=True, exist_ok=True)
    games_path = output.with_name(f"{output.stem}_games.csv")
    summary_path = output.with_name(f"{output.stem}_summary.csv")
    game_fields = list(records[0].keys()) if records else []
    with games_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=game_fields)
        writer.writeheader()
        writer.writerows(records)
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary.keys()))
        writer.writeheader()
        writer.writerow(summary)
    print(f"Wrote game records to {games_path}")
    print(f"Wrote summary to {summary_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first", required=True, help="random, minimax:N, or alphabeta:N")
    parser.add_argument("--second", required=True, help="random, minimax:N, or alphabeta:N")
    parser.add_argument("--games", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_DIR / "experiments" / "tournament_results.csv",
    )
    args = parser.parse_args()
    first_agent = parse_agent_spec(args.first)
    second_agent = parse_agent_spec(args.second)
    records, summary = run_tournament(first_agent, second_agent, args.games, args.seed)
    write_csv(records, summary, args.output)
    print(summary)


if __name__ == "__main__":
    main()
