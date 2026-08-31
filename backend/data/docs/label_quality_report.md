# Label Quality Report
Generated: 2026-08-28T21:24:42.052521

## Summary
- Total labeled projects: 1659
- Valid cost labels: 160
- Valid schedule labels: 160
- Excluded labels (invalid): 1499
- Cost leakage detected: 0
- Schedule leakage detected: 0

## Label Definitions

### Cost Label
- **Definition**: Final cumulative expenditure for completed projects (100% progress)
- **Validity**: Final expenditure must be available and comparable to revised cost
- **Leakage Check**: Final cost must not be used as a feature for prediction

### Schedule Label
- **Definition**: Actual completion date or delay against original target
- **Validity**: Completion date and approval date must be available
- **Leakage Check**: Completion date must not be used as a feature for prediction

## Possible Leakage Sources

### Structural Leakage
- Using final cost/expenditure as feature for cost prediction
- Using completion date as feature for schedule prediction
- Using future period values in historical features

### Temporal Leakage
- Features from period N+1 used to predict period N
- Rolling windows that include future data
- Target leakage through correlated features

## Recommendations

1. **Feature Engineering**: Ensure all features are as-of-date only
2. **Temporal Splitting**: Use time-series CV, not random splits
3. **Label Construction**: Separate label construction from feature pipeline
4. **Validation**: Automated leakage tests before training

## Label Quality by Project

| Project ID | Cost Valid | Schedule Valid | Observations |
|------------|------------|----------------|--------------|
| jabalpur sewerage management and treatment infrastructure project 702798|madhya pradesh | ✗ | ✗ | 1 |
| 705663 | ✗ | ✗ | 13 |
| 618434 | ✗ | ✗ | 8 |
| 618880 | ✗ | ✗ | 6 |
| 618019 | ✗ | ✗ | 8 |
| 618462 | ✓ | ✓ | 8 |
| construction of aviation fuel farm facilities at bhogapuram airport 616235|andhra pradesh | ✗ | ✗ | 1 |
| 618610 | ✗ | ✗ | 7 |
| 701991 | ✗ | ✗ | 13 |
| 618864 | ✓ | ✓ | 6 |
| 618600 | ✓ | ✓ | 8 |
| 400313 | ✗ | ✗ | 9 |
| 618358 | ✗ | ✗ | 16 |
| 618545 | ✗ | ✗ | 8 |
| 618166 | ✓ | ✓ | 8 |
| third railway line between patratu-sonnagar [291 kms] 400234|multi-states (bihar, jharkhand) | ✗ | ✗ | 1 |
| 602535 | ✗ | ✗ | 13 |
| upgradation of sewerage system in gandhinagar city 707267|gujarat | ✗ | ✗ | 1 |
| 707049 | ✗ | ✗ | 7 |
| 618387 | ✗ | ✗ | 16 |
| 618700 | ✗ | ✗ | 8 |
| 612786 | ✗ | ✗ | 13 |
| 701344 | ✗ | ✗ | 12 |
| 617251 | ✗ | ✗ | 13 |
| 619013 | ✗ | ✗ | 14 |
| 618597 | ✗ | ✗ | 8 |
| 616612 | ✗ | ✗ | 12 |
| 618715 | ✗ | ✗ | 8 |
| 618712 | ✗ | ✗ | 8 |
| 618505 | ✗ | ✗ | 7 |
| 705244 | ✗ | ✗ | 13 |
| 618063 | ✗ | ✗ | 7 |
| 618237 | ✗ | ✗ | 6 |
| 705784 | ✗ | ✗ | 5 |
| 619089 | ✗ | ✗ | 7 |
| 705512 | ✗ | ✗ | 13 |
| 706988 | ✗ | ✗ | 3 |
| 618292 | ✗ | ✗ | 8 |
| 617924 | ✓ | ✓ | 5 |
| 400369 | ✗ | ✗ | 13 |
| 705588 | ✗ | ✗ | 13 |
| delhi-amritsar-katra expressway phase-i pkg-iv from junction with jind-karnal road nh-709a near alewa village to junction with ambala-kaithal-hissar road nh-152 near kharak pandwa village km 91400 to km 120250 618485|haryana | ✗ | ✗ | 1 |
| 705502 | ✗ | ✗ | 13 |
| 619211 | ✗ | ✗ | 6 |
| 618392 | ✗ | ✗ | 7 |
| 618258 | ✗ | ✗ | 6 |
| 701719 | ✗ | ✗ | 11 |
| 619083 | ✓ | ✓ | 6 |
| 4l of left out existing road section from lalgopalganj km 161.450 to nawabganj km 180.200 in prayagraj 618755|multi-states (rajasthan, uttar pradesh) | ✗ | ✗ | 1 |
| 618099 | ✓ | ✓ | 4 |
| ... | ... | ... | ... (1609 more) |