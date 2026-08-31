import pandas as pd
import os

# Load the extracted mapping
mapping_df = pd.read_csv('data/validation/ministry_sector_mapping.csv')

# Clean up ministry names (remove extra whitespace and normalize line breaks)
mapping_df['ministry'] = mapping_df['ministry'].str.replace(r'\s+', ' ', regex=True).str.strip()

# Get unique ministry-sector combinations
canonical_mapping = mapping_df[['ministry', 'sector']].drop_duplicates().sort_values(['ministry', 'sector'])

# Save canonical mapping
output_file = 'data/validation/ministry_sector_mapping_canonical.csv'
canonical_mapping.to_csv(output_file, index=False)

print(f"Saved {len(canonical_mapping)} canonical mappings to {output_file}")
print(f"\nCanonical Ministry to Sector Mappings:")
print("=" * 80)

# Group by ministry and show sectors
for ministry, group in canonical_mapping.groupby('ministry'):
    sectors = ', '.join(sorted(group['sector'].unique()))
    print(f"{ministry}: {sectors}")

# Also create a simple lookup dictionary for the import script
lookup_dict = {}
for ministry, group in canonical_mapping.groupby('ministry'):
    lookup_dict[ministry] = list(sorted(group['sector'].unique()))

# Save as JSON for easy loading
import json
json_file = 'data/validation/ministry_sector_mapping.json'
with open(json_file, 'w') as f:
    json.dump(lookup_dict, f, indent=2)

print(f"\nSaved lookup dictionary to {json_file}")
