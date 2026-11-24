# F09 — Product Testing and Evidence

## 1. Automated regression

Run from `project-02-board-game`:

```powershell
pytest tests\ -v
```

The suite covers:

- Connect Four engine rules and win/draw detection.
- Legal move generation and full-column behavior.
- Minimax and Alpha-Beta return contracts.
- Alpha-Beta application integration.
- Human vs AI transitions and restart.
- AI vs AI transitions, pause/step controls, and terminal guards.
- Search depth values 1–7 and out-of-range clamping.
- Evaluation-bar normalization and labels.
- B1–B4 benchmark loading and metadata validation.
- Immediate win, block, fork, depth-7, and failure scenarios.

## 2. Manual UI matrix

| ID | Scenario | Steps | Expected result | Status |
|---|---|---|---|---|
| UI-01 | Human vs AI start | Run app; leave default mode; click an open column | X is placed; turn changes to O; AI responds | ☐ |
| UI-02 | Human restart | Press `R` during a game | Empty board; X to move | ☐ |
| UI-03 | Full column | Fill a column, then click it | Error/status is shown; board is unchanged | ☐ |
| UI-04 | AI vs AI | Select AI vs AI; observe | Both sides move with visible delay; game remains responsive | ☐ |
| UI-05 | Pause/resume | Press `Space` in AI vs AI | Automatic moves stop and resume | ☐ |
| UI-06 | Single step | Pause AI vs AI; press `N` | Exactly one AI move occurs; game remains paused | ☐ |
| UI-07 | Depth control | Select depth 1, 4, and 7 | Label updates and the selected value is used | ☐ |
| UI-08 | Evaluation bar | Play several moves | Bar and X/O score label update after each board change | ☐ |
| UI-09 | Benchmark playback | Load B1, B2, B3, and B4 | Board, ID, description, and to-move token are correct | ☐ |
| UI-10 | Terminal state | Complete a win or draw | Winner/draw is shown; no further AI move starts | ☐ |
| UI-11 | Restart after terminal | Press `R` after win/draw | New clean game starts with X | ☐ |

## 3. Evidence record

The automated suite is the reproducible evidence for core and adapter
behavior. Manual UI rows should be checked during the final rehearsal and
screenshots may be attached to the submission package. The application is
started with:

```powershell
python starter\app.py
```

No hosted service or external AI API is required.

## 4. Release gate

The final package is ready for UI rehearsal when:

- The automated command passes with zero failures.
- UI-01 through UI-11 are checked by the team.
- `presentation.pdf` and `report.pdf` are present.
- `.venv`, caches, and temporary files are excluded from the submitted archive.
