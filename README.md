# Safe but Unverified: Audit Starvation and Availability in AI Services with Delayed Feedback

This repository contains the code and data for the article *Safe but Unverified: Audit Starvation and Availability in AI Services with Delayed Feedback* (H. Hamam). It reproduces every experiment in the article.

## What the code shows

AI services often release predictions before an audit can check whether they are correct. The code simulates such services with a frozen binary classifier, delayed truthful audits, and a single auditor with limited capacity. It evaluates:

- **Admission policies:** static, confirmed-only, pending cap, reservation, and immediate audit. The reservation ledger keeps realised cumulative errors below the additive envelope `L_t <= eps * N_t + B`.
- **Audit schedulers:** FIFO, high-confidence, uncertainty, and age-capped priority. With the reservation gate held fixed, these runs show a finite-horizon starvation signature.
- **Dual-ledger admission:** an exposure ledger is combined with an earliest-deadline-first verification-debt test. When audit service time is bounded by `S_max`, every release is resolved within a declared deadline `D`, and the error envelope is preserved.

All data are synthetic. No external download is required.

## Contents

| Path | Description |
|---|---|
| `Supplementary/Pending_Audit_Feasibility_Executed.ipynb` | Executed notebook for the admission study (2,400 runs) and the exploratory scheduling study (360 runs) |
| `Supplementary/pending_audit_results/` | Per-run tables, summaries, paired bootstrap intervals, representative policy traces, and the run manifest |
| `Code/dual_ledger_sim.py` | Simulator for the dual-ledger experiment (630 runs) |
| `Code/dual_ledger_results.json` | Per-run results of the dual-ledger experiment |
| `Code/validate_dual_ledger.py` | Independent replay: checks both invariants on every request, matches the stored metrics, and follows every accepted output to completion |
| `Code/validation_results.json` | Validation output, including a hash of the result file |
| `Code/edf_only_ablation.py` | Deadline-only ablation: the same deadline-feasibility test without the exposure ledger (180 runs) |
| `Code/edf_only_results.json` | Per-run results of the deadline-only ablation |
| `Code/draw_framework.py` | Generates the framework overview figure |
| `Figures/` | Figures used in the article |

## Reproducing the results

```bash
pip install -r requirements.txt
cd Code
python dual_ledger_sim.py dual_ledger_results.json     # dual-ledger experiment
python validate_dual_ledger.py validation_results.json # independent validation
python edf_only_ablation.py edf_only_results.json     # deadline-only ablation
```

Run the notebook in `Supplementary/` to reproduce the admission and scheduling studies. The reference environment is Python 3.9.6 with NumPy 2.0.2.

## Scope

The experiments are synthetic and low-dimensional. They show mechanisms and verify the implementation against the stated guarantees. They are not estimates of deployment performance. The deadline guarantee holds only when audit service times truly stay below `S_max`.

## Citation

If you use this repository, please cite the associated article and this repository (see `CITATION.cff`).

## License

MIT License. See `LICENSE`.
