# Synthetic Data Usage Documentation

## Purpose

Synthetic data in the PAIMANA project is **exclusively for testing purposes**.
Real PAIMANA data is the primary ML dataset for production development.

## Synthetic Data Location

- `data/synthetic/` - Contains synthetic project data
- Used for: unit tests, frontend smoke tests, integration tests
- **NOT** used for: model training, validation, or production predictions

## Real Data Location

- `data/REPORTS 25/` - Real PAIMANA Flash Reports 2025
- `data/REPORTS 26/` - Real PAIMANA Flash Reports 2026
- `data/extracted/` - Tables extracted from real PDFs
- `data/processed/` - Processed real data (normalized, longitudinal)
- `data/validation/` - Validated real data (quality-gated, conflicts resolved)
- `data/training/` - Training datasets from real data

## Separation Policy

1. **Never mix synthetic and real data** in training sets
2. **Never use synthetic data for model evaluation** on real performance
3. **Never claim synthetic results as real data results**
4. **Clearly label all dashboards** using synthetic data with "SYNTHETIC DATA - FOR TESTING ONLY"

## Test Usage

Synthetic data is appropriate for:

- **Unit tests**: Testing individual functions without real data dependencies
- **Frontend smoke tests**: Verifying UI renders correctly with sample data
- **Integration tests**: Testing API endpoints with predictable data
- **Pipeline validation**: Testing ingestion pipeline structure

## Real Data Usage

Real PAIMANA data is used for:

- **Model training**: All ML models trained on real data only
- **Validation**: All validation metrics computed on real data only
- **Production predictions**: All production predictions use real data
- **Performance reporting**: All performance metrics based on real data

## Compliance

All dashboards, reports, and documentation must clearly distinguish:

- **SYNTHETIC DATA**: For testing/development only
- **REAL DATA**: For production/modeling

Any confusion between synthetic and real data must be explicitly resolved before deployment.
