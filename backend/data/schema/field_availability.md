# Field Availability Notes

The SRS marks several useful fields as not yet established or needing audit before modelling:

- Actual final cost: critical for supervised cost-overrun labels.
- Actual completion date: critical for supervised schedule-delay labels.
- Contractor ID or contractor information: high-priority P1 field; approximate only if unavailable and flag the limitation.
- Land acquisition status: high-priority P1 field; do not assume availability.
- Scope change or variation order records: high-priority P1 field; use revised-cost count as a proxy only with a limitation flag.
- Location below state level: medium-priority P1 field; enrich only when reliable.

Until real data confirms these fields, code must degrade gracefully and label derived thresholds, weights, and performance figures as proposed pending calibration on real data.
