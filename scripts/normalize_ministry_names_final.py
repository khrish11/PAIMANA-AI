import pandas as pd
import json
import re

# Load agency-ministry mapping
with open('data/validation/agency_ministry_mapping.json', 'r') as f:
    agency_ministry = json.load(f)

# Load ministry-sector mapping
with open('data/validation/ministry_sector_mapping.json', 'r') as f:
    ministry_sector = json.load(f)

# Define canonical ministry name normalization rules
ministry_normalization = {
    'Ministry of Road Transport & Highways': 'Ministry of Road Transport & Highways',
    'MoRTH': 'Ministry of Road Transport & Highways',
    
    'Ministry of Railways': 'Ministry of Railways',
    
    'Ministry of Coal': 'Ministry of Coal',
    
    'Ministry of Power': 'Ministry of Power',
    
    'Ministry of Petroleum & Natural Gas': 'Ministry of Petroleum & Natural Gas',
    'Ministry of Petroleum and Natural Gas': 'Ministry of Petroleum & Natural Gas',
    'Ministry of Petroleum': 'Ministry of Petroleum & Natural Gas',
    
    'Ministry of Civil Aviation': 'Ministry of Civil Aviation',
    
    'Ministry of Housing & Urban Affairs': 'Ministry of Housing & Urban Affairs',
    'Ministry of Housing and Urban Affairs': 'Ministry of Housing & Urban Affairs',
    'Ministry of Housing': 'Ministry of Housing & Urban Affairs',
    
    'Ministry of Steel': 'Ministry of Steel',
    
    'Ministry of Health & Family Welfare': 'Ministry of Health & Family Welfare',
    'Ministry of Health and Family Welfare': 'Ministry of Health & Family Welfare',
    'Ministry of Health': 'Ministry of Health & Family Welfare',
    
    'Department of Telecommunications': 'Department of Telecommunications',
    'Department of Telecommunications [DoT]': 'Department of Telecommunications',
    
    'Department of Water Resources, River Development & GR': 'Department of Water Resources, River Development & GR',
    'Department of Water Resources, River Development': 'Department of Water Resources, River Development & GR',
    'Department of Water Resources': 'Department of Water Resources, River Development & GR',
    
    'Department of Sports': 'Department of Sports',
    
    'Department of Higher Education': 'Department of Higher Education',
    
    'Ministry of Mines': 'Ministry of Mines',
    
    'Department for Promotion of Industry & Internal Trade': 'Department for Promotion of Industry & Internal Trade',
    
    'Ministry of Education': 'Ministry of Education',
}

def clean_ministry_name(ministry):
    """Aggressively clean ministry name by removing all artifacts"""
    if not ministry:
        return None
    
    ministry_str = str(ministry).strip()
    
    # Remove all trailing artifacts in sequence
    # 1. Remove patterns like "-) (", "-) :", "N06000245) (", etc.
    ministry_str = re.sub(r'\s*-\s*\)\s*\(\s*$', '', ministry_str)
    ministry_str = re.sub(r'\s*-\s*\)\s*\(\s*:', '', ministry_str)
    # 2. Remove patterns like "-) ("
    ministry_str = re.sub(r'\s*-\s*\)\s*\(\s*', '', ministry_str)
    # 3. Remove patterns like "-) :"
    ministry_str = re.sub(r'\s*-\s*\)\s*:\s*', '', ministry_str)
    # 4. Remove patterns like "-) (-"
    ministry_str = re.sub(r'\s*-\s*\)\s*\(\s*-', '', ministry_str)
    # 5. Remove trailing dash
    ministry_str = re.sub(r'\s*-\s*$', '', ministry_str)
    # 6. Remove trailing N followed by numbers and optional parentheses
    ministry_str = re.sub(r'\s*N\d+\)?\s*$', '', ministry_str)
    # 7. Remove trailing parentheses with numbers
    ministry_str = re.sub(r'\s*\(\d+\)\s*$', '', ministry_str)
    # 8. Remove trailing colon
    ministry_str = re.sub(r'\s*:\s*$', '', ministry_str)
    # 9. Remove any remaining trailing parentheses
    ministry_str = re.sub(r'\s*\)\s*$', '', ministry_str)
    # 10. Remove trailing dash with optional colon
    ministry_str = re.sub(r'\s*-\s*\)?\s*$', '', ministry_str)
    
    ministry_str = ministry_str.strip()
    return ministry_str

