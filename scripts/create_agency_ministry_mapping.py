import pandas as pd
import re

# Load agency analysis
df = pd.read_csv('data/validation/agency_analysis.csv')

# Define agency-to-ministry mapping rules
# Based on known agency classifications
agency_ministry_rules = {
    # Ministry of Road Transport & Highways (MoRTH)
    'NHIDCL': 'Ministry of Road Transport & Highways',
    'NHAI': 'Ministry of Road Transport & Highways',
    'National Highways Authority of India': 'Ministry of Road Transport & Highways',
    'MoRTH': 'Ministry of Road Transport & Highways',
    'RVNL': 'Ministry of Railways',  # Rail Vikas Nigam Limited
    
    # Ministry of Railways
    'Railway': 'Ministry of Railways',
    'ECoR': 'Ministry of Railways',
    'SCR': 'Ministry of Railways',
    'ECR': 'Ministry of Railways',
    'NWR': 'Ministry of Railways',
    'SWR': 'Ministry of Railways',
    'NFR': 'Ministry of Railways',
    'SECR': 'Ministry of Railways',
    'IRCON': 'Ministry of Railways',
    
    # Ministry of Power
    'POWERGRID': 'Ministry of Power',
    'Power Grid Corporation': 'Ministry of Power',
    'NHPC': 'Ministry of Power',
    'NTPC': 'Ministry of Power',
    'NLCIL': 'Ministry of Power',
    
    # Ministry of Coal
    'Coal': 'Ministry of Coal',
    'WCL': 'Ministry of Coal',
    'SECL': 'Ministry of Coal',
    'ECL': 'Ministry of Coal',
    'CIL': 'Ministry of Coal',
    'SCCL': 'Ministry of Coal',
    
    # Ministry of Petroleum & Natural Gas
    'ONGC': 'Ministry of Petroleum & Natural Gas',
    'BPCL': 'Ministry of Petroleum & Natural Gas',
    'HPCL': 'Ministry of Petroleum & Natural Gas',
    'GAIL': 'Ministry of Petroleum & Natural Gas',
    'IOCL': 'Ministry of Petroleum & Natural Gas',
    
    # Ministry of Steel
    'SAIL': 'Ministry of Steel',
    
    # Ministry of Civil Aviation
    'AAI': 'Ministry of Civil Aviation',
    'Airport Authority': 'Ministry of Civil Aviation',
    
    # Ministry of Health & Family Welfare
    'ESIC': 'Ministry of Health & Family Welfare',
    'Medical Education': 'Ministry of Health & Family Welfare',
    
    # Ministry of Housing & Urban Affairs
    'CPWD': 'Ministry of Housing & Urban Affairs',
    'NBCC': 'Ministry of Housing & Urban Affairs',
    
    # Department of Telecommunications
    'DoT': 'Department of Telecommunications',
    'BSNL': 'Department of Telecommunications',
    'MTNL': 'Department of Telecommunications',
}

def map_agency_to_ministry(agency):
    if pd.isna(agency) or agency == 'Unknown':
        return None
    
    agency_str = str(agency).strip()
    
    # Check if agency already contains a ministry name
    if 'Ministry of' in agency_str or 'Department of' in agency_str:
        # Extract the ministry name
        # Pattern: "Ministry of X" or "Department of X"
        match = re.search(r'(Ministry of [^&]+|Department of [^&]+)', agency_str)
        if match:
            ministry = match.group(1).strip()
            # Clean up trailing characters
            ministry = re.sub(r'\s*[-)]\s*\([^)]*\)\s*$', '', ministry)
            ministry = ministry.strip()
            return ministry
    
    # Check against known agency rules
    for pattern, ministry in agency_ministry_rules.items():
        if pattern in agency_str:
            return ministry
    
    return None

# Apply mapping
df['mapped_ministry'] = df['clean_agency'].apply(map_agency_to_ministry)

# Count mappings
mapped_count = df['mapped_ministry'].notna().sum()
total_count = len(df)
print(f"Mapped {mapped_count} out of {total_count} agencies ({mapped_count/total_count*100:.1f}%)")

# Show distribution of mapped ministries
ministry_counts = df['mapped_ministry'].value_counts()
print(f"\nMapped ministries:")
for ministry, count in ministry_counts.items():
    print(f"  {ministry}: {count}")

# Save mapping
output_file = 'data/validation/agency_ministry_mapping.csv'
df[['project_id', 'agency', 'clean_agency', 'mapped_ministry']].to_csv(output_file, index=False)
print(f"\nSaved agency-ministry mapping to {output_file}")

# Create a simple lookup dictionary
lookup_dict = {}
for _, row in df[df['mapped_ministry'].notna()].iterrows():
    agency = row['clean_agency']
    ministry = row['mapped_ministry']
    if agency not in lookup_dict:
        lookup_dict[agency] = ministry

# Save as JSON
import json
json_file = 'data/validation/agency_ministry_mapping.json'
with open(json_file, 'w') as f:
    json.dump(lookup_dict, f, indent=2)
print(f"Saved {len(lookup_dict)} agency-ministry mappings to {json_file}")
