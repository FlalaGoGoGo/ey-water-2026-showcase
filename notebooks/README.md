# Selected Notebooks

These are the public-facing notebooks linked from the showcase page.

Each notebook in this folder is a full workflow notebook in English and follows the same pattern:
- package imports
- official GitHub data loading
- lightweight raw-data QA and feature context
- archive-backed exact branch reproduction
- export and diagnostics

Notebook list:
- `v11_4_guard_ec.ipynb`
  - Archive-backed public workflow for the guarded EC branch from round 11. The notebook starts from official GitHub data, builds a readable feature table, and then reproduces the archived public submission exactly.
- `v15_3_ta_refine_push.ipynb`
  - Archive-backed public workflow for the round 15 TA refinement branch. The notebook walks through data loading, feature scaffolding, archived-branch reproduction, and simple diagnostics for the exported file.
- `v20_4_ta_ec_struct_farcal_alt.ipynb`
  - Archive-backed public workflow for the structural TA+EC branch from round 20. It emphasizes raw-data joins, engineered context features, and exact reproduction of the public archive file for a later-stage structural probe.
- `v37_5_ta40_ec40_push.ipynb`
  - Archive-backed public workflow for the first branch that reached the tracked best score of 0.376. The notebook reproduces the archived winner while still starting from official GitHub inputs and readable diagnostics.
- `v38_5_chirps_delta_safe.ipynb`
  - Archive-backed public workflow for the CHIRPS-guided safe probe that followed the breakthrough branch. It demonstrates how an external signal can enter the workflow without abandoning a stable archive-backed target.
- `v42_5_ta60_ec60_challenger_push.ipynb`
  - Archive-backed public workflow for a later challenger branch that pushed farther on the TA/EC boundary while remaining reproducible from public assets.

