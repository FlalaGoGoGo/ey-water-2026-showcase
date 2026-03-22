from __future__ import annotations

import io
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SHOWCASE_JSON_PATH = ROOT / "docs/assets/data/showcase_data.json"
LEADERBOARD_PATH = WORKSPACE / "ey-water-2026/experiments/round_tracking/leaderboard_scores.csv"
BRANCH_SUMMARY_PATH = WORKSPACE / "ey-water-2026/experiments/outputs/branch_summary.csv"
TRAINING_DATASET_PATH = WORKSPACE / "ey-water-2026/EY-AI-and-Data-Challenge-main/water_quality_training_dataset.csv"
TRAINING_DATASET_URL = (
    "https://raw.githubusercontent.com/Snowflake-Labs/EY-AI-and-Data-Challenge/refs/heads/main/"
    "water_quality_training_dataset.csv"
)

PALETTE = {
    "ta": "#ffe600",
    "ec": "#ffd166",
    "drp": "#9cd18b",
}


def read_bytes(path: Path) -> bytes:
    fd = os.open(path, os.O_RDONLY)
    try:
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1 << 16)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(fd)
    return b"".join(chunks)



def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(read_bytes(path)))



def read_training_dataset() -> pd.DataFrame:
    if TRAINING_DATASET_PATH.exists():
        return read_csv(TRAINING_DATASET_PATH)
    with urlopen(TRAINING_DATASET_URL, timeout=30) as response:
        return pd.read_csv(io.BytesIO(response.read()))



def load_existing_showcase() -> dict[str, Any]:
    if SHOWCASE_JSON_PATH.exists():
        return json.loads(SHOWCASE_JSON_PATH.read_text(encoding="utf-8"))
    return {}



def parse_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, format="%d-%m-%Y", errors="coerce")



def histogram_payload(series: pd.Series, bins: int = 28) -> dict[str, list[float]]:
    values = series.dropna().astype(float).to_numpy()
    counts, edges = np.histogram(values, bins=bins)
    centers = ((edges[:-1] + edges[1:]) / 2).tolist()
    return {
        "centers": [round(float(value), 4) for value in centers],
        "counts": counts.astype(int).tolist(),
    }



def target_emphasis(row: pd.Series) -> str:
    scores = {
        "TA": float(row["r2_ta"]),
        "EC": float(row["r2_ec"]),
        "DRP": float(row["r2_drp"]),
    }
    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    if ordered[0][1] - ordered[1][1] < 0.025:
        return "Balanced"
    return ordered[0][0]



def strategy_label(row: pd.Series) -> str:
    missing = str(row["missing_strategy"]).replace("_", " ")
    outlier = str(row["outlier_strategy"]).replace("_", " ")
    return f"{missing} + {outlier}"



def submission_family(file_name: str, notes: str, round_number: int) -> str:
    text = f"{file_name} {notes}".lower()
    if "control" in text or "benchmark" in text or "replay" in text:
        return "Control anchor"
    if "power" in text or "chirps" in text:
        return "POWER / CHIRPS probes"
    if "hydro" in text or re.search(r"ta\d+_ec\d+", text):
        return "Hydro micro corridor"
    if "graph" in text or "remote" in text or "laplacian" in text or "corridor" in text:
        return "Graph / remote routing"
    if "weather" in text:
        return "Weather / EC route"
    if "ta_refine" in text or "taec" in text or "ta_drp" in text or "ta_plus" in text:
        return "TA refinement line"
    if round_number <= 2:
        return "Control anchor"
    if round_number <= 11:
        return "Weather / EC route"
    if round_number <= 20:
        return "TA refinement line"
    if round_number <= 32:
        return "Graph / remote routing"
    if round_number <= 42:
        return "Hydro micro corridor"
    return "POWER / CHIRPS probes"



def build_round_distribution(scoreboard: pd.DataFrame) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for round_number, frame in scoreboard.groupby("round", sort=True):
        scores = frame["score"].astype(float).tolist()
        payload.append(
            {
                "round": int(round_number),
                "scores": [round(float(score), 4) for score in scores],
                "best_score": round(float(np.max(scores)), 4),
                "mean_score": round(float(np.mean(scores)), 4),
                "median_score": round(float(np.median(scores)), 4),
                "worst_score": round(float(np.min(scores)), 4),
                "n_submissions": int(len(scores)),
            }
        )
    return payload



