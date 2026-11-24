# F01 — Connect Four Final Architecture

## 1. Scope

The final product is a local Pygame application. The game rules remain isolated
in `starter/game_engine.py`; the AI algorithms remain isolated in
`starter/student_core.py`; `starter/app.py` coordinates user interaction,
search, rendering, and benchmark playback.

The application has two modes:

- **Human vs AI**: human controls X (blue), AI controls O (amber).
- **AI vs AI**: both sides use Alpha-Beta and the UI inserts a visible delay
  between turns.

## 2. Component Diagram

```text
+---------------------+       legal moves / apply move       +----------------------+
|     Pygame UI       | -----------------------------------> |    game_engine.py    |
|     starter/app.py  | <----------------------------------- |  GameState + Board   |
+----------+----------+          board / terminal state       +----------------------+
           |
           | board + to_move + depth
           v
+---------------------+       evaluate(board, player)        +----------------------+
|     AI adapter      | -----------------------------------> |   student_core.py    |
|  choose_ai_move()   | <----------------------------------- |     alphabeta()      |
+---------------------+          legal column + score        +----------------------+
           |
           v
+---------------------+
| sample_states.json  |
| B1 / B2 / B3 / B4   |
+---------------------+
```

## 3. State Model

`GameState` is the authoritative runtime state:

```text
GameState(
    board: 6 x 7 immutable tuple,
    to_move: "X" | "O",
)
```

The UI additionally owns presentation state:

| State | Allowed values | Purpose |
|---|---|---|
| `mode` | `Human vs AI`, `AI vs AI` | Selects the event policy |
| `depth` | integer 1–7 | Alpha-Beta search depth |
| `paused` | boolean | Stops automatic AI turns |
| `benchmark_index` | valid JSON index | Selects B1–B4 |
| `error` | string | Displays invalid input/search errors |

`GameState.apply(column)` is the only normal transition. It delegates to
`game_engine.apply_move()` and switches `to_move` using `other_player()`.

## 4. Event Flow

```text
Pygame event loop
  |
  +-- R / Restart button ----------> fresh GameState(X to move)
  +-- Mode button ------------------> mode change + restart
  +-- Depth slider -----------------> clamp to integer [1, 7]
  +-- Benchmark Load ---------------> board_from_rows() + paused state
  +-- Human board click -------------> legal_moves() -> apply() or error
  +-- Space ------------------------> pause/resume AI vs AI
  +-- N ----------------------------> one AI move, then pause
  |
  +-- automatic AI turn?
        |
        +-- no: render board/status/evaluation
        |
        +-- yes:
              legal_moves() and terminal guard
              -> choose_ai_move()
              -> alphabeta(board, to_move, depth, to_move)
              -> reject illegal result
              -> apply()
              -> render
```

No human or AI move is accepted after `state.is_terminal()` becomes true.

## 5. AI Adapter Contract

`choose_ai_move(state, depth)` performs the integration boundary:

1. Rejects terminal states and positions without legal moves.
2. Calls `student_core.alphabeta()` with the current player as both
   `player` and `maximizing_player`.
3. Clamps the requested depth to 1–7.
4. Verifies that the returned column belongs to `legal_moves(state.board)`.
5. Raises a visible `ValueError` rather than silently corrupting state.

The evaluation bar calls `evaluate(board, PLAYER_X)`, so positive values mean
an advantage for X and negative values mean an advantage for O.

## 6. Invariants

- Board dimensions are always 6 rows by 7 columns.
- A move is applied only when its column is in `legal_moves(board)`.
- `to_move` is always `PLAYER_X` or `PLAYER_O`.
- Search depth is always an integer in `[1, 7]`.
- Terminal boards do not trigger another AI search.
- `game_engine.py` does not import Pygame.
- The final application does not use `RandomAgent`.

## 7. Core Verification

From `project-02-board-game`:

```powershell
pytest tests\ -v
```

The regression suite covers engine rules, legal moves, terminal detection,
benchmark schemas, AI-core return contracts, and Pygame-independent imports.
