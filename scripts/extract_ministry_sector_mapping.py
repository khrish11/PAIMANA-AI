import pandas as pd
import glob
import os
from collections import defaultdict

# Find all table1 files that contain sector information
table1_files = glob.glob('data/extracted/*_table1.csv')

ministry_to_sectors = defaultdict(set)
all_mappings = []

for f in table1_files:
    try:
        df = pd.read_csv(f)
        cols = df.columns.tolist()
        
        # Check if this file has the ministry-sector structure
        if 'Allocated To' in cols and 'Sector' in cols:
            print(f"Processing: {os.path.basename(f)}")
            
            for _, row in df.iterrows():
                ministry = str(row.get('Allocated To', '')).strip()
                sector = str(row.get('Sector', '')).strip()
                
                # Skip empty rows and totals
                if ministry and ministry != 'nan' and ministry != 'Total':
                    if sector and sector != 'nan' and sector != 'Total':
                        ministry_to_sectors[ministry].add(sector)
                        all_mappings.append({
                            'ministry': ministry,
                            'sector': sector,
                            'source_file': os.path.basename(f)
                        })
    except Exception as e:
        print(f"Error processing {f}: {e}")

# Create mapping DataFrame
mapping_df = pd.DataFrame(all_mappings)

# Save to CSV
output_dir = 'data/validation'
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, 'ministry_sector_mapping.csv')
mapping_df.to_csv(output_file, index=False)

print(f"\nSaved {len(mapping_df)} mappings to {output_file}")
print(f"\nUnique ministries: {len(ministry_to_sectors)}")
print(f"\nMinistry to sectors mapping:")
for ministry, sectors in sorted(ministry_to_sectors.items()):
    print(f"  {ministry}: {', '.join(sorted(sectors))}")
