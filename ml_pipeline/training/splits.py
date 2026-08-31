from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ChronologicalSplit:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def chronological_split(
    frame: pd.DataFrame,
    *,
    date_column: str = "approved_date",
    train_fraction: float = 0.60,
    validation_fraction: float = 0.20,
) -> ChronologicalSplit:
    if date_column not in frame.columns:
        raise ValueError(f"Missing chronological split column: {date_column}")
    if not 0 < train_fraction < 1 or not 0 < validation_fraction < 1:
        raise ValueError("Split fractions must be between 0 and 1")
    if train_fraction + validation_fraction >= 1:
        raise ValueError("Train plus validation fractions must leave a non-empty test fraction")
    if len(frame) < 5:
        raise ValueError("At least 5 rows are required for chronological train/validation/test split")

    ordered = frame.copy()
    ordered[date_column] = pd.to_datetime(ordered[date_column], errors="coerce")
    if ordered[date_column].isna().any():
        raise ValueError(f"Column {date_column} contains invalid dates")

    ordered = ordered.sort_values(date_column).reset_index(drop=True)
    train_end = max(1, int(len(ordered) * train_fraction))
    validation_end = max(train_end + 1, int(len(ordered) * (train_fraction + validation_fraction)))
    validation_end = min(validation_end, len(ordered) - 1)

    return ChronologicalSplit(
        train=ordered.iloc[:train_end].copy(),
        validation=ordered.iloc[train_end:validation_end].copy(),
        test=ordered.iloc[validation_end:].copy(),
    )
