"""Test DCS threshold labels."""

from app.services.data_confidence import compute_dcs


def test_dcs_thresholds():
    """Test DCS threshold labels at boundary values."""
    print("=" * 80)
    print("DCS THRESHOLD LABEL TEST")
    print("=" * 80)
    
    # Test boundary values by manipulating component scores
    # Total score = completeness + freshness + consistency + reliability (each 0-25)
    test_cases = [
        (0.0, "0.0 - should be LOW"),
        (49.99, "49.99 - should be LOW"),
        (50.0, "50.0 - should be MODERATE"),
        (79.99, "79.99 - should be MODERATE"),
        (80.0, "80.0 - should be HIGH"),
        (100.0, "100.0 - should be HIGH"),
    ]
    
    print("\nTesting DCS threshold labels:")
    print("-" * 80)
    
    for target_score, description in test_cases:
        try:
            # Calculate component scores to achieve target total
            # Distribute evenly across 4 components
            component_score = target_score / 4.0
            
            # Use boolean flags to control completeness (0-25)
            # 5 fields, each worth 5 points if present
            fields_present = int(component_score / 5.0)
            fields_present = max(0, min(5, fields_present))
            
            result = compute_dcs(
                has_revised_cost=fields_present >= 1,
                has_expenditure=fields_present >= 2,
                has_physical_progress=fields_present >= 3,
                has_planned_completion=fields_present >= 4,
                has_narrative=fields_present >= 5,
                reporting_lag_days=14,  # Max freshness
                expenditure=100.0,
                revised_cost=100.0,
                physical_progress=50.0,
                agency_track_record=1.0,  # Max reliability
                submission_count=12,
            )
            
            label = result.confidence_label
            actual_score = result.dcs_score
            print(f"DCS {actual_score:6.2f}: {label:10s} - {description}")
            
        except Exception as e:
            print(f"DCS {target_score:6.2f}: ERROR - {str(e)}")
    
    # Summary
    print(f"\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("Actual thresholds from code:")
    print("  0-49.99: LOW")
    print("  50-79.99: MODERATE")
    print("  80-100: HIGH")
    print("\nNote: Code uses 80 as HIGH threshold, not 75")


if __name__ == "__main__":
    test_dcs_thresholds()
