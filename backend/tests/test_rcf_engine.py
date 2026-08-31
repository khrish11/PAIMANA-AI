import pandas as pd

from app.services.rcf_engine import fit_reference_class


def test_rcf_uses_national_sector_fallback_below_minimum_cluster_size() -> None:
    completed = pd.DataFrame(
        [
            {
                "sector": "Synthetic Sector A",
                "size_band": "150-500 Cr",
                "region": "Synthetic State A" if index < 4 else "Synthetic State B",
                "cost_overrun_ratio": index / 100,
                "schedule_delay_months": index,
            }
            for index in range(20)
        ]
    )

    result = fit_reference_class(
        completed,
        sector="Synthetic Sector A",
        size_band="150-500 Cr",
        region="Synthetic State A",
    )

    assert result.used_fallback is True
    assert result.sample_count == 20
    assert result.warning is not None
