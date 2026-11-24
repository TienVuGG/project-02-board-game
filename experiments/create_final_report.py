"""Generate the Project 02 final technical report PDF."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_DIR / "report.pdf"


def summary(filename: str) -> dict[str, str]:
    with (PROJECT_DIR / "experiments" / filename).open(
        encoding="utf-8", newline=""
    ) as handle:
        return next(csv.DictReader(handle))


def page(pdf: PdfPages, title: str, sections: list[tuple[str, list[str]]]) -> None:
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    fig.text(0.08, 0.94, title, fontsize=22, fontweight="bold", color="#12355B")
    y = 0.88
    for heading, lines in sections:
        fig.text(0.08, y, heading, fontsize=14, fontweight="bold", color="#D97706")
        y -= 0.035
        for line in lines:
            fig.text(0.10, y, line, fontsize=10.5, color="#1F2937", wrap=True)
            y -= 0.027
        y -= 0.025
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    e1 = summary("e1_random_minimax_d2_summary.csv")
    e2 = summary("e2_minimax_alphabeta_d3_summary.csv")
    e3 = summary("e3_alphabeta_d4_summary.csv")
    with PdfPages(OUTPUT) as pdf:
        page(
            pdf,
            "Project 02 — AI Board Game Arena",
            [
                ("Abstract", [
                    "This report presents an offline Connect Four application using "
                    "static evaluation, Minimax, and Alpha-Beta pruning.",
                    "The final Pygame product supports Human vs AI, AI vs AI, "
                    "depth control, evaluation feedback, and benchmark playback.",
                ]),
                ("Keywords", ["Connect Four; adversarial search; Minimax; Alpha-Beta; Pygame."]),
                ("Contributions", [
                    "The rules engine is isolated from the AI core and UI.",
                    "The UI validates every human and AI transition against legal_moves().",
                    "The AI core evaluates center control and open two/three-token windows.",
                ]),
            ],
        )
        page(
            pdf,
            "1. System Design",
            [
                ("State representation", [
                    "A board is an immutable 6 x 7 tuple. Row 0 is the top and row 5 is the bottom.",
                    "GameState stores board and to_move. apply() drops a token and alternates players.",
                ]),
                ("Search", [
                    "Minimax recursively selects the maximum value for the maximizing player "
                    "and the minimum value for the opponent.",
                    "Alpha-Beta adds alpha and beta bounds while preserving the Minimax result.",
                    "The application clamps user depth to the supported range 1..7.",
                ]),
                ("Evaluation", [
                    "Terminal wins receive a large signed score. Non-terminal positions combine "
                    "center-column control with open windows of two and three tokens.",
                ]),
            ],
        )
        page(
            pdf,
            "2. Experimental Results",
            [
                ("Random vs Minimax depth 2", [
                    f"Minimax wins {e1['wins']} of {e1['games']} games; "
                    f"average Minimax move time {e1['avg_second_time_ms_per_move']} ms.",
                ]),
                ("Minimax depth 3 vs Alpha-Beta depth 3", [
                    f"Minimax wins {e2['wins']} and Alpha-Beta wins {e2['losses']} "
                    f"of {e2['games']} games, with alternating first player.",
                    f"Average Minimax nodes/move: {e2['avg_first_nodes_per_move']}; "
                    f"Alpha-Beta nodes/move: {e2['avg_second_nodes_per_move']}.",
                ]),
                ("Alpha-Beta depth 4", [
                    f"The controlled tournament produced {e3['games']} games and "
                    f"{e3['avg_turns']} average turns per game.",
                ]),
                ("Limitations", [
                    "Search is synchronous and depth 7 can be slower on open boards.",
                    "The heuristic is not a solved Connect Four database.",
                ]),
            ],
        )
        page(
            pdf,
            "3. Final Product and Verification",
            [
                ("Product features", [
                    "Human vs AI and AI vs AI modes; pause/resume and one-step exhibition control.",
                    "Depth slider 1..7, real-time X/O evaluation bar, and B1–B4 playback.",
                    "Explicit errors for full columns, invalid states, and post-terminal actions.",
                ]),
                ("Verification", [
                    "The regression and final acceptance suite covers engine rules, integration, "
                    "UI adapters, benchmarks, stress scenarios, and failure handling.",
                    "Run: pytest tests\\ -v",
                ]),
                ("Reproducibility", [
                    "Run: python starter\\app.py",
                    "Dependencies are listed in requirements.txt; no hosted AI service is used.",
                ]),
            ],
        )


if __name__ == "__main__":
    main()
