from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from backend.app.services.rcf_engine import size_band_for_cost


@dataclass(frozen=True)
class FeatureBuildResult:
    features: pd.DataFrame
    limitation_flags: list[str]


def _months_between(start: pd.Series, end: pd.Series) -> pd.Series:
    return (end.dt.year - start.dt.year) * 12 + (end.dt.month - start.dt.month)


def _coerce_dates(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = frame.copy()
    for column in columns:
        if column in result.columns:
            result[column] = pd.to_datetime(result[column], errors="coerce", utc=True).dt.tz_convert(
                None
            )
    return result


def build_project_period_features(
    projects: pd.DataFrame,
    submissions: pd.DataFrame,
    *,
    as_of_month: date | None = None,
) -> FeatureBuildResult:
    required_projects = {"project_id", "sector", "state", "sanctioned_cost", "approved_date"}
    required_submissions = {
        "project_id",
        "reporting_month",
        "revised_cost",
        "expenditure",
        "physical_progress",
        "planned_completion",
        "submitted_at",
    }
    missing = (required_projects - set(projects.columns)) | (
        required_submissions - set(submissions.columns)
    )
    if missing:
        raise ValueError(f"Missing required feature columns: {sorted(missing)}")

    limitation_flags = [
        "actual_final_cost_not_established_supervised_labels_required_for_real_training",
        "actual_completion_date_not_established_schedule_labels_required_for_real_training",
        "contractor_id_not_established_pbe_or_blast_radius_must_flag_missing_relationships",
        "land_acquisition_status_not_established_no_direct_land_feature_assumed",
        "thresholds_and_weights_proposed_pending_calibration_on_real_data",
    ]

    projects = _coerce_dates(projects, ["approved_date"])
    submissions = _coerce_dates(submissions, ["reporting_month", "planned_completion", "submitted_at"])
    submissions = submissions.sort_values(["project_id", "reporting_month", "submitted_at"])

    if as_of_month is not None:
        submissions = submissions[submissions["reporting_month"].dt.date <= as_of_month]

    latest = submissions.groupby("project_id", as_index=False).tail(1)
    first_completion = (
        submissions.groupby("project_id", as_index=False)["planned_completion"]
        .first()
        .rename(columns={"planned_completion": "baseline_planned_completion"})
    )

    merged = (
        projects.merge(latest, on="project_id", how="inner", suffixes=("", "_submission"))
        .merge(first_completion, on="project_id", how="left")
        .copy()
    )

    merged["sanctioned_cost"] = pd.to_numeric(merged["sanctioned_cost"], errors="coerce")
    merged["revised_cost"] = pd.to_numeric(merged["revised_cost"], errors="coerce")
    merged["expenditure"] = pd.to_numeric(merged["expenditure"], errors="coerce")
    merged["physical_progress"] = pd.to_numeric(merged["physical_progress"], errors="coerce")

    merged["size_band"] = merged["sanctioned_cost"].apply(size_band_for_cost)
    merged["region"] = merged["state"]
    merged["cost_overrun_ratio"] = merged["revised_cost"] / merged["sanctioned_cost"]
    merged["schedule_slip_months"] = _months_between(
        merged["baseline_planned_completion"], merged["planned_completion"]
    )
    merged["expenditure_to_progress_gap"] = (merged["expenditure"] / merged["revised_cost"]) - (
        merged["physical_progress"] / 100
    )
    merged["months_since_sanction"] = _months_between(
        merged["approved_date"], merged["reporting_month"]
    )

    prior = submissions.copy()
    prior["physical_progress"] = pd.to_numeric(prior["physical_progress"], errors="coerce")
    prior["progress_3m_ago"] = prior.groupby("project_id")["physical_progress"].shift(3)
    velocity = prior.groupby("project_id", as_index=False).tail(1)[
        ["project_id", "progress_3m_ago", "physical_progress"]
    ]
    velocity["progress_velocity_3m"] = (
        velocity["physical_progress"] - velocity["progress_3m_ago"]
    ) / 3
    merged = merged.merge(velocity[["project_id", "progress_velocity_3m"]], on="project_id", how="left")

    cost_revision_count = (
        submissions.assign(revised_cost_numeric=pd.to_numeric(submissions["revised_cost"], errors="coerce"))
        .groupby("project_id")["revised_cost_numeric"]
        .nunique()
        .rename("cost_revision_count")
        .reset_index()
    )
    merged = merged.merge(cost_revision_count, on="project_id", how="left")

    merged["agency_track_record"] = pd.NA
    merged["nqc_score"] = pd.NA
    merged["ppi_percentile"] = pd.NA
    merged["reporting_lag_days"] = (
        merged["submitted_at"].dt.normalize() - merged["reporting_month"]
    ).dt.days
    merged["feature_limitation_flags"] = ";".join(limitation_flags)

    columns = [
        "project_id",
        "sector",
        "region",
        "size_band",
        "approved_date",
        "reporting_month",
        "cost_overrun_ratio",
        "schedule_slip_months",
        "expenditure_to_progress_gap",
        "months_since_sanction",
        "progress_velocity_3m",
        "cost_revision_count",
        "agency_track_record",
        "nqc_score",
        "ppi_percentile",
        "reporting_lag_days",
        "feature_limitation_flags",
    ]
    return FeatureBuildResult(features=merged[columns], limitation_flags=limitation_flags)
