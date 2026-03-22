#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = REPO_ROOT.parent
SOURCE_ROOT = WORKSPACE_ROOT / "ey-water-2026"
OUTPUT_PATH = REPO_ROOT / "docs" / "assets" / "data" / "showcase_data.json"


def series_hist(values: np.ndarray, bins: int = 24) -> dict:
    clean = values[~np.isnan(values)]
    counts, edges = np.histogram(clean, bins=bins)
    centers = ((edges[:-1] + edges[1:]) / 2).tolist()
    return {
        "centers": [round(float(x), 6) for x in centers],
        "counts": counts.astype(int).tolist(),
        "min": round(float(clean.min()), 6),
        "max": round(float(clean.max()), 6),
        "mean": round(float(clean.mean()), 6),
        "median": round(float(np.median(clean)), 6),
    }


def top_branch_table(df: pd.DataFrame, limit: int = 12) -> list[dict]:
    top = df.sort_values("r2_mean", ascending=False).head(limit).copy()
    cols = [
        "branch_id",
        "feature_set",
        "model_name",
        "missing_strategy",
        "outlier_strategy",
        "target_transform",
        "n_features",
        "r2_mean",
        "r2_total_alkalinity",
        "r2_electrical_conductance",
        "r2_drp",
    ]
    rows: list[dict] = []
    for row in top[cols].to_dict(orient="records"):
        rows.append(
            {
                "branch_id": row["branch_id"],
                "feature_set": row["feature_set"],
                "model_name": row["model_name"],
                "missing_strategy": row["missing_strategy"],
                "outlier_strategy": row["outlier_strategy"],
                "target_transform": row["target_transform"],
                "n_features": int(row["n_features"]),
                "r2_mean": round(float(row["r2_mean"]), 4),
                "r2_ta": round(float(row["r2_total_alkalinity"]), 4),
                "r2_ec": round(float(row["r2_electrical_conductance"]), 4),
                "r2_drp": round(float(row["r2_drp"]), 4),
            }
        )
    return rows


def feature_model_heatmap(df: pd.DataFrame) -> dict:
    agg = (
        df.groupby(["feature_set", "model_name"], as_index=False)
        .agg(
            mean_r2=("r2_mean", "mean"),
            n_branches=("branch_id", "count"),
        )
        .sort_values(["mean_r2", "n_branches"], ascending=[False, False])
    )
    feature_order = agg.groupby("feature_set")["mean_r2"].mean().sort_values(ascending=False).index.tolist()
    model_order = agg.groupby("model_name")["mean_r2"].mean().sort_values(ascending=False).index.tolist()

    matrix = []
    count_matrix = []
    for feature in feature_order:
        row = []
        count_row = []
        for model in model_order:
            hit = agg[(agg["feature_set"] == feature) & (agg["model_name"] == model)]
            if hit.empty:
                row.append(None)
                count_row.append(0)
            else:
                row.append(round(float(hit.iloc[0]["mean_r2"]), 4))
                count_row.append(int(hit.iloc[0]["n_branches"]))
        matrix.append(row)
        count_matrix.append(count_row)

    return {
        "feature_order": feature_order,
        "model_order": model_order,
        "values": matrix,
        "counts": count_matrix,
    }


