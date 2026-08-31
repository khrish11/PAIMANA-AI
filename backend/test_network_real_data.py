"""Test network intelligence with real PostgreSQL data."""

from app.services.network_intelligence import build_project_network, calculate_blast_radius


def test_network_real_data():
    """Verify network uses real PostgreSQL data with no synthetic entities."""
    print("=" * 80)
    print("NETWORK INTELLIGENCE REAL DATA TEST")
    print("=" * 80)
    
    # Test 1: Build full network
    print("\n1. Testing full network build...")
    network = build_project_network()
    
    print(f"Network available: {network.available}")
    print(f"Message: {network.message}")
    print(f"Total nodes: {len(network.nodes)}")
    print(f"Total edges: {len(network.edges)}")
    
    if network.available:
        print(f"\nMetadata:")
        for key, value in network.metadata.items():
            print(f"  {key}: {value}")
        
        # Check for synthetic entities
        print(f"\nChecking for synthetic entities...")
        synthetic_nodes = [n for n in network.nodes if 'synthetic' in n.id.lower()]
        if synthetic_nodes:
            print(f"  ❌ FAILED: Found {len(synthetic_nodes)} synthetic nodes")
            for node in synthetic_nodes[:5]:
                print(f"    - {node.id}")
        else:
            print(f"  ✅ PASSED: No synthetic nodes found")
        
        # Check data source metadata
        if network.metadata.get('data_source') == 'REAL_PAIMANA':
            print(f"  ✅ PASSED: Data source is REAL_PAIMANA")
        else:
            print(f"  ❌ FAILED: Data source is {network.metadata.get('data_source')}")
    
    # Test 2: Build focused network for a specific project
    print(f"\n2. Testing focused network for a project...")
    # Get a sample project ID from the network
    if network.available and network.nodes:
        sample_project = next((n for n in network.nodes if n.node_type == "PROJECT"), None)
        if sample_project:
            focused_network = build_project_network(sample_project.id)
            print(f"Focused network available: {focused_network.available}")
            print(f"Focused nodes: {len(focused_network.nodes)}")
            print(f"Focused edges: {len(focused_network.edges)}")
            
            # Check for synthetic entities in focused network
            synthetic_nodes = [n for n in focused_network.nodes if 'synthetic' in n.id.lower()]
            if synthetic_nodes:
                print(f"  ❌ FAILED: Found {len(synthetic_nodes)} synthetic nodes in focused network")
            else:
                print(f"  ✅ PASSED: No synthetic nodes in focused network")
    
    # Test 3: Blast radius calculation
    print(f"\n3. Testing blast radius calculation...")
    if network.available and network.nodes:
        sample_project = next((n for n in network.nodes if n.node_type == "PROJECT"), None)
        if sample_project:
            blast_radius = calculate_blast_radius(sample_project.id, depth=1)
            print(f"Blast radius available: {blast_radius.get('available')}")
            print(f"Affected nodes: {len(blast_radius.get('affected_nodes', []))}")
            print(f"Affected projects: {len(blast_radius.get('affected_projects', []))}")
            
            if blast_radius.get('available'):
                # Check for synthetic entities
                synthetic_in_blast = [n for n in blast_radius.get('affected_nodes', []) if 'synthetic' in str(n).lower()]
                if synthetic_in_blast:
                    print(f"  ❌ FAILED: Found synthetic entities in blast radius")
                else:
                    print(f"  ✅ PASSED: No synthetic entities in blast radius")
    
    print("\n" + "=" * 80)
    print("NETWORK TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_network_real_data()
