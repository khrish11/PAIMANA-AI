import pandas as pd
import glob
import os
from collections import Counter

# Find all table0 files (project-level data)
table0_files = glob.glob('data/extracted/*_table0.csv')

agencies = []
agency_samples = []

for f in table0_files[:50]:  # Check first 50 files
    try:
        df = pd.read_csv(f)
        cols = df.columns.tolist()
        
        # Check if this file has project data
        if 'Project Name' in cols:
            print(f"Processing: {os.path.basename(f)}")
            
            for _, row in df.iterrows():
                project_name = str(row.get('Project Name', ''))
                # Extract agency from project name (usually in parentheses)
                # Pattern: (Agency) or (Agency) (Code)
                import re
                matches = re.findall(r'\(([^)]+)\)', project_name)
                if matches:
                    # First match is usually the agency
                    agency = matches[0].strip()
                    # Remove any codes or extra info
                    agency = re.sub(r'\s*\([^)]+\)$', '', agency)  # Remove trailing (code)
                    agency = re.sub(r'\s*\d+$', '', agency)  # Remove trailing numbers
                    agency = agency.strip()
                    
                    if agency and len(agency) > 2:  # Filter out very short matches
                        agencies.append(agency)
                        if len(agency_samples) < 100:  # Collect samples
                            agency_samples.append({
                                'agency': agency,
                                'project_name': project_name[:100],
                                'source_file': os.path.basename(f)
                            })
    except Exception as e:
        print(f"Error processing {f}: {e}")

# Count agency occurrences
agency_counts = Counter(agencies)

print(f"\nFound {len(agency_counts)} unique agencies")
print(f"\nTop 50 agencies by frequency:")
for agency, count in agency_counts.most_common(50):
    print(f"  {agency}: {count}")

# Save samples
samples_df = pd.DataFrame(agency_samples)
output_file = 'data/validation/agency_samples.csv'
samples_df.to_csv(output_file, index=False)
print(f"\nSaved {len(samples_df)} agency samples to {output_file}")
