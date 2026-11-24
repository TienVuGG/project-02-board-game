# F06 — Real-Time Board Evaluation

## Delivered behavior

The Pygame UI displays a `Board advantage` bar after every event-loop update.
The bar is evaluated from X's perspective:

- Blue fill toward the right means an X advantage.
- Amber is labeled on the opposite side for O.
- The center position represents an even board.
- A numeric label shows `X score`, `O score`, or `even`.

`evaluate(board, PLAYER_X)` supplies the raw heuristic score.
`evaluation_fraction()` maps that unbounded score to the safe interval `[0, 1]`
using a saturating transform, preventing the fill width from exceeding the
bar bounds even for terminal scores.

## Acceptance evidence

`tests/test_z_final_integration.py` verifies:

- Equal positions map to the center.
- Positive and negative scores map to the correct side.
- Extreme scores remain inside `[0, 1]`.
- Labels identify X, O, or an even position.
- The UI calls the evaluation helper while rendering the current board.

Run:

```powershell
pytest tests\ -v
```