def curated_milestones() -> list[dict]:
    return [
        {
            "round": 1,
            "title": "Benchmark Start",
            "score": 0.2590,
            "phase": "Baseline",
            "detail": "We started from the official benchmark and used it as the reproducibility anchor for every later round.",
        },
        {
            "round": 2,
            "title": "Early Lift",
            "score": 0.2849,
            "phase": "Tuning",
            "detail": "Target-wise tuning and cleaner search discipline produced the first meaningful jump.",
        },
        {
            "round": 7,
            "title": "EC Signal Breakthrough",
            "score": 0.3160,
            "phase": "Feature Search",
            "detail": "Weather-enriched EC modeling became the first clear sign that external signals could help when used carefully.",
        },
        {
            "round": 10,
            "title": "Corridor Regime",
            "score": 0.3499,
            "phase": "Calibration",
            "detail": "TA/EC link calibration and near-region corrections moved the project into a much stronger operating regime.",
        },
        {
            "round": 15,
            "title": "Stable TA Refinement",
            "score": 0.3659,
            "phase": "Refinement",
            "detail": "TA-focused refinement became a reliable way to improve without sacrificing the rest of the stack.",
        },
        {
            "round": 37,
            "title": "Hydro Corridor Peak",
            "score": 0.3760,
            "phase": "Hydro Corridor",
            "detail": "A hydro micro-corridor boundary push at 40/40 became the first confirmed frontier above the long 0.375 plateau.",
        },
        {
            "round": 42,
            "title": "Plateau Confirmed",
            "score": 0.3760,
            "phase": "Plateau",
            "detail": "By round 42, safe pushes out to 60/60 still tied the same frontier, showing this family had become a stability baseline.",
        },
        {
            "round": 43,
            "title": "POWER Reset Failure",
            "score": 0.3709,
            "phase": "Failure Review",
            "detail": "The first NASA POWER attack regressed online, proving that broad direct replacement was not submission-safe.",
        },
        {
            "round": 44,
            "title": "Recovery via Positive-Only Guards",
            "score": 0.3760,
            "phase": "Recovery",
            "detail": "Freezing EC and allowing only tiny positive TA deltas recovered safety and restored the frontier score.",
        },
        {
            "round": 46,
            "title": "Strong Attack Postmortem",
            "score": 0.3760,
            "phase": "Reset",
            "detail": "A direct-family strong attack failed hard, which became one of the most useful failure analyses in the project.",
        },
    ]


def worked_failed_cards() -> dict:
    return {
        "worked": [
            {
                "title": "Target-wise modeling",
                "detail": "Separating TA, EC, and DRP decisions made the search much more controlled than one-size-fits-all modeling.",
            },
            {
                "title": "External data with tight safety gates",
                "detail": "Landsat, TerraClimate, CHIRPS, hydro, terrain, and weather signals helped only when injected conservatively.",
            },
            {
                "title": "Risk-aware post-processing",
                "detail": "Fallback logic, corridor boundaries, and replay anchors repeatedly prevented avoidable leaderboard collapses.",
            },
            {
                "title": "Failure reviews as part of the loop",
                "detail": "Major review rounds and postmortems turned bad submissions into better strategy, not just frustration.",
            },
        ],
        "failed": [
            {
                "title": "Direct full replacement with new families",
                "detail": "Aggressive swaps with POWER/CHIRPS-style families caused large online regressions when calibration drift was too broad.",
            },
            {
                "title": "Overly cautious micro-edits",
                "detail": "Very safe DRP or tiny TA/EC edits often looked principled but could not move the leaderboard.",
            },
            {
                "title": "Family changes without anchoring",
                "detail": "Changing model families alone was rarely enough; structure and calibration had to come with it.",
            },
        ],
    }


def method_stack() -> list[dict]:
    return [
        {
            "label": "Core data",
            "detail": "Official water quality training data, river coordinates, dates, Landsat, and TerraClimate features.",
        },
        {
            "label": "External signals",
            "detail": "HydroBASINS, terrain, soil, CHIRPS rainfall, NASA POWER, and weather proxies were explored as additional context.",
        },
        {
            "label": "Model families",
            "detail": "HGB, Extra Trees, KNN, graph smoothing, corridor logic, calibration layers, and target-wise blends.",
        },
        {
            "label": "Validation discipline",
            "detail": "Repeated offline ranking, branch tracking, leaderboard feedback, and round-by-round strategy resets.",
        },
    ]


def selected_notebooks() -> list[dict]:
    return [
        {
            "title": "Official Benchmark Reference",
            "path": "notebooks/reference_benchmark_model_notebook_snowflake.ipynb",
            "summary": "The starting point provided by the official challenge package.",
        },
        {
            "title": "Round 11 EC Guard Notebook",
            "path": "notebooks/v11_4_guard_ec.ipynb",
            "summary": "A curated public notebook brief for the EC-focused stabilization phase.",
        },
        {
            "title": "Round 15 TA Refine Push",
            "path": "notebooks/v15_3_ta_refine_push.ipynb",
            "summary": "A curated public notebook brief for the TA-focused refinement phase that pushed the score into the mid 0.36 range.",
        },
        {
            "title": "Round 18 DRP Ultralight Probe",
            "path": "notebooks/v18_5_ta_core_drp_ultralight.ipynb",
            "summary": "A curated public notebook brief for a careful DRP probe without destabilizing the full submission.",
        },
        {
            "title": "Round 20 Structural TA+EC Notebook",
            "path": "notebooks/v20_4_ta_ec_struct_farcal_alt.ipynb",
            "summary": "A curated public notebook brief showing the move toward structural routing and corridor-aware adjustments.",
        },
    ]


