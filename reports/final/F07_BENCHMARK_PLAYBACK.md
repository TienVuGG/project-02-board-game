# F07 — Benchmark Playback

## Delivered behavior

The settings panel in `starter/app.py` supports all four records in
`starter/sample_states.json`:

- `B1_open_start`
- `B2_depth_sensitive_block`
- `B3_alphabeta_reduction`
- `B4_full_column_failure`

Selecting a benchmark loads it through `benchmark_state()` and opens a paused
details view. The view shows the benchmark ID, current `to_move`, and the full
description. Press `N` to make one AI move, `Space` to resume automatic AI vs AI
play, or `I` to reopen the details. A compact ID/turn summary remains visible
during playback.

The adapter validates required fields and the player token before constructing
`GameState`. The game engine remains responsible for board shape validation and
legal-column behavior.

## Acceptance evidence

`tests/test_z_final_integration.py` verifies:

- All B1–B4 records load as the expected board and turn.
- The details view shows the ID, current turn, and complete description.
- Loading pauses play so the initial benchmark position can be inspected.
- B2 remains the immediate-block demonstration.
- B4 keeps column 3 unavailable.
- Invalid benchmark records are rejected with an explicit error.

Run:

```powershell
pytest tests\ -v
```
