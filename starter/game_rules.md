# Connect Four — game rules

## Board

- A grid of **6 rows x 7 columns**, empty at the start.
- Two players: **X** and **O**. X moves first.
- On the starter Pygame board, **X is blue** (human) and **O is amber** (opponent).
  The engine still stores cells as the characters `X` and `O`.

## Moves

- A move drops one piece into one of the 7 columns.
- The piece falls to the lowest empty row in that column (gravity).
- A column that already has 6 pieces (full) is not a legal move.

## Winning

A player wins immediately when they have **four of their own pieces in an
unbroken line**:

- horizontally,
- vertically, or
- diagonally (either diagonal direction),

anywhere on the board.

## Draw

If the board fills completely (all 7 columns full) and neither player has
four in a row, the game is a draw.

## Board indexing convention used by `game_engine.py`

- Row **0** is the TOP row.
- Row **5** (`ROWS - 1`) is the BOTTOM row.
- `board[row][col]` uses `EMPTY = "."`, `PLAYER_X = "X"`, `PLAYER_O = "O"`.
- A move only specifies the column; the engine (`apply_move`) computes the
  landing row for you.
- `sample_states.json` stores each board as a list of **6** strings of
  length **7**, top row first, using the same `.`/`X`/`O` characters. Load
  one with `game_engine.board_from_rows(rows)`.

## What the starter engine does and does not do

`starter/game_engine.py` provides:

- legal move generation (`legal_moves`);
- applying a move (`apply_move`);
- terminal detection (`is_terminal`, `is_full`);
- win/loss/draw detection (`check_winner`, `result_label`).

`starter/game_engine.py` does **not** provide Minimax, Alpha-Beta pruning,
or any evaluation function. Those are the graded AI core in
`starter/student_core.py`. `starter/random_agent.py` is only a random
baseline for comparison, not a search algorithm.
