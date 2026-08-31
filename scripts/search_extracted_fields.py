import os
import pandas as pd
import glob

files = glob.glob('data/extracted/*.csv')
print(f'Total CSV files: {len(files)}')

sector_count = 0
ministry_count = 0
narrative_count = 0
sector_files = []
ministry_files = []
narrative_files = []

for f in files[:100]:  # Check first 100 files
    try:
        df = pd.read_csv(f, nrows=1)
        cols = df.columns.tolist()
        cols_lower = [c.lower() for c in cols]
        
        if 'sector' in cols_lower:
            sector_count += 1
            sector_files.append(os.path.basename(f))
        
        if 'ministry' in cols_lower:
            ministry_count += 1
            ministry_files.append(os.path.basename(f))
        
        if any('narrative' in c or 'remark' in c or 'observation' in c or 'reason' in c for c in cols_lower):
            narrative_count += 1
            narrative_files.append(os.path.basename(f))
    except Exception as e:
        pass

print(f'\nFiles with sector: {sector_count}')
if sector_files:
    print(f'Sample: {sector_files[:5]}')

print(f'\nFiles with ministry: {ministry_count}')
if ministry_files:
    print(f'Sample: {ministry_files[:5]}')

print(f'\nFiles with narrative/remark/observation/reason: {narrative_count}')
if narrative_files:
    print(f'Sample: {narrative_files[:5]}')