def build_leaderboard_by_round(scoreboard: pd.DataFrame) -> list[dict[str, Any]]:
    grouped = scoreboard.groupby("round", sort=True)["score"].agg(["max", "mean", "size"])
    return [
        {
            "round": int(round_number),
            "best_score": round(float(row["max"]), 4),
            "mean_score": round(float(row["mean"]), 4),
            "n_submissions": int(row["size"]),
        }
        for round_number, row in grouped.iterrows()
    ]



def build_selected_transitions(scoreboard: pd.DataFrame, milestones: list[dict[str, Any]]) -> list[dict[str, Any]]:
    milestone_lookup = {item["round"]: item for item in milestones}
    transition_rounds = [1, 2, 7, 15, 37, 46]
    rows: list[dict[str, Any]] = []
    for round_number in transition_rounds:
        frame = scoreboard.loc[scoreboard["round"] == round_number].copy()
        if frame.empty:
            continue
        best_row = frame.loc[frame["score"].idxmax()]
        meta = milestone_lookup.get(round_number, {})
        rows.append(
            {
                "round": int(round_number),
                "label": meta.get("title", f"Round {round_number}"),
                "phase": meta.get("phase", "Transition"),
                "best_score": round(float(frame["score"].max()), 4),
                "median_score": round(float(frame["score"].median()), 4),
                "worst_score": round(float(frame["score"].min()), 4),
                "best_file": str(best_row["file"]),
            }
        )
    return rows



def build_frontier_family_ranks(scoreboard: pd.DataFrame) -> list[dict[str, Any]]:
    selected_rounds = [1, 2, 7, 10, 15, 21, 27, 33, 37, 42, 44, 46]
    families = [
        "Control anchor",
        "Weather / EC route",
        "TA refinement line",
        "Graph / remote routing",
        "Hydro micro corridor",
        "POWER / CHIRPS probes",
    ]
    scoreboard = scoreboard.copy()
    scoreboard["family"] = [
        submission_family(file_name, notes, round_number)
        for file_name, notes, round_number in scoreboard[["file", "notes", "round"]].itertuples(index=False)
    ]
    frontier: list[dict[str, Any]] = []
    for round_number in selected_rounds:
        upto = scoreboard.loc[scoreboard["round"] <= round_number]
        family_scores = (
            upto.groupby("family", sort=False)["score"].max().reindex(families)
        )
        ranked = family_scores.dropna().sort_values(ascending=False)
        rank_lookup = {family: rank + 1 for rank, family in enumerate(ranked.index.tolist())}
        for family in families:
            score = family_scores.get(family)
            if pd.isna(score):
                continue
            frontier.append(
                {
                    "round": int(round_number),
                    "family": family,
                    "score": round(float(score), 4),
                    "rank": int(rank_lookup[family]),
                }
            )
    return frontier



