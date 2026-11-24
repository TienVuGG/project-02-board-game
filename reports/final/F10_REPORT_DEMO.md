# F10 — Report and Demo Acceptance

## Deliverables

- `report.pdf`: technical report covering formulation, architecture, algorithm,
  experiments, limitations, and verification.
- `presentation.pdf`: project presentation.
- `F10_DEMO_SCRIPT.md`: reproducible live demonstration sequence.
- `F10_CONTRIBUTIONS.md`: team responsibility record.

The report uses the recorded tournament CSV files under `experiments/` and does
not invent additional measurements. Regenerate it with:

```powershell
python experiments\create_final_report.py
```

Run the final regression before submission:

```powershell
pytest tests\ -v
```
