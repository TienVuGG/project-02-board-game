"""Analyze controlled tournament summaries from T08."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_summary(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one summary row in {path}")
    return rows[0]


def number(row: dict[str, str], key: str) -> float:
    return float(row[key])


def analyze_summary(path: Path) -> dict[str, object]:
    row = read_summary(path)
    first = row["first_agent"]
    second = row["second_agent"]
    result: dict[str, object] = {
        "experiment": path.stem.removesuffix("_summary"),
        "first_agent": first,
        "second_agent": second,
        "games": int(row["games"]),
        "wins": int(row["wins"]),
        "draws": int(row["draws"]),
        "losses": int(row["losses"]),
        "win_rate": number(row, "win_rate"),
        "draw_rate": number(row, "draw_rate"),
        "loss_rate": number(row, "loss_rate"),
        "avg_turns": number(row, "avg_turns"),
        "first_nodes_per_move": number(row, "avg_first_nodes_per_move"),
        "second_nodes_per_move": number(row, "avg_second_nodes_per_move"),
        "first_time_ms_per_move": number(row, "avg_first_time_ms_per_move"),
        "second_time_ms_per_move": number(row, "avg_second_time_ms_per_move"),
        "node_ratio_first_over_second": None,
        "node_reduction_percent": None,
        "time_ratio_first_over_second": None,
        "time_reduction_percent": None,
    }

    first_nodes = result["first_nodes_per_move"]
    second_nodes = result["second_nodes_per_move"]
    first_time = result["first_time_ms_per_move"]
    second_time = result["second_time_ms_per_move"]
    if first_nodes > 0 and second_nodes > 0:
        result["node_ratio_first_over_second"] = first_nodes / second_nodes
        result["node_reduction_percent"] = (1 - second_nodes / first_nodes) * 100
    if first_time > 0 and second_time > 0:
        result["time_ratio_first_over_second"] = first_time / second_time
        result["time_reduction_percent"] = (1 - second_time / first_time) * 100
    return result


def write_analysis(records: list[dict[str, object]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(records[0].keys())
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def write_charts(records: list[dict[str, object]], output_dir: Path) -> None:
    """Write depth-cost charts for the Alpha-Beta self-play experiments."""
    import matplotlib.pyplot as plt

    depth_records = [
        record
        for record in records
        if str(record["experiment"]).startswith("e3_alphabeta_d")
    ]
    depth_records.sort(
        key=lambda record: int(str(record["first_agent"]).split(":")[1])
    )
    if not depth_records:
        return

    depths = [int(str(record["first_agent"]).split(":")[1]) for record in depth_records]
    nodes = [record["first_nodes_per_move"] for record in depth_records]
    times = [record["first_time_ms_per_move"] for record in depth_records]

    output_dir.mkdir(parents=True, exist_ok=True)
    fig, axis = plt.subplots(figsize=(7, 4.2))
    axis.plot(depths, nodes, marker="o", color="#1f77b4")
    axis.set_title("Alpha-Beta node expansion by search depth")
    axis.set_xlabel("Search depth")
    axis.set_ylabel("Average nodes per move")
    axis.set_xticks(depths)
    axis.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "t09_alphabeta_nodes_by_depth.png", dpi=160)
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(7, 4.2))
    axis.plot(depths, times, marker="o", color="#d62728")
    axis.set_title("Alpha-Beta time by search depth")
    axis.set_xlabel("Search depth")
    axis.set_ylabel("Average milliseconds per move")
    axis.set_xticks(depths)
    axis.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "t09_alphabeta_time_by_depth.png", dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "t09_analysis.csv",
    )
    parser.add_argument(
        "--charts-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
    )
    args = parser.parse_args()

    paths = sorted(args.input_dir.glob("e*_summary.csv"))
    if not paths:
        raise SystemExit(f"No e*_summary.csv files found in {args.input_dir}")
    records = [analyze_summary(path) for path in paths]
    write_analysis(records, args.output)
    write_charts(records, args.charts_dir)

    for record in records:
        ratio = record["node_ratio_first_over_second"]
        reduction = record["node_reduction_percent"]
        print(
            f"{record['experiment']}: "
            f"nodes ratio={ratio if ratio is not None else 'n/a'}; "
            f"reduction={reduction if reduction is not None else 'n/a'}%"
        )
    print(f"Wrote analysis to {args.output}")


if __name__ == "__main__":
    main()
