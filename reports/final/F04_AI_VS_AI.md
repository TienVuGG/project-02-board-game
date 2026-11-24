# F04 — AI vs AI Exhibition

## Delivered behavior

The final Pygame application provides an **AI vs AI** exhibition mode:

- Both players use the same Alpha-Beta adapter with the selected depth.
- The board and current token are rendered after every move.
- Automatic play waits 0.45 seconds between moves so the game is observable.
- `Space` pauses and resumes automatic play.
- `N` performs exactly one guarded AI move and leaves the exhibition paused.
- Restart returns to an empty board with X to move.
- The loop stops searching once the board becomes terminal.

`apply_ai_move()` is the shared transition boundary for the automatic loop and
the single-step command. It rejects terminal states and relies on the adapter's
legal-column check before applying a move.

## Acceptance evidence

`tests/test_z_final_integration.py` verifies:

- Each AI move changes the board and alternates the player.
- A short AI-vs-AI sequence contains only legal moves.
- Terminal states reject another AI move.
- The application contains AI-vs-AI mode, pause, step, and an observable delay.

Run:

```powershell
pytest tests\ -v
```
