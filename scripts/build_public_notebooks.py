from __future__ import annotations

import json
import shutil
from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
ASSET_DIR = NOTEBOOK_DIR / "assets"
TARGET_DIR = ASSET_DIR / "targets"
MANIFEST_PATH = NOTEBOOK_DIR / "manifest.json"
README_PATH = NOTEBOOK_DIR / "README.md"

OFFICIAL_RAW_BASE = (
    "https://raw.githubusercontent.com/Snowflake-Labs/EY-AI-and-Data-Challenge/refs/heads/main"
)
PUBLIC_RAW_BASE = (
    "https://raw.githubusercontent.com/FlalaGoGoGo/ey-water-2026-showcase/main/notebooks/assets/targets"
)

PUBLIC_TARGET_SOURCES = {
    "v11_4_guard_ec.csv": Path("/Users/zhangziling/Documents/New project/v11_4_guard_ec.csv"),
    "v15_3_ta_refine_push.csv": Path(
        "/Users/zhangziling/Documents/New project/round15/v15_3_ta_refine_push.csv"
    ),
    "v20_4_ta_ec_struct_farcal_alt.csv": Path(
        "/Users/zhangziling/Documents/New project/round20/v20_4_ta_ec_struct_farcal_alt.csv"
    ),
    "v37_5_ta40_ec40_push.csv": Path(
        "/Users/zhangziling/Documents/New project/round37/v37_5_ta40_ec40_push.csv"
    ),
    "v38_5_chirps_delta_safe.csv": Path(
        "/Users/zhangziling/Documents/New project/round38/v38_5_chirps_delta_safe.csv"
    ),
    "v42_5_ta60_ec60_challenger_push.csv": Path(
        "/Users/zhangziling/Documents/New project/round42/v42_5_ta60_ec60_challenger_push.csv"
    ),
}

NOTEBOOK_CONFIGS = [
    {
        "file_name": "v11_4_guard_ec.ipynb",
        "title": "Round 11 EC Guard Full Workflow",
        "branch_file": "v11_4_guard_ec.csv",
        "phase": "EC Guard",
        "summary": (
            "Archive-backed public workflow for the guarded EC branch from round 11. "
            "The notebook starts from official GitHub data, builds a readable feature table, "
            "and then reproduces the archived public submission exactly."
        ),
        "highlights": [
            "Focuses on EC stabilization while keeping the rest of the submission conservative.",
            "Shows how the public notebook package uses archived exact targets for stable reproduction.",
            "Useful as an early-stage example of guard-first competition thinking.",
        ],
    },
    {
        "file_name": "v15_3_ta_refine_push.ipynb",
        "title": "Round 15 TA Refine Push Full Workflow",
        "branch_file": "v15_3_ta_refine_push.csv",
        "phase": "TA Refine Push",
        "summary": (
            "Archive-backed public workflow for the round 15 TA refinement branch. "
            "The notebook walks through data loading, feature scaffolding, archived-branch "
            "reproduction, and simple diagnostics for the exported file."
        ),
        "highlights": [
            "Represents a targeted TA push rather than a broad three-target move.",
            "Keeps the notebook understandable by separating raw-data prep from branch reproduction.",
            "Useful for showing how the team structured branch-level experiments under limited uploads.",
        ],
    },
    {
        "file_name": "v20_4_ta_ec_struct_farcal_alt.ipynb",
        "title": "Round 20 Structural TA+EC Full Workflow",
        "branch_file": "v20_4_ta_ec_struct_farcal_alt.csv",
        "phase": "Structural TA+EC",
        "summary": (
            "Archive-backed public workflow for the structural TA+EC branch from round 20. "
            "It emphasizes raw-data joins, engineered context features, and exact reproduction "
            "of the public archive file for a later-stage structural probe."
        ),
        "highlights": [
            "Shows a structural exploration phase rather than a pure control replay.",
            "Uses the same readable workflow pattern as the other public notebooks.",
            "Useful as a mid-competition example of controlled experimentation on top of stronger anchors.",
        ],
    },
    {
        "file_name": "v37_5_ta40_ec40_push.ipynb",
        "title": "Round 37 Hydro Corridor Breakthrough",
        "branch_file": "v37_5_ta40_ec40_push.csv",
        "phase": "Hydro Corridor Breakthrough",
        "summary": (
            "Archive-backed public workflow for the first branch that reached the tracked best score "
            "of 0.376. The notebook reproduces the archived winner while still starting from "
            "official GitHub inputs and readable diagnostics."
        ),
        "highlights": [
            "Represents the first tracked breakthrough to 0.376.",
            "Documents the TA/EC corridor style that defined the later competition phase.",
            "Useful as the public reference notebook for the strongest method family.",
        ],
    },
    {
        "file_name": "v38_5_chirps_delta_safe.ipynb",
        "title": "Round 38 CHIRPS Safe Probe",
        "branch_file": "v38_5_chirps_delta_safe.csv",
        "phase": "CHIRPS Safe Probe",
        "summary": (
            "Archive-backed public workflow for the CHIRPS-guided safe probe that followed the "
            "breakthrough branch. It demonstrates how an external signal can enter the workflow "
            "without abandoning a stable archive-backed target."
        ),
        "highlights": [
            "Represents an external-signal probe rather than a complete strategy reset.",
            "Explains the role of rainfall-aware guard logic in a public and readable format.",
            "Useful for readers who want to see how external data enters late-stage experimentation.",
        ],
    },
    {
        "file_name": "v42_5_ta60_ec60_challenger_push.ipynb",
        "title": "Round 42 Challenger Push",
        "branch_file": "v42_5_ta60_ec60_challenger_push.csv",
        "phase": "Challenger Push",
        "summary": (
            "Archive-backed public workflow for a later challenger branch that pushed farther on "
            "the TA/EC boundary while remaining reproducible from public assets."
        ),
        "highlights": [
            "Represents the plateau-stage challenger mindset rather than a default replay.",
            "Keeps the notebook readable by separating raw-data context from exact archived reproduction.",
            "Useful as a public example of 'push with guard' thinking late in the project timeline.",
        ],
    },
]


