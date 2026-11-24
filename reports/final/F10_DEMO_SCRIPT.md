# F10 — Demo Script

## 1. Setup

```powershell
cd project-02-board-game
.\.venv\Scripts\Activate.ps1
pytest tests\ -q
python starter\app.py
```

## 2. Live demonstration

1. Start in **Human vs AI**, click an open column, and show X blue followed by
   the AI's O amber response.
2. Set depth to **1**, then **4**, then **7** and point out the status label.
3. Press `R` to demonstrate restart.
4. Select **AI vs AI**. Press `Space` to pause, `N` for one move, then `Space`
   again to resume the visible exhibition.
5. Show the evaluation bar moving between X, even, and O positions.
6. Load B1, B2, B3, and B4. On B2, run the AI and show the block at column 3.
   On B4, show that column 3 is full and unavailable.
7. Finish a game and show the winner/draw status and terminal guard.

## 3. Defense points

- Explain that `game_engine.py` owns rules, `student_core.py` owns search, and
  `app.py` owns integration and presentation.
- Explain why Alpha-Beta returns the same choice as Minimax while expanding fewer
  nodes when bounds prune a branch.
- Explain that the heuristic is from the requested player's perspective.
