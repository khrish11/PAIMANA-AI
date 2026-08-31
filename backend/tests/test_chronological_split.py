import pandas as pd

from ml_pipeline.training.splits import chronological_split


def test_chronological_split_preserves_time_order() -> None:
    frame = pd.DataFrame(
        {
            "approved_date": pd.date_range("2020-01-01", periods=10, freq="MS"),
            "value": range(10),
        }
    )

    split = chronological_split(frame, date_column="approved_date")

    assert len(split.train) == 6
    assert len(split.validation) == 2
    assert len(split.test) == 2
    assert split.train["approved_date"].max() < split.validation["approved_date"].min()
    assert split.validation["approved_date"].max() < split.test["approved_date"].min()