def md_cell(source: str):
    return nbf.v4.new_markdown_cell(source=source)


def code_cell(source: str):
    return nbf.v4.new_code_cell(source=source)


def step_md(step: int, title: str, purpose: str, why: str, output: str) -> str:
    return (
        f"## Step {step} | {title}\n\n"
        f"**What This Step Does**\n{purpose}\n\n"
        f"**Why This Step Matters**\n{why}\n\n"
        f"**Expected Output**\n{output}"
    )


COMMON_IMPORTS = """import json
from pathlib import Path
from urllib.request import urlretrieve

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pd.set_option("display.max_columns", 120)
pd.set_option("display.max_rows", 120)

OFFICIAL_RAW_BASE = "https://raw.githubusercontent.com/Snowflake-Labs/EY-AI-and-Data-Challenge/refs/heads/main"
PUBLIC_RAW_BASE = "https://raw.githubusercontent.com/FlalaGoGoGo/ey-water-2026-showcase/main/notebooks/assets/targets"

OFFICIAL_URLS = {
    "train_targets": f"{OFFICIAL_RAW_BASE}/water_quality_training_dataset.csv",
    "train_landsat": f"{OFFICIAL_RAW_BASE}/landsat_features_training.csv",
    "train_terraclimate": f"{OFFICIAL_RAW_BASE}/terraclimate_features_training.csv",
    "val_landsat": f"{OFFICIAL_RAW_BASE}/landsat_features_validation.csv",
    "val_terraclimate": f"{OFFICIAL_RAW_BASE}/terraclimate_features_validation.csv",
    "submission_template": f"{OFFICIAL_RAW_BASE}/submission_template.csv",
}


def safe_read_csv(url: str) -> pd.DataFrame:
    try:
        return pd.read_csv(url)
    except Exception:
        local_name = Path(url).name
        urlretrieve(url, local_name)
        return pd.read_csv(local_name)
"""


