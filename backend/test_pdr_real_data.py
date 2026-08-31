"""Test PDR with real PostgreSQL data."""

from app.services.positive_deviance import PositiveDevianceDetector


def test_pdr_real_data():
    """Verify PDR uses real PostgreSQL data with no synthetic fallback."""
    print("=" * 80)
    print("PDR REAL DATA TEST")
    print("=" * 80)
    
    detector = PositiveDevianceDetector()
    
    # Test batch_detect
    print("\n1. Testing batch_detect with real database...")
    result = detector.batch_detect(limit=10)
    
    print(f"Total positive deviants found: {result['metadata'].get('total_count', 0)}")
    print(f"Returned: {len(result.get('positive_deviants', []))}")
    print(f"Data source: {result['metadata'].get('data_source')}")
    
    if result['metadata'].get('data_source') == 'REAL_PAIMANA':
        print(f"  ✅ PASSED: Data source is REAL_PAIMANA")
    else:
        print(f"  ❌ FAILED: Data source is {result['metadata'].get('data_source')}")
    
    # Check for synthetic entities in results
    print(f"\nChecking for synthetic entities in results...")
    synthetic_found = False
    for deviant in result.get('positive_deviants', []):
        if 'synthetic' in str(deviant.get('project_id', '')).lower():
            synthetic_found = True
            print(f"  ❌ FAILED: Found synthetic project ID: {deviant['project_id']}")
    
    if not synthetic_found:
        print(f"  ✅ PASSED: No synthetic project IDs found")
    
    # Test with filters
    print(f"\n2. Testing with sector filter...")
    result_filtered = detector.batch_detect(limit=10, sector="Railways")
    print(f"Total with sector filter: {result_filtered['metadata'].get('total_count', 0)}")
    print(f"Data source: {result_filtered['metadata'].get('data_source')}")
    
    print("\n" + "=" * 80)
    print("PDR TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_pdr_real_data()
