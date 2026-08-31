import pandas as pd

from ml_pipeline.data_prep.features import build_project_period_features


def test_feature_engineering_flags_not_established_fields() -> None:
    projects = pd.DataFrame(
        [
            {
                "project_id": "p1",
                "sector": "Synthetic Sector A",
                "state": "Synthetic State A",
                "sanctioned_cost": 200.0,
                "approved_date": "2024-01-01",
            }
        ]
    )
    submissions = pd.DataFrame(
        [
            {
                "project_id": "p1",
                "reporting_month": "2024-02-01",
                "revised_cost": 210.0,
                "expenditure": 50.0,
                "physical_progress": 20.0,
                "planned_completion": "2025-01-01",
                "submitted_at": "2024-02-15T00:00:00Z",
            },
            {
                "project_id": "p1",
                "reporting_month": "2024-05-01",
                "revised_cost": 220.0,
                "expenditure": 90.0,
                "physical_progress": 42.0,
                "planned_completion": "2025-03-01",
                "submitted_at": "2024-05-16T00:00:00Z",
            },
        ]
    )

    result = build_project_period_features(projects, submissions)

    assert result.features.loc[0, "cost_overrun_ratio"] == 1.1
    assert "contractor_id_not_established" in result.features.loc[0, "feature_limitation_flags"]
    assert "thresholds_and_weights_proposed_pending_calibration" in result.limitation_flags[-1]
