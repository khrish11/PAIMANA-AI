from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from ml_pipeline.training.evaluate import classification_metrics, side_by_side_table
from ml_pipeline.training.splits import chronological_split
from ml_pipeline.training.train_baseline import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    merge_features_and_labels,
    preprocessing_pipeline,
    sector_average_probability,
)


def _optional_xgboost():
    try:
        from xgboost import XGBClassifier
    except ImportError:
        return None
    return XGBClassifier


def _optional_lightgbm():
    try:
        from lightgbm import LGBMClassifier
    except ImportError:
        return None
    return LGBMClassifier


def train_ensemble_candidates(
    dataset: pd.DataFrame,
    *,
    label_column: str = "cost_overrun_gt_10",
) -> pd.DataFrame:
    split = chronological_split(dataset, date_column="approved_date")
    feature_columns = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    metrics = [
        classification_metrics(
            "Naive baseline (sector avg)",
            split.test[label_column],
            sector_average_probability(split.train, split.test, label_column),
            notes="Always reported beside ensemble models.",
        )
    ]

    candidates: list[tuple[str, object, str]] = [
        (
            "Random Forest",
            RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=20260828),
            "Primary ensemble; random_state affects model bootstrap only, not data split.",
        )
    ]

    xgb_classifier = _optional_xgboost()
    if xgb_classifier is not None:
        candidates.append(
            (
                "XGBoost",
                xgb_classifier(
                    n_estimators=200,
                    eval_metric="logloss",
                    learning_rate=0.05,
                    max_depth=3,
                    random_state=20260828,
                ),
                "Primary ensemble candidate; hyperparameters are proposed pending Optuna tuning.",
            )
        )

    lgbm_classifier = _optional_lightgbm()
    if lgbm_classifier is not None:
        candidates.append(
            (
                "LightGBM",
                lgbm_classifier(
                    n_estimators=200,
                    learning_rate=0.05,
                    random_state=20260828,
                    verbose=-1,
                ),
                "Primary ensemble candidate; hyperparameters are proposed pending Optuna tuning.",
            )
        )

    for name, estimator, notes in candidates:
        model = Pipeline(steps=[("preprocess", preprocessing_pipeline()), ("model", estimator)])
        model.fit(split.train[feature_columns], split.train[label_column])
        probability = model.predict_proba(split.test[feature_columns])[:, 1]
        metrics.append(
            classification_metrics(name, split.test[label_column], probability, notes=notes)
        )

    return side_by_side_table(metrics)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train PAIMANA-AI ensemble candidates.")
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--label-column", default="cost_overrun_gt_10")
    args = parser.parse_args()

    features = pd.read_csv(args.features)
    labels = pd.read_csv(args.labels)
    dataset = merge_features_and_labels(features, labels)
    table = train_ensemble_candidates(dataset, label_column=args.label_column)
    print(table.to_string(index=False))
    print("Metrics are development-only when run on synthetic labels.")


if __name__ == "__main__":
    main()
