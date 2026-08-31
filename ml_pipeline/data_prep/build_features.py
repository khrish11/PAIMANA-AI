from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from ml_pipeline.data_prep.features import build_project_period_features


def main() -> None:
    parser = argparse.ArgumentParser(description="Build PAIMANA-AI feature rows from project/CUF CSVs.")
    parser.add_argument("--projects", type=Path, required=True)
    parser.add_argument("--submissions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metadata", type=Path)
    args = parser.parse_args()

    projects = pd.read_csv(args.projects)
    submissions = pd.read_csv(args.submissions)
    result = build_project_period_features(projects, submissions)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.features.to_csv(args.output, index=False)

    if args.metadata:
        args.metadata.parent.mkdir(parents=True, exist_ok=True)
        args.metadata.write_text(
            json.dumps({"limitation_flags": result.limitation_flags}, indent=2),
            encoding="utf-8",
        )

    print(f"Wrote {len(result.features)} feature rows to {args.output}")
    print("Thresholds, weights, and metrics remain proposed pending calibration on real data.")


if __name__ == "__main__":
    main()
