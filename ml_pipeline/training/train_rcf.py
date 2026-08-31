from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from backend.app.services.rcf_engine import fit_reference_class, size_band_for_cost


def completed_reference_frame(projects: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    required_projects = {"project_id", "sector", "state", "sanctioned_cost"}
    required_labels = {"project_id", "cost_overrun_ratio", "schedule_delay_months"}
    missing = (required_projects - set(projects.columns)) | (required_labels - set(labels.columns))
    if missing:
        raise ValueError(f"Missing required RCF training columns: {sorted(missing)}")

    frame = projects.merge(labels, on="project_id", how="inner")
    frame["size_band"] = pd.to_numeric(frame["sanctioned_cost"], errors="coerce").apply(
        size_band_for_cost
    )
    frame["region"] = frame["state"]
    return frame[
        ["project_id", "sector", "size_band", "region", "cost_overrun_ratio", "schedule_delay_months"]
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Fit empirical reference-class forecast statistics.")
    parser.add_argument("--projects", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--sector", required=True)
    parser.add_argument("--size-band", required=True)
    parser.add_argument("--region", required=True)
    args = parser.parse_args()

    projects = pd.read_csv(args.projects)
    labels = pd.read_csv(args.labels)
    completed = completed_reference_frame(projects, labels)
    result = fit_reference_class(
        completed, sector=args.sector, size_band=args.size_band, region=args.region
    )
    print(result)


if __name__ == "__main__":
    main()
