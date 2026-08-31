from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ml_pipeline.training.evaluate import classification_metrics, side_by_side_table
from ml_pipeline.training.splits import chronological_split

NUMERIC_FEATURES = [
    "cost_overrun_ratio",
    "schedule_slip_months",
    "expenditure_to_progress_gap",
    "months_since_sanction",
    "progress_velocity_3m",
    "cost_revision_count",
    "reporting_lag_days",
]
CATEGORICAL_FEATURES = ["sector", "region", "size_band"]


def merge_features_and_labels(features: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    label_columns = ["project_id", "cost_overrun_gt_10", "schedule_delay_gt_6m"]
    missing = set(label_columns) - set(labels.columns)
    if missing:
        raise ValueError(
            "Supervised training requires audited completion labels; "
            f"missing label columns: {sorted(missing)}"
        )
    return features.merge(labels[label_columns], on="project_id", how="inner")


def sector_average_probability(train: pd.DataFrame, test: pd.DataFrame, label_column: str) -> pd.Series:
    global_rate = float(train[label_column].mean())
    sector_rates = train.groupby("sector")[label_column].mean()
    return test["sector"].map(sector_rates).fillna(global_rate).clip(0, 1)


def preprocessing_pipeline() -> ColumnTransformer:
    numeric = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric, NUMERIC_FEATURES),
            ("categorical", categorical, CATEGORICAL_FEATURES),
        ]
    )


def train_baselines(
    dataset: pd.DataFrame,
    *,
    label_column: str = "cost_overrun_gt_10",
) -> pd.DataFrame:
    split = chronological_split(dataset, date_column="approved_date")
    metrics = []

    naive_probability = sector_average_probability(split.train, split.test, label_column)
    metrics.append(
        classification_metrics(
            "Naive baseline (sector avg)",
            split.test[label_column],
            naive_probability,
            notes="Lower bound; development-only if synthetic labels are used.",
        )
    )

    model = Pipeline(
        steps=[
            ("preprocess", preprocessing_pipeline()),
            ("model", LogisticRegression(max_iter=1000)),
        ]
    )
    model.fit(split.train[NUMERIC_FEATURES + CATEGORICAL_FEATURES], split.train[label_column])
    logistic_probability = model.predict_proba(
        split.test[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    )[:, 1]
    metrics.append(
        classification_metrics(
            "Logistic Regression",
            split.test[label_column],
            logistic_probability,
            notes="Statistical baseline; fit only on chronological training split.",
        )
    )

    return side_by_side_table(metrics)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train PAIMANA-AI baseline classifiers.")
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--label-column", default="cost_overrun_gt_10")
    args = parser.parse_args()

    features = pd.read_csv(args.features)
    labels = pd.read_csv(args.labels)
    dataset = merge_features_and_labels(features, labels)
    table = train_baselines(dataset, label_column=args.label_column)
    print(table.to_string(index=False))
    print("All metrics are proposed pending calibration on audited real PAIMANA/OCMS data.")


if __name__ == "__main__":
    main()