def normalize_ministry(ministry):
    if not ministry:
        return None
    
    ministry_str = clean_ministry_name(ministry)
    
    if not ministry_str:
        return None
    
    # Look up in normalization table (case-insensitive)
    for variant, canonical in ministry_normalization.items():
        if variant.lower() == ministry_str.lower():
            return canonical
    
    # If not found, try partial matching for ministry names
    if 'ministry of' in ministry_str.lower():
        # Extract the ministry name
        match = re.search(r'ministry of (.+)', ministry_str, re.IGNORECASE)
        if match:
            ministry_name = match.group(1).strip()
            # Check against known ministries
            for variant, canonical in ministry_normalization.items():
                if canonical.lower().startswith('ministry of') and ministry_name.lower() in canonical.lower():
                    return canonical
    
    if 'department of' in ministry_str.lower():
        # Extract the department name
        match = re.search(r'department of (.+)', ministry_str, re.IGNORECASE)
        if match:
            dept_name = match.group(1).strip()
            # Check against known departments
            for variant, canonical in ministry_normalization.items():
                if canonical.lower().startswith('department of') and dept_name.lower() in canonical.lower():
                    return canonical
    
    # If still not found, return cleaned original
    return ministry_str

# Normalize agency-ministry mapping
canonical_agency_ministry = {}
for agency, ministry in agency_ministry.items():
    canonical_ministry = normalize_ministry(ministry)
    if canonical_ministry:
        canonical_agency_ministry[agency] = canonical_ministry

# Count normalized ministries
from collections import Counter
ministry_counts = Counter(canonical_agency_ministry.values())
print(f"Normalized {len(canonical_agency_ministry)} agency-ministry mappings")
print(f"\nCanonical ministries (top 20):")
for ministry, count in sorted(ministry_counts.items(), key=lambda x: -x[1])[:20]:
    print(f"  {ministry}: {count}")

# Check for remaining unmapped or poorly normalized ministries
unmapped = [m for m in ministry_counts.keys() if m not in ministry_normalization.values()]
if unmapped:
    print(f"\n{len(unmapped)} ministries not in canonical list:")
    for m in unmapped[:20]:
        print(f"  {m}: {ministry_counts[m]}")
else:
    print(f"\nAll ministries successfully normalized to canonical list!")

# Save canonical agency-ministry mapping
json_file = 'data/validation/agency_ministry_mapping_canonical.json'
with open(json_file, 'w') as f:
    json.dump(canonical_agency_ministry, f, indent=2)
print(f"\nSaved canonical agency-ministry mapping to {json_file}")

# Create combined agency → ministry → sector mapping
combined_mapping = {}
for agency, ministry in canonical_agency_ministry.items():
    sectors = ministry_sector.get(ministry, [])
    combined_mapping[agency] = {
        'ministry': ministry,
        'sectors': sectors
    }

# Save combined mapping
combined_file = 'data/validation/agency_ministry_sector_mapping.json'
with open(combined_file, 'w') as f:
    json.dump(combined_mapping, f, indent=2)
print(f"Saved combined agency-ministry-sector mapping to {combined_file}")

# Show sample mappings
print(f"\nSample combined mappings:")
for i, (agency, mapping) in enumerate(list(combined_mapping.items())[:10]):
    print(f"  {agency}: {mapping['ministry']} → {', '.join(mapping['sectors'])}")
