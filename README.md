# Project 02 — AI Board Game Arena (Connect Four)

## 1. Problem Description

Adversarial game playing is a foundational domain in Artificial Intelligence for studying rational decision-making under competition and bounded resources. In a zero-sum, perfect-information environment an agent must anticipate opponent counter-strategies while optimising its own path to victory.

This project builds an intelligent agent for **Connect Four**, played on a 6 × 7 vertical grid. Players alternate dropping tokens into columns; tokens fall to the lowest empty cell. The first player to form four consecutive tokens—horizontally, vertically, or diagonally—wins. The engine uses `PLAYER_X = "X"` and `PLAYER_O = "O"`: in the Pygame interface **X is the human player (displayed in blue)** and **O is the AI opponent (displayed in amber)**. Students must design minimax game trees, manage the branching factor ($b \approx 7$), craft static board evaluation heuristics, and apply pruning to meet per-turn time limits.

---

## 2. Provided Materials & Starter Resources

The project provides an optimised board game engine, a baseline random agent, and a Pygame graphical interface.

### File Structure
```text
project-02-board-game/
├── starter/
│   ├── game_engine.py      # Rules, board representation, win/draw detection (do not modify)
│   ├── game_rules.md       # Game mechanics and column coordinate indexing
│   ├── random_agent.py     # Baseline agent selecting uniformly random legal moves
│   ├── sample_states.json  # Benchmark board configurations for testing
│   ├── student_core.py     # Algorithmic stubs — implement here
│   └── app.py              # Pygame graphical interface (provided)
├── tests/
│   └── test_project_02_sanity.py
└── requirements.txt
```

### Starter Infrastructure vs. Student Implementation
`starter/game_engine.py` handles legal move generation, piece dropping, and terminal state evaluation. Students implement all AI logic in `starter/student_core.py`.

### Installation and Execution
```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python starter/app.py
```

---

## 3. Requirements & Deliverables

### 3.1 Midterm Milestone — AI Core
- **Implement**: `evaluate`, `minimax`, and `alphabeta` in `starter/student_core.py` from first principles. The evaluation function must score centre control, open-ended three-token threats, and defensive counter-blocks for non-terminal states.
- **Experiment**: Run automated round-robin tournaments (≥ 50 games per matchup): (i) Random vs. Minimax ($d=2$); (ii) Minimax vs. AlphaBeta ($d=3$); (iii) AlphaBeta at depths $d \in \{2, 4, 6\}$. Record win/draw/loss rates, average nodes expanded per turn, time per move, and the pruning efficiency ratio of AlphaBeta over plain Minimax.
- **Deliverables**: Completed `student_core.py`, tournament evaluation script/notebook, `presentation.pdf`.
- **Grading Criteria**: Problem formalization and algorithmic correctness (15 pts); heuristic design and pruning analysis (10 pts); oral defence and live gameplay demo (15 pts). **Total: 40 pts.**

### 3.2 Final Milestone — AI Product
- **Interactive Application**: Pygame desktop application featuring Human vs. AI mode (X = human, blue; O = AI, amber), AI vs. AI exhibition mode, an adjustable search depth slider (depth 1–7), a real-time board advantage evaluation bar, and interactive playback of benchmark states from `starter/sample_states.json`.
- **Stress Scenarios**: Demonstrate the agent correctly solving immediate winning threats and preventing opponent forks on complex board configurations without timeout or memory exhaustion.
- **Deliverables**: Fully functional Pygame application, GitHub repository, `report.pdf` (IEEE format).
- **Grading Criteria**: Product UI, game controls, and stability (25 pts); technical report depth and mathematical formulation (15 pts); oral defence against benchmark boards (10 pts). **Total: 50 pts.**

---

## 4. References

- [1] D. E. Knuth and R. W. Moore, "An analysis of alpha-beta pruning," *Artificial Intelligence*, vol. 6, no. 4, pp. 293–326, 1975, doi: 10.1016/0004-3702(75)90019-3.
- [2] S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. Hoboken, NJ, USA: Pearson, 2020, pp. 146–174.
- [3] J. Allen, "A complete solver for Connect Four," M.S. thesis, Dept. Comput. Sci., Univ. Victoria, Victoria, BC, Canada, 1990.