def build_branch_dataset(
    branch_df: pd.DataFrame,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    data = branch_df.rename(
        columns={
            "r2_total_alkalinity": "r2_ta",
            "r2_electrical_conductance": "r2_ec",
        }
    ).copy()
    data["target_emphasis"] = data.apply(target_emphasis, axis=1)
    data["strategy_label"] = data.apply(strategy_label, axis=1)

    branch_scatter_points = [
        {
            "branch_id": row.branch_id,
            "feature_set": row.feature_set,
            "model_name": row.model_name,
            "missing_strategy": row.missing_strategy,
            "outlier_strategy": row.outlier_strategy,
            "strategy_label": row.strategy_label,
            "target_transform": row.target_transform,
            "target_emphasis": row.target_emphasis,
            "n_features": int(row.n_features),
            "r2_ta": round(float(row.r2_ta), 4),
            "r2_ec": round(float(row.r2_ec), 4),
            "r2_drp": round(float(row.r2_drp), 4),
            "r2_mean": round(float(row.r2_mean), 4),
        }
        for row in data.itertuples(index=False)
    ]

    family_aggregate = (
        data.groupby(["feature_set", "model_name", "strategy_label"], as_index=False)
        .agg(
            branch_count=("branch_id", "size"),
            mean_score=("r2_mean", "mean"),
            max_score=("r2_mean", "max"),
            avg_features=("n_features", "mean"),
        )
        .sort_values(["mean_score", "branch_count"], ascending=[False, False])
    )
    family_records = [
        {
            "feature_set": row.feature_set,
            "model_name": row.model_name,
            "strategy_label": row.strategy_label,
            "branch_count": int(row.branch_count),
            "mean_score": round(float(row.mean_score), 4),
            "max_score": round(float(row.max_score), 4),
            "avg_features": round(float(row.avg_features), 2),
        }
        for row in family_aggregate.itertuples(index=False)
    ]

    heatmap_grouped = (
        data.groupby(["feature_set", "model_name"], as_index=False)
        .agg(mean_score=("r2_mean", "mean"), branch_count=("branch_id", "size"))
    )
    model_order = (
        heatmap_grouped.groupby("model_name")["mean_score"].mean().sort_values(ascending=False).index.tolist()
    )
    feature_order = (
        heatmap_grouped.groupby("feature_set")["mean_score"].mean().sort_values(ascending=False).index.tolist()
    )
    value_lookup = {
        (row.feature_set, row.model_name): (round(float(row.mean_score), 4), int(row.branch_count))
        for row in heatmap_grouped.itertuples(index=False)
    }
    heatmap = {
        "feature_order": feature_order,
        "model_order": model_order,
        "values": [],
        "counts": [],
    }
    for feature in feature_order:
        row_values: list[float | None] = []
        row_counts: list[int] = []
        for model in model_order:
            if (feature, model) not in value_lookup:
                row_values.append(None)
                row_counts.append(0)
                continue
            mean_score, count = value_lookup[(feature, model)]
            row_values.append(mean_score)
            row_counts.append(count)
        heatmap["values"].append(row_values)
        heatmap["counts"].append(row_counts)

    target_summary = []
    for target_key, title, column, color in [
        ("TA", "Total Alkalinity", "r2_ta", PALETTE["ta"]),
        ("EC", "Electrical Conductance", "r2_ec", PALETTE["ec"]),
        ("DRP", "Dissolved Reactive Phosphorus", "r2_drp", PALETTE["drp"]),
    ]:
        series = data[column].astype(float)
        target_summary.append(
            {
                "target": target_key,
                "title": title,
                "color": color,
                "mean": round(float(series.mean()), 4),
                "median": round(float(series.median()), 4),
                "max": round(float(series.max()), 4),
                "p90": round(float(series.quantile(0.9)), 4),
                "positive_rate": round(float((series > 0).mean()), 4),
                "std": round(float(series.std(ddof=0)), 4),
                "values": [round(float(value), 4) for value in series.tolist()],
            }
        )

    top_table = (
        data.sort_values("r2_mean", ascending=False)
        .head(12)
        [[
            "branch_id",
            "feature_set",
            "model_name",
            "missing_strategy",
            "outlier_strategy",
            "target_transform",
            "n_features",
            "r2_mean",
            "r2_ta",
            "r2_ec",
            "r2_drp",
        ]]
    )
    top_table_records = [
        {
            "branch_id": row.branch_id,
            "feature_set": row.feature_set,
            "model_name": row.model_name,
            "missing_strategy": row.missing_strategy,
            "outlier_strategy": row.outlier_strategy,
            "target_transform": row.target_transform,
            "n_features": int(row.n_features),
            "r2_mean": round(float(row.r2_mean), 4),
            "r2_ta": round(float(row.r2_ta), 4),
            "r2_ec": round(float(row.r2_ec), 4),
            "r2_drp": round(float(row.r2_drp), 4),
        }
        for row in top_table.itertuples(index=False)
    ]

    return branch_scatter_points, family_records, heatmap, target_summary, top_table_records



def build_training_payload(training_df: pd.DataFrame) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    data = training_df.rename(
        columns={
            "Latitude": "lat",
            "Longitude": "lon",
            "Sample Date": "date",
            "Total Alkalinity": "total_alkalinity",
            "Electrical Conductance": "electrical_conductance",
            "Dissolved Reactive Phosphorus": "dissolved_reactive_phosphorus",
        }
    ).copy()
    data["date"] = parse_date(data["date"])

    training_map = (
        data.groupby(["lat", "lon"], as_index=False)
        .size()
        .rename(columns={"size": "samples"})
        .sort_values("samples", ascending=False)
    )
    training_map_records = [
        {
            "lat": round(float(row.lat), 6),
            "lon": round(float(row.lon), 6),
            "samples": int(row.samples),
        }
        for row in training_map.itertuples(index=False)
    ]

    target_distributions = {
        "total_alkalinity": histogram_payload(data["total_alkalinity"]),
        "electrical_conductance": histogram_payload(data["electrical_conductance"]),
        "dissolved_reactive_phosphorus": histogram_payload(data["dissolved_reactive_phosphorus"]),
    }

    summary = {
        "samples": int(len(data)),
        "unique_sites": int(data[["lat", "lon"]].drop_duplicates().shape[0]),
        "date_start": data["date"].min().strftime("%Y-%m-%d"),
        "date_end": data["date"].max().strftime("%Y-%m-%d"),
    }
    return training_map_records, target_distributions, summary



def build_strategy_filters(points: list[dict[str, Any]]) -> dict[str, list[str]]:
    features = sorted({row["feature_set"] for row in points})
    models = sorted({row["model_name"] for row in points})
    emphasis = ["Balanced", "TA", "EC", "DRP"]
    return {
        "feature_set": features,
        "model_name": models,
        "target_emphasis": emphasis,
    }



def main() -> None:
    existing = load_existing_showcase()
    scoreboard = read_csv(LEADERBOARD_PATH)
    branch_summary = read_csv(BRANCH_SUMMARY_PATH)
    training_df = read_training_dataset()

    training_map, target_distributions, training_summary = build_training_payload(training_df)
    round_distribution = build_round_distribution(scoreboard)
    leaderboard_by_round = build_leaderboard_by_round(scoreboard)

    branch_points, family_aggregate, branch_heatmap, target_difficulty_summary, branch_top_table = build_branch_dataset(
        branch_summary
    )

    milestones = existing.get("milestones", [])
    selected_transition_scores = build_selected_transitions(scoreboard, milestones)
    frontier_family_ranks = build_frontier_family_ranks(scoreboard)

    best_score = float(scoreboard["score"].max())
    summary = {
        "project_title": existing.get("summary", {}).get("project_title", "Optimizing Clean Water Supply"),
        "challenge_name": existing.get("summary", {}).get("challenge_name", "2026 EY AI & Data Challenge"),
        "tagline": existing.get("summary", {}).get(
            "tagline",
            "An independent team project exploring water-quality prediction, external data enrichment, and leaderboard-driven model iteration.",
        ),
        "best_score": round(best_score, 3),
        "official_rounds": int(scoreboard["round"].nunique()),
        "official_submissions": int(len(scoreboard)),
        "latest_round": int(scoreboard["round"].max()),
        "tracked_branch_notebooks": int(len(branch_summary)),
        "public_notebooks": int(len(existing.get("selected_notebooks", []))),
        **training_summary,
    }

    payload = {
        "summary": summary,
        "links": existing.get(
            "links",
            {
                "challenge_page": "https://challenge.ey.com/",
                "official_repo": "https://github.com/Snowflake-Labs/EY-AI-and-Data-Challenge",
            },
        ),
        "method_stack": existing.get("method_stack", []),
        "milestones": milestones,
        "worked_failed": existing.get("worked_failed", {"worked": [], "failed": []}),
        "selected_notebooks": existing.get("selected_notebooks", []),
        "frontier_methods": existing.get("frontier_methods", []),
        "leaderboard_by_round": leaderboard_by_round,
        "round_score_distribution": round_distribution,
        "selected_transition_scores": selected_transition_scores,
        "frontier_family_ranks": frontier_family_ranks,
        "training_map": training_map,
        "target_distributions": target_distributions,
        "target_difficulty_summary": target_difficulty_summary,
        "branch_scatter_points": branch_points,
        "family_aggregate": family_aggregate,
        "branch_heatmap": branch_heatmap,
        "branch_top_table": branch_top_table,
        "strategy_filters": build_strategy_filters(branch_points),
    }

    SHOWCASE_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {SHOWCASE_JSON_PATH}")


if __name__ == "__main__":
    main()