COMMON_LOAD = """train_targets = safe_read_csv(OFFICIAL_URLS["train_targets"])
train_landsat = safe_read_csv(OFFICIAL_URLS["train_landsat"])
train_terraclimate = safe_read_csv(OFFICIAL_URLS["train_terraclimate"])
val_landsat = safe_read_csv(OFFICIAL_URLS["val_landsat"])
val_terraclimate = safe_read_csv(OFFICIAL_URLS["val_terraclimate"])
submission_template = safe_read_csv(OFFICIAL_URLS["submission_template"])

archive_url = f"{PUBLIC_RAW_BASE}/{BRANCH_FILE}"
archived_submission = safe_read_csv(archive_url)

print("Loaded official tables:")
for name, frame in {
    "train_targets": train_targets,
    "train_landsat": train_landsat,
    "train_terraclimate": train_terraclimate,
    "val_landsat": val_landsat,
    "val_terraclimate": val_terraclimate,
    "submission_template": submission_template,
    "archived_submission": archived_submission,
}.items():
    print(f"{name:20s} -> {frame.shape}")
"""


COMMON_FEATURES = """join_keys = ["date", "site_id", "lat", "lon"]

for frame in [train_targets, train_landsat, train_terraclimate, val_landsat, val_terraclimate]:
    frame["date"] = pd.to_datetime(frame["date"])

train_full = (
    train_targets
    .merge(train_landsat, on=join_keys, how="left")
    .merge(train_terraclimate, on=join_keys, how="left")
    .copy()
)

val_full = (
    submission_template[["date", "site_id", "lat", "lon"]]
    .assign(date=lambda x: pd.to_datetime(x["date"]))
    .merge(val_landsat, on=join_keys, how="left")
    .merge(val_terraclimate, on=join_keys, how="left")
    .copy()
)

for frame in [train_full, val_full]:
    frame["month"] = frame["date"].dt.month
    frame["year"] = frame["date"].dt.year
    frame["dayofyear"] = frame["date"].dt.dayofyear
    frame["lat_lon_sum"] = frame["lat"] + frame["lon"]
    frame["lat_lon_diff"] = frame["lat"] - frame["lon"]

qa_summary = pd.DataFrame(
    {
        "frame": ["train_full", "val_full"],
        "rows": [len(train_full), len(val_full)],
        "columns": [train_full.shape[1], val_full.shape[1]],
        "missing_cells": [int(train_full.isna().sum().sum()), int(val_full.isna().sum().sum())],
    }
)

qa_summary
"""


COMMON_REPRO = """submission = archived_submission.copy()

assert list(submission.columns) == list(submission_template.columns), "Column order mismatch"
assert len(submission) == len(submission_template), "Row-count mismatch"
assert submission["site_id"].tolist() == submission_template["site_id"].tolist(), "site_id mismatch"

output_name = BRANCH_FILE
submission.to_csv(output_name, index=False)

exact_match = submission.equals(archived_submission)
print("Exported file:", output_name)
print("Exact archive match:", exact_match)
submission.head()
"""


COMMON_DIAGNOSTICS = """numeric_cols = [
    "total_alkalinity_mg_per_l",
    "electrical_conductivity_ms_per_m",
    "dissolved_reactive_phosphorus_mg_per_l",
]

diagnostic_summary = submission[numeric_cols].agg(["mean", "std", "min", "max"]).T
diagnostic_summary

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, col in zip(axes, numeric_cols):
    ax.hist(submission[col], bins=30, color="#ffe600", edgecolor="#222222")
    ax.set_title(col.replace("_", " "))
    ax.set_xlabel("value")
    ax.set_ylabel("count")
plt.tight_layout()
plt.show()
"""


def branch_intro(cfg: dict) -> str:
    bullets = "\n".join(f"- {item}" for item in cfg["highlights"])
    return (
        f"# {cfg['title']}: `{cfg['branch_file']}`\n\n"
        f"{cfg['summary']}\n\n"
        f"**Why this branch matters**\n"
        f"{bullets}"
    )


def branch_context(cfg: dict) -> str:
    return (
        f"**Branch label**\n- {cfg['phase']}\n\n"
        f"**Archive-backed workflow**\n"
        "- This public notebook begins from the official GitHub challenge files.\n"
        "- It then prepares a readable merged feature table for context and diagnostics.\n"
        "- The final export is reproduced exactly from the archived public branch file.\n"
        "- That design keeps the notebook stable for external readers while preserving the exact public result."
    )


def branch_notes_md(cfg: dict) -> str:
    return (
        f"**Branch interpretation**\n"
        f"- Public branch file: `{cfg['branch_file']}`\n"
        f"- Phase label: `{cfg['phase']}`\n"
        "- The notebook keeps raw-data loading and archive-backed export in one place so outside readers can "
        "follow the workflow from source data to final CSV.\n"
        "- The merged feature table is included for context even though the final public export is reproduced "
        "from the archived exact branch file."
    )


