from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass(frozen=True)
class ClassificationMetrics:
    model: str
    auc_roc: float | None
    auc_pr: float | None
    recall: float
    precision: float
    f1: float
    brier_score: float
    notes: str


def classification_metrics(
    model_name: str,
    y_true: pd.Series | np.ndarray,
    y_probability: pd.Series | np.ndarray,
    *,
    notes: str,
    threshold: float = 0.5,
) -> ClassificationMetrics:
    y_true_array = np.asarray(y_true).astype(int)
    probability = np.asarray(y_probability).astype(float)
    prediction = (probability >= threshold).astype(int)

    auc_roc = None
    auc_pr = None
    if len(set(y_true_array.tolist())) == 2:
        auc_roc = float(roc_auc_score(y_true_array, probability))
        auc_pr = float(average_precision_score(y_true_array, probability))

    return ClassificationMetrics(
        model=model_name,
        auc_roc=auc_roc,
        auc_pr=auc_pr,
        recall=float(recall_score(y_true_array, prediction, zero_division=0)),
        precision=float(precision_score(y_true_array, prediction, zero_division=0)),
        f1=float(f1_score(y_true_array, prediction, zero_division=0)),
        brier_score=float(brier_score_loss(y_true_array, probability)),
        notes=notes,
    )


def side_by_side_table(metrics: list[ClassificationMetrics]) -> pd.DataFrame:
    rows = []
    for item in metrics:
        rows.append(
            {
                "Model": item.model,
                "AUC-ROC": item.auc_roc,
                "AUC-PR": item.auc_pr,
                "Recall": item.recall,
                "Precision": item.precision,
                "F1 (0.5 threshold)": item.f1,
                "Brier Score": item.brier_score,
                "Notes": item.notes,
            }
        )
    return pd.DataFrame(rows)
