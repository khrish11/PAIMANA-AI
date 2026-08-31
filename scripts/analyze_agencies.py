import pandas as pd
import re
from collections import Counter

# Load normalized data
df = pd.read_csv('data/processed/all_projects_normalized.csv')

# Extract clean agency names
def clean_agency(agency_str):
    if pd.isna(agency_str) or agency_str == '':
        return 'Unknown'
    
    # Remove trailing codes and parentheses
    # Pattern: NHIDCL N24002025) (- → NHIDCL
    agency_str = str(agency_str).strip()
    
    # Remove trailing codes in parentheses
    agency_str = re.sub(r'\s*\([^)]+\)\s*$', '', agency_str)
    
    # Remove trailing numbers
    agency_str = re.sub(r'\s*\d+$', '', agency_str)
    
    # Remove any remaining parentheses content
    agency_str = re.sub(r'\s*\([^)]+\)', '', agency_str)
    
    agency_str = agency_str.strip()
    
    if not agency_str or len(agency_str) < 2:
        return 'Unknown'
    
    return agency_str

# Apply cleaning
df['clean_agency'] = df['agency'].apply(clean_agency)

# Count agencies
agency_counts = Counter(df['clean_agency'].tolist())

print(f"Found {len(agency_counts)} unique agencies")
print(f"\nTop 50 agencies by frequency:")
for agency, count in agency_counts.most_common(50):
    print(f"  {agency}: {count}")

# Save cleaned agency data
output_file = 'data/validation/agency_analysis.csv'
df[['project_id', 'agency', 'clean_agency']].to_csv(output_file, index=False)
print(f"\nSaved agency analysis to {output_file}")

# Create agency list for manual ministry mapping
unique_agencies = sorted([a for a in agency_counts.keys() if a != 'Unknown'])
agency_list_file = 'data/validation/unique_agencies.txt'
with open(agency_list_file, 'w') as f:
    for agency in unique_agencies:
        f.write(f"{agency}\n")
print(f"Saved {len(unique_agencies)} unique agencies to {agency_list_file}")
