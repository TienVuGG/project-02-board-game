# F05 — Search Depth Control

## Delivered behavior

The Pygame application exposes a horizontal depth control labeled
`Search depth: N`. The supported product range is the inclusive integer range
**1 through 7**.

`set_search_depth()` is the UI boundary and `clamp_depth()` is the shared
normalization helper. Both automatic AI turns and the single-step `N` command
pass the selected value to `apply_ai_move()`, which passes it to
`choose_ai_move()` and then Alpha-Beta.

Values below 1 become 1 and values above 7 become 7. The search core itself
also receives a clamped value, so invalid UI state cannot create an invalid
search depth.

## Acceptance evidence

`tests/test_z_final_integration.py` verifies:

- Every integer depth from 1 to 7 is accepted unchanged.
- Out-of-range values are bounded to 1 or 7.
- AI moves remain legal at depth 1 and depth 7.
- The UI displays the selected depth and uses the slider to update it.

Run:

```powershell
pytest tests\ -v
```