def build() -> None:
    leaderboard = pd.read_csv(SOURCE_ROOT / "experiments" / "round_tracking" / "leaderboard_scores.csv")
    official = leaderboard[leaderboard["status"] == "official"].copy()
    official["score"] = official["score"].astype(float)

    branch_summary = pd.read_csv(SOURCE_ROOT / "experiments" / "outputs" / "branch_summary.csv")
    train = pd.read_csv(SOURCE_ROOT / "data" / "raw" / "water_quality_training_dataset.csv")
    train["Sample Date"] = pd.to_datetime(train["Sample Date"], dayfirst=True, errors="coerce")

    by_round = (
        official.groupby("round", as_index=False)
        .agg(
            best_score=("score", "max"),
            mean_score=("score", "mean"),
            n_submissions=("file", "count"),
        )
        .sort_values("round")
    )

    sites = (
        train.groupby(["Latitude", "Longitude"], as_index=False)
        .agg(samples=("Sample Date", "count"))
        .sort_values("samples", ascending=False)
    )

    best_score = float(official["score"].max())
    best_rows = official[official["score"] == best_score].sort_values(["round", "file"])

    payload = {
        "summary": {
            "project_title": "Optimizing Clean Water Supply",
            "challenge_name": "2026 EY AI & Data Challenge",
            "tagline": "An independent team project exploring water-quality prediction, external data enrichment, and leaderboard-driven model iteration.",
            "best_score": round(best_score, 4),
            "official_rounds": int(official["round"].nunique()),
            "official_submissions": int(len(official)),
            "latest_round": int(official["round"].max()),
            "tracked_branch_notebooks": int(len(list((SOURCE_ROOT / "experiments" / "notebooks").glob("branch_*.ipynb")))),
            "public_notebooks": 5,
            "samples": int(len(train)),
            "unique_sites": int(len(sites)),
            "date_start": train["Sample Date"].min().strftime("%Y-%m-%d"),
            "date_end": train["Sample Date"].max().strftime("%Y-%m-%d"),
        },
        "frontier_methods": [
            {
                "file": row["file"],
                "round": int(row["round"]),
                "score": round(float(row["score"]), 4),
                "note": row["notes"],
            }
            for row in best_rows[["round", "file", "score", "notes"]].to_dict(orient="records")
        ],
        "leaderboard_by_round": [
            {
                "round": int(row["round"]),
                "best_score": round(float(row["best_score"]), 4),
                "mean_score": round(float(row["mean_score"]), 4),
                "n_submissions": int(row["n_submissions"]),
            }
            for row in by_round.to_dict(orient="records")
        ],
        "training_map": [
            {
                "lat": round(float(row["Latitude"]), 6),
                "lon": round(float(row["Longitude"]), 6),
                "samples": int(row["samples"]),
            }
            for row in sites.to_dict(orient="records")
        ],
        "target_distributions": {
            "total_alkalinity": series_hist(train["Total Alkalinity"].to_numpy(dtype=float), bins=24),
            "electrical_conductance": series_hist(train["Electrical Conductance"].to_numpy(dtype=float), bins=28),
            "dissolved_reactive_phosphorus": series_hist(train["Dissolved Reactive Phosphorus"].to_numpy(dtype=float), bins=24),
        },
        "branch_top_table": top_branch_table(branch_summary, limit=12),
        "branch_heatmap": feature_model_heatmap(branch_summary),
        "milestones": curated_milestones(),
        "worked_failed": worked_failed_cards(),
        "method_stack": method_stack(),
        "selected_notebooks": selected_notebooks(),
        "links": {
            "challenge_page": "https://challenge.ey.com/",
            "official_repo": "https://github.com/Snowflake-Labs/EY-AI-and-Data-Challenge",
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
