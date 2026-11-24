# F02 — Alpha-Beta AI Integration

## Implementation

`starter/app.py` integrates the completed AI core through
`choose_ai_move(state, depth)`. The adapter:

1. Checks that the board is not terminal and has at least one legal column.
2. Calls `student_core.alphabeta()` with `state.board`,
   `state.to_move`, the selected depth, and the same player as
   `maximizing_player`.
3. Restricts depth to the product range 1–7.
4. Verifies the returned column against `legal_moves(state.board)`.
5. Raises a visible error instead of applying an illegal move.

The main event loop calls the adapter only when the current state is
non-terminal and it is an AI turn. Human moves are also checked with
`legal_moves()` before `GameState.apply()`.

## Acceptance Evidence

The integration checks in `tests/test_final_integration.py` verify:

- Alpha-Beta returns a legal move on an ordinary board.
- B2 selects column 3 to block O's immediate threat.
- B4 never selects its full column 3.
- Terminal boards are rejected before search.
- The final application imports Alpha-Beta and does not use `RandomAgent`.

Run from `project-02-board-game`:

```powershell
pytest tests\ -v
```

## Runtime Flow

```text
AI turn
  -> state.is_terminal() guard
  -> legal_moves(state.board)
  -> alphabeta(...)
  -> returned-column legality check
  -> state.apply(column)
  -> next render
```
