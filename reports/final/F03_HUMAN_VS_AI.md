# F03 — Human vs AI Acceptance

## Delivered behavior

`starter/app.py` runs Human vs AI with:

- Human player X displayed in blue.
- AI player O displayed in amber.
- Mouse column input for the human turn.
- A visible status line showing the current actor, token, and search depth.
- Restart through the `R` key or the Restart button.
- Clear errors for full/unavailable columns.
- No move accepted after a win or draw.

The `apply_human_move()` adapter centralizes the human-side guards before
delegating the state transition to `GameState.apply()`.

## Acceptance evidence

`tests/test_z_final_integration.py` verifies:

- A legal human move lands in the selected column and changes the turn.
- A full column is rejected without changing the board.
- A terminal board rejects further human input.
- Restart creates a clean board with X to move.
- The final UI contains the required X/O colors and restart/status controls.

Run:

```powershell
pytest tests\ -v
```