def create_notebook(cfg: dict):
    nb = nbf.v4.new_notebook()
    nb.cells = [
        md_cell(branch_intro(cfg)),
        md_cell(
            step_md(
                1,
                "Experiment Objective",
                "Introduce the role of this archived branch in the larger competition timeline.",
                "A public-facing notebook should explain why the branch existed, not just dump the output file.",
                "A clear branch definition with enough context for a new reader.",
            )
        ),
        md_cell(branch_context(cfg)),
        md_cell(
            step_md(
                2,
                "Environment Setup",
                "Import the libraries and define the official GitHub data URLs used by every public notebook.",
                "This keeps the workflow transparent and makes the notebook runnable from a clean environment.",
                "A stable environment block plus reusable URL constants.",
            )
        ),
        code_cell(f'BRANCH_FILE = "{cfg["branch_file"]}"\n\n' + COMMON_IMPORTS),
        md_cell(
            step_md(
                3,
                "Load Official Data And Archived Branch Target",
                "Load the official challenge tables from GitHub and pull the archived public branch file from this repo.",
                "The notebook should make it obvious which data is official input and which file is the archived public target.",
                "A complete set of official input tables plus the archived branch output.",
            )
        ),
        code_cell(COMMON_LOAD),
        md_cell(
            step_md(
                4,
                "Merge Tables And Build Context Features",
                "Join the official source tables and create a lightweight feature context for QA and interpretation.",
                "Even when the final public export is archive-backed, readers still benefit from seeing the underlying raw-data structure.",
                "Readable training and validation master tables with simple contextual features.",
            )
        ),
        code_cell(COMMON_FEATURES),
        md_cell(
            step_md(
                5,
                "Reproduce The Public Branch File",
                "Create the final submission by reproducing the archived public branch target exactly.",
                "This is the safest way to keep the public notebook precise, stable, and fully aligned with the published branch file.",
                "A final submission DataFrame and an exact-match verification against the archived branch target.",
            )
        ),
        code_cell(COMMON_REPRO),
        md_cell(
            step_md(
                6,
                "Diagnostics And Interpretation",
                "Summarize the exported branch numerically and plot the target distributions for a quick review.",
                "A public notebook should not stop at file export; it should also help readers understand what the file looks like.",
                "Simple diagnostics that make the branch file easier to inspect.",
            )
        ),
        code_cell(COMMON_DIAGNOSTICS),
        md_cell(branch_notes_md(cfg)),
    ]
    return nb


def sync_public_targets():
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    for file_name, src in PUBLIC_TARGET_SOURCES.items():
        if not src.exists():
            raise FileNotFoundError(f"Missing public target source: {src}")
        shutil.copy2(src, TARGET_DIR / file_name)


def write_manifest():
    manifest = {
        "notebooks": [
            {
                "title": cfg["title"],
                "path": f"notebooks/{cfg['file_name']}",
                "summary": cfg["summary"],
            }
            for cfg in NOTEBOOK_CONFIGS
        ]
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")


def write_readme():
    lines = [
        "# Selected Notebooks",
        "",
        "These are the public-facing notebooks linked from the showcase page.",
        "",
        "Each notebook in this folder is a full workflow notebook in English and follows the same pattern:",
        "- package imports",
        "- official GitHub data loading",
        "- lightweight raw-data QA and feature context",
        "- archive-backed exact branch reproduction",
        "- export and diagnostics",
        "",
        "Notebook list:",
    ]
    for cfg in NOTEBOOK_CONFIGS:
        lines.extend(
            [
                f"- `{cfg['file_name']}`",
                f"  - {cfg['summary']}",
            ]
        )
    lines.append("")
    README_PATH.write_text("\n".join(lines) + "\n")


def main():
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    sync_public_targets()

    for cfg in NOTEBOOK_CONFIGS:
        nb = create_notebook(cfg)
        nbf.write(nb, NOTEBOOK_DIR / cfg["file_name"])
        print(f"Wrote {cfg['file_name']}")

    write_manifest()
    write_readme()
    print("Updated manifest and README.")


if __name__ == "__main__":
    main()
