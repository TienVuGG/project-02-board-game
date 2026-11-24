# F08 — Stress and Failure Scenarios

## Covered scenarios

The final application guards every transition at the UI/adapter boundary:

| Scenario | Expected behavior |
|---|---|
| Immediate win | Alpha-Beta selects a legal winning column |
| Immediate block | B2 selects column 3 to stop O's threat |
| Opponent fork | Search completes and returns a legal defensive move |
| Full column | Full columns are excluded before applying a move |
| Terminal board | No further human or AI move is accepted |
| Depth 7 | The configured maximum depth is accepted and remains legal |
| Restart | A fresh board is created with X to move |

`choose_ai_move()` rejects terminal/no-move positions and validates the search
result. `apply_human_move()` and `apply_ai_move()` surface `ValueError` messages
to the status line. The application never applies a move after terminal state.

## Depth-7 policy

Depth 7 is the supported maximum. It is intentionally an explicit user choice
through the depth control. Search runs synchronously for deterministic behavior;
the status line keeps the selected depth visible, and the adapter rejects
invalid results rather than silently falling back to a random move. Demonstration
boards should use B2/B3 or another mid-game state when showcasing depth 7.

## Acceptance evidence

The stress tests in `tests/test_z_final_integration.py` cover the scenarios above
and assert that all returned moves are legal and that invalid/terminal actions
fail explicitly.

Run:

```powershell
pytest tests\ -v
```
